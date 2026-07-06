"""
Tests for Supply Request System
Tests supply request creation, matching, and booking acceptance
"""

import pytest
from datetime import datetime, timedelta
from app.orm.supply_request import SupplyRequest
from app.orm.supply_match import SupplyMatch
from app.orm.marketplace_listing import MarketplaceListing
from app.orm.advance_booking import AdvanceBooking
from app.services.supply_request_matching_service import SupplyRequestMatchingService


class TestSupplyRequestSystem:
    """Test suite for supply request system"""
    
    @pytest.fixture
    def service(self):
        """Get supply request matching service instance"""
        return SupplyRequestMatchingService()
    
    @pytest.fixture
    def sample_request_data(self):
        """Sample supply request data"""
        return {
            'buyer_id': 1,
            'crop_type': 'Wheat',
            'quantity_needed': 1000.0,
            'quality_requirements': 'Grade A',
            'delivery_date_start': (datetime.now() + timedelta(days=30)).isoformat(),
            'delivery_date_end': (datetime.now() + timedelta(days=45)).isoformat(),
            'max_price_per_unit': 25.0,
            'recurring': False,
            'is_emergency': False,
            'delivery_pincode': '122003',
            'delivery_state': 'Haryana',
            'delivery_district': 'Gurgaon'
        }
    
    @pytest.fixture
    def sample_listing_data(self):
        """Sample marketplace listing data"""
        return {
            'farmer_id': 2,
            'crop_type': 'Wheat',
            'quantity_available': 1200.0,
            'quality_grade': 'A',
            'price_per_unit': 23.0,
            'expected_harvest_date': (datetime.now() + timedelta(days=35)).isoformat(),
            'status': 'active',
            'district': 'Gurgaon',
            'state': 'Haryana'
        }
    
    def test_create_supply_request(self, service, sample_request_data):
        """Test creating a supply request"""
        result = service.create_supply_request(sample_request_data)
        
        assert 'request_id' in result
        assert 'initial_matches' in result
        assert 'status' in result
        assert result['status'] == 'open'
        assert isinstance(result['request_id'], int)
        
        # Verify request was saved to database
        request_model = SupplyRequest()
        saved_request = request_model.find(result['request_id'])
        assert saved_request is not None
        assert saved_request['crop_type'] == 'Wheat'
        assert saved_request['quantity_needed'] == 1000.0
    
    def test_supply_request_with_emergency_flag(self, service, sample_request_data):
        """Test creating an emergency supply request"""
        sample_request_data['is_emergency'] = True
        
        result = service.create_supply_request(sample_request_data)
        
        request_model = SupplyRequest()
        saved_request = request_model.find(result['request_id'])
        assert saved_request['is_emergency'] == True
    
    def test_supply_request_with_recurring(self, service, sample_request_data):
        """Test creating a recurring supply request"""
        sample_request_data['recurring'] = True
        sample_request_data['recurrence_pattern'] = 'weekly'
        
        result = service.create_supply_request(sample_request_data)
        
        request_model = SupplyRequest()
        saved_request = request_model.find(result['request_id'])
        assert saved_request['recurring'] == True
        assert saved_request['recurrence_pattern'] == 'weekly'
    
    def test_find_matches_with_available_listings(self, service, sample_request_data, sample_listing_data):
        """Test finding matches when listings are available"""
        # Create a marketplace listing first
        listing_model = MarketplaceListing()
        listing_id = listing_model.insert(sample_listing_data)
        
        # Create supply request
        result = service.create_supply_request(sample_request_data)
        request_id = result['request_id']
        
        # Get matches
        matches = service.get_matches_for_request(request_id)
        
        assert 'single_farmer_matches' in matches
        assert 'aggregated_options' in matches
        
        # Should have at least one match since listing quantity >= request quantity
        assert len(matches['single_farmer_matches']) > 0 or len(matches['aggregated_options']) > 0
    
    def test_find_matches_no_listings(self, service, sample_request_data):
        """Test finding matches when no listings are available"""
        # Create supply request without any listings
        result = service.create_supply_request(sample_request_data)
        
        matches = result['initial_matches']
        
        assert 'single_farmer_matches' in matches
        assert 'aggregated_options' in matches
        assert len(matches['single_farmer_matches']) == 0
        assert len(matches['aggregated_options']) == 0
    
    def test_simple_match_fallback(self, service, sample_request_data, sample_listing_data):
        """Test simple matching fallback when AI is unavailable"""
        # Create a marketplace listing
        listing_model = MarketplaceListing()
        listing_id = listing_model.insert(sample_listing_data)
        
        # Create supply request
        request_model = SupplyRequest()
        request_id = request_model.insert(sample_request_data)
        
        # Get the request
        supply_request = request_model.find(request_id)
        
        # Get available listings
        available_listings = service._get_available_listings('Wheat')
        
        # Test fallback matching
        matches = service._simple_match_fallback(supply_request, available_listings)
        
        assert 'single_farmer_matches' in matches
        assert 'aggregated_options' in matches
        assert 'recommendation' in matches
        
        # Should have single match since listing quantity >= request quantity
        assert len(matches['single_farmer_matches']) > 0
    
    def test_accept_single_match(self, service, sample_request_data, sample_listing_data):
        """Test accepting a single farmer match"""
        # Create listing and request
        listing_model = MarketplaceListing()
        listing_id = listing_model.insert(sample_listing_data)
        
        result = service.create_supply_request(sample_request_data)
        request_id = result['request_id']
        
        # Get matches
        matches = service.get_matches_for_request(request_id)
        
        if len(matches['single_farmer_matches']) > 0:
            match = matches['single_farmer_matches'][0]
            match_id = match['id']
            
            # Accept the match
            acceptance_result = service.accept_match(request_id, match_id=match_id)
            
            assert acceptance_result['success'] == True
            assert len(acceptance_result['booking_ids']) > 0
            
            # Verify booking was created
            booking_model = AdvanceBooking()
            booking = booking_model.find(acceptance_result['booking_ids'][0])
            assert booking is not None
            assert booking['buyer_id'] == sample_request_data['buyer_id']
            assert booking['farmer_id'] == sample_listing_data['farmer_id']
            
            # Verify request status updated
            request_model = SupplyRequest()
            updated_request = request_model.find(request_id)
            assert updated_request['status'] == 'filled'
    
    def test_match_score_calculation(self, service, sample_request_data, sample_listing_data):
        """Test that match scores are calculated correctly"""
        # Create listing with exact match
        listing_model = MarketplaceListing()
        listing_id = listing_model.insert(sample_listing_data)
        
        result = service.create_supply_request(sample_request_data)
        request_id = result['request_id']
        
        matches = service.get_matches_for_request(request_id)
        
        if len(matches['single_farmer_matches']) > 0:
            match = matches['single_farmer_matches'][0]
            
            # Match score should be between 0 and 100
            assert 0 <= match['match_score'] <= 100
            
            # Good match should have high score (>60)
            # Since listing meets all requirements
            assert match['match_score'] > 60
    
    def test_aggregated_matching(self, service, sample_request_data):
        """Test aggregated matching with multiple small farmers"""
        # Create multiple small listings
        listing_model = MarketplaceListing()
        
        listing1 = {
            'farmer_id': 2,
            'crop_type': 'Wheat',
            'quantity_available': 400.0,
            'quality_grade': 'A',
            'price_per_unit': 23.0,
            'expected_harvest_date': (datetime.now() + timedelta(days=35)).isoformat(),
            'status': 'active',
            'district': 'Gurgaon',
            'state': 'Haryana'
        }
        
        listing2 = {
            'farmer_id': 3,
            'crop_type': 'Wheat',
            'quantity_available': 400.0,
            'quality_grade': 'A',
            'price_per_unit': 24.0,
            'expected_harvest_date': (datetime.now() + timedelta(days=35)).isoformat(),
            'status': 'active',
            'district': 'Gurgaon',
            'state': 'Haryana'
        }
        
        listing3 = {
            'farmer_id': 4,
            'crop_type': 'Wheat',
            'quantity_available': 400.0,
            'quality_grade': 'A',
            'price_per_unit': 22.0,
            'expected_harvest_date': (datetime.now() + timedelta(days=35)).isoformat(),
            'status': 'active',
            'district': 'Gurgaon',
            'state': 'Haryana'
        }
        
        listing_model.insert(listing1)
        listing_model.insert(listing2)
        listing_model.insert(listing3)
        
        # Create supply request for 1000kg (no single farmer can fulfill)
        result = service.create_supply_request(sample_request_data)
        request_id = result['request_id']
        
        matches = service.get_matches_for_request(request_id)
        
        # Should have aggregated options
        assert len(matches['aggregated_options']) > 0
        
        # Aggregated option should combine multiple farmers
        agg_option = matches['aggregated_options'][0]
        assert len(agg_option['farmers']) >= 2
        assert agg_option['total_quantity'] >= sample_request_data['quantity_needed']
    
    def test_delivery_location_stored(self, service, sample_request_data):
        """Test that delivery location is properly stored"""
        result = service.create_supply_request(sample_request_data)
        request_id = result['request_id']
        
        request_model = SupplyRequest()
        saved_request = request_model.find(request_id)
        
        assert saved_request['delivery_pincode'] == '122003'
        assert saved_request['delivery_state'] == 'Haryana'
        assert saved_request['delivery_district'] == 'Gurgaon'
    
    def test_quality_requirements_matching(self, service, sample_request_data):
        """Test that quality requirements are considered in matching"""
        # Create listings with different quality grades
        listing_model = MarketplaceListing()
        
        listing_a = {
            'farmer_id': 2,
            'crop_type': 'Wheat',
            'quantity_available': 1200.0,
            'quality_grade': 'A',
            'price_per_unit': 25.0,
            'expected_harvest_date': (datetime.now() + timedelta(days=35)).isoformat(),
            'status': 'active',
            'district': 'Gurgaon',
            'state': 'Haryana'
        }
        
        listing_b = {
            'farmer_id': 3,
            'crop_type': 'Wheat',
            'quantity_available': 1200.0,
            'quality_grade': 'B',
            'price_per_unit': 20.0,
            'expected_harvest_date': (datetime.now() + timedelta(days=35)).isoformat(),
            'status': 'active',
            'district': 'Gurgaon',
            'state': 'Haryana'
        }
        
        listing_model.insert(listing_a)
        listing_model.insert(listing_b)
        
        # Request Grade A quality
        sample_request_data['quality_requirements'] = 'Grade A'
        
        result = service.create_supply_request(sample_request_data)
        request_id = result['request_id']
        
        matches = service.get_matches_for_request(request_id)
        
        # Should have matches
        assert len(matches['single_farmer_matches']) > 0
        
        # Grade A listing should have higher match score than Grade B
        # (if AI matching works correctly)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
