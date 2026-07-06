"""
Tests for marketplace search functionality

Validates: AC4 - Marketplace search with filters, pagination, and sorting
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
import uuid
import sys
from pathlib import Path

# Import test models from conftest
from tests.conftest import User, Farm, FarmPlot, Crop, MarketplaceListing

# Monkey patch the imports in marketplace_service to use test models
sys.path.insert(0, str(Path(__file__).parent))
import conftest
sys.modules['app.models.user'] = type('module', (), {'User': conftest.User})()
sys.modules['app.models.farm'] = type('module', (), {'Farm': conftest.Farm})()
sys.modules['app.models.farm_plot'] = type('module', (), {'FarmPlot': conftest.FarmPlot})()
sys.modules['app.models.crop'] = type('module', (), {'Crop': conftest.Crop})()
sys.modules['app.models.marketplace_listing'] = type('module', (), {'MarketplaceListing': conftest.MarketplaceListing})()
sys.modules['app.models.buyer_interest'] = type('module', (), {'BuyerInterest': conftest.BuyerInterest})()

from app.services.marketplace_service import MarketplaceService


@pytest.fixture
def sample_listings(db_session):
    """Create sample listings for testing"""
    # Create test user
    user = User(
        id=uuid.uuid4(),
        email="farmer@test.com",
        phone_number="+919876543210",
        full_name="Test Farmer"
    )
    db_session.add(user)
    
    # Create test farm
    farm = Farm(
        id=uuid.uuid4(),
        farmer_id=user.id,
        name="Test Farm",
        location_state="Maharashtra",
        location_district="Pune",
        total_area=10.0
    )
    db_session.add(farm)
    
    # Create test plot
    plot = FarmPlot(
        id=uuid.uuid4(),
        farm_id=farm.id,
        plot_number="P1",
        area=5.0,
        soil_type="Black",
        irrigation_type="Borewell"
    )
    db_session.add(plot)
    
    # Create test crop
    crop = Crop(
        id=uuid.uuid4(),
        plot_id=plot.id,
        planting_date=date.today() - timedelta(days=60),
        expected_harvest_date=date.today() + timedelta(days=60),
        area_planted=5.0
    )
    db_session.add(crop)
    
    # Create sample listings with different attributes
    listings_data = [
        {
            'crop_type': 'Rice',
            'crop_variety': 'Basmati',
            'estimated_quantity': Decimal('100.0'),
            'quality_grade': 'A',
            'expected_harvest_date': date.today() + timedelta(days=30),
            'asking_price_per_unit': Decimal('2500.0'),
            'location_state': 'Maharashtra',
            'location_district': 'Pune'
        },
        {
            'crop_type': 'Wheat',
            'crop_variety': 'Lokwan',
            'estimated_quantity': Decimal('150.0'),
            'quality_grade': 'B',
            'expected_harvest_date': date.today() + timedelta(days=60),
            'asking_price_per_unit': Decimal('2100.0'),
            'location_state': 'Maharashtra',
            'location_district': 'Nashik'
        },
        {
            'crop_type': 'Rice',
            'crop_variety': 'Sona Masuri',
            'estimated_quantity': Decimal('80.0'),
            'quality_grade': 'A',
            'expected_harvest_date': date.today() + timedelta(days=45),
            'asking_price_per_unit': Decimal('2300.0'),
            'location_state': 'Karnataka',
            'location_district': 'Bangalore'
        },
        {
            'crop_type': 'Maize',
            'crop_variety': 'Hybrid',
            'estimated_quantity': Decimal('200.0'),
            'quality_grade': 'C',
            'expected_harvest_date': date.today() + timedelta(days=90),
            'asking_price_per_unit': Decimal('1800.0'),
            'location_state': 'Maharashtra',
            'location_district': 'Pune'
        },
        {
            'crop_type': 'Cotton',
            'crop_variety': 'BT Cotton',
            'estimated_quantity': Decimal('120.0'),
            'quality_grade': 'B',
            'expected_harvest_date': date.today() + timedelta(days=120),
            'asking_price_per_unit': Decimal('5500.0'),
            'location_state': 'Gujarat',
            'location_district': 'Ahmedabad'
        }
    ]
    
    created_listings = []
    for listing_data in listings_data:
        listing = MarketplaceListing(
            id=uuid.uuid4(),
            crop_id=crop.id,
            farmer_id=user.id,
            title=f"{listing_data['crop_type']} - {listing_data['location_district']}",
            description=f"High quality {listing_data['crop_type']}",
            status='active',
            quantity_unit='quintals',
            harvest_window_start=listing_data['expected_harvest_date'] - timedelta(days=7),
            harvest_window_end=listing_data['expected_harvest_date'] + timedelta(days=7),
            contact_enabled=True,
            farmer_phone=user.phone_number,
            farmer_email=user.email,
            **listing_data
        )
        db_session.add(listing)
        created_listings.append(listing)
    
    db_session.commit()
    
    return created_listings


class TestMarketplaceSearch:
    """Test marketplace search functionality"""
    
    def test_get_all_active_listings(self, db_session, sample_listings):
        """Test retrieving all active listings without filters"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings()
        
        assert len(listings) == 5
        assert total_count == 5
        assert all(listing.status == 'active' for listing in listings)
    
    def test_filter_by_crop_type(self, db_session, sample_listings):
        """Test filtering by crop type"""
        service = MarketplaceService(db_session)
        
        # Filter for Rice
        listings, total_count = service.get_listings(filters={'crop_type': 'Rice'})
        
        assert len(listings) == 2
        assert total_count == 2
        assert all(listing.crop_type == 'Rice' for listing in listings)
    
    def test_filter_by_crop_type_partial_match(self, db_session, sample_listings):
        """Test filtering by crop type with partial match"""
        service = MarketplaceService(db_session)
        
        # Filter for 'rice' (case-insensitive partial match)
        listings, total_count = service.get_listings(filters={'crop_type': 'rice'})
        
        assert len(listings) == 2
        assert total_count == 2
    
    def test_filter_by_state(self, db_session, sample_listings):
        """Test filtering by state"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(filters={'state': 'Maharashtra'})
        
        assert len(listings) == 3
        assert total_count == 3
        assert all(listing.location_state == 'Maharashtra' for listing in listings)
    
    def test_filter_by_district(self, db_session, sample_listings):
        """Test filtering by district"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(filters={'district': 'Pune'})
        
        assert len(listings) == 2
        assert total_count == 2
        assert all(listing.location_district == 'Pune' for listing in listings)
    
    def test_filter_by_state_and_district(self, db_session, sample_listings):
        """Test filtering by both state and district"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(
            filters={'state': 'Maharashtra', 'district': 'Pune'}
        )
        
        assert len(listings) == 2
        assert total_count == 2
    
    def test_filter_by_quantity_range(self, db_session, sample_listings):
        """Test filtering by quantity range"""
        service = MarketplaceService(db_session)
        
        # Filter for quantities between 100 and 150 quintals
        listings, total_count = service.get_listings(
            filters={'min_quantity': 100, 'max_quantity': 150}
        )
        
        assert len(listings) == 3  # Rice (100), Wheat (150), Cotton (120)
        assert total_count == 3
        assert all(100 <= listing.estimated_quantity <= 150 for listing in listings)
    
    def test_filter_by_harvest_date_range(self, db_session, sample_listings):
        """Test filtering by harvest date range"""
        service = MarketplaceService(db_session)
        
        harvest_from = date.today() + timedelta(days=20)
        harvest_to = date.today() + timedelta(days=70)
        
        listings, total_count = service.get_listings(
            filters={'harvest_from': harvest_from, 'harvest_to': harvest_to}
        )
        
        assert len(listings) == 3  # Rice (30 days), Rice (45 days), Wheat (60 days)
        assert total_count == 3
        assert all(
            harvest_from <= listing.expected_harvest_date <= harvest_to
            for listing in listings
        )
    
    def test_filter_by_quality_grade(self, db_session, sample_listings):
        """Test filtering by quality grade"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(filters={'quality_grade': 'A'})
        
        assert len(listings) == 2
        assert total_count == 2
        assert all(listing.quality_grade == 'A' for listing in listings)
    
    def test_filter_by_price_range(self, db_session, sample_listings):
        """Test filtering by price range"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(
            filters={'min_price': 2000, 'max_price': 2500}
        )
        
        assert len(listings) == 3  # Rice (2500), Wheat (2100), Rice (2300)
        assert total_count == 3
        assert all(
            2000 <= listing.asking_price_per_unit <= 2500
            for listing in listings
        )
    
    def test_multiple_filters_combined(self, db_session, sample_listings):
        """Test combining multiple filters"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(
            filters={
                'crop_type': 'Rice',
                'quality_grade': 'A',
                'state': 'Maharashtra'
            }
        )
        
        assert len(listings) == 1
        assert total_count == 1
        assert listings[0].crop_type == 'Rice'
        assert listings[0].quality_grade == 'A'
        assert listings[0].location_state == 'Maharashtra'
    
    def test_sort_by_harvest_date_asc(self, db_session, sample_listings):
        """Test sorting by harvest date ascending"""
        service = MarketplaceService(db_session)
        
        listings, _ = service.get_listings(sort_by='harvest_date', sort_order='asc')
        
        # Verify listings are sorted by harvest date ascending
        for i in range(len(listings) - 1):
            assert listings[i].expected_harvest_date <= listings[i + 1].expected_harvest_date
    
    def test_sort_by_harvest_date_desc(self, db_session, sample_listings):
        """Test sorting by harvest date descending"""
        service = MarketplaceService(db_session)
        
        listings, _ = service.get_listings(sort_by='harvest_date', sort_order='desc')
        
        # Verify listings are sorted by harvest date descending
        for i in range(len(listings) - 1):
            assert listings[i].expected_harvest_date >= listings[i + 1].expected_harvest_date
    
    def test_sort_by_quantity_asc(self, db_session, sample_listings):
        """Test sorting by quantity ascending"""
        service = MarketplaceService(db_session)
        
        listings, _ = service.get_listings(sort_by='quantity', sort_order='asc')
        
        # Verify listings are sorted by quantity ascending
        for i in range(len(listings) - 1):
            assert listings[i].estimated_quantity <= listings[i + 1].estimated_quantity
    
    def test_sort_by_quantity_desc(self, db_session, sample_listings):
        """Test sorting by quantity descending"""
        service = MarketplaceService(db_session)
        
        listings, _ = service.get_listings(sort_by='quantity', sort_order='desc')
        
        # Verify listings are sorted by quantity descending
        for i in range(len(listings) - 1):
            assert listings[i].estimated_quantity >= listings[i + 1].estimated_quantity
    
    def test_sort_by_price_asc(self, db_session, sample_listings):
        """Test sorting by price ascending"""
        service = MarketplaceService(db_session)
        
        listings, _ = service.get_listings(sort_by='price', sort_order='asc')
        
        # Verify listings are sorted by price ascending
        for i in range(len(listings) - 1):
            assert listings[i].asking_price_per_unit <= listings[i + 1].asking_price_per_unit
    
    def test_sort_by_quality_grade(self, db_session, sample_listings):
        """Test sorting by quality grade"""
        service = MarketplaceService(db_session)
        
        listings, _ = service.get_listings(sort_by='quality_grade', sort_order='asc')
        
        # Verify listings are sorted by quality grade
        assert len(listings) == 5
    
    def test_pagination_first_page(self, db_session, sample_listings):
        """Test pagination - first page"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(limit=2, offset=0)
        
        assert len(listings) == 2
        assert total_count == 5
    
    def test_pagination_second_page(self, db_session, sample_listings):
        """Test pagination - second page"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(limit=2, offset=2)
        
        assert len(listings) == 2
        assert total_count == 5
    
    def test_pagination_last_page(self, db_session, sample_listings):
        """Test pagination - last page with partial results"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(limit=2, offset=4)
        
        assert len(listings) == 1  # Only 1 item on last page
        assert total_count == 5
    
    def test_pagination_with_filters(self, db_session, sample_listings):
        """Test pagination combined with filters"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(
            filters={'state': 'Maharashtra'},
            limit=2,
            offset=0
        )
        
        assert len(listings) == 2
        assert total_count == 3  # Total Maharashtra listings
    
    def test_pagination_with_sorting(self, db_session, sample_listings):
        """Test pagination combined with sorting"""
        service = MarketplaceService(db_session)
        
        # Get first page sorted by quantity descending
        page1, total = service.get_listings(
            sort_by='quantity',
            sort_order='desc',
            limit=2,
            offset=0
        )
        
        # Get second page
        page2, _ = service.get_listings(
            sort_by='quantity',
            sort_order='desc',
            limit=2,
            offset=2
        )
        
        assert len(page1) == 2
        assert len(page2) == 2
        assert total == 5
        
        # Verify sorting is maintained across pages
        assert page1[0].estimated_quantity >= page1[1].estimated_quantity
        assert page1[1].estimated_quantity >= page2[0].estimated_quantity
    
    def test_empty_results(self, db_session, sample_listings):
        """Test search with no matching results"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings(
            filters={'crop_type': 'Sugarcane'}  # No sugarcane listings
        )
        
        assert len(listings) == 0
        assert total_count == 0
    
    def test_default_page_size(self, db_session, sample_listings):
        """Test default page size of 20 items"""
        service = MarketplaceService(db_session)
        
        listings, total_count = service.get_listings()
        
        # With only 5 listings, should return all
        assert len(listings) == 5
        assert total_count == 5
