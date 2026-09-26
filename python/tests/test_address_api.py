"""
Integration Tests for Address API Endpoints

Tests the address management API endpoints including pincode lookup,
address auto-fill, and validation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestAddressAPI:
    """Test suite for Address API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def sample_pincode_data(self):
        """Sample pincode lookup data"""
        return {
            "pincode": "110001",
            "state": "Delhi",
            "district": "Central Delhi",
            "villages": ["Connaught Place", "Parliament Street"],
        }

    def test_auto_fill_address_success(self, client, sample_pincode_data):
        """Test successful address auto-fill"""
        with patch(
            "app.services.address_service.AddressService.auto_fill_from_pincode"
        ) as mock_auto_fill:
            mock_auto_fill.return_value = sample_pincode_data

            response = client.post("/address/auto-fill", json={"pincode": "110001"})

            assert response.status_code == 200
            data = response.json()
            assert data["pincode"] == "110001"
            assert data["state"] == "Delhi"
            assert data["district"] == "Central Delhi"
            assert len(data["villages"]) == 2

    def test_auto_fill_address_not_found(self, client):
        """Test address auto-fill with invalid pincode"""
        with patch(
            "app.services.address_service.AddressService.auto_fill_from_pincode"
        ) as mock_auto_fill:
            mock_auto_fill.return_value = None

            response = client.post("/address/auto-fill", json={"pincode": "999999"})

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_auto_fill_address_invalid_format(self, client):
        """Test address auto-fill with invalid pincode format"""
        response = client.post("/address/auto-fill", json={"pincode": "12345"})  # Only 5 digits

        # Should fail validation
        assert response.status_code in [400, 422]

    def test_lookup_pincode_get_success(self, client, sample_pincode_data):
        """Test GET pincode lookup endpoint"""
        with patch(
            "app.services.address_service.AddressService.auto_fill_from_pincode"
        ) as mock_auto_fill:
            mock_auto_fill.return_value = sample_pincode_data

            response = client.get("/address/pincode/110001")

            assert response.status_code == 200
            data = response.json()
            assert data["pincode"] == "110001"
            assert data["state"] == "Delhi"

    def test_lookup_pincode_get_invalid_format(self, client):
        """Test GET pincode lookup with invalid format"""
        response = client.get("/address/pincode/12345")

        assert response.status_code == 400
        assert "6 digits" in response.json()["detail"]

    def test_lookup_pincode_get_non_numeric(self, client):
        """Test GET pincode lookup with non-numeric pincode"""
        response = client.get("/address/pincode/ABCDEF")

        assert response.status_code == 400
        assert "6 digits" in response.json()["detail"]

    def test_lookup_pincode_get_not_found(self, client):
        """Test GET pincode lookup with non-existent pincode"""
        with patch(
            "app.services.address_service.AddressService.auto_fill_from_pincode"
        ) as mock_auto_fill:
            mock_auto_fill.return_value = None

            response = client.get("/address/pincode/999999")

            assert response.status_code == 404

    def test_validate_address_success(self, client):
        """Test successful address validation"""
        with patch("app.services.address_service.AddressService.validate_address") as mock_validate:
            mock_validate.return_value = (True, None)

            with patch(
                "app.services.address_service.AddressService.has_gps_coordinates"
            ) as mock_has_gps:
                mock_has_gps.return_value = True

                with patch(
                    "app.services.address_service.AddressService.format_full_address"
                ) as mock_format:
                    mock_format.return_value = "Connaught Place, Central Delhi, Delhi - 110001"

                    response = client.post(
                        "/address/validate",
                        json={
                            "pincode": "110001",
                            "state": "Delhi",
                            "district": "Central Delhi",
                            "village": "Connaught Place",
                            "latitude": 28.6139,
                            "longitude": 77.2090,
                        },
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["valid"] is True
                    assert data["has_gps"] is True
                    assert "formatted_address" in data

    def test_validate_address_invalid(self, client):
        """Test address validation with invalid address"""
        with patch("app.services.address_service.AddressService.validate_address") as mock_validate:
            mock_validate.return_value = (False, "State does not match pincode")

            response = client.post(
                "/address/validate",
                json={
                    "pincode": "110001",
                    "state": "Maharashtra",
                    "district": "Central Delhi",
                    "village": "Connaught Place",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
            assert "error" in data
            assert "State" in data["error"]

    def test_validate_address_missing_required_fields(self, client):
        """Test address validation with missing required fields"""
        response = client.post(
            "/address/validate",
            json={
                "pincode": "110001",
                "state": "Delhi",
                # Missing district and village
            },
        )

        # Should fail validation
        assert response.status_code == 422

    def test_calculate_distance_success(self, client):
        """Test distance calculation between two points"""
        with patch("app.services.address_service.AddressService.calculate_distance") as mock_calc:
            mock_calc.return_value = 10.5

            response = client.post(
                "/address/distance",
                params={"lat1": 28.6139, "lon1": 77.2090, "lat2": 28.7041, "lon2": 77.1025},
            )

            assert response.status_code == 200
            data = response.json()
            assert "distance_km" in data
            assert "distance_miles" in data
            assert data["distance_km"] == 10.5

    def test_calculate_distance_invalid_coordinates(self, client):
        """Test distance calculation with invalid coordinates"""
        response = client.post(
            "/address/distance",
            params={
                "lat1": 200,  # Invalid latitude
                "lon1": 77.2090,
                "lat2": 28.7041,
                "lon2": 77.1025,
            },
        )

        # Should fail validation or return error
        assert response.status_code in [400, 422]


class TestAddressAPIIntegration:
    """Integration tests with real external API (optional, can be skipped in CI)"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires external API access")
    def test_real_pincode_lookup_delhi(self, client):
        """Test real pincode lookup for Delhi"""
        response = client.get("/address/pincode/110001")

        if response.status_code == 200:
            data = response.json()
            assert data["state"] == "Delhi"
            assert data["district"] is not None
            assert len(data["villages"]) > 0

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires external API access")
    def test_real_pincode_lookup_mumbai(self, client):
        """Test real pincode lookup for Mumbai"""
        response = client.get("/address/pincode/400001")

        if response.status_code == 200:
            data = response.json()
            assert data["state"] == "Maharashtra"
            assert "Mumbai" in data["district"]

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires external API access")
    def test_real_pincode_lookup_bangalore(self, client):
        """Test real pincode lookup for Bangalore"""
        response = client.get("/address/pincode/560001")

        if response.status_code == 200:
            data = response.json()
            assert data["state"] == "Karnataka"
            assert "Bangalore" in data["district"] or "Bengaluru" in data["district"]
