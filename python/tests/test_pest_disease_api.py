"""
API tests for Pest and Disease Early Warning System

Tests cover:
- Risk checking endpoint
- Management recommendations endpoint
- Crop-specific risks endpoint
- Prevention guidance endpoint
- Alert management endpoints
- Farm-wide alert retrieval
- Available pests listing

Validates: Requirements AC10 (Phase 6 - Required)
Task 25.2: Build pest and disease early warning system
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_pest_disease_service():
    """Mock pest disease service"""
    service = Mock()
    service.check_pest_disease_risk = AsyncMock()
    service.get_management_recommendations = AsyncMock()
    service.get_crop_specific_risks = AsyncMock()
    service.get_prevention_guidance = AsyncMock()
    return service


class TestRiskCheckEndpoint:
    """Test POST /pest-disease/check-risk endpoint"""

    def test_check_risk_success(self, client):
        """Test successful risk check"""
        # Setup
        request_data = {
            "crop_id": 1,
            "weather_data": {"temperature": 25, "humidity": 70, "rainfall": 0},
            "current_stage": "vegetative",
        }

        mock_risks = [
            {
                "pest_disease": "aphids",
                "severity": "medium",
                "description": "Aphid infestation risk",
                "current_conditions": {
                    "temperature": 25,
                    "humidity": 70,
                    "rainfall": 0,
                    "crop_stage": "vegetative",
                },
                "management": {
                    "organic": ["Spray neem oil"],
                    "chemical": ["Apply Imidacloprid"],
                    "timing": "Apply at first sign",
                    "prevention": ["Monitor plants weekly"],
                },
                "detected_at": datetime.now().isoformat(),
            }
        ]

        # Mock service
        with patch("app.api.v1.pest_disease.get_pest_disease_service") as mock_get_service:
            mock_service = Mock()
            mock_service.check_pest_disease_risk = AsyncMock(return_value=mock_risks)
            mock_get_service.return_value = mock_service

            # Execute
            response = client.post("/pest-disease/check-risk", json=request_data)

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["pest_disease"] == "aphids"
            assert data[0]["severity"] == "medium"

    def test_check_risk_no_risks_detected(self, client):
        """Test risk check when no risks are detected"""
        # Setup
        request_data = {
            "crop_id": 1,
            "weather_data": {"temperature": 35, "humidity": 40, "rainfall": 0},
            "current_stage": "vegetative",
        }

        # Mock service
        with patch("app.api.v1.pest_disease.get_pest_disease_service") as mock_get_service:
            mock_service = Mock()
            mock_service.check_pest_disease_risk = AsyncMock(return_value=[])
            mock_get_service.return_value = mock_service

            # Execute
            response = client.post("/pest-disease/check-risk", json=request_data)

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0

    def test_check_risk_invalid_humidity(self, client):
        """Test risk check with invalid humidity value"""
        # Setup
        request_data = {
            "crop_id": 1,
            "weather_data": {
                "temperature": 25,
                "humidity": 150,  # Invalid - over 100
                "rainfall": 0,
            },
            "current_stage": "vegetative",
        }

        # Execute
        response = client.post("/pest-disease/check-risk", json=request_data)

        # Verify
        assert response.status_code == 422  # Validation error

    def test_check_risk_missing_required_fields(self, client):
        """Test risk check with missing required fields"""
        # Setup
        request_data = {
            "crop_id": 1,
            "weather_data": {
                "temperature": 25
                # Missing humidity
            },
            "current_stage": "vegetative",
        }

        # Execute
        response = client.post("/pest-disease/check-risk", json=request_data)

        # Verify
        assert response.status_code == 422  # Validation error


class TestManagementRecommendationsEndpoint:
    """Test GET /pest-disease/management/{pest_disease} endpoint"""

    def test_get_organic_recommendations(self, client):
        """Test getting organic recommendations"""
        # Mock service
        mock_recommendations = {
            "pest_disease": "aphids",
            "timing": "Apply at first sign",
            "prevention": ["Monitor plants weekly"],
            "organic_options": ["Spray neem oil", "Release ladybugs"],
        }

        with patch("app.api.v1.pest_disease.get_pest_disease_service") as mock_get_service:
            mock_service = Mock()
            mock_service.get_management_recommendations = AsyncMock(
                return_value=mock_recommendations
            )
            mock_get_service.return_value = mock_service

            # Execute
            response = client.get("/pest-disease/management/aphids?preference=organic")

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["pest_disease"] == "aphids"
            assert "organic_options" in data
            assert "chemical_options" not in data

    def test_get_chemical_recommendations(self, client):
        """Test getting chemical recommendations"""
        # Mock service
        mock_recommendations = {
            "pest_disease": "fungal_diseases",
            "timing": "Apply preventively",
            "prevention": ["Ensure good drainage"],
            "chemical_options": ["Spray Mancozeb", "Apply Carbendazim"],
        }

        with patch("app.api.v1.pest_disease.get_pest_disease_service") as mock_get_service:
            mock_service = Mock()
            mock_service.get_management_recommendations = AsyncMock(
                return_value=mock_recommendations
            )
            mock_get_service.return_value = mock_service

            # Execute
            response = client.get("/pest-disease/management/fungal_diseases?preference=chemical")

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["pest_disease"] == "fungal_diseases"
            assert "chemical_options" in data
            assert "organic_options" not in data

    def test_get_both_recommendations(self, client):
        """Test getting both organic and chemical recommendations"""
        # Mock service
        mock_recommendations = {
            "pest_disease": "stem_borer",
            "timing": "Apply at early vegetative stage",
            "prevention": ["Remove crop residues"],
            "organic_options": ["Release Trichogramma wasps"],
            "chemical_options": ["Apply Chlorantraniliprole"],
        }

        with patch("app.api.v1.pest_disease.get_pest_disease_service") as mock_get_service:
            mock_service = Mock()
            mock_service.get_management_recommendations = AsyncMock(
                return_value=mock_recommendations
            )
            mock_get_service.return_value = mock_service

            # Execute
            response = client.get("/pest-disease/management/stem_borer?preference=both")

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert "organic_options" in data
            assert "chemical_options" in data

    def test_get_recommendations_invalid_pest(self, client):
        """Test getting recommendations for invalid pest"""
        # Mock service
        with patch("app.api.v1.pest_disease.get_pest_disease_service") as mock_get_service:
            mock_service = Mock()
            mock_service.get_management_recommendations = AsyncMock(
                return_value={"error": "No management data available for invalid_pest"}
            )
            mock_get_service.return_value = mock_service

            # Execute
            response = client.get("/pest-disease/management/invalid_pest")

            # Verify
            assert response.status_code == 404

    def test_get_recommendations_invalid_preference(self, client):
        """Test getting recommendations with invalid preference"""
        # Execute
        response = client.get("/pest-disease/management/aphids?preference=invalid")

        # Verify
        assert response.status_code == 422  # Validation error


class TestCropSpecificRisksEndpoint:
    """Test GET /pest-disease/crop-risks/{crop_id} endpoint"""

    def test_get_crop_risks_success(self, client):
        """Test getting crop-specific risks"""
        # Mock crop
        mock_crop = Mock()
        mock_crop.id = 1
        mock_crop.crop_name = "wheat"

        # Mock risks
        mock_risks = [
            {
                "pest_disease": "aphids",
                "severity": "medium",
                "description": "Aphid infestation risk",
                "risk_stages": ["vegetative", "flowering"],
                "management": {},
            }
        ]

        with (
            patch("app.api.v1.pest_disease.get_pest_disease_service") as mock_get_service,
            patch("app.api.v1.pest_disease.get_db") as mock_get_db,
        ):

            # Mock service
            mock_service = Mock()
            mock_service.get_crop_specific_risks = AsyncMock(return_value=mock_risks)
            mock_get_service.return_value = mock_service

            # Mock database
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_crop
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = mock_db

            # Execute
            response = client.get("/pest-disease/crop-risks/1?current_stage=vegetative")

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["crop_id"] == 1
            assert data["crop_name"] == "wheat"
            assert data["current_stage"] == "vegetative"
            assert len(data["risks"]) == 1

    def test_get_crop_risks_crop_not_found(self, client):
        """Test getting risks for non-existent crop"""
        with patch("app.api.v1.pest_disease.get_db") as mock_get_db:
            # Mock database
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = mock_db

            # Execute
            response = client.get("/pest-disease/crop-risks/999?current_stage=vegetative")

            # Verify
            assert response.status_code == 404


class TestPreventionGuidanceEndpoint:
    """Test GET /pest-disease/prevention-guidance/{crop_id} endpoint"""

    def test_get_prevention_guidance_success(self, client):
        """Test getting prevention guidance"""
        # Mock guidance
        mock_guidance = {
            "crop_id": 1,
            "current_stage": "vegetative",
            "relevant_risks": ["aphids", "fungal_diseases"],
            "prevention_measures": ["Monitor plants weekly", "Ensure good drainage"],
            "timing_instructions": ["Aphids: Apply at first sign"],
            "general_guidance": ["Monitor crops regularly"],
        }

        with patch("app.api.v1.pest_disease.get_pest_disease_service") as mock_get_service:
            mock_service = Mock()
            mock_service.get_prevention_guidance = AsyncMock(return_value=mock_guidance)
            mock_get_service.return_value = mock_service

            # Execute
            response = client.get("/pest-disease/prevention-guidance/1?current_stage=vegetative")

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["crop_id"] == 1
            assert data["current_stage"] == "vegetative"
            assert len(data["prevention_measures"]) > 0
            assert len(data["general_guidance"]) > 0


class TestAlertManagementEndpoints:
    """Test alert management endpoints"""

    def test_get_crop_alerts(self, client):
        """Test getting alerts for a crop"""
        # Mock alerts
        mock_alert = Mock()
        mock_alert.to_dict.return_value = {
            "id": 1,
            "crop_id": 1,
            "pest_disease_name": "aphids",
            "severity": "medium",
            "is_resolved": False,
        }

        with patch("app.api.v1.pest_disease.get_db") as mock_get_db:
            # Mock database
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_alert]
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = mock_db

            # Execute
            response = client.get("/pest-disease/alerts/1")

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["crop_id"] == 1
            assert data["total_alerts"] == 1
            assert len(data["alerts"]) == 1

    def test_get_crop_alerts_include_resolved(self, client):
        """Test getting alerts including resolved ones"""
        with patch("app.api.v1.pest_disease.get_db") as mock_get_db:
            # Mock database
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = []
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = mock_db

            # Execute
            response = client.get("/pest-disease/alerts/1?include_resolved=true")

            # Verify
            assert response.status_code == 200

    def test_resolve_alert_success(self, client):
        """Test resolving an alert"""
        # Mock alert
        mock_alert = Mock()
        mock_alert.id = 1
        mock_alert.is_resolved = False
        mock_alert.save = AsyncMock()
        mock_alert.to_dict.return_value = {"id": 1, "is_resolved": True}

        with patch("app.api.v1.pest_disease.get_db") as mock_get_db:
            # Mock database
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_alert
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = mock_db

            # Execute
            response = client.patch("/pest-disease/alerts/1/resolve")

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "alert" in data

    def test_resolve_alert_not_found(self, client):
        """Test resolving non-existent alert"""
        with patch("app.api.v1.pest_disease.get_db") as mock_get_db:
            # Mock database
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = mock_db

            # Execute
            response = client.patch("/pest-disease/alerts/999/resolve")

            # Verify
            assert response.status_code == 404

    def test_get_farm_alerts(self, client):
        """Test getting alerts for a farm"""
        # Mock alerts
        mock_alert = Mock()
        mock_alert.to_dict.return_value = {
            "id": 1,
            "farm_id": 100,
            "pest_disease_name": "fungal_diseases",
            "severity": "high",
        }

        with patch("app.api.v1.pest_disease.get_db") as mock_get_db:
            # Mock database
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_alert]
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = mock_db

            # Execute
            response = client.get("/pest-disease/alerts/farm/100")

            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["farm_id"] == 100
            assert data["total_alerts"] == 1

    def test_get_farm_alerts_with_limit(self, client):
        """Test getting farm alerts with limit"""
        with patch("app.api.v1.pest_disease.get_db") as mock_get_db:
            # Mock database
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = []
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = mock_db

            # Execute
            response = client.get("/pest-disease/alerts/farm/100?limit=10")

            # Verify
            assert response.status_code == 200


class TestAvailablePestsEndpoint:
    """Test GET /pest-disease/available-pests endpoint"""

    def test_get_available_pests(self, client):
        """Test getting list of available pests and diseases"""
        # Execute
        response = client.get("/pest-disease/available-pests")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "pests_diseases" in data
        assert data["total"] > 0
        assert len(data["pests_diseases"]) == data["total"]

        # Check structure of first pest
        first_pest = data["pests_diseases"][0]
        assert "name" in first_pest
        assert "description" in first_pest
        assert "severity" in first_pest
        assert "risk_stages" in first_pest


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
