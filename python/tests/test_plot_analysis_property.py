"""
Property-based tests for plot analysis completeness
Tests Property 19: Plot Analysis Completeness

**Validates: Requirements AC7 (Smart Land Plot Management)**
"""

import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime

from app.services.plot_analysis_service import PlotAnalysisService
from app.orm.farm_plot import FarmPlot
from app.orm.soil_test_result import SoilTestResult


# Custom strategies for generating valid plot data
@st.composite
def plot_data_strategy(draw):
    """
    Generate valid plot data with soil and water information
    
    This strategy creates plots that should generate comprehensive analysis
    with all required fields.
    """
    
    # Indian states and districts
    states = [
        "Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan",
        "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Gujarat"
    ]
    
    districts = [
        "Ludhiana", "Amritsar", "Patiala", "Jalandhar", "Bathinda",
        "Karnal", "Hisar", "Panipat", "Agra", "Lucknow"
    ]
    
    soil_types = ["clay", "sandy", "loamy", "black", "red"]
    irrigation_types = ["Canal", "Borewell", "Rain-fed", "Mixed"]
    
    # Generate plot data
    plot_id = draw(st.integers(min_value=1, max_value=10000))
    plot_name = draw(st.text(min_size=5, max_size=30, alphabet=st.characters(min_codepoint=65, max_codepoint=122)))
    area = draw(st.floats(min_value=0.5, max_value=100.0))
    soil_type = draw(st.sampled_from(soil_types))
    irrigation_type = draw(st.sampled_from(irrigation_types))
    state = draw(st.sampled_from(states))
    district = draw(st.sampled_from(districts))
    
    # Generate soil test data
    ph_level = draw(st.floats(min_value=4.5, max_value=9.0))
    nitrogen = draw(st.floats(min_value=100.0, max_value=500.0))
    phosphorus = draw(st.floats(min_value=5.0, max_value=50.0))
    potassium = draw(st.floats(min_value=100.0, max_value=400.0))
    organic_matter = draw(st.floats(min_value=0.5, max_value=5.0))
    soil_health_score = draw(st.floats(min_value=40.0, max_value=100.0))
    
    # Create mock plot object
    plot = Mock(spec=FarmPlot)
    plot.id = plot_id
    plot.plot_name = plot_name
    plot.area = Decimal(str(area))
    plot.soil_type = soil_type
    plot.irrigation_type = irrigation_type
    plot.state = state
    plot.district = district
    plot.previous_crops = "[]"
    
    # Create mock soil test object
    soil_test = Mock(spec=SoilTestResult)
    soil_test.ph_level = Decimal(str(ph_level))
    soil_test.nitrogen_kg_per_ha = Decimal(str(nitrogen))
    soil_test.phosphorus_kg_per_ha = Decimal(str(phosphorus))
    soil_test.potassium_kg_per_ha = Decimal(str(potassium))
    soil_test.organic_matter_percent = Decimal(str(organic_matter))
    soil_test.soil_health_score = Decimal(str(soil_health_score))
    soil_test.test_date = datetime(2024, 1, 15)
    
    return plot, soil_test


@st.composite
def season_strategy(draw):
    """Generate valid season values"""
    return draw(st.sampled_from(["kharif", "rabi", "zaid"]))



@st.composite
def comprehensive_analysis_response_strategy(draw):
    """
    Generate comprehensive plot analysis response with all required fields
    
    This strategy creates analysis responses that should contain:
    - Suitability scores
    - Profitability metrics
    - Yield predictions
    - Quality grades
    """
    
    # Generate 3-5 crop recommendations
    num_crops = draw(st.integers(min_value=3, max_value=5))
    
    crops = []
    for rank in range(1, num_crops + 1):
        crop = {
            "rank": rank,
            "crop_name": draw(st.sampled_from(["Rice", "Wheat", "Cotton", "Maize", "Soybean"])),
            "variety": draw(st.text(min_size=5, max_size=30)),
            
            # Suitability scores (required)
            "suitability_score": draw(st.floats(min_value=0.0, max_value=10.0)),
            "soil_compatibility": draw(st.floats(min_value=0.0, max_value=10.0)),
            "water_match": draw(st.floats(min_value=0.0, max_value=10.0)),
            "climate_suitability": draw(st.floats(min_value=0.0, max_value=10.0)),
            
            # Profitability metrics (required)
            "investment_per_acre": draw(st.integers(min_value=5000, max_value=50000)),
            "expected_yield_per_acre": f"{draw(st.integers(min_value=15, max_value=30))}-{draw(st.integers(min_value=30, max_value=40))} quintals",
            "market_price_per_quintal": draw(st.integers(min_value=1500, max_value=5000)),
            "expected_revenue_per_acre": draw(st.integers(min_value=30000, max_value=150000)),
            "expected_profit_per_acre": draw(st.integers(min_value=10000, max_value=100000)),
            "roi_percentage": draw(st.floats(min_value=50.0, max_value=400.0)),
            "breakeven_yield": f"{draw(st.floats(min_value=5.0, max_value=15.0)):.1f} quintals",
            
            # Yield predictions (required)
            "planting_window": draw(st.sampled_from(["June-July", "November-December", "March-April"])),
            "harvest_window": draw(st.sampled_from(["October-November", "March-April", "June-July"])),
            "duration_days": draw(st.integers(min_value=90, max_value=180)),
            
            # Quality grades (required)
            "quality_grade": draw(st.sampled_from(["A", "B", "C"])),
            "quality_confidence": draw(st.floats(min_value=0.5, max_value=1.0)),
            "quality_factors": draw(st.lists(st.text(min_size=10, max_size=50), min_size=1, max_size=3)),
            
            # Additional fields
            "water_requirement": draw(st.sampled_from(["Low", "Medium", "High"])),
            "labor_requirement": draw(st.sampled_from(["Low", "Medium", "High"])),
            "demand_level": draw(st.sampled_from(["Low", "Medium", "High"])),
            "risk_probability": draw(st.sampled_from(["Low", "Medium", "High"])),
            "confidence_score": draw(st.floats(min_value=0.5, max_value=1.0))
        }
        crops.append(crop)
    
    return {
        "recommended_crops": crops,
        "annual_strategy": {
            "current_season_crop": crops[0]["crop_name"],
            "next_season_crop": draw(st.sampled_from(["Wheat", "Rice", "Vegetables"])),
            "total_annual_profit": draw(st.integers(min_value=50000, max_value=200000)),
            "annual_roi": draw(st.floats(min_value=150.0, max_value=400.0))
        },
        "plot_health": {
            "soil_health_score": draw(st.floats(min_value=40.0, max_value=100.0)),
            "water_resource_score": draw(st.floats(min_value=40.0, max_value=100.0)),
            "overall_suitability_score": draw(st.floats(min_value=40.0, max_value=100.0))
        }
    }



class TestPlotAnalysisCompleteness:
    """
    Property 19: Plot Analysis Completeness
    
    Test that for any valid plot with soil and water data, system generates
    comprehensive analysis with all required fields: suitability scores,
    profitability metrics, yield predictions, quality grades.
    
    Also validates response time < 10 seconds (95th percentile).
    """
    
    @given(
        plot_data=plot_data_strategy(),
        season=season_strategy(),
        analysis_response=comprehensive_analysis_response_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,  # 15 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_all_fields_present(
        self,
        plot_data,
        season,
        analysis_response
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any valid plot with soil and water data, the system
        generates comprehensive analysis with all required fields present.
        """
        plot, soil_test = plot_data
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)
        service.cache_manager = None  # Disable cache for testing
        
        # Mock the internal methods
        with patch.object(service, '_get_plot_details', return_value=plot), \
             patch.object(service, '_get_latest_soil_test', return_value=soil_test), \
             patch.object(service, '_analyze_with_bedrock', return_value=analysis_response):
            
            # Execute
            result = await service.analyze_plot(
                plot_id=plot.id,
                season=season,
                budget_per_acre=20000
            )
            
            # Assert: Basic response structure
            assert result is not None, "Analysis result cannot be None"
            assert "plot_id" in result, "plot_id missing from response"
            assert "plot_name" in result, "plot_name missing from response"
            assert "season" in result, "season missing from response"
            assert "recommended_crops" in result, "recommended_crops missing from response"
            
            # Assert: Recommended crops is a list with at least one crop
            assert isinstance(result["recommended_crops"], list), \
                "recommended_crops must be a list"
            assert len(result["recommended_crops"]) > 0, \
                "At least one crop recommendation must be provided"
            
            # Test each crop recommendation for completeness
            for idx, crop in enumerate(result["recommended_crops"]):
                # Suitability scores (required)
                assert "suitability_score" in crop, \
                    f"Crop {idx}: suitability_score missing"
                assert isinstance(crop["suitability_score"], (int, float)), \
                    f"Crop {idx}: suitability_score must be numeric"
                assert 0.0 <= crop["suitability_score"] <= 10.0, \
                    f"Crop {idx}: suitability_score {crop['suitability_score']} out of range [0, 10]"
                
                # Profitability metrics (required)
                assert "investment_per_acre" in crop, \
                    f"Crop {idx}: investment_per_acre missing"
                assert "expected_revenue_per_acre" in crop or "profitability" in crop, \
                    f"Crop {idx}: revenue information missing"
                assert "expected_profit_per_acre" in crop or "profitability" in crop, \
                    f"Crop {idx}: profit information missing"
                assert "roi_percentage" in crop or "profitability" in crop, \
                    f"Crop {idx}: ROI information missing"
                
                # Yield predictions (required)
                assert "expected_yield_per_acre" in crop, \
                    f"Crop {idx}: expected_yield_per_acre missing"
                assert crop["expected_yield_per_acre"] is not None, \
                    f"Crop {idx}: expected_yield_per_acre cannot be None"
                
                # Quality grades (required)
                assert "quality_grade" in crop, \
                    f"Crop {idx}: quality_grade missing"
                assert crop["quality_grade"] in ["A", "B", "C"], \
                    f"Crop {idx}: quality_grade must be A, B, or C, got {crop['quality_grade']}"
                assert "quality_confidence" in crop, \
                    f"Crop {idx}: quality_confidence missing"
                assert 0.0 <= crop["quality_confidence"] <= 1.0, \
                    f"Crop {idx}: quality_confidence {crop['quality_confidence']} out of range [0, 1]"

    
    @given(
        plot_data=plot_data_strategy(),
        season=season_strategy(),
        analysis_response=comprehensive_analysis_response_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_profitability_metrics_completeness(
        self,
        plot_data,
        season,
        analysis_response
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any plot analysis, profitability metrics must be
        complete and mathematically consistent.
        """
        plot, soil_test = plot_data
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)
        service.cache_manager = None
        
        # Mock the internal methods
        with patch.object(service, '_get_plot_details', return_value=plot), \
             patch.object(service, '_get_latest_soil_test', return_value=soil_test), \
             patch.object(service, '_analyze_with_bedrock', return_value=analysis_response):
            
            # Execute
            result = await service.analyze_plot(
                plot_id=plot.id,
                season=season,
                budget_per_acre=20000
            )
            
            # Test profitability metrics for each crop
            for idx, crop in enumerate(result["recommended_crops"]):
                # Check if profitability is calculated
                if "profitability" in crop:
                    prof = crop["profitability"]
                    
                    # Per-acre metrics
                    assert "per_acre" in prof, \
                        f"Crop {idx}: per_acre profitability missing"
                    per_acre = prof["per_acre"]
                    
                    assert "investment" in per_acre, \
                        f"Crop {idx}: investment missing from profitability"
                    assert "revenue" in per_acre, \
                        f"Crop {idx}: revenue missing from profitability"
                    assert "profit" in per_acre, \
                        f"Crop {idx}: profit missing from profitability"
                    assert "roi_percentage" in per_acre, \
                        f"Crop {idx}: roi_percentage missing from profitability"
                    
                    # Verify mathematical consistency
                    investment = per_acre["investment"]
                    revenue = per_acre["revenue"]
                    profit = per_acre["profit"]
                    roi = per_acre["roi_percentage"]
                    
                    # Profit = Revenue - Investment (with tolerance for rounding)
                    expected_profit = revenue - investment
                    assert abs(profit - expected_profit) < 10, \
                        f"Crop {idx}: Profit calculation inconsistent. " \
                        f"Expected {expected_profit}, got {profit}"
                    
                    # ROI = (Profit / Investment) * 100 (with tolerance)
                    if investment > 0:
                        expected_roi = (profit / investment) * 100
                        assert abs(roi - expected_roi) < 5, \
                            f"Crop {idx}: ROI calculation inconsistent. " \
                            f"Expected {expected_roi:.2f}%, got {roi:.2f}%"
                    
                    # Total plot metrics
                    assert "total_plot" in prof, \
                        f"Crop {idx}: total_plot profitability missing"
                    total = prof["total_plot"]
                    
                    assert "area_acres" in total, \
                        f"Crop {idx}: area_acres missing from total_plot"
                    assert "total_investment" in total, \
                        f"Crop {idx}: total_investment missing from total_plot"
                    assert "total_profit" in total, \
                        f"Crop {idx}: total_profit missing from total_plot"
                    
                    # Investment breakdown
                    assert "investment_breakdown" in prof, \
                        f"Crop {idx}: investment_breakdown missing"
                    breakdown = prof["investment_breakdown"]
                    
                    assert "seeds" in breakdown, \
                        f"Crop {idx}: seeds missing from investment_breakdown"
                    assert "fertilizer" in breakdown, \
                        f"Crop {idx}: fertilizer missing from investment_breakdown"
                    assert "labor" in breakdown, \
                        f"Crop {idx}: labor missing from investment_breakdown"
                    assert "irrigation" in breakdown, \
                        f"Crop {idx}: irrigation missing from investment_breakdown"
                    assert "other" in breakdown, \
                        f"Crop {idx}: other missing from investment_breakdown"

    
    @given(
        plot_data=plot_data_strategy(),
        season=season_strategy(),
        analysis_response=comprehensive_analysis_response_strategy()
    )
    @settings(
        max_examples=50,  # Fewer examples for performance test
        deadline=20000,  # 20 seconds deadline
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_response_time_under_10_seconds(
        self,
        plot_data,
        season,
        analysis_response
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any plot analysis request, response time must be
        under 10 seconds (95th percentile requirement).
        
        Note: This test measures the service layer response time.
        In production, Bedrock API calls are cached for 6 hours to
        ensure consistent performance.
        """
        plot, soil_test = plot_data
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)
        service.cache_manager = None
        
        # Mock the internal methods
        with patch.object(service, '_get_plot_details', return_value=plot), \
             patch.object(service, '_get_latest_soil_test', return_value=soil_test), \
             patch.object(service, '_analyze_with_bedrock', return_value=analysis_response):
            
            # Measure execution time
            start_time = time.time()
            
            result = await service.analyze_plot(
                plot_id=plot.id,
                season=season,
                budget_per_acre=20000
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Assert: Response time under 10 seconds
            assert execution_time < 10.0, \
                f"Response time {execution_time:.2f}s exceeds 10 second limit"
            
            # Assert: Result is valid
            assert result is not None, "Result cannot be None"
            assert "recommended_crops" in result, "recommended_crops missing"
    
    @given(
        plot_data=plot_data_strategy(),
        season=season_strategy(),
        analysis_response=comprehensive_analysis_response_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_annual_strategy_present(
        self,
        plot_data,
        season,
        analysis_response
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any plot analysis, annual strategy information
        must be present with crop rotation recommendations.
        """
        plot, soil_test = plot_data
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)
        service.cache_manager = None
        
        # Mock the internal methods
        with patch.object(service, '_get_plot_details', return_value=plot), \
             patch.object(service, '_get_latest_soil_test', return_value=soil_test), \
             patch.object(service, '_analyze_with_bedrock', return_value=analysis_response):
            
            # Execute
            result = await service.analyze_plot(
                plot_id=plot.id,
                season=season,
                budget_per_acre=20000
            )
            
            # Assert: Annual strategy is present
            assert "annual_strategy" in result, \
                "annual_strategy missing from response"
            
            strategy = result["annual_strategy"]
            
            # Assert: Current season crop recommendation
            assert "current_season_crop" in strategy, \
                "current_season_crop missing from annual_strategy"
            assert strategy["current_season_crop"] is not None, \
                "current_season_crop cannot be None"
            assert len(strategy["current_season_crop"]) > 0, \
                "current_season_crop cannot be empty"
            
            # Assert: Next season crop recommendation (crop rotation)
            assert "next_season_crop" in strategy, \
                "next_season_crop missing from annual_strategy"
            assert strategy["next_season_crop"] is not None, \
                "next_season_crop cannot be None"
            assert len(strategy["next_season_crop"]) > 0, \
                "next_season_crop cannot be empty"
            
            # Assert: Annual profit projection
            assert "total_annual_profit" in strategy, \
                "total_annual_profit missing from annual_strategy"
            assert isinstance(strategy["total_annual_profit"], (int, float)), \
                "total_annual_profit must be numeric"
            assert strategy["total_annual_profit"] > 0, \
                "total_annual_profit must be positive"
            
            # Assert: Annual ROI
            assert "annual_roi" in strategy, \
                "annual_roi missing from annual_strategy"
            assert isinstance(strategy["annual_roi"], (int, float)), \
                "annual_roi must be numeric"

    
    @given(
        plot_data=plot_data_strategy(),
        season=season_strategy(),
        analysis_response=comprehensive_analysis_response_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_plot_health_scores_present(
        self,
        plot_data,
        season,
        analysis_response
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any plot analysis, plot health scores must be
        present with soil health, water resource, and overall suitability.
        """
        plot, soil_test = plot_data
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)
        service.cache_manager = None
        
        # Mock the internal methods
        with patch.object(service, '_get_plot_details', return_value=plot), \
             patch.object(service, '_get_latest_soil_test', return_value=soil_test), \
             patch.object(service, '_analyze_with_bedrock', return_value=analysis_response):
            
            # Execute
            result = await service.analyze_plot(
                plot_id=plot.id,
                season=season,
                budget_per_acre=20000
            )
            
            # Assert: Plot health is present
            assert "plot_health" in result, \
                "plot_health missing from response"
            
            health = result["plot_health"]
            
            # Assert: Soil health score
            assert "soil_health_score" in health, \
                "soil_health_score missing from plot_health"
            assert isinstance(health["soil_health_score"], (int, float)), \
                "soil_health_score must be numeric"
            assert 0.0 <= health["soil_health_score"] <= 100.0, \
                f"soil_health_score {health['soil_health_score']} out of range [0, 100]"
            
            # Assert: Water resource score
            assert "water_resource_score" in health, \
                "water_resource_score missing from plot_health"
            assert isinstance(health["water_resource_score"], (int, float)), \
                "water_resource_score must be numeric"
            assert 0.0 <= health["water_resource_score"] <= 100.0, \
                f"water_resource_score {health['water_resource_score']} out of range [0, 100]"
            
            # Assert: Overall suitability score
            assert "overall_suitability_score" in health, \
                "overall_suitability_score missing from plot_health"
            assert isinstance(health["overall_suitability_score"], (int, float)), \
                "overall_suitability_score must be numeric"
            assert 0.0 <= health["overall_suitability_score"] <= 100.0, \
                f"overall_suitability_score {health['overall_suitability_score']} out of range [0, 100]"
    
    @given(
        plot_data=plot_data_strategy(),
        season=season_strategy()
    )
    @settings(
        max_examples=50,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_analysis_with_missing_soil_data(
        self,
        plot_data,
        season
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any plot without soil test data, system should
        still generate analysis with fallback values.
        """
        plot, _ = plot_data  # Ignore soil test
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)
        service.cache_manager = None
        
        # Create fallback response
        fallback_response = {
            "recommended_crops": [
                {
                    "rank": 1,
                    "crop_name": "Rice",
                    "variety": "Local variety",
                    "suitability_score": 7.0,
                    "investment_per_acre": 18000,
                    "expected_yield_per_acre": "20-25 quintals",
                    "market_price_per_quintal": 2000,
                    "quality_grade": "B",
                    "quality_confidence": 0.6,
                    "confidence_score": 0.6
                }
            ],
            "annual_strategy": {
                "current_season_crop": "Rice",
                "next_season_crop": "Wheat",
                "total_annual_profit": 60000,
                "annual_roi": 200
            },
            "plot_health": {
                "soil_health_score": 70,
                "water_resource_score": 75,
                "overall_suitability_score": 72
            }
        }
        
        # Mock the internal methods - no soil test data
        with patch.object(service, '_get_plot_details', return_value=plot), \
             patch.object(service, '_get_latest_soil_test', return_value=None), \
             patch.object(service, '_analyze_with_bedrock', return_value=fallback_response):
            
            # Execute
            result = await service.analyze_plot(
                plot_id=plot.id,
                season=season,
                budget_per_acre=20000
            )
            
            # Assert: Analysis is still generated
            assert result is not None, "Analysis should be generated even without soil data"
            assert "recommended_crops" in result, "recommended_crops missing"
            assert len(result["recommended_crops"]) > 0, "At least one crop should be recommended"
            
            # Assert: All required fields are present
            crop = result["recommended_crops"][0]
            assert "suitability_score" in crop, "suitability_score missing"
            assert "quality_grade" in crop, "quality_grade missing"
            assert "investment_per_acre" in crop, "investment_per_acre missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
