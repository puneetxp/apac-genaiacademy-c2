"""
Unit tests for farm registration with address support

Tests farm creation, update, and validation with address fields including
pincode lookup integration and GPS coordinates.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.address import AddressBase
from app.schemas.farm import FarmCreate, FarmUpdate
from app.services.address_service import AddressService


class TestFarmAddressValidation:
    """Test farm address validation"""

    @pytest.mark.asyncio
    async def test_valid_farm_address(self):
        """Test farm creation with valid address"""
        address_service = AddressService()

        # Mock pincode lookup
        with patch.object(address_service.pincode_service, "validate_address", return_value=True):
            address = AddressBase(
                latitude=30.7333,
                longitude=76.7794,
                pincode="160001",
                state="Punjab",
                district="Chandigarh",
                village="Sector 17",
                address_line1="Farm House 123",
                address_line2="Near Market",
            )

            is_valid, error = await address_service.validate_address(address)

            assert is_valid is True
            assert error is None

    @pytest.mark.asyncio
    async def test_invalid_pincode_format(self):
        """Test farm address with invalid pincode format"""
        address_service = AddressService()

        address = AddressBase(
            pincode="12345",  # Only 5 digits
            state="Punjab",
            district="Chandigarh",
            village="Sector 17",
        )

        is_valid, error = await address_service.validate_address(address)

        assert is_valid is False
        assert "6 digits" in error

    @pytest.mark.asyncio
    async def test_gps_coordinates_validation(self):
        """Test GPS coordinates must be provided together"""
        address_service = AddressService()

        # Only latitude provided
        address = AddressBase(
            latitude=30.7333,
            longitude=None,
            pincode="160001",
            state="Punjab",
            district="Chandigarh",
            village="Sector 17",
        )

        is_valid, error = await address_service.validate_address(address)

        assert is_valid is False
        assert "together" in error.lower()

    @pytest.mark.asyncio
    async def test_address_mismatch_with_pincode(self):
        """Test address validation fails when data doesn't match pincode"""
        address_service = AddressService()

        # Mock pincode lookup to return False
        with patch.object(address_service.pincode_service, "validate_address", return_value=False):
            address = AddressBase(
                pincode="160001",
                state="Wrong State",
                district="Wrong District",
                village="Wrong Village",
            )

            is_valid, error = await address_service.validate_address(address)

            assert is_valid is False
            assert "does not match" in error


class TestFarmCreateWithAddress:
    """Test farm creation with address fields"""

    def test_farm_create_schema_with_address(self):
        """Test FarmCreate schema accepts address fields"""
        farm_data = FarmCreate(
            name="Green Valley Farm",
            state="Punjab",
            district="Ludhiana",
            village="Khanna",
            pincode="141401",
            address_line1="Khasra No. 123",
            address_line2="Near Canal",
            total_area_acres=10.5,
            latitude=30.7046,
            longitude=76.2263,
        )

        assert farm_data.name == "Green Valley Farm"
        assert farm_data.pincode == "141401"
        assert farm_data.village == "Khanna"
        assert farm_data.latitude == 30.7046
        assert farm_data.longitude == 76.2263

    def test_farm_create_without_gps(self):
        """Test farm creation without GPS coordinates"""
        farm_data = FarmCreate(
            name="Organic Farm",
            state="Punjab",
            district="Patiala",
            village="Rajpura",
            pincode="140401",
            total_area_acres=5.0,
        )

        assert farm_data.latitude is None
        assert farm_data.longitude is None
        assert farm_data.pincode == "140401"

    def test_farm_create_pincode_validation(self):
        """Test pincode validation in FarmCreate"""
        with pytest.raises(ValueError, match="6 digits"):
            FarmCreate(
                name="Test Farm",
                state="Punjab",
                district="Amritsar",
                village="Test Village",
                pincode="12345",  # Invalid: only 5 digits
                total_area_acres=10.0,
            )

    def test_farm_create_with_optional_address_lines(self):
        """Test farm creation with optional address lines"""
        farm_data = FarmCreate(
            name="Sunrise Farm",
            state="Haryana",
            district="Karnal",
            village="Assandh",
            pincode="132039",
            address_line1="Plot No. 456",
            total_area_acres=15.0,
        )

        assert farm_data.address_line1 == "Plot No. 456"
        assert farm_data.address_line2 is None


class TestFarmUpdateWithAddress:
    """Test farm update with address fields"""

    def test_farm_update_address_fields(self):
        """Test updating farm address fields"""
        update_data = FarmUpdate(
            pincode="160002", village="Sector 22", address_line1="New Address Line 1"
        )

        assert update_data.pincode == "160002"
        assert update_data.village == "Sector 22"
        assert update_data.address_line1 == "New Address Line 1"

    def test_farm_update_gps_coordinates(self):
        """Test updating GPS coordinates"""
        update_data = FarmUpdate(latitude=30.7500, longitude=76.8000)

        assert update_data.latitude == 30.7500
        assert update_data.longitude == 76.8000

    def test_farm_update_partial_address(self):
        """Test partial address update"""
        update_data = FarmUpdate(address_line2="Updated landmark")

        assert update_data.address_line2 == "Updated landmark"
        assert update_data.pincode is None
        assert update_data.state is None


class TestFarmAddressService:
    """Test address service integration with farms"""

    @pytest.mark.asyncio
    async def test_has_gps_coordinates(self):
        """Test checking if farm has GPS coordinates"""
        address_service = AddressService()

        # With GPS
        address_with_gps = AddressBase(
            latitude=30.7333,
            longitude=76.7794,
            pincode="160001",
            state="Punjab",
            district="Chandigarh",
            village="Sector 17",
        )

        assert address_service.has_gps_coordinates(address_with_gps) is True

        # Without GPS
        address_without_gps = AddressBase(
            pincode="160001", state="Punjab", district="Chandigarh", village="Sector 17"
        )

        assert address_service.has_gps_coordinates(address_without_gps) is False

    def test_format_full_farm_address(self):
        """Test formatting complete farm address"""
        address_service = AddressService()

        address = AddressBase(
            pincode="141401",
            state="Punjab",
            district="Ludhiana",
            village="Khanna",
            address_line1="Khasra No. 123",
            address_line2="Near Canal",
        )

        formatted = address_service.format_full_address(address)

        assert "Khasra No. 123" in formatted
        assert "Near Canal" in formatted
        assert "Khanna" in formatted
        assert "Ludhiana" in formatted
        assert "Punjab" in formatted
        assert "141401" in formatted

    @pytest.mark.asyncio
    async def test_calculate_distance_between_farms(self):
        """Test calculating distance between two farm locations"""
        address_service = AddressService()

        # Chandigarh to Ludhiana (approximately 100 km)
        lat1, lon1 = 30.7333, 76.7794  # Chandigarh
        lat2, lon2 = 30.9010, 75.8573  # Ludhiana

        distance = address_service.calculate_distance(lat1, lon1, lat2, lon2)

        # Distance should be approximately 100 km
        assert 90 < distance < 110

    @pytest.mark.asyncio
    async def test_find_nearby_farms(self):
        """Test finding farms within specified distance"""
        address_service = AddressService()

        center_lat, center_lon = 30.7333, 76.7794  # Chandigarh

        farms = [
            {"id": 1, "name": "Farm 1", "latitude": 30.7500, "longitude": 76.8000},  # ~5 km
            {"id": 2, "name": "Farm 2", "latitude": 30.9010, "longitude": 75.8573},  # ~100 km
            {"id": 3, "name": "Farm 3", "latitude": 30.7400, "longitude": 76.7900},  # ~1 km
        ]

        nearby = await address_service.find_nearby_locations(
            center_lat, center_lon, max_distance_km=10, locations=farms
        )

        # Should find 2 farms within 10 km
        assert len(nearby) == 2
        assert nearby[0]["id"] == 3  # Closest first
        assert nearby[1]["id"] == 1


class TestFarmAddressIntegration:
    """Integration tests for farm address functionality"""

    @pytest.mark.asyncio
    async def test_farm_registration_flow_with_address(self):
        """Test complete farm registration flow with address"""
        # This would be an integration test with actual API calls
        # For now, we test the schema validation flow

        # Step 1: User enters pincode
        pincode = "141401"

        # Step 2: System looks up address (mocked)
        address_service = AddressService()
        with patch.object(
            address_service.pincode_service,
            "lookup_pincode",
            return_value={
                "pincode": "141401",
                "state": "Punjab",
                "district": "Ludhiana",
                "villages": ["Khanna", "Samrala"],
            },
        ):
            lookup_result = await address_service.auto_fill_from_pincode(pincode)

            assert lookup_result is not None
            assert lookup_result.state == "Punjab"
            assert "Khanna" in lookup_result.villages

        # Step 3: User creates farm with auto-filled data
        farm_data = FarmCreate(
            name="Test Farm",
            state=lookup_result.state,
            district=lookup_result.district,
            village=lookup_result.villages[0],
            pincode=pincode,
            total_area_acres=10.0,
        )

        assert farm_data.pincode == "141401"
        assert farm_data.state == "Punjab"

    @pytest.mark.asyncio
    async def test_farm_update_address_validation(self):
        """Test farm address update with validation"""
        address_service = AddressService()

        # Mock validation
        with patch.object(address_service.pincode_service, "validate_address", return_value=True):
            # Update farm address
            update_data = FarmUpdate(pincode="160002", village="Sector 22")

            # Validate new address
            address = AddressBase(
                pincode=update_data.pincode,
                state="Punjab",
                district="Chandigarh",
                village=update_data.village,
            )

            is_valid, error = await address_service.validate_address(address)

            assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
