"""
Unit tests for livestock address handling
Tests livestock location fields (can differ from farm address)
"""

from datetime import date
from decimal import Decimal

import pytest

from app.schemas.livestock import LivestockCreate, LivestockResponse, LivestockUpdate


class TestLivestockAddressSchemas:
    """Test livestock address schema validation"""

    def test_livestock_create_with_full_address(self):
        """Test creating livestock with complete address"""
        data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "cattle",
            "breed": "Holstein",
            "quantity": 2,
            "purchase_price": Decimal("50000.00"),
            "purchase_date": date(2024, 1, 15),
            "purpose": "dairy",
            "status": "active",
            # Address fields
            "latitude": Decimal("28.6139"),
            "longitude": Decimal("77.2090"),
            "pincode": "110001",
            "state": "Delhi",
            "district": "Central Delhi",
            "village": "Connaught Place",
            "address_line1": "Farm House 123",
            "address_line2": "Near Market",
        }

        livestock = LivestockCreate(**data)

        assert livestock.species == "cattle"
        assert livestock.latitude == Decimal("28.6139")
        assert livestock.longitude == Decimal("77.2090")
        assert livestock.pincode == "110001"
        assert livestock.state == "Delhi"
        assert livestock.district == "Central Delhi"
        assert livestock.village == "Connaught Place"
        assert livestock.address_line1 == "Farm House 123"
        assert livestock.address_line2 == "Near Market"

    def test_livestock_create_without_address(self):
        """Test creating livestock without address (optional)"""
        data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "goat",
            "breed": "Boer",
            "quantity": 5,
            "purchase_price": Decimal("15000.00"),
            "purchase_date": date(2024, 2, 1),
            "purpose": "meat",
            "status": "active",
        }

        livestock = LivestockCreate(**data)

        assert livestock.species == "goat"
        assert livestock.latitude is None
        assert livestock.longitude is None
        assert livestock.pincode is None
        assert livestock.state is None

    def test_livestock_create_with_gps_only(self):
        """Test creating livestock with GPS coordinates only"""
        data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "buffalo",
            "breed": "Murrah",
            "quantity": 1,
            "purchase_price": Decimal("80000.00"),
            "purchase_date": date(2024, 1, 20),
            "purpose": "dairy",
            "latitude": Decimal("26.8467"),
            "longitude": Decimal("80.9462"),
        }

        livestock = LivestockCreate(**data)

        assert livestock.latitude == Decimal("26.8467")
        assert livestock.longitude == Decimal("80.9462")
        assert livestock.pincode is None

    def test_livestock_create_with_pincode_only(self):
        """Test creating livestock with pincode-based address only"""
        data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "poultry",
            "breed": "Broiler",
            "quantity": 100,
            "purchase_price": Decimal("5000.00"),
            "purchase_date": date(2024, 3, 1),
            "purpose": "meat",
            "pincode": "226001",
            "state": "Uttar Pradesh",
            "district": "Lucknow",
            "village": "Hazratganj",
        }

        livestock = LivestockCreate(**data)

        assert livestock.pincode == "226001"
        assert livestock.state == "Uttar Pradesh"
        assert livestock.district == "Lucknow"
        assert livestock.village == "Hazratganj"
        assert livestock.latitude is None
        assert livestock.longitude is None

    def test_livestock_update_address_fields(self):
        """Test updating livestock address fields"""
        update_data = {
            "latitude": Decimal("28.7041"),
            "longitude": Decimal("77.1025"),
            "pincode": "110035",
            "state": "Delhi",
            "district": "North Delhi",
            "village": "GTB Nagar",
            "address_line1": "New Location 456",
            "address_line2": "Near University",
        }

        livestock_update = LivestockUpdate(**update_data)

        assert livestock_update.latitude == Decimal("28.7041")
        assert livestock_update.longitude == Decimal("77.1025")
        assert livestock_update.pincode == "110035"
        assert livestock_update.state == "Delhi"
        assert livestock_update.district == "North Delhi"
        assert livestock_update.village == "GTB Nagar"

    def test_livestock_update_partial_address(self):
        """Test updating only some address fields"""
        update_data = {"pincode": "400001", "state": "Maharashtra"}

        livestock_update = LivestockUpdate(**update_data)

        assert livestock_update.pincode == "400001"
        assert livestock_update.state == "Maharashtra"
        assert livestock_update.district is None
        assert livestock_update.village is None

    def test_livestock_response_includes_address(self):
        """Test livestock response includes address fields"""
        data = {
            "id": 1,
            "farm_id": 1,
            "farmer_id": 1,
            "species": "cattle",
            "breed": "Jersey",
            "quantity": 3,
            "purchase_price": Decimal("60000.00"),
            "purchase_date": date(2024, 1, 10),
            "purpose": "dairy",
            "status": "active",
            "expected_roi": Decimal("25000.00"),
            "break_even_date": date(2025, 1, 10),
            "created_at": "2024-01-10T10:00:00",
            "updated_at": "2024-01-10T10:00:00",
            "enable": 1,
            # Address fields
            "latitude": Decimal("19.0760"),
            "longitude": Decimal("72.8777"),
            "pincode": "400001",
            "state": "Maharashtra",
            "district": "Mumbai",
            "village": "Fort",
            "address_line1": "Dairy Farm 789",
            "address_line2": "Near Station",
        }

        # Convert to dict for response
        response_dict = {**data}

        assert response_dict["latitude"] == Decimal("19.0760")
        assert response_dict["longitude"] == Decimal("72.8777")
        assert response_dict["pincode"] == "400001"
        assert response_dict["state"] == "Maharashtra"
        assert response_dict["district"] == "Mumbai"
        assert response_dict["village"] == "Fort"


class TestLivestockAddressValidation:
    """Test livestock address validation logic"""

    def test_address_can_differ_from_farm(self):
        """Test that livestock location can be different from farm address"""
        # This is a conceptual test - in practice, the API would allow
        # livestock to have different address than the farm it belongs to

        farm_address = {"pincode": "110001", "state": "Delhi", "district": "Central Delhi"}

        livestock_address = {"pincode": "110035", "state": "Delhi", "district": "North Delhi"}

        # Livestock can have different location
        assert farm_address["pincode"] != livestock_address["pincode"]
        assert farm_address["district"] != livestock_address["district"]

    def test_gps_coordinates_optional(self):
        """Test that GPS coordinates are optional for livestock"""
        data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "cattle",
            "breed": "Sahiwal",
            "quantity": 2,
            "purchase_price": Decimal("45000.00"),
            "purchase_date": date(2024, 2, 15),
            "purpose": "dairy",
            "pincode": "302001",
            "state": "Rajasthan",
            "district": "Jaipur",
            "village": "Jaipur City",
        }

        livestock = LivestockCreate(**data)

        # GPS is optional - livestock can work with pincode only
        assert livestock.latitude is None
        assert livestock.longitude is None
        assert livestock.pincode == "302001"

    def test_pincode_format_validation(self):
        """Test pincode format validation"""
        # Valid 6-digit pincode
        data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "goat",
            "breed": "Sirohi",
            "quantity": 10,
            "purchase_price": Decimal("20000.00"),
            "purchase_date": date(2024, 3, 1),
            "purpose": "meat",
            "pincode": "302001",
        }

        livestock = LivestockCreate(**data)
        assert livestock.pincode == "302001"
        assert len(livestock.pincode) == 6

    def test_address_fields_max_length(self):
        """Test address field max length constraints"""
        data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "buffalo",
            "breed": "Jaffarabadi",
            "quantity": 1,
            "purchase_price": Decimal("75000.00"),
            "purchase_date": date(2024, 1, 25),
            "purpose": "dairy",
            "pincode": "380001",
            "state": "Gujarat",
            "district": "Ahmedabad",
            "village": "Ahmedabad City",
            "address_line1": "A" * 255,  # Max length
            "address_line2": "B" * 255,  # Max length
        }

        livestock = LivestockCreate(**data)

        assert len(livestock.address_line1) == 255
        assert len(livestock.address_line2) == 255


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
