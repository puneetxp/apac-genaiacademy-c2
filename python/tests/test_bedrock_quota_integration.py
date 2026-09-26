"""
Integration tests for quota-aware Bedrock service

Tests the integration between AI quota service and Bedrock service
to ensure proper quota checking, fallback behavior, and usage tracking.

Task 40.2: Integrate quota system with Bedrock service
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytz

from app.orm.ai_usage_quota import AiUsageQuota
from app.services.ai_quota_service import AIQuotaService
from app.services.bedrock_service import BedrockService


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    return session


@pytest.fixture
def bedrock_service_instance():
    """Create Bedrock service instance"""
    return BedrockService()


@pytest.fixture
async def quota_service(mock_db_session):
    """Create AI quota service instance"""
    return AIQuotaService(mock_db_session)


@pytest.mark.asyncio
async def test_annual_strategy_with_gps_and_quota_available(
    bedrock_service_instance, mock_db_session
):
    """
    Test annual strategy generation with GPS coordinates when quota is available

    Should:
    - Check quota before making Bedrock call
    - Use GPS-enhanced recommendation
    - Increment GPS usage counter
    - Return quota status in response
    """
    user_id = 123
    today = date.today()

    # Mock quota record with available quota
    mock_quota = AiUsageQuota(
        id=1,
        user_id=user_id,
        date=today,
        gps_enhanced_requests=5,
        pincode_requests=10,
        quota_limit=20,
        last_reset=datetime.now(pytz.timezone("Asia/Kolkata")),
    )

    # Mock database queries
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_quota
    mock_db_session.execute.return_value = mock_result

    # Mock Bedrock API call
    with patch.object(bedrock_service_instance, "_invoke_claude") as mock_invoke:
        mock_invoke.return_value = """
        {
            "kharif": {
                "recommended_crop": "Rice",
                "variety": "IR64",
                "expected_yield_per_acre": "25 quintals",
                "expected_profit_per_acre": 45000,
                "investment_per_acre": 15000,
                "planting_window": "June-July",
                "harvest_window": "October-November",
                "key_success_factors": ["Timely planting", "Water management"],
                "confidence_score": 0.9,
                "seasonal_weather_pattern": "Monsoon rainfall",
                "weather_aware_planting_timing": "After first good rains",
                "weather_aware_harvest_timing": "Before monsoon withdrawal",
                "weather_alerts": []
            },
            "rabi": {
                "recommended_crop": "Wheat",
                "variety": "HD2967",
                "expected_yield_per_acre": "22 quintals",
                "expected_profit_per_acre": 38000,
                "investment_per_acre": 12000,
                "planting_window": "November-December",
                "harvest_window": "March-April",
                "key_success_factors": ["Irrigation", "Fertilizer"],
                "confidence_score": 0.85,
                "seasonal_weather_pattern": "Cool winter",
                "weather_aware_planting_timing": "When temperature drops",
                "weather_aware_harvest_timing": "Before summer heat",
                "weather_alerts": []
            },
            "zaid": {
                "recommended_crop": null,
                "expected_profit_per_acre": 0,
                "seasonal_weather_pattern": "",
                "weather_aware_planting_timing": "",
                "weather_aware_harvest_timing": "",
                "weather_alerts": []
            },
            "annual_summary": {
                "total_expected_profit_per_acre": 83000,
                "total_investment_per_acre": 27000,
                "roi_percentage": 207,
                "risk_level": "medium",
                "sustainability_score": 0.8
            },
            "alternative_options": [],
            "monthly_action_plan": []
        }
        """

        # Call service with GPS coordinates
        result = await bedrock_service_instance.get_annual_crop_strategy(
            state="Punjab",
            district="Ludhiana",
            soil_type="loamy",
            area_acres=5.0,
            irrigation_type="canal",
            user_id=user_id,
            latitude=30.9010,
            longitude=75.8573,
            db_session=mock_db_session,
        )

    # Verify quota status in response
    assert "quota_status" in result
    assert result["quota_status"]["gps_enhanced"] is True
    assert result["quota_status"]["remaining_quota"] == 15  # 20 - 5
    assert result["quota_status"]["quota_exceeded"] is False

    # Verify Bedrock was called with GPS context
    mock_invoke.assert_called_once()
    call_args = mock_invoke.call_args[0][0]
    assert "GPS Coordinates: 30.9010, 75.8573" in call_args
    assert "precise microclimate analysis" in call_args


@pytest.mark.asyncio
async def test_annual_strategy_quota_exceeded_fallback(bedrock_service_instance, mock_db_session):
    """
    Test annual strategy falls back to pincode-based when quota exceeded

    Should:
    - Check quota and find it exceeded
    - Fall back to pincode-based recommendation
    - Increment pincode usage counter
    - Return quota_exceeded flag in response
    """
    user_id = 456
    today = date.today()

    # Mock quota record with exceeded quota
    mock_quota = AiUsageQuota(
        id=2,
        user_id=user_id,
        date=today,
        gps_enhanced_requests=20,  # At limit
        pincode_requests=50,
        quota_limit=20,
        last_reset=datetime.now(pytz.timezone("Asia/Kolkata")),
    )

    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_quota
    mock_db_session.execute.return_value = mock_result

    # Mock Bedrock API call
    with patch.object(bedrock_service_instance, "_invoke_claude") as mock_invoke:
        mock_invoke.return_value = """
        {
            "kharif": {
                "recommended_crop": "Cotton",
                "variety": "Bt Cotton",
                "expected_yield_per_acre": "20 quintals",
                "expected_profit_per_acre": 40000,
                "investment_per_acre": 18000,
                "planting_window": "May-June",
                "harvest_window": "October-November",
                "key_success_factors": ["Pest control", "Water management"],
                "confidence_score": 0.8,
                "seasonal_weather_pattern": "Monsoon",
                "weather_aware_planting_timing": "Early monsoon",
                "weather_aware_harvest_timing": "Dry weather",
                "weather_alerts": []
            },
            "rabi": {
                "recommended_crop": "Mustard",
                "variety": "Pusa Bold",
                "expected_yield_per_acre": "15 quintals",
                "expected_profit_per_acre": 30000,
                "investment_per_acre": 10000,
                "planting_window": "October-November",
                "harvest_window": "February-March",
                "key_success_factors": ["Timely sowing", "Weed control"],
                "confidence_score": 0.75,
                "seasonal_weather_pattern": "Cool winter",
                "weather_aware_planting_timing": "After kharif harvest",
                "weather_aware_harvest_timing": "Before heat",
                "weather_alerts": []
            },
            "zaid": {
                "recommended_crop": null,
                "expected_profit_per_acre": 0,
                "seasonal_weather_pattern": "",
                "weather_aware_planting_timing": "",
                "weather_aware_harvest_timing": "",
                "weather_alerts": []
            },
            "annual_summary": {
                "total_expected_profit_per_acre": 70000,
                "total_investment_per_acre": 28000,
                "roi_percentage": 150,
                "risk_level": "medium",
                "sustainability_score": 0.7
            },
            "alternative_options": [],
            "monthly_action_plan": []
        }
        """

        # Call service with GPS coordinates (should fallback)
        result = await bedrock_service_instance.get_annual_crop_strategy(
            state="Gujarat",
            district="Ahmedabad",
            soil_type="clay",
            area_acres=3.0,
            irrigation_type="borewell",
            user_id=user_id,
            latitude=23.0225,
            longitude=72.5714,
            db_session=mock_db_session,
        )

    # Verify quota status shows fallback
    assert "quota_status" in result
    assert result["quota_status"]["gps_enhanced"] is False
    assert result["quota_status"]["quota_exceeded"] is True
    assert result["quota_status"]["remaining_quota"] == 0
    assert "quota exceeded" in result["quota_status"]["fallback_message"].lower()

    # Verify Bedrock was called WITHOUT GPS context
    mock_invoke.assert_called_once()
    call_args = mock_invoke.call_args[0][0]
    assert "GPS Coordinates" not in call_args
    assert "regional recommendations" in call_args


@pytest.mark.asyncio
async def test_annual_strategy_no_gps_provided(bedrock_service_instance, mock_db_session):
    """
    Test annual strategy without GPS coordinates

    Should:
    - Use pincode-based recommendation
    - Not consume GPS quota
    - Increment pincode usage counter
    """
    user_id = 789
    today = date.today()

    mock_quota = AiUsageQuota(
        id=3,
        user_id=user_id,
        date=today,
        gps_enhanced_requests=10,
        pincode_requests=25,
        quota_limit=20,
        last_reset=datetime.now(pytz.timezone("Asia/Kolkata")),
    )

    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_quota
    mock_db_session.execute.return_value = mock_result

    with patch.object(bedrock_service_instance, "_invoke_claude") as mock_invoke:
        mock_invoke.return_value = """
        {
            "kharif": {
                "recommended_crop": "Soybean",
                "variety": "JS 335",
                "expected_yield_per_acre": "18 quintals",
                "expected_profit_per_acre": 35000,
                "investment_per_acre": 12000,
                "planting_window": "June-July",
                "harvest_window": "September-October",
                "key_success_factors": ["Drainage", "Seed treatment"],
                "confidence_score": 0.82,
                "seasonal_weather_pattern": "Monsoon",
                "weather_aware_planting_timing": "After good rains",
                "weather_aware_harvest_timing": "Dry period",
                "weather_alerts": []
            },
            "rabi": {
                "recommended_crop": "Chickpea",
                "variety": "JG 11",
                "expected_yield_per_acre": "12 quintals",
                "expected_profit_per_acre": 28000,
                "investment_per_acre": 8000,
                "planting_window": "October-November",
                "harvest_window": "February-March",
                "key_success_factors": ["Seed treatment", "Weed control"],
                "confidence_score": 0.78,
                "seasonal_weather_pattern": "Cool dry",
                "weather_aware_planting_timing": "Post-monsoon",
                "weather_aware_harvest_timing": "Before heat",
                "weather_alerts": []
            },
            "zaid": {
                "recommended_crop": null,
                "expected_profit_per_acre": 0,
                "seasonal_weather_pattern": "",
                "weather_aware_planting_timing": "",
                "weather_aware_harvest_timing": "",
                "weather_alerts": []
            },
            "annual_summary": {
                "total_expected_profit_per_acre": 63000,
                "total_investment_per_acre": 20000,
                "roi_percentage": 215,
                "risk_level": "low",
                "sustainability_score": 0.85
            },
            "alternative_options": [],
            "monthly_action_plan": []
        }
        """

        # Call service WITHOUT GPS coordinates
        result = await bedrock_service_instance.get_annual_crop_strategy(
            state="Madhya Pradesh",
            district="Indore",
            soil_type="black",
            area_acres=4.0,
            irrigation_type="rainfed",
            user_id=user_id,
            latitude=None,
            longitude=None,
            db_session=mock_db_session,
        )

    # Verify quota status shows pincode-based
    assert "quota_status" in result
    assert result["quota_status"]["gps_enhanced"] is False
    assert result["quota_status"]["quota_exceeded"] is False
    assert result["quota_status"]["remaining_quota"] == 10  # Unchanged

    # Verify Bedrock was called with regional context
    mock_invoke.assert_called_once()
    call_args = mock_invoke.call_args[0][0]
    assert "GPS Coordinates" not in call_args
    assert "regional recommendations" in call_args


@pytest.mark.asyncio
async def test_quota_increment_after_successful_call(bedrock_service_instance, mock_db_session):
    """
    Test that quota usage is incremented after successful Bedrock call
    """
    user_id = 999
    today = date.today()

    mock_quota = AiUsageQuota(
        id=4,
        user_id=user_id,
        date=today,
        gps_enhanced_requests=8,
        pincode_requests=15,
        quota_limit=20,
        last_reset=datetime.now(pytz.timezone("Asia/Kolkata")),
    )

    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_quota
    mock_db_session.execute.return_value = mock_result

    with patch.object(bedrock_service_instance, "_invoke_claude") as mock_invoke:
        mock_invoke.return_value = '{"kharif": {"recommended_crop": "Rice", "variety": "IR64", "expected_yield_per_acre": "25 quintals", "expected_profit_per_acre": 45000, "investment_per_acre": 15000, "planting_window": "June-July", "harvest_window": "October-November", "key_success_factors": ["Water"], "confidence_score": 0.9, "seasonal_weather_pattern": "Monsoon", "weather_aware_planting_timing": "After rains", "weather_aware_harvest_timing": "Dry period", "weather_alerts": []}, "rabi": {"recommended_crop": "Wheat", "variety": "HD2967", "expected_yield_per_acre": "22 quintals", "expected_profit_per_acre": 38000, "investment_per_acre": 12000, "planting_window": "November-December", "harvest_window": "March-April", "key_success_factors": ["Irrigation"], "confidence_score": 0.85, "seasonal_weather_pattern": "Cool", "weather_aware_planting_timing": "Cool weather", "weather_aware_harvest_timing": "Before heat", "weather_alerts": []}, "zaid": {"recommended_crop": null, "expected_profit_per_acre": 0, "seasonal_weather_pattern": "", "weather_aware_planting_timing": "", "weather_aware_harvest_timing": "", "weather_alerts": []}, "annual_summary": {"total_expected_profit_per_acre": 83000, "total_investment_per_acre": 27000, "roi_percentage": 207, "risk_level": "medium", "sustainability_score": 0.8}, "alternative_options": [], "monthly_action_plan": []}'

        # Call with GPS
        await bedrock_service_instance.get_annual_crop_strategy(
            state="Punjab",
            district="Ludhiana",
            soil_type="loamy",
            area_acres=5.0,
            irrigation_type="canal",
            user_id=user_id,
            latitude=30.9010,
            longitude=75.8573,
            db_session=mock_db_session,
        )

    # Verify commit was called (quota incremented)
    mock_db_session.commit.assert_called()

    # Verify quota was incremented
    assert mock_quota.gps_enhanced_requests == 9  # 8 + 1


@pytest.mark.asyncio
async def test_crop_recommendations_with_quota(bedrock_service_instance, mock_db_session):
    """
    Test crop recommendations with quota tracking
    """
    user_id = 111
    today = date.today()

    mock_quota = AiUsageQuota(
        id=5,
        user_id=user_id,
        date=today,
        gps_enhanced_requests=3,
        pincode_requests=8,
        quota_limit=20,
        last_reset=datetime.now(pytz.timezone("Asia/Kolkata")),
    )

    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_quota
    mock_db_session.execute.return_value = mock_result

    with patch.object(bedrock_service_instance, "_invoke_claude") as mock_invoke:
        mock_invoke.return_value = """
        [
            {
                "rank": 1,
                "crop_name": "Rice",
                "variety": "IR64",
                "suitability_reason": "Ideal for clay soil",
                "expected_yield_per_acre": "25 quintals",
                "expected_profit_per_acre": 45000,
                "investment_per_acre": 15000,
                "key_requirements": ["Water", "Fertilizer"],
                "challenges": ["Pest management"],
                "market_demand": "High",
                "confidence_score": 0.9
            }
        ]
        """

        result = await bedrock_service_instance.get_crop_recommendations(
            state="Punjab",
            district="Ludhiana",
            season="kharif",
            soil_type="clay",
            area_acres=5.0,
            irrigation_type="canal",
            user_id=user_id,
            latitude=30.9010,
            longitude=75.8573,
            db_session=mock_db_session,
        )

    # Verify response structure
    assert "recommendations" in result
    assert "quota_status" in result
    assert result["quota_status"]["gps_enhanced"] is True
    assert result["quota_status"]["remaining_quota"] == 17  # 20 - 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
