"""
Test AC2: Annual Crop Strategy & Recommendations (MVP Core)

Tests all acceptance criteria for AC2:
1. System calls Amazon Bedrock API with complete farm profile data
2. Bedrock returns comprehensive annual strategy (Kharif, Rabi, Zaid)
3. System displays profit estimates, confidence scores, investment requirements, ROI
4. System provides month-by-month implementation timeline (12 months)
5. System includes alternative crop options with risk-benefit analysis
6. System persists strategy to database and schedules reminders
7. System stores complete Bedrock response in JSONB field for audit
"""

import json

# Mock the ORM models before importing the API
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

# Add app directory to path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir.parent))


@pytest.fixture
def mock_farm():
    """Mock farm data"""
    farm = Mock()
    farm.id = 1
    farm.farmer_id = 100
    farm.state = "Maharashtra"
    farm.district = "Pune"
    farm.soil_type = "Black"
    farm.total_area = 5.0
    farm.irrigation_type = "Borewell"
    return farm


@pytest.fixture
def mock_bedrock_response():
    """Mock Bedrock API response with comprehensive annual strategy"""
    return {
        "kharif": {
            "recommended_crop": "Soybean",
            "variety": "JS 335",
            "expected_yield_per_acre": "12-15 quintals",
            "expected_profit_per_acre": 45000,
            "investment_per_acre": 18000,
            "planting_window": "June-July",
            "harvest_window": "October-November",
            "key_success_factors": [
                "Timely sowing in June",
                "Adequate drainage",
                "Pest management for pod borer",
            ],
            "confidence_score": 0.87,
        },
        "rabi": {
            "recommended_crop": "Wheat",
            "variety": "HD 2967",
            "expected_yield_per_acre": "20-25 quintals",
            "expected_profit_per_acre": 52000,
            "investment_per_acre": 22000,
            "planting_window": "November-December",
            "harvest_window": "March-April",
            "key_success_factors": [
                "Proper irrigation scheduling",
                "Timely fertilizer application",
                "Weed control in early stages",
            ],
            "confidence_score": 0.92,
        },
        "zaid": {
            "recommended_crop": "Green Gram",
            "variety": "IPM 02-3",
            "expected_yield_per_acre": "4-6 quintals",
            "expected_profit_per_acre": 18000,
            "investment_per_acre": 8000,
            "planting_window": "April-May",
            "harvest_window": "June-July",
            "confidence_score": 0.75,
        },
        "annual_summary": {
            "total_expected_profit_per_acre": 115000,
            "total_investment_per_acre": 48000,
            "roi_percentage": 139.6,
            "risk_level": "medium",
            "sustainability_score": 0.85,
        },
        "alternative_options": [
            {
                "season": "kharif",
                "crop": "Cotton",
                "profit_difference": -5000,
                "risk_comparison": "Higher risk due to pest pressure, but better market stability",
            },
            {
                "season": "rabi",
                "crop": "Chickpea",
                "profit_difference": -8000,
                "risk_comparison": "Lower water requirement, suitable for limited irrigation",
            },
        ],
        "monthly_action_plan": [
            {"month": "January", "actions": ["Wheat irrigation", "Apply urea fertilizer"]},
            {
                "month": "February",
                "actions": ["Monitor wheat for rust disease", "Plan for zaid crop"],
            },
            {"month": "March", "actions": ["Harvest wheat", "Prepare land for zaid"]},
            {"month": "April", "actions": ["Sow green gram", "Apply basal fertilizer"]},
            {"month": "May", "actions": ["Green gram irrigation", "Pest monitoring"]},
            {
                "month": "June",
                "actions": ["Harvest green gram", "Prepare for kharif", "Sow soybean"],
            },
            {"month": "July", "actions": ["Soybean weeding", "Monitor for pests"]},
            {"month": "August", "actions": ["Soybean flowering stage care", "Apply fertilizer"]},
            {"month": "September", "actions": ["Pod formation monitoring", "Pest control"]},
            {"month": "October", "actions": ["Harvest soybean", "Prepare for rabi"]},
            {"month": "November", "actions": ["Sow wheat", "Apply basal fertilizer"]},
            {"month": "December", "actions": ["Wheat irrigation", "Weed control"]},
        ],
    }


@pytest.fixture
def mock_current_user():
    """Mock authenticated user"""
    return {"user_id": 100, "email": "farmer@example.com", "cognito_user_id": "test-cognito-id"}


@pytest.mark.asyncio
async def test_ac2_1_bedrock_api_called_with_complete_farm_data(
    mock_farm, mock_bedrock_response, mock_current_user
):
    """
    AC2.1: WHEN farmer requests annual crop strategy
    THEN system SHALL call Amazon Bedrock API with complete farm profile data
    """
    with (
        patch("app.api.v1.annual_strategy.Farm") as MockFarm,
        patch("app.api.v1.annual_strategy.bedrock_service") as mock_bedrock,
        patch("app.api.v1.annual_strategy.AnnualStrategy") as MockStrategy,
    ):

        # Setup mocks
        MockFarm.find = AsyncMock(return_value=mock_farm)
        mock_bedrock.get_annual_crop_strategy = Mock(return_value=mock_bedrock_response)

        mock_strategy = Mock()
        mock_strategy.id = 1
        mock_strategy.farm_id = 1
        mock_strategy.farmer_id = 100
        mock_strategy.year = 2024
        mock_strategy.status = "draft"
        mock_strategy.created_at = datetime.now()
        MockStrategy.create = AsyncMock(return_value=mock_strategy)

        # Import after mocking
        from app.api.v1.annual_strategy import AnnualStrategyRequest, generate_annual_strategy

        # Create request
        request = AnnualStrategyRequest(
            farm_id=1, year=2024, budget_per_acre=50000, previous_crops="Rice, Wheat"
        )

        # Call endpoint
        response = await generate_annual_strategy(
            request=request, current_user=mock_current_user, db=Mock()
        )

        # Verify Bedrock API was called with complete farm data
        mock_bedrock.get_annual_crop_strategy.assert_called_once()
        call_args = mock_bedrock.get_annual_crop_strategy.call_args

        # AC2.1: Verify all required farm profile data is passed
        assert call_args.kwargs["state"] == "Maharashtra"
        assert call_args.kwargs["district"] == "Pune"
        assert call_args.kwargs["soil_type"] == "Black"
        assert call_args.kwargs["area_acres"] == 5.0
        assert call_args.kwargs["irrigation_type"] == "Borewell"
        assert call_args.kwargs["previous_crops"] == "Rice, Wheat"
        assert call_args.kwargs["budget_per_acre"] == 50000

        print("✓ AC2.1: Bedrock API called with complete farm profile data")


@pytest.mark.asyncio
async def test_ac2_2_comprehensive_annual_strategy_returned(
    mock_farm, mock_bedrock_response, mock_current_user
):
    """
    AC2.2: WHEN Bedrock API responds
    THEN system SHALL parse and display comprehensive annual strategy
    INCLUDING Kharif, Rabi, and Zaid season recommendations
    """
    with (
        patch("app.api.v1.annual_strategy.Farm") as MockFarm,
        patch("app.api.v1.annual_strategy.bedrock_service") as mock_bedrock,
        patch("app.api.v1.annual_strategy.AnnualStrategy") as MockStrategy,
    ):

        # Setup mocks
        MockFarm.find = AsyncMock(return_value=mock_farm)
        mock_bedrock.get_annual_crop_strategy = Mock(return_value=mock_bedrock_response)

        mock_strategy = Mock()
        mock_strategy.id = 1
        mock_strategy.farm_id = 1
        mock_strategy.farmer_id = 100
        mock_strategy.year = 2024
        mock_strategy.status = "draft"
        mock_strategy.created_at = datetime.now()
        MockStrategy.create = AsyncMock(return_value=mock_strategy)

        # Import after mocking
        from app.api.v1.annual_strategy import AnnualStrategyRequest, generate_annual_strategy

        # Create request
        request = AnnualStrategyRequest(farm_id=1, year=2024)

        # Call endpoint
        response = await generate_annual_strategy(
            request=request, current_user=mock_current_user, db=Mock()
        )

        # AC2.2: Verify comprehensive annual strategy is returned
        assert response.kharif is not None, "Kharif season recommendations missing"
        assert response.rabi is not None, "Rabi season recommendations missing"
        assert response.zaid is not None, "Zaid season recommendations missing"

        # Verify Kharif details
        assert response.kharif["recommended_crop"] == "Soybean"
        assert response.kharif["variety"] == "JS 335"

        # Verify Rabi details
        assert response.rabi["recommended_crop"] == "Wheat"
        assert response.rabi["variety"] == "HD 2967"

        # Verify Zaid details
        assert response.zaid["recommended_crop"] == "Green Gram"

        print("✓ AC2.2: Comprehensive annual strategy with all three seasons returned")


@pytest.mark.asyncio
async def test_ac2_3_profit_confidence_investment_roi_displayed(
    mock_farm, mock_bedrock_response, mock_current_user
):
    """
    AC2.3: WHEN displaying recommendations
    THEN system SHALL show profit estimates, confidence scores (0-1 range),
    investment requirements, and expected ROI for each season
    """
    with (
        patch("app.api.v1.annual_strategy.Farm") as MockFarm,
        patch("app.api.v1.annual_strategy.bedrock_service") as mock_bedrock,
        patch("app.api.v1.annual_strategy.AnnualStrategy") as MockStrategy,
    ):

        # Setup mocks
        MockFarm.find = AsyncMock(return_value=mock_farm)
        mock_bedrock.get_annual_crop_strategy = Mock(return_value=mock_bedrock_response)

        mock_strategy = Mock()
        mock_strategy.id = 1
        mock_strategy.farm_id = 1
        mock_strategy.farmer_id = 100
        mock_strategy.year = 2024
        mock_strategy.status = "draft"
        mock_strategy.created_at = datetime.now()
        MockStrategy.create = AsyncMock(return_value=mock_strategy)

        # Import after mocking
        from app.api.v1.annual_strategy import AnnualStrategyRequest, generate_annual_strategy

        # Create request
        request = AnnualStrategyRequest(farm_id=1, year=2024)

        # Call endpoint
        response = await generate_annual_strategy(
            request=request, current_user=mock_current_user, db=Mock()
        )

        # AC2.3: Verify profit estimates for all seasons
        assert response.kharif["expected_profit_per_acre"] == 45000
        assert response.rabi["expected_profit_per_acre"] == 52000
        assert response.zaid["expected_profit_per_acre"] == 18000

        # AC2.3: Verify confidence scores are in 0-1 range
        assert 0 <= response.kharif["confidence_score"] <= 1, "Kharif confidence score out of range"
        assert 0 <= response.rabi["confidence_score"] <= 1, "Rabi confidence score out of range"
        assert 0 <= response.zaid["confidence_score"] <= 1, "Zaid confidence score out of range"

        # AC2.3: Verify investment requirements
        assert response.kharif["investment_per_acre"] == 18000
        assert response.rabi["investment_per_acre"] == 22000
        assert response.zaid["investment_per_acre"] == 8000

        # AC2.3: Verify ROI in annual summary
        assert response.annual_summary["total_expected_profit_per_acre"] == 115000
        assert response.annual_summary["total_investment_per_acre"] == 48000
        assert response.annual_summary["roi_percentage"] == 139.6

        print("✓ AC2.3: Profit estimates, confidence scores, investment, and ROI displayed")


@pytest.mark.asyncio
async def test_ac2_4_month_by_month_timeline_12_months(
    mock_farm, mock_bedrock_response, mock_current_user
):
    """
    AC2.4: WHEN presenting annual strategy
    THEN system SHALL include month-by-month implementation timeline
    covering all 12 months of the agricultural year
    """
    with (
        patch("app.api.v1.annual_strategy.Farm") as MockFarm,
        patch("app.api.v1.annual_strategy.bedrock_service") as mock_bedrock,
        patch("app.api.v1.annual_strategy.AnnualStrategy") as MockStrategy,
    ):

        # Setup mocks
        MockFarm.find = AsyncMock(return_value=mock_farm)
        mock_bedrock.get_annual_crop_strategy = Mock(return_value=mock_bedrock_response)

        mock_strategy = Mock()
        mock_strategy.id = 1
        mock_strategy.farm_id = 1
        mock_strategy.farmer_id = 100
        mock_strategy.year = 2024
        mock_strategy.status = "draft"
        mock_strategy.created_at = datetime.now()
        MockStrategy.create = AsyncMock(return_value=mock_strategy)

        # Import after mocking
        from app.api.v1.annual_strategy import AnnualStrategyRequest, generate_annual_strategy

        # Create request
        request = AnnualStrategyRequest(farm_id=1, year=2024)

        # Call endpoint
        response = await generate_annual_strategy(
            request=request, current_user=mock_current_user, db=Mock()
        )

        # AC2.4: Verify month-by-month timeline covers all 12 months
        assert len(response.monthly_action_plan) == 12, "Timeline must cover all 12 months"

        # Verify all months are present
        months = [item["month"] for item in response.monthly_action_plan]
        expected_months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        assert months == expected_months, "All 12 months must be present in order"

        # Verify each month has actions
        for month_plan in response.monthly_action_plan:
            assert "month" in month_plan
            assert "actions" in month_plan
            assert len(month_plan["actions"]) > 0, f"Month {month_plan['month']} must have actions"

        print("✓ AC2.4: Month-by-month implementation timeline covers all 12 months")


@pytest.mark.asyncio
async def test_ac2_5_alternative_options_with_risk_analysis(
    mock_farm, mock_bedrock_response, mock_current_user
):
    """
    AC2.5: WHEN providing recommendations
    THEN system SHALL include alternative crop options
    with risk-benefit analysis for each season
    """
    with (
        patch("app.api.v1.annual_strategy.Farm") as MockFarm,
        patch("app.api.v1.annual_strategy.bedrock_service") as mock_bedrock,
        patch("app.api.v1.annual_strategy.AnnualStrategy") as MockStrategy,
    ):

        # Setup mocks
        MockFarm.find = AsyncMock(return_value=mock_farm)
        mock_bedrock.get_annual_crop_strategy = Mock(return_value=mock_bedrock_response)

        mock_strategy = Mock()
        mock_strategy.id = 1
        mock_strategy.farm_id = 1
        mock_strategy.farmer_id = 100
        mock_strategy.year = 2024
        mock_strategy.status = "draft"
        mock_strategy.created_at = datetime.now()
        MockStrategy.create = AsyncMock(return_value=mock_strategy)

        # Import after mocking
        from app.api.v1.annual_strategy import AnnualStrategyRequest, generate_annual_strategy

        # Create request
        request = AnnualStrategyRequest(farm_id=1, year=2024)

        # Call endpoint
        response = await generate_annual_strategy(
            request=request, current_user=mock_current_user, db=Mock()
        )

        # AC2.5: Verify alternative options are provided
        assert len(response.alternative_options) > 0, "Alternative crop options must be provided"

        # Verify each alternative has required fields
        for alternative in response.alternative_options:
            assert "season" in alternative, "Alternative must specify season"
            assert "crop" in alternative, "Alternative must specify crop name"
            assert "profit_difference" in alternative, "Alternative must show profit difference"
            assert (
                "risk_comparison" in alternative
            ), "Alternative must include risk-benefit analysis"

        # Verify specific alternatives from mock data
        kharif_alt = next(
            (a for a in response.alternative_options if a["season"] == "kharif"), None
        )
        assert kharif_alt is not None, "Kharif alternative must be present"
        assert kharif_alt["crop"] == "Cotton"
        assert "risk" in kharif_alt["risk_comparison"].lower(), "Risk analysis must be present"

        print("✓ AC2.5: Alternative crop options with risk-benefit analysis provided")


@pytest.mark.asyncio
async def test_ac2_6_strategy_persisted_to_database(
    mock_farm, mock_bedrock_response, mock_current_user
):
    """
    AC2.6: WHEN farmer confirms strategy
    THEN system SHALL persist complete strategy to database
    and schedule monthly implementation reminders
    """
    with (
        patch("app.api.v1.annual_strategy.Farm") as MockFarm,
        patch("app.api.v1.annual_strategy.bedrock_service") as mock_bedrock,
        patch("app.api.v1.annual_strategy.AnnualStrategy") as MockStrategy,
    ):

        # Setup mocks
        MockFarm.find = AsyncMock(return_value=mock_farm)
        mock_bedrock.get_annual_crop_strategy = Mock(return_value=mock_bedrock_response)

        mock_strategy = Mock()
        mock_strategy.id = 1
        mock_strategy.farm_id = 1
        mock_strategy.farmer_id = 100
        mock_strategy.year = 2024
        mock_strategy.status = "draft"
        mock_strategy.created_at = datetime.now()
        MockStrategy.create = AsyncMock(return_value=mock_strategy)

        # Import after mocking
        from app.api.v1.annual_strategy import AnnualStrategyRequest, generate_annual_strategy

        # Create request
        request = AnnualStrategyRequest(farm_id=1, year=2024)

        # Call endpoint
        response = await generate_annual_strategy(
            request=request, current_user=mock_current_user, db=Mock()
        )

        # AC2.6: Verify strategy was persisted to database
        MockStrategy.create.assert_called_once()
        create_call_args = MockStrategy.create.call_args[0][0]

        # Verify all required fields are persisted
        assert create_call_args["farm_id"] == 1
        assert create_call_args["farmer_id"] == 100
        assert create_call_args["year"] == 2024
        assert create_call_args["kharif_crop"] == "Soybean"
        assert create_call_args["rabi_crop"] == "Wheat"
        assert create_call_args["zaid_crop"] == "Green Gram"
        assert create_call_args["total_annual_profit"] == 115000
        assert create_call_args["status"] == "draft"

        # Verify JSON fields are stored
        assert create_call_args["implementation_timeline"] is not None
        assert create_call_args["alternative_options"] is not None
        assert create_call_args["bedrock_response"] is not None

        # Verify JSON can be parsed
        timeline = json.loads(create_call_args["implementation_timeline"])
        assert len(timeline) == 12, "Timeline must have 12 months"

        alternatives = json.loads(create_call_args["alternative_options"])
        assert len(alternatives) > 0, "Alternatives must be stored"

        print("✓ AC2.6: Strategy persisted to database with all required fields")


@pytest.mark.asyncio
async def test_ac2_7_bedrock_response_stored_for_audit(
    mock_farm, mock_bedrock_response, mock_current_user
):
    """
    AC2.7: WHEN strategy is saved
    THEN system SHALL store complete Bedrock response
    in JSONB field for reference and audit
    """
    with (
        patch("app.api.v1.annual_strategy.Farm") as MockFarm,
        patch("app.api.v1.annual_strategy.bedrock_service") as mock_bedrock,
        patch("app.api.v1.annual_strategy.AnnualStrategy") as MockStrategy,
    ):

        # Setup mocks
        MockFarm.find = AsyncMock(return_value=mock_farm)
        mock_bedrock.get_annual_crop_strategy = Mock(return_value=mock_bedrock_response)

        mock_strategy = Mock()
        mock_strategy.id = 1
        mock_strategy.farm_id = 1
        mock_strategy.farmer_id = 100
        mock_strategy.year = 2024
        mock_strategy.status = "draft"
        mock_strategy.created_at = datetime.now()
        MockStrategy.create = AsyncMock(return_value=mock_strategy)

        # Import after mocking
        from app.api.v1.annual_strategy import AnnualStrategyRequest, generate_annual_strategy

        # Create request
        request = AnnualStrategyRequest(farm_id=1, year=2024)

        # Call endpoint
        response = await generate_annual_strategy(
            request=request, current_user=mock_current_user, db=Mock()
        )

        # AC2.7: Verify complete Bedrock response is stored
        create_call_args = MockStrategy.create.call_args[0][0]
        bedrock_response_stored = create_call_args["bedrock_response"]

        assert bedrock_response_stored is not None, "Bedrock response must be stored"

        # Parse and verify complete response is stored
        stored_response = json.loads(bedrock_response_stored)

        # Verify all sections are present
        assert "kharif" in stored_response, "Kharif data must be in stored response"
        assert "rabi" in stored_response, "Rabi data must be in stored response"
        assert "zaid" in stored_response, "Zaid data must be in stored response"
        assert "annual_summary" in stored_response, "Annual summary must be in stored response"
        assert "alternative_options" in stored_response, "Alternatives must be in stored response"
        assert "monthly_action_plan" in stored_response, "Monthly plan must be in stored response"

        # Verify data integrity
        assert stored_response["kharif"]["recommended_crop"] == "Soybean"
        assert stored_response["rabi"]["recommended_crop"] == "Wheat"
        assert stored_response["annual_summary"]["total_expected_profit_per_acre"] == 115000

        print("✓ AC2.7: Complete Bedrock response stored in JSONB field for audit")


@pytest.mark.asyncio
async def test_api_response_time_under_10_seconds():
    """
    Validation Metric: API response time < 10 seconds (95th percentile)

    Note: This is a mock test. Real performance testing should be done with load testing tools.
    """
    import time

    with (
        patch("app.api.v1.annual_strategy.Farm") as MockFarm,
        patch("app.api.v1.annual_strategy.bedrock_service") as mock_bedrock,
        patch("app.api.v1.annual_strategy.AnnualStrategy") as MockStrategy,
    ):

        # Setup mocks
        mock_farm = Mock()
        mock_farm.id = 1
        mock_farm.farmer_id = 100
        mock_farm.state = "Maharashtra"
        mock_farm.district = "Pune"
        mock_farm.soil_type = "Black"
        mock_farm.total_area = 5.0
        mock_farm.irrigation_type = "Borewell"

        MockFarm.find = AsyncMock(return_value=mock_farm)

        # Simulate Bedrock API response time (should be < 10 seconds)
        def mock_bedrock_call(*args, **kwargs):
            time.sleep(0.1)  # Simulate 100ms API call
            return {
                "kharif": {"recommended_crop": "Soybean", "confidence_score": 0.85},
                "rabi": {"recommended_crop": "Wheat", "confidence_score": 0.90},
                "zaid": {"recommended_crop": None},
                "annual_summary": {"total_expected_profit_per_acre": 100000},
                "alternative_options": [],
                "monthly_action_plan": [],
            }

        mock_bedrock.get_annual_crop_strategy = Mock(side_effect=mock_bedrock_call)

        mock_strategy = Mock()
        mock_strategy.id = 1
        mock_strategy.farm_id = 1
        mock_strategy.farmer_id = 100
        mock_strategy.year = 2024
        mock_strategy.status = "draft"
        mock_strategy.created_at = datetime.now()
        MockStrategy.create = AsyncMock(return_value=mock_strategy)

        # Import after mocking
        from app.api.v1.annual_strategy import AnnualStrategyRequest, generate_annual_strategy

        # Measure response time
        start_time = time.time()

        request = AnnualStrategyRequest(farm_id=1, year=2024)
        response = await generate_annual_strategy(
            request=request, current_user={"user_id": 100}, db=Mock()
        )

        end_time = time.time()
        response_time = end_time - start_time

        # Verify response time is under 10 seconds
        assert response_time < 10.0, f"API response time {response_time}s exceeds 10 second limit"

        print(f"✓ API response time: {response_time:.2f}s (< 10s requirement)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
