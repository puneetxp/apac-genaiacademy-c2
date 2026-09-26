"""
Comprehensive tests for Pest and Disease Early Warning Service

Tests cover:
- Risk detection for different pests/diseases
- Temperature and humidity threshold validation
- Stage-specific risk detection
- Multiple simultaneous risk detection
- Organic and chemical recommendation retrieval
- Prevention guidance generation
- Alert notification system
- Data integrity validation

Validates: Requirements AC10 (Phase 6 - Required)
Task 25.2: Build pest and disease early warning system
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.pest_disease_service import (
    PEST_DISEASE_MANAGEMENT,
    PEST_DISEASE_THRESHOLDS,
    PestDiseaseService,
)


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = AsyncMock(spec=AsyncSession)
    return db


@pytest.fixture
def pest_disease_service(mock_db):
    """Create pest disease service instance"""
    return PestDiseaseService(mock_db)


@pytest.fixture
def mock_crop():
    """Mock crop object"""
    crop = Mock()
    crop.id = 1
    crop.farm_id = 100
    crop.crop_name = "wheat"
    crop.status = "active"
    crop.expected_harvest_date = (datetime.now() + timedelta(days=60)).date()
    return crop


class TestRiskDetection:
    """Test pest and disease risk detection"""

    @pytest.mark.asyncio
    async def test_aphid_risk_detection_temperature_range(
        self, pest_disease_service, mock_db, mock_crop
    ):
        """Test aphid risk detection within temperature range"""
        # Setup
        weather_data = {
            "temperature": 25,  # Within 20-30°C range
            "humidity": 65,  # Above 60% threshold
            "rainfall": 0,
        }
        current_stage = "vegetative"

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_crop
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Execute
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1, weather_data=weather_data, current_stage=current_stage, save_to_db=False
        )

        # Verify
        assert len(risks) > 0
        aphid_risk = next((r for r in risks if r["pest_disease"] == "aphids"), None)
        assert aphid_risk is not None
        assert aphid_risk["severity"] == "medium"
        assert aphid_risk["description"] == "Aphid infestation risk"
        assert aphid_risk["current_conditions"]["temperature"] == 25
        assert aphid_risk["current_conditions"]["humidity"] == 65

    @pytest.mark.asyncio
    async def test_no_risk_outside_temperature_range(
        self, pest_disease_service, mock_db, mock_crop
    ):
        """Test no aphid risk when temperature is outside range"""
        # Setup
        weather_data = {"temperature": 35, "humidity": 65, "rainfall": 0}  # Outside 20-30°C range
        current_stage = "vegetative"

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_crop
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Execute
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1, weather_data=weather_data, current_stage=current_stage, save_to_db=False
        )

        # Verify - aphids should not be detected
        aphid_risk = next((r for r in risks if r["pest_disease"] == "aphids"), None)
        assert aphid_risk is None

    @pytest.mark.asyncio
    async def test_fungal_disease_risk_with_rainfall(
        self, pest_disease_service, mock_db, mock_crop
    ):
        """Test fungal disease risk detection with rainfall threshold"""
        # Setup
        weather_data = {
            "temperature": 22,  # Within 15-28°C range
            "humidity": 85,  # Above 80% threshold
            "rainfall": 8,  # Above 5mm threshold
        }
        current_stage = "vegetative"

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_crop
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Execute
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1, weather_data=weather_data, current_stage=current_stage, save_to_db=False
        )

        # Verify
        fungal_risk = next((r for r in risks if r["pest_disease"] == "fungal_diseases"), None)
        assert fungal_risk is not None
        assert fungal_risk["severity"] == "high"
        assert fungal_risk["current_conditions"]["rainfall"] == 8

    @pytest.mark.asyncio
    async def test_no_fungal_risk_insufficient_rainfall(
        self, pest_disease_service, mock_db, mock_crop
    ):
        """Test no fungal disease risk when rainfall is insufficient"""
        # Setup
        weather_data = {"temperature": 22, "humidity": 85, "rainfall": 2}  # Below 5mm threshold
        current_stage = "vegetative"

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_crop
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Execute
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1, weather_data=weather_data, current_stage=current_stage, save_to_db=False
        )

        # Verify - fungal diseases should not be detected
        fungal_risk = next((r for r in risks if r["pest_disease"] == "fungal_diseases"), None)
        assert fungal_risk is None

    @pytest.mark.asyncio
    async def test_stage_specific_risk_detection(self, pest_disease_service, mock_db, mock_crop):
        """Test that risks are only detected for appropriate growth stages"""
        # Setup - fruit borer only affects flowering and maturation stages
        weather_data = {"temperature": 25, "humidity": 65, "rainfall": 0}

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_crop
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Test vegetative stage - should NOT detect fruit borer
        risks_vegetative = await pest_disease_service.check_pest_disease_risk(
            crop_id=1, weather_data=weather_data, current_stage="vegetative", save_to_db=False
        )
        fruit_borer_veg = next(
            (r for r in risks_vegetative if r["pest_disease"] == "fruit_borer"), None
        )
        assert fruit_borer_veg is None

        # Test flowering stage - SHOULD detect fruit borer
        risks_flowering = await pest_disease_service.check_pest_disease_risk(
            crop_id=1, weather_data=weather_data, current_stage="flowering", save_to_db=False
        )
        fruit_borer_flower = next(
            (r for r in risks_flowering if r["pest_disease"] == "fruit_borer"), None
        )
        assert fruit_borer_flower is not None
        assert fruit_borer_flower["severity"] == "high"

    @pytest.mark.asyncio
    async def test_multiple_simultaneous_risks(self, pest_disease_service, mock_db, mock_crop):
        """Test detection of multiple pest/disease risks simultaneously"""
        # Setup - conditions favorable for multiple pests
        weather_data = {
            "temperature": 26,  # Favorable for aphids, whitefly, stem borer
            "humidity": 75,  # Favorable for multiple pests
            "rainfall": 0,
        }
        current_stage = "vegetative"

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_crop
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Execute
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1, weather_data=weather_data, current_stage=current_stage, save_to_db=False
        )

        # Verify - should detect multiple risks
        assert len(risks) >= 2
        pest_names = [r["pest_disease"] for r in risks]
        assert "aphids" in pest_names
        assert "stem_borer" in pest_names or "whitefly" in pest_names

    @pytest.mark.asyncio
    async def test_powdery_mildew_humidity_range(self, pest_disease_service, mock_db, mock_crop):
        """Test powdery mildew detection with humidity range (50-70%)"""
        # Setup
        weather_data = {
            "temperature": 23,  # Within 18-28°C range
            "humidity": 60,  # Within 50-70% range
            "rainfall": 0,
        }
        current_stage = "vegetative"

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_crop
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Execute
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1, weather_data=weather_data, current_stage=current_stage, save_to_db=False
        )

        # Verify
        mildew_risk = next((r for r in risks if r["pest_disease"] == "powdery_mildew"), None)
        assert mildew_risk is not None
        assert mildew_risk["severity"] == "medium"

    @pytest.mark.asyncio
    async def test_no_risk_for_wrong_stage(self, pest_disease_service, mock_db, mock_crop):
        """Test that no risks are detected for inappropriate growth stages"""
        # Setup - perfect conditions but wrong stage
        weather_data = {"temperature": 25, "humidity": 70, "rainfall": 0}
        current_stage = "harvesting"  # No pests target this stage

        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_crop
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Execute
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1, weather_data=weather_data, current_stage=current_stage, save_to_db=False
        )

        # Verify - should detect no risks
        assert len(risks) == 0


class TestManagementRecommendations:
    """Test pest and disease management recommendations"""

    @pytest.mark.asyncio
    async def test_get_organic_recommendations(self, pest_disease_service):
        """Test retrieval of organic treatment recommendations"""
        # Execute
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease="aphids", preference="organic"
        )

        # Verify
        assert recommendations["pest_disease"] == "aphids"
        assert "organic_options" in recommendations
        assert len(recommendations["organic_options"]) > 0
        assert "neem oil" in recommendations["organic_options"][0].lower()
        assert "chemical_options" not in recommendations
        assert "timing" in recommendations
        assert "prevention" in recommendations

    @pytest.mark.asyncio
    async def test_get_chemical_recommendations(self, pest_disease_service):
        """Test retrieval of chemical treatment recommendations"""
        # Execute
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease="fungal_diseases", preference="chemical"
        )

        # Verify
        assert recommendations["pest_disease"] == "fungal_diseases"
        assert "chemical_options" in recommendations
        assert len(recommendations["chemical_options"]) > 0
        assert "organic_options" not in recommendations
        assert "timing" in recommendations
        assert "prevention" in recommendations

    @pytest.mark.asyncio
    async def test_get_both_recommendations(self, pest_disease_service):
        """Test retrieval of both organic and chemical recommendations"""
        # Execute
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease="stem_borer", preference="both"
        )

        # Verify
        assert recommendations["pest_disease"] == "stem_borer"
        assert "organic_options" in recommendations
        assert "chemical_options" in recommendations
        assert len(recommendations["organic_options"]) > 0
        assert len(recommendations["chemical_options"]) > 0
        assert "timing" in recommendations
        assert "prevention" in recommendations

    @pytest.mark.asyncio
    async def test_invalid_pest_disease_name(self, pest_disease_service):
        """Test handling of invalid pest/disease name"""
        # Execute
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease="invalid_pest", preference="both"
        )

        # Verify
        assert "error" in recommendations
        assert "invalid_pest" in recommendations["error"]

    @pytest.mark.asyncio
    async def test_timing_instructions_present(self, pest_disease_service):
        """Test that timing instructions are included in recommendations"""
        # Execute
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease="whitefly", preference="both"
        )

        # Verify
        assert "timing" in recommendations
        assert len(recommendations["timing"]) > 0
        assert (
            "apply" in recommendations["timing"].lower()
            or "repeat" in recommendations["timing"].lower()
        )

    @pytest.mark.asyncio
    async def test_prevention_measures_present(self, pest_disease_service):
        """Test that prevention measures are included in recommendations"""
        # Execute
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease="bacterial_wilt", preference="both"
        )

        # Verify
        assert "prevention" in recommendations
        assert len(recommendations["prevention"]) > 0
        assert isinstance(recommendations["prevention"], list)


class TestCropSpecificRisks:
    """Test crop-specific risk information"""

    @pytest.mark.asyncio
    async def test_get_vegetative_stage_risks(self, pest_disease_service):
        """Test retrieval of risks for vegetative stage"""
        # Execute
        risks = await pest_disease_service.get_crop_specific_risks(
            crop_name="wheat", current_stage="vegetative"
        )

        # Verify
        assert len(risks) > 0
        for risk in risks:
            assert "vegetative" in risk["risk_stages"]
            assert "pest_disease" in risk
            assert "severity" in risk
            assert "management" in risk

    @pytest.mark.asyncio
    async def test_get_flowering_stage_risks(self, pest_disease_service):
        """Test retrieval of risks for flowering stage"""
        # Execute
        risks = await pest_disease_service.get_crop_specific_risks(
            crop_name="wheat", current_stage="flowering"
        )

        # Verify
        assert len(risks) > 0
        for risk in risks:
            assert "flowering" in risk["risk_stages"]

    @pytest.mark.asyncio
    async def test_get_maturation_stage_risks(self, pest_disease_service):
        """Test retrieval of risks for maturation stage"""
        # Execute
        risks = await pest_disease_service.get_crop_specific_risks(
            crop_name="wheat", current_stage="maturation"
        )

        # Verify
        # Maturation stage has fewer risks
        for risk in risks:
            assert "maturation" in risk["risk_stages"]

    @pytest.mark.asyncio
    async def test_risk_includes_management_data(self, pest_disease_service):
        """Test that crop-specific risks include management data"""
        # Execute
        risks = await pest_disease_service.get_crop_specific_risks(
            crop_name="wheat", current_stage="vegetative"
        )

        # Verify
        assert len(risks) > 0
        for risk in risks:
            assert "management" in risk
            management = risk["management"]
            assert "organic" in management or "chemical" in management
            assert "timing" in management
            assert "prevention" in management


class TestPreventionGuidance:
    """Test disease prevention guidance"""

    @pytest.mark.asyncio
    async def test_get_prevention_guidance_vegetative(self, pest_disease_service):
        """Test prevention guidance for vegetative stage"""
        # Execute
        guidance = await pest_disease_service.get_prevention_guidance(
            crop_id=1, current_stage="vegetative"
        )

        # Verify
        assert guidance["crop_id"] == 1
        assert guidance["current_stage"] == "vegetative"
        assert "relevant_risks" in guidance
        assert "prevention_measures" in guidance
        assert "timing_instructions" in guidance
        assert "general_guidance" in guidance
        assert len(guidance["prevention_measures"]) > 0
        assert len(guidance["general_guidance"]) > 0

    @pytest.mark.asyncio
    async def test_prevention_measures_unique(self, pest_disease_service):
        """Test that prevention measures are deduplicated"""
        # Execute
        guidance = await pest_disease_service.get_prevention_guidance(
            crop_id=1, current_stage="vegetative"
        )

        # Verify - no duplicate measures
        measures = guidance["prevention_measures"]
        assert len(measures) == len(set(measures))

    @pytest.mark.asyncio
    async def test_timing_instructions_present(self, pest_disease_service):
        """Test that timing instructions are provided"""
        # Execute
        guidance = await pest_disease_service.get_prevention_guidance(
            crop_id=1, current_stage="flowering"
        )

        # Verify
        assert "timing_instructions" in guidance
        assert len(guidance["timing_instructions"]) > 0

    @pytest.mark.asyncio
    async def test_general_guidance_always_present(self, pest_disease_service):
        """Test that general guidance is always provided"""
        # Execute
        guidance = await pest_disease_service.get_prevention_guidance(
            crop_id=1, current_stage="maturation"
        )

        # Verify
        assert "general_guidance" in guidance
        assert len(guidance["general_guidance"]) >= 5
        assert any("monitor" in g.lower() for g in guidance["general_guidance"])
        assert any(
            "sanitation" in g.lower() or "debris" in g.lower() for g in guidance["general_guidance"]
        )


class TestDataIntegrity:
    """Test data integrity and completeness"""

    def test_all_pests_have_management_data(self):
        """Test that all pests in thresholds have management data"""
        for pest_disease in PEST_DISEASE_THRESHOLDS.keys():
            assert (
                pest_disease in PEST_DISEASE_MANAGEMENT
            ), f"Missing management data for {pest_disease}"

    def test_all_management_has_required_fields(self):
        """Test that all management data has required fields"""
        required_fields = ["organic", "chemical", "timing", "prevention"]

        for pest_disease, management in PEST_DISEASE_MANAGEMENT.items():
            for field in required_fields:
                assert field in management, f"Missing {field} in management data for {pest_disease}"
                assert (
                    len(management[field]) > 0
                ), f"Empty {field} in management data for {pest_disease}"

    def test_all_thresholds_have_required_fields(self):
        """Test that all thresholds have required fields"""
        required_fields = ["risk_stages", "severity", "description"]

        for pest_disease, thresholds in PEST_DISEASE_THRESHOLDS.items():
            for field in required_fields:
                assert field in thresholds, f"Missing {field} in thresholds for {pest_disease}"

    def test_severity_levels_valid(self):
        """Test that all severity levels are valid"""
        valid_severities = ["low", "medium", "high"]

        for pest_disease, thresholds in PEST_DISEASE_THRESHOLDS.items():
            severity = thresholds["severity"]
            assert severity in valid_severities, f"Invalid severity '{severity}' for {pest_disease}"

    def test_risk_stages_valid(self):
        """Test that all risk stages are valid"""
        valid_stages = ["vegetative", "flowering", "maturation", "harvesting"]

        for pest_disease, thresholds in PEST_DISEASE_THRESHOLDS.items():
            risk_stages = thresholds["risk_stages"]
            assert len(risk_stages) > 0, f"No risk stages defined for {pest_disease}"
            for stage in risk_stages:
                assert stage in valid_stages, f"Invalid stage '{stage}' for {pest_disease}"

    def test_temperature_ranges_logical(self):
        """Test that temperature ranges are logical"""
        for pest_disease, thresholds in PEST_DISEASE_THRESHOLDS.items():
            if "temp_min" in thresholds and "temp_max" in thresholds:
                assert (
                    thresholds["temp_min"] < thresholds["temp_max"]
                ), f"Invalid temperature range for {pest_disease}"
                assert 0 <= thresholds["temp_min"] <= 50, f"Invalid temp_min for {pest_disease}"
                assert 0 <= thresholds["temp_max"] <= 50, f"Invalid temp_max for {pest_disease}"

    def test_humidity_ranges_logical(self):
        """Test that humidity ranges are logical"""
        for pest_disease, thresholds in PEST_DISEASE_THRESHOLDS.items():
            if "humidity_min" in thresholds:
                assert (
                    0 <= thresholds["humidity_min"] <= 100
                ), f"Invalid humidity_min for {pest_disease}"
            if "humidity_max" in thresholds:
                assert (
                    0 <= thresholds["humidity_max"] <= 100
                ), f"Invalid humidity_max for {pest_disease}"
                assert (
                    thresholds["humidity_min"] < thresholds["humidity_max"]
                ), f"Invalid humidity range for {pest_disease}"

    def test_coverage_of_common_pests(self):
        """Test that common pests and diseases are covered"""
        expected_pests = ["aphids", "whitefly", "stem_borer", "fruit_borer", "leaf_miner"]
        expected_diseases = ["fungal_diseases", "bacterial_wilt", "powdery_mildew"]

        for pest in expected_pests:
            assert pest in PEST_DISEASE_THRESHOLDS, f"Missing common pest: {pest}"

        for disease in expected_diseases:
            assert disease in PEST_DISEASE_THRESHOLDS, f"Missing common disease: {disease}"


class TestAlertNotification:
    """Test alert notification system"""

    @pytest.mark.asyncio
    async def test_send_pest_disease_alert(self, pest_disease_service):
        """Test sending pest/disease alert to farmer"""
        # Setup
        risk = {
            "pest_disease": "aphids",
            "severity": "medium",
            "description": "Aphid infestation risk",
            "management": {
                "organic": ["Spray neem oil solution"],
                "chemical": ["Apply Imidacloprid"],
                "timing": "Apply at first sign",
                "prevention": ["Monitor plants weekly"],
            },
        }

        # Mock notification service
        with patch.object(
            pest_disease_service.notification_service, "send_strategy_reminder"
        ) as mock_send:
            mock_send.return_value = {"success": True}

            # Execute
            result = await pest_disease_service.send_pest_disease_alert(
                crop_id=1,
                farmer_phone="+919876543210",
                farmer_email="farmer@example.com",
                farmer_name="Test Farmer",
                crop_name="wheat",
                risk=risk,
            )

            # Verify
            assert result["success"] is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args[1]
            assert call_args["farmer_phone"] == "+919876543210"
            assert call_args["farmer_name"] == "Test Farmer"
            assert len(call_args["action_items"]) > 0

    @pytest.mark.asyncio
    async def test_alert_includes_action_items(self, pest_disease_service):
        """Test that alert includes actionable recommendations"""
        # Setup
        risk = {
            "pest_disease": "fungal_diseases",
            "severity": "high",
            "description": "Fungal disease risk",
            "management": {
                "organic": ["Apply Trichoderma viride"],
                "chemical": ["Spray Mancozeb"],
                "timing": "Apply preventively before monsoon",
                "prevention": ["Ensure good drainage"],
            },
        }

        # Mock notification service
        with patch.object(
            pest_disease_service.notification_service, "send_strategy_reminder"
        ) as mock_send:
            mock_send.return_value = {"success": True}

            # Execute
            await pest_disease_service.send_pest_disease_alert(
                crop_id=1,
                farmer_phone="+919876543210",
                farmer_email=None,
                farmer_name="Test Farmer",
                crop_name="wheat",
                risk=risk,
            )

            # Verify action items
            call_args = mock_send.call_args[1]
            action_items = call_args["action_items"]
            assert len(action_items) > 0
            assert any("organic" in item.lower() for item in action_items)
            assert any("timing" in item.lower() for item in action_items)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
