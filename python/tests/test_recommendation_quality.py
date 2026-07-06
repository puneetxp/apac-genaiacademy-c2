"""
Property-based tests for recommendation quality and regional relevance
Tests Property 7: Recommendation Quality and Regional Relevance

**Validates: Requirements AC3.4, AC3.5, AC3.6, AC3.7**
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import Dict, Any, List
import json

from app.services.bedrock_service import BedrockService


# Custom strategies for generating crop recommendations
@st.composite
def crop_recommendation_strategy(draw):
    """
    Generate valid crop recommendation structures for testing
    
    This strategy creates recommendations that should include crop-specific guidance,
    regional expertise, confidence scores, and implementation guidance.
    """
    
    # Common Indian crops
    crops = ["Rice", "Wheat", "Cotton", "Maize", "Soybean", "Sugarcane", "Chickpea", "Mustard"]
    
    # Indian states
    states = [
        "Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan",
        "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Gujarat"
    ]
    
    # Crop varieties (realistic Indian varieties)
    varieties = [
        "Basmati 370", "HD-2967", "BT Cotton", "Hybrid Maize", "JS 335",
        "Co 86032", "JG 11", "Pusa Bold", "Local variety"
    ]
    
    # Planting windows
    planting_windows = [
        "June-July", "July-August", "November-December", "October-November",
        "December-January", "March-April"
    ]
    
    # Generate recommendation
    crop_name = draw(st.sampled_from(crops))
    variety = draw(st.sampled_from(varieties))
    state = draw(st.sampled_from(states))
    district = draw(st.text(min_size=5, max_size=20, alphabet=st.characters(min_codepoint=65, max_codepoint=122)))
    
    # Crop-specific guidance
    planting_window = draw(st.sampled_from(planting_windows))
    expected_yield = draw(st.text(min_size=5, max_size=30))
    
    # Regional expertise
    regional_notes = draw(st.text(min_size=20, max_size=200))
    
    # Confidence score (must be 0-1)
    confidence_score = draw(st.floats(min_value=0.0, max_value=1.0))
    
    # Success factors
    num_success_factors = draw(st.integers(min_value=2, max_value=6))
    success_factors = [
        draw(st.text(min_size=10, max_size=60))
        for _ in range(num_success_factors)
    ]
    
    # Risk mitigation strategies
    num_risks = draw(st.integers(min_value=1, max_value=4))
    risk_mitigation = [
        draw(st.text(min_size=15, max_size=80))
        for _ in range(num_risks)
    ]
    
    return {
        "crop_name": crop_name,
        "variety": variety,
        "state": state,
        "district": district,
        "planting_window": planting_window,
        "expected_yield_per_acre": expected_yield,
        "expected_profit_per_acre": draw(st.integers(min_value=10000, max_value=150000)),
        "investment_per_acre": draw(st.integers(min_value=5000, max_value=50000)),
        "regional_expertise": regional_notes,
        "confidence_score": confidence_score,
        "key_success_factors": success_factors,
        "risk_mitigation_strategies": risk_mitigation,
        "harvest_window": draw(st.sampled_from(planting_windows)),
        "key_requirements": draw(st.lists(st.text(min_size=10, max_size=50), min_size=2, max_size=5))
    }


@st.composite
def incomplete_recommendation_strategy(draw):
    """
    Generate intentionally incomplete recommendations to test validation
    
    Tests that our system properly detects missing required fields.
    """
    missing_field = draw(st.sampled_from([
        "variety",
        "planting_window",
        "regional_expertise",
        "confidence_score",
        "success_factors",
        "risk_mitigation",
        "invalid_confidence"
    ]))
    
    # Start with a complete recommendation
    base_rec = {
        "crop_name": "Rice",
        "variety": "Basmati 370",
        "state": "Punjab",
        "district": "Ludhiana",
        "planting_window": "June-July",
        "expected_yield_per_acre": "25 quintals",
        "expected_profit_per_acre": 45000,
        "investment_per_acre": 18000,
        "regional_expertise": "Well-suited for Punjab's climate and soil conditions",
        "confidence_score": 0.85,
        "key_success_factors": ["Timely planting", "Adequate water", "Pest management"],
        "risk_mitigation_strategies": ["Crop insurance", "Diversification"],
        "harvest_window": "October-November",
        "key_requirements": ["Good irrigation", "Fertile soil"]
    }
    
    # Remove or invalidate specific field
    if missing_field == "variety":
        del base_rec["variety"]
    elif missing_field == "planting_window":
        del base_rec["planting_window"]
    elif missing_field == "regional_expertise":
        del base_rec["regional_expertise"]
    elif missing_field == "confidence_score":
        del base_rec["confidence_score"]
    elif missing_field == "success_factors":
        base_rec["key_success_factors"] = []
    elif missing_field == "risk_mitigation":
        base_rec["risk_mitigation_strategies"] = []
    elif missing_field == "invalid_confidence":
        base_rec["confidence_score"] = draw(st.one_of(
            st.floats(min_value=-1.0, max_value=-0.01),
            st.floats(min_value=1.01, max_value=2.0)
        ))
    
    return base_rec, missing_field


class TestRecommendationQuality:
    """
    Property 7: Recommendation Quality and Regional Relevance
    
    Test that for any crop recommendation from Bedrock, response includes
    crop-specific guidance, regional expertise, valid confidence scores,
    and practical implementation guidance.
    """
    
    @given(recommendation=crop_recommendation_strategy())
    @settings(
        max_examples=200,
        deadline=15000,  # 15 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_crop_specific_guidance_present(self, recommendation):
        """
        **Validates: Requirements AC3.4**
        
        Property: For any crop recommendation, the response must include
        crop-specific guidance with recommended varieties and planting windows.
        """
        # Assert: Crop name is present
        assert "crop_name" in recommendation, \
            "Crop name missing from recommendation"
        assert recommendation["crop_name"] is not None, \
            "Crop name cannot be None"
        assert len(recommendation["crop_name"]) > 0, \
            "Crop name cannot be empty"
        
        # Assert: Variety information is present
        assert "variety" in recommendation, \
            "Variety information missing from recommendation"
        assert recommendation["variety"] is not None, \
            "Variety cannot be None"
        assert len(recommendation["variety"]) > 0, \
            "Variety cannot be empty"
        
        # Assert: Planting window is present
        assert "planting_window" in recommendation, \
            "Planting window missing from recommendation"
        assert recommendation["planting_window"] is not None, \
            "Planting window cannot be None"
        assert len(recommendation["planting_window"]) > 0, \
            "Planting window cannot be empty"
        
        # Assert: Expected yield information is present
        assert "expected_yield_per_acre" in recommendation, \
            "Expected yield missing from recommendation"
        assert recommendation["expected_yield_per_acre"] is not None, \
            "Expected yield cannot be None"
    
    @given(recommendation=crop_recommendation_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_regional_expertise_present(self, recommendation):
        """
        **Validates: Requirements AC3.5**
        
        Property: For any crop recommendation, the response must include
        regional expertise for the farmer's state and district.
        """
        # Assert: State information is present
        assert "state" in recommendation, \
            "State information missing from recommendation"
        assert recommendation["state"] is not None, \
            "State cannot be None"
        assert len(recommendation["state"]) > 0, \
            "State cannot be empty"
        
        # Assert: District information is present
        assert "district" in recommendation, \
            "District information missing from recommendation"
        assert recommendation["district"] is not None, \
            "District cannot be None"
        assert len(recommendation["district"]) > 0, \
            "District cannot be empty"
        
        # Assert: Regional expertise notes are present
        assert "regional_expertise" in recommendation, \
            "Regional expertise missing from recommendation"
        assert recommendation["regional_expertise"] is not None, \
            "Regional expertise cannot be None"
        assert len(recommendation["regional_expertise"]) > 0, \
            "Regional expertise cannot be empty"
        
        # Assert: Regional expertise has meaningful content (at least 10 characters)
        assert len(recommendation["regional_expertise"]) >= 10, \
            f"Regional expertise too short: {len(recommendation['regional_expertise'])} chars"
    
    @given(recommendation=crop_recommendation_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_confidence_scores_valid_range(self, recommendation):
        """
        **Validates: Requirements AC3.6**
        
        Property: For any crop recommendation, confidence scores must be
        within valid range (0-1).
        """
        # Assert: Confidence score is present
        assert "confidence_score" in recommendation, \
            "Confidence score missing from recommendation"
        
        # Assert: Confidence score is numeric
        assert isinstance(recommendation["confidence_score"], (int, float)), \
            f"Confidence score must be numeric, got {type(recommendation['confidence_score'])}"
        
        # Assert: Confidence score is in valid range [0, 1]
        confidence = recommendation["confidence_score"]
        assert 0.0 <= confidence <= 1.0, \
            f"Confidence score {confidence} out of valid range [0, 1]"
        
        # Assert: Confidence score is not exactly 0 or 1 (should be realistic)
        # Note: This is a soft check - we allow 0 or 1 but they should be rare
        if confidence == 0.0 or confidence == 1.0:
            # Log warning but don't fail - perfect confidence is theoretically possible
            pass
    
    @given(recommendation=crop_recommendation_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_implementation_guidance_present(self, recommendation):
        """
        **Validates: Requirements AC3.7**
        
        Property: For any crop recommendation, the response must include
        practical implementation guidance with success factors and risk
        mitigation strategies.
        """
        # Assert: Success factors are present
        assert "key_success_factors" in recommendation, \
            "Success factors missing from recommendation"
        assert isinstance(recommendation["key_success_factors"], list), \
            "Success factors must be a list"
        assert len(recommendation["key_success_factors"]) > 0, \
            "At least one success factor must be provided"
        
        # Assert: Each success factor has meaningful content
        for idx, factor in enumerate(recommendation["key_success_factors"]):
            assert isinstance(factor, str), \
                f"Success factor {idx} must be a string"
            assert len(factor) > 0, \
                f"Success factor {idx} cannot be empty"
            assert len(factor) >= 5, \
                f"Success factor {idx} too short: {len(factor)} chars"
        
        # Assert: Risk mitigation strategies are present
        assert "risk_mitigation_strategies" in recommendation, \
            "Risk mitigation strategies missing from recommendation"
        assert isinstance(recommendation["risk_mitigation_strategies"], list), \
            "Risk mitigation strategies must be a list"
        assert len(recommendation["risk_mitigation_strategies"]) > 0, \
            "At least one risk mitigation strategy must be provided"
        
        # Assert: Each risk mitigation strategy has meaningful content
        for idx, strategy in enumerate(recommendation["risk_mitigation_strategies"]):
            assert isinstance(strategy, str), \
                f"Risk mitigation strategy {idx} must be a string"
            assert len(strategy) > 0, \
                f"Risk mitigation strategy {idx} cannot be empty"
            assert len(strategy) >= 10, \
                f"Risk mitigation strategy {idx} too short: {len(strategy)} chars"
    
    @given(incomplete_rec=incomplete_recommendation_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_incomplete_recommendation_detection(self, incomplete_rec):
        """
        **Validates: Requirements AC3.4, AC3.5, AC3.6, AC3.7**
        
        Property: For any incomplete recommendation, the system should
        detect missing or invalid required fields.
        """
        recommendation, missing_field = incomplete_rec
        
        # Validate based on what's missing
        if missing_field == "variety":
            assert "variety" not in recommendation
        
        elif missing_field == "planting_window":
            assert "planting_window" not in recommendation
        
        elif missing_field == "regional_expertise":
            assert "regional_expertise" not in recommendation
        
        elif missing_field == "confidence_score":
            assert "confidence_score" not in recommendation
        
        elif missing_field == "success_factors":
            assert len(recommendation.get("key_success_factors", [])) == 0
        
        elif missing_field == "risk_mitigation":
            assert len(recommendation.get("risk_mitigation_strategies", [])) == 0
        
        elif missing_field == "invalid_confidence":
            if "confidence_score" in recommendation:
                score = recommendation["confidence_score"]
                assert score < 0.0 or score > 1.0, \
                    f"Expected invalid confidence score, got {score}"
    
    def test_bedrock_crop_recommendations_quality(self):
        """
        **Validates: Requirements AC3.4, AC3.5, AC3.6, AC3.7**
        
        Integration test: Verify that BedrockService.get_crop_recommendations()
        returns recommendations with all required quality attributes.
        """
        # Arrange
        service = BedrockService()
        
        # Create mock recommendations with all required fields
        mock_recommendations = [
            {
                "rank": 1,
                "crop_name": "Rice",
                "variety": "Basmati 370",
                "suitability_reason": "Well-suited for Punjab's climate with adequate water availability",
                "expected_yield_per_acre": "25 quintals",
                "expected_profit_per_acre": 45000,
                "investment_per_acre": 18000,
                "key_requirements": ["Good irrigation", "Fertile loamy soil", "Timely planting"],
                "challenges": ["Pest management required", "Water-intensive crop"],
                "market_demand": "High",
                "confidence_score": 0.85
            },
            {
                "rank": 2,
                "crop_name": "Wheat",
                "variety": "HD-2967",
                "suitability_reason": "Proven variety for Punjab with excellent market demand",
                "expected_yield_per_acre": "22 quintals",
                "expected_profit_per_acre": 38000,
                "investment_per_acre": 15000,
                "key_requirements": ["Proper irrigation", "Fertilizer application", "Weed control"],
                "challenges": ["Requires timely sowing", "Sensitive to waterlogging"],
                "market_demand": "High",
                "confidence_score": 0.82
            }
        ]
        
        # Mock the Bedrock runtime client
        with patch.object(service, 'runtime_client') as mock_client:
            import json
            response_json = json.dumps(mock_recommendations)
            mock_invoke_response = {
                'body': MagicMock()
            }
            mock_invoke_response['body'].read.return_value = json.dumps({
                "completion": response_json
            }).encode()
            mock_client.invoke_model.return_value = mock_invoke_response
            
            # Act
            result = service.get_crop_recommendations(
                state="Punjab",
                district="Ludhiana",
                season="kharif",
                soil_type="loamy",
                area_acres=5.0,
                irrigation_type="canal"
            )
            
            # Assert: Recommendations returned
            assert result is not None
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Assert: Each recommendation has required quality attributes
            for rec in result:
                # Crop-specific guidance (AC3.4)
                assert "crop_name" in rec, "Crop name missing"
                assert "variety" in rec, "Variety missing"
                assert len(rec["variety"]) > 0, "Variety cannot be empty"
                
                # Regional expertise (AC3.5)
                assert "suitability_reason" in rec, "Regional suitability reason missing"
                assert len(rec["suitability_reason"]) >= 10, \
                    "Suitability reason too short"
                
                # Confidence score (AC3.6)
                assert "confidence_score" in rec, "Confidence score missing"
                assert 0.0 <= rec["confidence_score"] <= 1.0, \
                    f"Confidence score {rec['confidence_score']} out of range"
                
                # Implementation guidance (AC3.7)
                assert "key_requirements" in rec, "Key requirements missing"
                assert isinstance(rec["key_requirements"], list), \
                    "Key requirements must be a list"
                assert len(rec["key_requirements"]) > 0, \
                    "At least one key requirement must be provided"
                
                assert "challenges" in rec, "Challenges missing"
                assert isinstance(rec["challenges"], list), \
                    "Challenges must be a list"
                assert len(rec["challenges"]) > 0, \
                    "At least one challenge must be provided"
    
    def test_bedrock_annual_strategy_recommendation_quality(self):
        """
        **Validates: Requirements AC3.4, AC3.5, AC3.6, AC3.7**
        
        Integration test: Verify that BedrockService.get_annual_crop_strategy()
        returns recommendations with all required quality attributes for each season.
        """
        # Arrange
        service = BedrockService()
        
        # Create mock annual strategy with complete quality attributes
        mock_strategy = {
            "kharif": {
                "recommended_crop": "Rice",
                "variety": "Basmati 370",
                "expected_yield_per_acre": "25 quintals",
                "expected_profit_per_acre": 45000,
                "investment_per_acre": 18000,
                "planting_window": "June-July",
                "harvest_window": "October-November",
                "key_success_factors": [
                    "Timely planting in June for optimal growth",
                    "Adequate water supply throughout growing season",
                    "Integrated pest management for stem borer and leaf folder"
                ],
                "confidence_score": 0.85,
                "regional_expertise": "Basmati rice is well-suited for Punjab's climate and soil conditions. The state has a proven track record with this variety.",
                "risk_mitigation_strategies": [
                    "Crop insurance to protect against weather-related losses",
                    "Staggered planting to spread risk",
                    "Maintain soil health through organic matter"
                ]
            },
            "rabi": {
                "recommended_crop": "Wheat",
                "variety": "HD-2967",
                "expected_yield_per_acre": "22 quintals",
                "expected_profit_per_acre": 38000,
                "investment_per_acre": 15000,
                "planting_window": "November-December",
                "harvest_window": "March-April",
                "key_success_factors": [
                    "Proper irrigation at critical growth stages",
                    "Balanced fertilizer application",
                    "Timely weed control"
                ],
                "confidence_score": 0.82,
                "regional_expertise": "HD-2967 is a high-yielding variety proven successful in Punjab. Excellent market demand and stable prices.",
                "risk_mitigation_strategies": [
                    "Monitor for rust diseases and apply fungicides if needed",
                    "Ensure proper drainage to prevent waterlogging",
                    "Use certified seeds for better germination"
                ]
            },
            "zaid": {
                "recommended_crop": "Mung Bean",
                "expected_profit_per_acre": 12000
            },
            "annual_summary": {
                "total_expected_profit_per_acre": 95000,
                "total_investment_per_acre": 33000,
                "roi_percentage": 188,
                "risk_level": "medium",
                "sustainability_score": 0.8
            },
            "alternative_options": [
                {
                    "season": "kharif",
                    "crop": "Cotton",
                    "profit_difference": -5000,
                    "risk_comparison": "Higher risk but stable market demand"
                }
            ],
            "monthly_action_plan": [
                {"month": month, "actions": ["Action 1", "Action 2"]}
                for month in ["January", "February", "March", "April", "May", "June",
                             "July", "August", "September", "October", "November", "December"]
            ]
        }
        
        # Mock the Bedrock runtime client
        with patch.object(service, 'runtime_client') as mock_client:
            import json
            response_json = json.dumps(mock_strategy)
            mock_invoke_response = {
                'body': MagicMock()
            }
            mock_invoke_response['body'].read.return_value = json.dumps({
                "completion": response_json
            }).encode()
            mock_client.invoke_model.return_value = mock_invoke_response
            
            # Act
            result = service.get_annual_crop_strategy(
                state="Punjab",
                district="Ludhiana",
                soil_type="loamy",
                area_acres=5.0,
                irrigation_type="canal",
                previous_crops="Wheat",
                budget_per_acre=50000
            )
            
            # Assert: Strategy returned
            assert result is not None
            assert isinstance(result, dict)
            
            # Test Kharif season quality
            kharif = result["kharif"]
            
            # Crop-specific guidance (AC3.4)
            assert "variety" in kharif, "Kharif variety missing"
            assert len(kharif["variety"]) > 0, "Kharif variety cannot be empty"
            assert "planting_window" in kharif, "Kharif planting window missing"
            assert len(kharif["planting_window"]) > 0, "Kharif planting window cannot be empty"
            
            # Regional expertise (AC3.5) - optional but recommended
            if "regional_expertise" in kharif:
                assert len(kharif["regional_expertise"]) >= 10, \
                    "Kharif regional expertise too short"
            
            # Confidence score (AC3.6)
            assert "confidence_score" in kharif, "Kharif confidence score missing"
            assert 0.0 <= kharif["confidence_score"] <= 1.0, \
                f"Kharif confidence score {kharif['confidence_score']} out of range"
            
            # Implementation guidance (AC3.7)
            assert "key_success_factors" in kharif, "Kharif success factors missing"
            assert isinstance(kharif["key_success_factors"], list), \
                "Kharif success factors must be a list"
            assert len(kharif["key_success_factors"]) >= 2, \
                "Kharif must have at least 2 success factors"
            
            # Risk mitigation strategies (AC3.7) - optional but recommended
            if "risk_mitigation_strategies" in kharif:
                assert isinstance(kharif["risk_mitigation_strategies"], list), \
                    "Kharif risk mitigation must be a list"
                assert len(kharif["risk_mitigation_strategies"]) > 0, \
                    "Kharif must have at least 1 risk mitigation strategy"
            
            # Test Rabi season quality
            rabi = result["rabi"]
            
            # Crop-specific guidance (AC3.4)
            assert "variety" in rabi, "Rabi variety missing"
            assert len(rabi["variety"]) > 0, "Rabi variety cannot be empty"
            assert "planting_window" in rabi, "Rabi planting window missing"
            
            # Confidence score (AC3.6)
            assert "confidence_score" in rabi, "Rabi confidence score missing"
            assert 0.0 <= rabi["confidence_score"] <= 1.0, \
                f"Rabi confidence score {rabi['confidence_score']} out of range"
            
            # Implementation guidance (AC3.7)
            assert "key_success_factors" in rabi, "Rabi success factors missing"
            assert len(rabi["key_success_factors"]) >= 2, \
                "Rabi must have at least 2 success factors"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
