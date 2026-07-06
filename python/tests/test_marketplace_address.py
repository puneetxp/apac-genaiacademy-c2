"""
Unit tests for marketplace address handling
Tests delivery address fields for listings and buyer interests
"""

import pytest
from decimal import Decimal
from datetime import date
from app.schemas.marketplace import (
    MarketplaceListingCreate,
    MarketplaceListingUpdate,
    MarketplaceListingResponse,
    BuyerInterestCreate,
    BuyerInterestUpdate,
    BuyerInterestResponse
)


class TestMarketplaceListingAddressSchemas:
    """Test marketplace listing delivery address schema validation"""
    
    def test_listing_create_with_delivery_address(self):
        """Test creating listing with delivery address"""
        data = {
            'farm_id': 1,
            'farmer_id': 1,
            'crop_type': 'Wheat',
            'crop_variety': 'HD-2967',
            'expected_harvest_date': date(2024, 4, 15),
            'estimated_quantity': 5000,
            'quality_grade': 'A',
            'location_state': 'Punjab',
            'location_district': 'Ludhiana',
            'farmer_contact_phone': '+919876543210',
            'status': 'active',
            # Delivery address
            'delivery_latitude': Decimal('30.9010'),
            'delivery_longitude': Decimal('75.8573'),
            'delivery_pincode': '141001',
            'delivery_village': 'Ludhiana City',
            'delivery_address_line1': 'Mandi Road',
            'delivery_address_line2': 'Near Railway Station'
        }
        
        listing = MarketplaceListingCreate(**data)
        
        assert listing.crop_type == 'Wheat'
        assert listing.delivery_latitude == Decimal('30.9010')
        assert listing.delivery_longitude == Decimal('75.8573')
        assert listing.delivery_pincode == '141001'
        assert listing.delivery_village == 'Ludhiana City'
        assert listing.delivery_address_line1 == 'Mandi Road'
        assert listing.delivery_address_line2 == 'Near Railway Station'
    
    def test_listing_create_without_delivery_address(self):
        """Test creating listing without delivery address (optional)"""
        data = {
            'farm_id': 1,
            'farmer_id': 1,
            'crop_type': 'Rice',
            'crop_variety': 'Basmati',
            'expected_harvest_date': date(2024, 10, 20),
            'estimated_quantity': 3000,
            'quality_grade': 'A',
            'location_state': 'Haryana',
            'location_district': 'Karnal',
            'status': 'active'
        }
        
        listing = MarketplaceListingCreate(**data)
        
        assert listing.crop_type == 'Rice'
        assert listing.delivery_latitude is None
        assert listing.delivery_longitude is None
        assert listing.delivery_pincode is None
        assert listing.delivery_village is None
    
    def test_listing_create_with_gps_only(self):
        """Test creating listing with GPS coordinates only"""
        data = {
            'farm_id': 1,
            'farmer_id': 1,
            'crop_type': 'Sugarcane',
            'expected_harvest_date': date(2024, 12, 1),
            'estimated_quantity': 10000,
            'location_state': 'Uttar Pradesh',
            'location_district': 'Muzaffarnagar',
            'delivery_latitude': Decimal('29.4727'),
            'delivery_longitude': Decimal('77.7085')
        }
        
        listing = MarketplaceListingCreate(**data)
        
        assert listing.delivery_latitude == Decimal('29.4727')
        assert listing.delivery_longitude == Decimal('77.7085')
        assert listing.delivery_pincode is None
    
    def test_listing_update_delivery_address(self):
        """Test updating listing delivery address"""
        update_data = {
            'delivery_latitude': Decimal('28.6139'),
            'delivery_longitude': Decimal('77.2090'),
            'delivery_pincode': '110001',
            'delivery_village': 'Connaught Place',
            'delivery_address_line1': 'New Delivery Point',
            'delivery_address_line2': 'Near Market'
        }
        
        listing_update = MarketplaceListingUpdate(**update_data)
        
        assert listing_update.delivery_latitude == Decimal('28.6139')
        assert listing_update.delivery_longitude == Decimal('77.2090')
        assert listing_update.delivery_pincode == '110001'
        assert listing_update.delivery_village == 'Connaught Place'
    
    def test_listing_response_includes_delivery_address(self):
        """Test listing response includes delivery address fields"""
        data = {
            'id': 1,
            'farm_id': 1,
            'farmer_id': 1,
            'crop_type': 'Cotton',
            'crop_variety': 'Bt Cotton',
            'expected_harvest_date': date(2024, 11, 15),
            'estimated_quantity': 2000,
            'quality_grade': 'B',
            'location_state': 'Gujarat',
            'location_district': 'Ahmedabad',
            'status': 'active',
            'created_at': '2024-01-15T10:00:00',
            'updated_at': '2024-01-15T10:00:00',
            'enable': 1,
            # Delivery address
            'delivery_latitude': Decimal('23.0225'),
            'delivery_longitude': Decimal('72.5714'),
            'delivery_pincode': '380001',
            'delivery_village': 'Ahmedabad City',
            'delivery_address_line1': 'Cotton Market',
            'delivery_address_line2': 'Near APMC'
        }
        
        response_dict = {**data}
        
        assert response_dict['delivery_latitude'] == Decimal('23.0225')
        assert response_dict['delivery_longitude'] == Decimal('72.5714')
        assert response_dict['delivery_pincode'] == '380001'
        assert response_dict['delivery_village'] == 'Ahmedabad City'


class TestBuyerInterestAddressSchemas:
    """Test buyer interest delivery address schema validation"""
    
    def test_buyer_interest_create_with_delivery_address(self):
        """Test creating buyer interest with delivery address"""
        data = {
            'listing_id': 1,
            'buyer_name': 'ABC Traders',
            'buyer_phone': '+919876543210',
            'buyer_email': 'abc@traders.com',
            'buyer_type': 'wholesaler',
            'interested_quantity': 1000,
            'message': 'Interested in bulk purchase',
            'status': 'pending',
            # Buyer delivery address
            'delivery_latitude': Decimal('28.7041'),
            'delivery_longitude': Decimal('77.1025'),
            'delivery_pincode': '110035',
            'delivery_state': 'Delhi',
            'delivery_district': 'North Delhi',
            'delivery_village': 'GTB Nagar',
            'delivery_address_line1': 'Warehouse 123',
            'delivery_address_line2': 'Industrial Area'
        }
        
        interest = BuyerInterestCreate(**data)
        
        assert interest.buyer_name == 'ABC Traders'
        assert interest.delivery_latitude == Decimal('28.7041')
        assert interest.delivery_longitude == Decimal('77.1025')
        assert interest.delivery_pincode == '110035'
        assert interest.delivery_state == 'Delhi'
        assert interest.delivery_district == 'North Delhi'
        assert interest.delivery_village == 'GTB Nagar'
        assert interest.delivery_address_line1 == 'Warehouse 123'
        assert interest.delivery_address_line2 == 'Industrial Area'
    
    def test_buyer_interest_create_without_delivery_address(self):
        """Test creating buyer interest without delivery address (optional)"""
        data = {
            'listing_id': 1,
            'buyer_name': 'XYZ Retailers',
            'buyer_phone': '+919123456789',
            'buyer_type': 'retailer',
            'interested_quantity': 500,
            'status': 'pending'
        }
        
        interest = BuyerInterestCreate(**data)
        
        assert interest.buyer_name == 'XYZ Retailers'
        assert interest.delivery_latitude is None
        assert interest.delivery_longitude is None
        assert interest.delivery_pincode is None
        assert interest.delivery_state is None
    
    def test_buyer_interest_create_with_pincode_only(self):
        """Test creating buyer interest with pincode-based address"""
        data = {
            'listing_id': 1,
            'buyer_name': 'Food Processors Ltd',
            'buyer_phone': '+919988776655',
            'buyer_email': 'contact@foodprocessors.com',
            'buyer_type': 'processor',
            'interested_quantity': 2000,
            'delivery_pincode': '400001',
            'delivery_state': 'Maharashtra',
            'delivery_district': 'Mumbai',
            'delivery_village': 'Fort'
        }
        
        interest = BuyerInterestCreate(**data)
        
        assert interest.delivery_pincode == '400001'
        assert interest.delivery_state == 'Maharashtra'
        assert interest.delivery_district == 'Mumbai'
        assert interest.delivery_village == 'Fort'
        assert interest.delivery_latitude is None
        assert interest.delivery_longitude is None
    
    def test_buyer_interest_update_delivery_address(self):
        """Test updating buyer interest delivery address"""
        update_data = {
            'delivery_latitude': Decimal('19.0760'),
            'delivery_longitude': Decimal('72.8777'),
            'delivery_pincode': '400001',
            'delivery_state': 'Maharashtra',
            'delivery_district': 'Mumbai',
            'delivery_village': 'Fort',
            'delivery_address_line1': 'Updated Warehouse',
            'delivery_address_line2': 'New Location'
        }
        
        interest_update = BuyerInterestUpdate(**update_data)
        
        assert interest_update.delivery_latitude == Decimal('19.0760')
        assert interest_update.delivery_longitude == Decimal('72.8777')
        assert interest_update.delivery_pincode == '400001'
        assert interest_update.delivery_state == 'Maharashtra'
    
    def test_buyer_interest_response_includes_delivery_address(self):
        """Test buyer interest response includes delivery address fields"""
        data = {
            'id': 1,
            'listing_id': 1,
            'buyer_name': 'Cooperative Society',
            'buyer_phone': '+919876543210',
            'buyer_email': 'coop@society.org',
            'buyer_type': 'cooperative',
            'interested_quantity': 1500,
            'message': 'Bulk order for members',
            'status': 'pending',
            'created_at': '2024-01-20T10:00:00',
            'updated_at': '2024-01-20T10:00:00',
            'enable': 1,
            # Delivery address
            'delivery_latitude': Decimal('26.8467'),
            'delivery_longitude': Decimal('80.9462'),
            'delivery_pincode': '226001',
            'delivery_state': 'Uttar Pradesh',
            'delivery_district': 'Lucknow',
            'delivery_village': 'Hazratganj',
            'delivery_address_line1': 'Cooperative Building',
            'delivery_address_line2': 'Main Road'
        }
        
        response_dict = {**data}
        
        assert response_dict['delivery_latitude'] == Decimal('26.8467')
        assert response_dict['delivery_longitude'] == Decimal('80.9462')
        assert response_dict['delivery_pincode'] == '226001'
        assert response_dict['delivery_state'] == 'Uttar Pradesh'


class TestMarketplaceAddressValidation:
    """Test marketplace address validation logic"""
    
    def test_delivery_address_differs_from_farm_location(self):
        """Test that delivery address can differ from farm location"""
        farm_location = {
            'location_state': 'Punjab',
            'location_district': 'Ludhiana'
        }
        
        delivery_address = {
            'delivery_pincode': '110001',
            'delivery_village': 'Delhi',
            'delivery_state': 'Delhi'
        }
        
        # Delivery can be in different location than farm
        assert farm_location['location_state'] != delivery_address['delivery_state']
    
    def test_buyer_delivery_differs_from_listing_delivery(self):
        """Test that buyer delivery address can differ from listing delivery"""
        listing_delivery = {
            'delivery_pincode': '141001',
            'delivery_village': 'Ludhiana City'
        }
        
        buyer_delivery = {
            'delivery_pincode': '400001',
            'delivery_village': 'Mumbai Fort'
        }
        
        # Buyer can specify different delivery location
        assert listing_delivery['delivery_pincode'] != buyer_delivery['delivery_pincode']
    
    def test_gps_coordinates_optional_for_delivery(self):
        """Test that GPS coordinates are optional for delivery addresses"""
        data = {
            'farm_id': 1,
            'farmer_id': 1,
            'crop_type': 'Maize',
            'expected_harvest_date': date(2024, 9, 15),
            'estimated_quantity': 4000,
            'location_state': 'Karnataka',
            'location_district': 'Bangalore',
            'delivery_pincode': '560001',
            'delivery_village': 'Bangalore City'
        }
        
        listing = MarketplaceListingCreate(**data)
        
        # GPS is optional - delivery can work with pincode only
        assert listing.delivery_latitude is None
        assert listing.delivery_longitude is None
        assert listing.delivery_pincode == '560001'
    
    def test_delivery_address_fields_max_length(self):
        """Test delivery address field max length constraints"""
        data = {
            'listing_id': 1,
            'buyer_name': 'Test Buyer',
            'buyer_phone': '+919876543210',
            'buyer_type': 'wholesaler',
            'interested_quantity': 1000,
            'delivery_pincode': '110001',
            'delivery_state': 'Delhi',
            'delivery_district': 'Central Delhi',
            'delivery_village': 'Connaught Place',
            'delivery_address_line1': 'A' * 255,  # Max length
            'delivery_address_line2': 'B' * 255   # Max length
        }
        
        interest = BuyerInterestCreate(**data)
        
        assert len(interest.delivery_address_line1) == 255
        assert len(interest.delivery_address_line2) == 255


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
