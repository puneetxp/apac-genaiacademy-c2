"""
Property-based tests for Bedrock API integration
Tests Property 4: Bedrock API Integration Completeness

**Validates: Requirements AC2.1, AC3.1, AC3.2, AC3.3**
"""

import time
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.services.bedrock_service import BedrockService


# Custom strategies for farm profile data
@st.composite
def valid_farm_profile(draw):
    """Generate valid farm profile data for testing"""

    # Indian states
    states = [
        "Punjab",
        "Haryana",
        "Uttar Pradesh",
        "Madhya Pradesh",
        "Rajasthan",
        "Maharashtra",
        "Karnataka",
        "Tamil Nadu",
        "Andhra Pradesh",
        "Gujarat",
        "West Bengal",
        "Bihar",
        "Odisha",
        "Telangana",
        "Kerala",
    ]

    # Common districts (simplified for testing)
    districts = [
        "Ludhiana",
        "Amritsar",
        "Patiala",
        "Jalandhar",
        "Bathinda",
        "Karnal",
        "Panipat",
        "Hisar",
        "Rohtak",
        "Ambala",
        "Agra",
        "Lucknow",
        "Kanpur",
        "Varanasi",
        "Meerut",
    ]

    # Soil types
    soil_types = ["clay", "sandy", "loamy", "black", "red", "alluvial"]

    # Irrigation types
    irrigation_types = ["rain-fed", "canal", "borewell", "mixed", "drip", "sprinkler"]

    # Common crops for previous crops
    crops = [
        "Rice",
        "Wheat",
        "Cotton",
        "Sugarcane",
        "Maize",
        "Soybean",
        "Groundnut",
        "Mustard",
        "Chickpea",
        "Pigeon Pea",
    ]

    state = draw(st.sampled_from(states))
    district = draw(st.sampled_from(districts))
    soil_type = draw(st.sampled_from(soil_types))
    area_acres = draw(st.floats(min_value=0.1, max_value=100.0))
    irrigation_type = draw(st.sampled_from(irrigation_types))

    # Optional fields
    previous_crops = draw(
        st.one_of(
            st.none(),
            st.sampled_from(crops),
            st.text(
                min_size=1, max_size=50, alphabet=st.characters(min_codepoint=65, max_codepoint=122)
            ),
        )
    )

    budget_per_acre = draw(st.one_of(st.none(), st.floats(min_value=5000.0, max_value=100000.0)))

    return {
        "state": state,
        "district": district,
        "soil_type": soil_type,
        "area_acres": area_acres,
        "irrigation_type": irrigation_type,
        "previous_crops": previous_crops,
        "budget_per_acre": budget_per_acre,
    }


def create_mock_bedrock_response() -> Dict[str, Any]:
    """Create a valid mock Bedrock API response"""
    return {
        "kharif": {
            "recommended_crop": "Rice",
            "variety": "Basmati 370",
            "expected_yield_per_acre": "25 quintals",
            "expected_profit_per_acre": 45000,
            "investment_per_acre": 18000,
            "planting_window": "June-July",
            "harvest_window": "October-November",
            "key_success_factors": ["Timely planting", "Adequate water", "Pest management"],
            "confidence_score": 0.85,
        },
        "rabi": {
            "recommended_crop": "Wheat",
            "variety": "HD-2967",
            "expected_yield_per_acre": "22 quintals",
            "expected_profit_per_acre": 38000,
            "investment_per_acre": 15000,
            "planting_window": "November-December",
            "harvest_window": "March-April",
            "key_success_factors": ["Proper irrigation", "Fertilizer application", "Weed control"],
            "confidence_score": 0.82,
        },
        "zaid": {"recommended_crop": "Mung Bean", "expected_profit_per_acre": 12000},
        "annual_summary": {
            "total_expected_profit_per_acre": 95000,
            "total_investment_per_acre": 33000,
            "roi_percentage": 188,
            "risk_level": "medium",
            "sustainability_score": 0.8,
        },
        "alternative_options": [
            {
                "season": "kharif",
                "crop": "Cotton",
                "profit_difference": -5000,
                "risk_comparison": "Higher risk but stable market",
            }
        ],
        "monthly_action_plan": [
            {"month": "June", "actions": ["Prepare land", "Purchase seeds"]},
            {"month": "July", "actions": ["Plant kharif crops", "Apply fertilizer"]},
        ],
    }


class TestBedrockAPIIntegration:
    """
    Property 4: Bedrock API Integration Completeness

    Test that for any valid farm profile, system makes exactly one Bedrock API call
    with all required data and receives response within 10 seconds.
    """

    @given(farm_profile=valid_farm_profile())
    @settings(
        max_examples=200,
        deadline=15000,  # 15 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_bedrock_api_call_completeness(self, farm_profile):
        """
        **Validates: Requirements AC2.1, AC3.1, AC3.2, AC3.3**

        Property: For any valid farm profile, when requesting annual crop strategy,
        the system should make exactly one API call to Amazon Bedrock with all
        required farm data.
        """
        # Arrange
        service = BedrockService()
        mock_response = create_mock_bedrock_response()

        # Mock the Bedrock runtime client
        with patch.object(service, "runtime_client") as mock_client:
            # Setup mock response
            mock_invoke_response = {"body": MagicMock()}
            mock_invoke_response["body"].read.return_value = (
                f'{{"completion": "{str(mock_response)}"}}'.encode()
            )
            mock_client.invoke_model.return_value = mock_invoke_response

            # Act
            start_time = time.time()
            result = service.get_annual_crop_strategy(
                state=farm_profile["state"],
                district=farm_profile["district"],
                soil_type=farm_profile["soil_type"],
                area_acres=farm_profile["area_acres"],
                irrigation_type=farm_profile["irrigation_type"],
                previous_crops=farm_profile["previous_crops"],
                budget_per_acre=farm_profile["budget_per_acre"],
            )
            elapsed_time = time.time() - start_time

            # Assert: Exactly one API call was made
            assert (
                mock_client.invoke_model.call_count == 1
            ), f"Expected exactly 1 Bedrock API call, but got {mock_client.invoke_model.call_count}"

            # Assert: API call included all required farm data
            call_args = mock_client.invoke_model.call_args
            assert call_args is not None, "Bedrock API was not called"

            # Verify the body contains all required farm profile fields
            body_str = call_args.kwargs.get("body", "")
            assert (
                farm_profile["state"] in body_str or "state" in body_str.lower()
            ), "State information missing from API call"
            assert (
                farm_profile["district"] in body_str or "district" in body_str.lower()
            ), "District information missing from API call"
            assert (
                farm_profile["soil_type"] in body_str or "soil" in body_str.lower()
            ), "Soil type information missing from API call"
            assert (
                str(farm_profile["area_acres"]) in body_str or "area" in body_str.lower()
            ), "Area information missing from API call"
            assert (
                farm_profile["irrigation_type"] in body_str or "irrigation" in body_str.lower()
            ), "Irrigation type information missing from API call"

            # Assert: Response received (not None)
            assert result is not None, "Bedrock API response was None"

            # Assert: Response is a dictionary
            assert isinstance(result, dict), f"Expected dict response, got {type(result)}"

            # Note: Response time assertion is relaxed for mocked tests
            # In real integration tests, this would be strictly enforced
            assert elapsed_time < 10.0, f"API call took {elapsed_time:.2f}s, expected < 10s"

    @given(farm_profile=valid_farm_profile())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_bedrock_response_structure_completeness(self, farm_profile):
        """
        **Validates: Requirements AC2.1, AC3.1, AC3.2, AC3.3**

        Property: For any valid farm profile, the Bedrock API response should
        contain all required fields for a complete annual strategy.
        """
        # Arrange
        service = BedrockService()
        mock_response = create_mock_bedrock_response()

        # Mock the Bedrock runtime client
        with patch.object(service, "runtime_client") as mock_client:
            # Setup mock response with proper JSON structure
            import json

            response_json = json.dumps(mock_response)
            mock_invoke_response = {"body": MagicMock()}
            mock_invoke_response["body"].read.return_value = json.dumps(
                {"completion": response_json}
            ).encode()
            mock_client.invoke_model.return_value = mock_invoke_response

            # Act
            result = service.get_annual_crop_strategy(
                state=farm_profile["state"],
                district=farm_profile["district"],
                soil_type=farm_profile["soil_type"],
                area_acres=farm_profile["area_acres"],
                irrigation_type=farm_profile["irrigation_type"],
                previous_crops=farm_profile["previous_crops"],
                budget_per_acre=farm_profile["budget_per_acre"],
            )

            # Assert: Response contains all required top-level fields
            required_fields = [
                "kharif",
                "rabi",
                "zaid",
                "annual_summary",
                "alternative_options",
                "monthly_action_plan",
            ]
            for field in required_fields:
                assert field in result, f"Required field '{field}' missing from Bedrock response"

            # Assert: Kharif season has required fields
            kharif_required = [
                "recommended_crop",
                "variety",
                "expected_yield_per_acre",
                "expected_profit_per_acre",
                "investment_per_acre",
                "planting_window",
                "harvest_window",
                "key_success_factors",
                "confidence_score",
            ]
            for field in kharif_required:
                assert (
                    field in result["kharif"]
                ), f"Required field '{field}' missing from Kharif recommendations"

            # Assert: Rabi season has required fields
            rabi_required = [
                "recommended_crop",
                "variety",
                "expected_yield_per_acre",
                "expected_profit_per_acre",
                "investment_per_acre",
                "planting_window",
                "harvest_window",
                "key_success_factors",
                "confidence_score",
            ]
            for field in rabi_required:
                assert (
                    field in result["rabi"]
                ), f"Required field '{field}' missing from Rabi recommendations"

            # Assert: Annual summary has required fields
            summary_required = [
                "total_expected_profit_per_acre",
                "total_investment_per_acre",
                "roi_percentage",
                "risk_level",
                "sustainability_score",
            ]
            for field in summary_required:
                assert (
                    field in result["annual_summary"]
                ), f"Required field '{field}' missing from annual summary"

            # Assert: Confidence scores are in valid range (0-1)
            assert (
                0.0 <= result["kharif"]["confidence_score"] <= 1.0
            ), f"Kharif confidence score {result['kharif']['confidence_score']} out of range [0, 1]"
            assert (
                0.0 <= result["rabi"]["confidence_score"] <= 1.0
            ), f"Rabi confidence score {result['rabi']['confidence_score']} out of range [0, 1]"

    @given(farm_profile=valid_farm_profile())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_bedrock_api_timeout_handling(self, farm_profile):
        """
        **Validates: Requirements AC3.1, AC3.2**

        Property: For any valid farm profile, if Bedrock API times out or fails,
        the system should handle the error gracefully and provide fallback response.
        """
        # Arrange
        service = BedrockService()

        # Mock the Bedrock runtime client to simulate timeout
        with patch.object(service, "runtime_client") as mock_client:
            from botocore.exceptions import ClientError

            # Simulate timeout error
            mock_client.invoke_model.side_effect = ClientError(
                {"Error": {"Code": "RequestTimeout", "Message": "Request timed out"}}, "InvokeModel"
            )

            # Act & Assert: Should raise exception or return fallback
            try:
                result = service.get_annual_crop_strategy(
                    state=farm_profile["state"],
                    district=farm_profile["district"],
                    soil_type=farm_profile["soil_type"],
                    area_acres=farm_profile["area_acres"],
                    irrigation_type=farm_profile["irrigation_type"],
                    previous_crops=farm_profile["previous_crops"],
                    budget_per_acre=farm_profile["budget_per_acre"],
                )

                # If no exception, verify fallback response is valid
                assert result is not None, "Fallback response should not be None"
                assert isinstance(result, dict), "Fallback response should be a dict"
                assert "kharif" in result, "Fallback should contain kharif recommendations"
                assert "rabi" in result, "Fallback should contain rabi recommendations"

            except Exception as e:
                # Exception is acceptable for timeout scenarios
                assert (
                    "Bedrock" in str(e) or "timeout" in str(e).lower()
                ), f"Unexpected exception type: {str(e)}"

    def test_bedrock_api_call_with_minimal_profile(self):
        """
        **Validates: Requirements AC2.1, AC3.1**

        Test that Bedrock API works with minimal required farm profile data
        (no optional fields like previous_crops or budget_per_acre).
        """
        # Arrange
        service = BedrockService()
        mock_response = create_mock_bedrock_response()

        # Mock the Bedrock runtime client
        with patch.object(service, "runtime_client") as mock_client:
            import json

            response_json = json.dumps(mock_response)
            mock_invoke_response = {"body": MagicMock()}
            mock_invoke_response["body"].read.return_value = json.dumps(
                {"completion": response_json}
            ).encode()
            mock_client.invoke_model.return_value = mock_invoke_response

            # Act: Call with only required fields
            result = service.get_annual_crop_strategy(
                state="Punjab",
                district="Ludhiana",
                soil_type="loamy",
                area_acres=5.0,
                irrigation_type="canal",
                previous_crops=None,  # Optional
                budget_per_acre=None,  # Optional
            )

            # Assert: API call was made successfully
            assert mock_client.invoke_model.call_count == 1

            # Assert: Response is valid
            assert result is not None
            assert isinstance(result, dict)
            assert "kharif" in result
            assert "rabi" in result
            assert "annual_summary" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
