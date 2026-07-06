"""
Tests for Address Management Service

Tests address validation, auto-fill, GPS operations, and utility functions.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.address_service import AddressService
from app.schemas.address import AddressBase, AddressAutoFillResponse


class TestAddressService:
    """Test suite for AddressService"""
    
    @pytest.fixture
    def service(self):
        """Create service instance without Redis"""
        return AddressService(redis_client=None)
    
    @pytest.fixture
    def valid_address(self):
        """Create valid address object"""
        return AddressBase(
            pincode="110001",
            state="Delhi",
            district="Central Delhi",
            village="Connaught Place",
            address_line="123 Main Street, Near Parliament",
            latitude=28.6139,
            longitude=77.2090
        )
    
    @pytest.fixture
    def address_without_gps(self):
        """Create address without GPS coordinates"""
        return AddressBase(
            pincode="110001",
            state="Delhi",
            district="Central Delhi",
            village="Connaught Place",
            address_line="123 Main Street"
        )
    
    @pytest.fixture
    def sample_pincode_data(self):
        """Sample pincode lookup data"""
        return {
            'pincode': '110001',
            'state': 'Delhi',
            'district': 'Central Delhi',
            'villages': ['Connaught Place', 'Parliament Street']
        }
    
    @pytest.mark.asyncio
    async def test_auto_fill_from_pincode_success(self, service, sample_pincode_data):
        """Test successful auto-fill from pincode"""
        with patch.object(service.pincode_service, 'lookup_pincode', new=AsyncMock(return_value=sample_pincode_data)):
            result = await service.auto_fill_from_pincode("110001")
            
            assert result is not None
            assert isinstance(result, AddressAutoFillResponse)
            assert result.pincode == "110001"
            assert result.state == "Delhi"
            assert result.district == "Central Delhi"
            assert len(result.villages) == 2
    
    @pytest.mark.asyncio
    async def test_auto_fill_from_pincode_not_found(self, service):
        """Test auto-fill with invalid pincode"""
        with patch.object(service.pincode_service, 'lookup_pincode', new=AsyncMock(return_value=None)):
            result = await service.auto_fill_from_pincode("999999")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_validate_address_success(self, service, valid_address):
        """Test successful address validation"""
        with patch.object(service.pincode_service, 'validate_address', new=AsyncMock(return_value=True)):
            is_valid, error = await service.validate_address(valid_address)
            
            assert is_valid is True
            assert error is None
    
    @pytest.mark.asyncio
    async def test_validate_address_pincode_mismatch(self, service, valid_address):
        """Test address validation with pincode mismatch"""
        with patch.object(service.pincode_service, 'validate_address', new=AsyncMock(return_value=False)):
            is_valid, error = await service.validate_address(valid_address)
            
            assert is_valid is False
            assert error is not None
            assert "does not match pincode" in error.lower()
    
    @pytest.mark.asyncio
    async def test_validate_address_invalid_pincode_format(self, service):
        """Test address validation with invalid pincode format"""
        address = AddressBase(
            pincode="12345",  # Only 5 digits
            state="Delhi",
            district="Central Delhi",
            village="Connaught Place"
        )
        
        is_valid, error = await service.validate_address(address)
        
        assert is_valid is False
        assert "6 digits" in error
    
    @pytest.mark.asyncio
    async def test_validate_address_missing_pincode(self, service):
        """Test address validation with missing pincode"""
        address = AddressBase(
            pincode="",
            state="Delhi",
            district="Central Delhi",
            village="Connaught Place"
        )
        
        is_valid, error = await service.validate_address(address)
        
        assert is_valid is False
        assert "6 digits" in error
    
    @pytest.mark.asyncio
    async def test_validate_address_gps_inconsistency_lat_only(self, service):
        """Test address validation with only latitude provided"""
        address = AddressBase(
            pincode="110001",
            state="Delhi",
            district="Central Delhi",
            village="Connaught Place",
            latitude=28.6139,
            longitude=None  # Missing longitude
        )
        
        is_valid, error = await service.validate_address(address)
        
        assert is_valid is False
        assert "latitude and longitude" in error.lower()
    
    @pytest.mark.asyncio
    async def test_validate_address_gps_inconsistency_lon_only(self, service):
        """Test address validation with only longitude provided"""
        address = AddressBase(
            pincode="110001",
            state="Delhi",
            district="Central Delhi",
            village="Connaught Place",
            latitude=None,  # Missing latitude
            longitude=77.2090
        )
        
        is_valid, error = await service.validate_address(address)
        
        assert is_valid is False
        assert "latitude and longitude" in error.lower()
    
    def test_has_gps_coordinates_true(self, service, valid_address):
        """Test GPS coordinate check with both coordinates"""
        assert service.has_gps_coordinates(valid_address) is True
    
    def test_has_gps_coordinates_false(self, service, address_without_gps):
        """Test GPS coordinate check without coordinates"""
        assert service.has_gps_coordinates(address_without_gps) is False
    
    def test_has_gps_coordinates_partial(self, service):
        """Test GPS coordinate check with partial coordinates"""
        address = AddressBase(
            pincode="110001",
            state="Delhi",
            district="Central Delhi",
            village="Connaught Place",
            latitude=28.6139,
            longitude=None
        )
        
        assert service.has_gps_coordinates(address) is False
    
    def test_format_full_address_complete(self, service, valid_address):
        """Test formatting complete address"""
        formatted = service.format_full_address(valid_address)
        
        assert "123 Main Street" in formatted
        assert "Connaught Place" in formatted
        assert "Central Delhi" in formatted
        assert "Delhi" in formatted
        assert "110001" in formatted
    
    def test_format_full_address_minimal(self, service, address_without_gps):
        """Test formatting minimal address"""
        formatted = service.format_full_address(address_without_gps)
        
        assert "123 Main Street" in formatted
        assert "Connaught Place" in formatted
        assert "Central Delhi" in formatted
        assert "Delhi" in formatted
        assert "110001" in formatted
    
    def test_format_full_address_no_address_lines(self, service):
        """Test formatting address without address lines"""
        address = AddressBase(
            pincode="110001",
            state="Delhi",
            district="Central Delhi",
            village="Connaught Place"
        )
        
        formatted = service.format_full_address(address)
        
        assert "Connaught Place" in formatted
        assert "Central Delhi" in formatted
        assert "Delhi" in formatted
        assert "110001" in formatted
    
    def test_calculate_distance_same_point(self, service):
        """Test distance calculation for same point"""
        distance = service.calculate_distance(28.6139, 77.2090, 28.6139, 77.2090)
        
        assert distance == 0.0
    
    def test_calculate_distance_delhi_to_mumbai(self, service):
        """Test distance calculation between Delhi and Mumbai"""
        # Delhi: 28.6139, 77.2090
        # Mumbai: 19.0760, 72.8777
        distance = service.calculate_distance(28.6139, 77.2090, 19.0760, 72.8777)
        
        # Approximate distance is ~1150 km
        assert 1100 < distance < 1200
    
    def test_calculate_distance_delhi_to_bangalore(self, service):
        """Test distance calculation between Delhi and Bangalore"""
        # Delhi: 28.6139, 77.2090
        # Bangalore: 12.9716, 77.5946
        distance = service.calculate_distance(28.6139, 77.2090, 12.9716, 77.5946)
        
        # Approximate distance is ~1740 km
        assert 1700 < distance < 1800
    
    def test_calculate_distance_short_distance(self, service):
        """Test distance calculation for short distance"""
        # Two points in Delhi ~10 km apart
        distance = service.calculate_distance(28.6139, 77.2090, 28.7041, 77.1025)
        
        # Approximate distance is ~10-15 km
        assert 8 < distance < 20
    
    @pytest.mark.asyncio
    async def test_find_nearby_locations_within_range(self, service):
        """Test finding locations within specified range"""
        center_lat, center_lon = 28.6139, 77.2090
        
        locations = [
            {'id': 1, 'name': 'Location 1', 'latitude': 28.6200, 'longitude': 77.2100},  # ~1 km
            {'id': 2, 'name': 'Location 2', 'latitude': 28.7041, 'longitude': 77.1025},  # ~12 km
            {'id': 3, 'name': 'Location 3', 'latitude': 28.5000, 'longitude': 77.3000},  # ~20 km
        ]
        
        nearby = await service.find_nearby_locations(center_lat, center_lon, 15.0, locations)
        
        assert len(nearby) == 2  # Only first two within 15 km
        assert nearby[0]['id'] == 1  # Closest first
        assert nearby[1]['id'] == 2
        assert 'distance_km' in nearby[0]
    
    @pytest.mark.asyncio
    async def test_find_nearby_locations_none_in_range(self, service):
        """Test finding locations with none in range"""
        center_lat, center_lon = 28.6139, 77.2090
        
        locations = [
            {'id': 1, 'name': 'Location 1', 'latitude': 19.0760, 'longitude': 72.8777},  # Mumbai
            {'id': 2, 'name': 'Location 2', 'latitude': 12.9716, 'longitude': 77.5946},  # Bangalore
        ]
        
        nearby = await service.find_nearby_locations(center_lat, center_lon, 100.0, locations)
        
        assert len(nearby) == 0
    
    @pytest.mark.asyncio
    async def test_find_nearby_locations_missing_coordinates(self, service):
        """Test finding locations with missing GPS coordinates"""
        center_lat, center_lon = 28.6139, 77.2090
        
        locations = [
            {'id': 1, 'name': 'Location 1', 'latitude': 28.6200, 'longitude': 77.2100},
            {'id': 2, 'name': 'Location 2', 'latitude': None, 'longitude': None},  # No GPS
            {'id': 3, 'name': 'Location 3'},  # Missing GPS fields
        ]
        
        nearby = await service.find_nearby_locations(center_lat, center_lon, 10.0, locations)
        
        assert len(nearby) == 1  # Only first location
        assert nearby[0]['id'] == 1
    
    @pytest.mark.asyncio
    async def test_find_nearby_locations_sorted_by_distance(self, service):
        """Test that nearby locations are sorted by distance"""
        center_lat, center_lon = 28.6139, 77.2090
        
        locations = [
            {'id': 1, 'name': 'Far', 'latitude': 28.7041, 'longitude': 77.1025},  # ~12 km
            {'id': 2, 'name': 'Close', 'latitude': 28.6200, 'longitude': 77.2100},  # ~1 km
            {'id': 3, 'name': 'Medium', 'latitude': 28.6500, 'longitude': 77.2500},  # ~5 km
        ]
        
        nearby = await service.find_nearby_locations(center_lat, center_lon, 20.0, locations)
        
        assert len(nearby) == 3
        assert nearby[0]['id'] == 2  # Closest
        assert nearby[1]['id'] == 3  # Medium
        assert nearby[2]['id'] == 1  # Farthest
        assert nearby[0]['distance_km'] < nearby[1]['distance_km'] < nearby[2]['distance_km']
    
    def test_extract_address_fields_no_prefix(self, service):
        """Test extracting address fields without prefix"""
        data = {
            'pincode': '110001',
            'state': 'Delhi',
            'district': 'Central Delhi',
            'village': 'Connaught Place',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'other_field': 'ignored'
        }
        
        address = service.extract_address_fields(data)
        
        assert address['pincode'] == '110001'
        assert address['state'] == 'Delhi'
        assert address['district'] == 'Central Delhi'
        assert address['village'] == 'Connaught Place'
        assert address['latitude'] == 28.6139
        assert address['longitude'] == 77.2090
        assert 'other_field' not in address
    
    def test_extract_address_fields_with_prefix(self, service):
        """Test extracting address fields with prefix"""
        data = {
            'delivery_pincode': '110001',
            'delivery_state': 'Delhi',
            'delivery_district': 'Central Delhi',
            'delivery_village': 'Connaught Place',
            'delivery_latitude': 28.6139,
            'delivery_longitude': 77.2090,
            'other_field': 'ignored'
        }
        
        address = service.extract_address_fields(data, prefix="delivery_")
        
        assert address['pincode'] == '110001'
        assert address['state'] == 'Delhi'
        assert address['district'] == 'Central Delhi'
        assert address['village'] == 'Connaught Place'
        assert address['latitude'] == 28.6139
        assert address['longitude'] == 77.2090
    
    def test_extract_address_fields_partial_data(self, service):
        """Test extracting address fields with partial data"""
        data = {
            'pincode': '110001',
            'state': 'Delhi',
            'district': 'Central Delhi'
            # Missing village and GPS
        }
        
        address = service.extract_address_fields(data)
        
        assert address['pincode'] == '110001'
        assert address['state'] == 'Delhi'
        assert address['district'] == 'Central Delhi'
        assert 'village' not in address
        assert 'latitude' not in address
    
    def test_extract_address_fields_empty_data(self, service):
        """Test extracting address fields from empty data"""
        data = {}
        
        address = service.extract_address_fields(data)
        
        assert address == {}
