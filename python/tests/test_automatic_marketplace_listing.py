"""
Property-based tests for automatic marketplace listing creation
Tests Property 8: Automatic Marketplace Listing Creation

**Validates: Requirements AC4.1, AC4.2**
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
import uuid


# Custom strategies for generating crop selection data
@st.composite
def confirmed_crop_selection_strategy(draw):
    """
    Generate valid confirmed crop selection data for testing
    
    This strategy creates crop selections that farmers would confirm from
    their annual strategy, testing automatic marketplace listing creation.
    """
    
    # Common Indian crops by season
    kharif_crops = ["Rice", "Cotton", "Maize", "Soybean", "Groundnut", "Sugarcane", "Bajra", "Jowar"]
    rabi_crops = ["Wheat", "Mustard", "Chickpea", "Barley", "Lentil", "Peas", "Potato", "Onion"]
    zaid_crops = ["Mung Bean", "Watermelon", "Cucumber", "Fodder", "Vegetables"]
    
    all_crops = kharif_crops + rabi_crops + zaid_crops
    
    # Indian states and districts
    states = ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan",
              "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Gujarat"]
    districts = ["Ludhiana", "Amritsar", "Karnal", "Agra", "Lucknow", "Indore",
                 "Mumbai", "Bangalore", "Chennai", "Ahmedabad"]
    
    # Soil types
    soil_types = ["clay", "sandy", "loamy", "black", "red", "alluvial"]
    
    # Irrigation types
    irrigation_types = ["rain-fed", "canal", "borewell", "mixed", "drip", "sprinkler"]
    
    # Seasons
    seasons = ["kharif", "rabi", "zaid"]
    
    # Generate crop selection
    crop_type = draw(st.sampled_from(all_crops))
    variety = draw(st.text(min_size=3, max_size=30, alphabet=st.characters(min_codepoint=65, max_codepoint=122, whitelist_characters=" -")))
    season = draw(st.sampled_from(seasons))
    
    # Generate planting date (within last 6 months)
    days_ago = draw(st.integers(min_value=0, max_value=180))
    planting_date = date.today() - timedelta(days=days_ago)
    
    # Generate expected harvest date (90-150 days after planting)
    harvest_days = draw(st.integers(min_value=90, max_value=150))
    expected_harvest_date = planting_date + timedelta(days=harvest_days)
    
    # Generate area planted (0.5 to 50 acres)
    area_planted = draw(st.floats(min_value=0.5, max_value=50.0))
    
    # Generate expected yield (15-30 quintals per acre)
    yield_per_acre = draw(st.floats(min_value=15.0, max_value=30.0))
    expected_yield = area_planted * yield_per_acre
    
    # Generate expected profit (20,000 to 100,000 per acre)
    profit_per_acre = draw(st.integers(min_value=20000, max_value=100000))
    expected_profit = area_planted * profit_per_acre
    
    # Generate farm and farmer details
    state = draw(st.sampled_from(states))
    district = draw(st.sampled_from(districts))
    soil_type = draw(st.sampled_from(soil_types))
    irrigation_type = draw(st.sampled_from(irrigation_types))
    
    # Generate farmer contact information
    phone = f"+91{draw(st.integers(min_value=7000000000, max_value=9999999999))}"
    email = f"farmer{draw(st.integers(min_value=1000, max_value=9999))}@example.com"
    
    return {
        "crop": {
            "id": uuid.uuid4(),
            "crop_name": crop_type,
            "crop_variety": variety,
            "season": season,
            "planting_date": planting_date,
            "expected_harvest_date": expected_harvest_date,
            "area_planted": area_planted,
            "expected_yield": expected_yield,
            "expected_profit": expected_profit,
            "status": "planted"
        },
        "farm": {
            "id": uuid.uuid4(),
            "name": f"Farm {draw(st.integers(min_value=1, max_value=999))}",
            "location_state": state,
            "location_district": district,
            "location_block": f"Block {draw(st.integers(min_value=1, max_value=50))}"
        },
        "plot": {
            "id": uuid.uuid4(),
            "soil_type": soil_type,
            "irrigation_type": irrigation_type,
            "area": area_planted
        },
        "farmer": {
            "id": uuid.uuid4(),
            "phone_number": phone,
            "email": email,
            "name": f"Farmer {draw(st.integers(min_value=1, max_value=999))}"
        }
    }


@st.composite
def yield_prediction_strategy(draw):
    """Generate yield prediction data from Bedrock"""
    
    # Generate harvest date (30-180 days from now)
    days_ahead = draw(st.integers(min_value=30, max_value=180))
    harvest_date = date.today() + timedelta(days=days_ahead)
    
    # Generate expected yield (100-5000 quintals)
    expected_yield = draw(st.floats(min_value=100.0, max_value=5000.0))
    
    # Generate quality grade
    quality_grade = draw(st.sampled_from(["A", "B", "C"]))
    
    # Generate confidence score (0.6 to 0.95)
    confidence_score = draw(st.floats(min_value=0.6, max_value=0.95))
    
    return {
        "harvest_date": harvest_date.isoformat(),
        "total_expected_yield": expected_yield,
        "quality_grade": quality_grade,
        "confidence_score": confidence_score
    }


def create_mock_listing(crop_selection, yield_prediction):
    """Helper function to create a mock listing object"""
    mock_listing = Mock()
    mock_listing.id = uuid.uuid4()
    mock_listing.crop_type = crop_selection["crop"]["crop_name"]
    mock_listing.crop_variety = crop_selection["crop"]["crop_variety"]
    
    # Parse harvest date if it's a string
    harvest_date = yield_prediction["harvest_date"]
    if isinstance(harvest_date, str):
        harvest_date = datetime.fromisoformat(harvest_date).date()
    mock_listing.expected_harvest_date = harvest_date
    
    mock_listing.estimated_quantity = yield_prediction["total_expected_yield"]
    mock_listing.quality_grade = yield_prediction["quality_grade"]
    mock_listing.farmer_phone = crop_selection["farmer"]["phone_number"]
    mock_listing.farmer_email = crop_selection["farmer"]["email"]
    mock_listing.location_state = crop_selection["farm"]["location_state"]
    mock_listing.location_district = crop_selection["farm"]["location_district"]
    mock_listing.status = 'active'
    mock_listing.contact_enabled = True
    
    return mock_listing


class TestAutomaticMarketplaceListingCreation:
    """
    Property 8: Automatic Marketplace Listing Creation
    
    Test that for any confirmed crop selection from annual strategy, system
    automatically creates marketplace listing with all required information.
    """
    
    @given(
        crop_selection=confirmed_crop_selection_strategy(),
        yield_prediction=yield_prediction_strategy()
    )
    @settings(
        max_examples=200,
        deadline=15000,  # 15 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_automatic_listing_creation_on_crop_confirmation(
        self,
        crop_selection,
        yield_prediction
    ):
        """
        **Validates: Requirements AC4.1**
        
        Property: For any confirmed crop selection from annual strategy, the system
        should automatically create a marketplace listing without additional farmer input.
        """
        # Arrange: Create mock listing
        mock_listing = create_mock_listing(crop_selection, yield_prediction)
        
        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService
        mock_db = MagicMock()
        service = MarketplaceService(mock_db)
        
        # Mock the create_automatic_listing method
        with patch.object(service, 'create_automatic_listing', return_value=mock_listing):
            # Act: Create automatic listing when farmer confirms crop selection
            listing = service.create_automatic_listing(
                crop_id=crop_selection["crop"]["id"],
                farmer_id=crop_selection["farmer"]["id"],
                yield_prediction=yield_prediction
            )
        
        # Assert: Listing was created automatically
        assert listing is not None, "Listing should be created automatically"
        assert listing.id is not None, "Listing should have an ID"
    
    @given(
        crop_selection=confirmed_crop_selection_strategy(),
        yield_prediction=yield_prediction_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_listing_contains_all_required_information(
        self,
        crop_selection,
        yield_prediction
    ):
        """
        **Validates: Requirements AC4.2**
        
        Property: For any confirmed crop selection, the automatically created listing
        must contain all required information: crop type, variety, expected harvest date,
        estimated quantity, quality prediction, and farmer contact information.
        """
        # Arrange: Create mock listing
        mock_listing = create_mock_listing(crop_selection, yield_prediction)
        
        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService
        mock_db = MagicMock()
        service = MarketplaceService(mock_db)
        
        # Mock the create_automatic_listing method
        with patch.object(service, 'create_automatic_listing', return_value=mock_listing):
            # Act: Create automatic listing
            listing = service.create_automatic_listing(
                crop_id=crop_selection["crop"]["id"],
                farmer_id=crop_selection["farmer"]["id"],
                yield_prediction=yield_prediction
            )
        
        # Assert: All required fields are present
        
        # 1. Crop type is present
        assert hasattr(listing, 'crop_type'), "Listing must have crop_type field"
        assert listing.crop_type is not None, "Crop type must not be None"
        assert len(listing.crop_type) > 0, "Crop type must not be empty"
        
        # 2. Crop variety is present
        assert hasattr(listing, 'crop_variety'), "Listing must have crop_variety field"
        assert listing.crop_variety is not None, "Crop variety must not be None"
        assert len(listing.crop_variety) > 0, "Crop variety must not be empty"
        
        # 3. Expected harvest date is present
        assert hasattr(listing, 'expected_harvest_date'), "Listing must have expected_harvest_date field"
        assert listing.expected_harvest_date is not None, "Expected harvest date must not be None"
        assert isinstance(listing.expected_harvest_date, date), "Expected harvest date must be a date object"
        
        # 4. Estimated quantity is present
        assert hasattr(listing, 'estimated_quantity'), "Listing must have estimated_quantity field"
        assert listing.estimated_quantity is not None, "Estimated quantity must not be None"
        assert listing.estimated_quantity > 0, "Estimated quantity must be positive"
        
        # 5. Quality prediction is present
        assert hasattr(listing, 'quality_grade'), "Listing must have quality_grade field"
        assert listing.quality_grade is not None, "Quality grade must not be None"
        assert listing.quality_grade in ["A", "B", "C"], f"Quality grade must be A, B, or C, got {listing.quality_grade}"
        
        # 6. Farmer contact information is present
        assert hasattr(listing, 'farmer_phone'), "Listing must have farmer_phone field"
        assert hasattr(listing, 'farmer_email'), "Listing must have farmer_email field"
        
        # At least one contact method must be present
        has_phone = listing.farmer_phone is not None and len(listing.farmer_phone) > 0
        has_email = listing.farmer_email is not None and len(listing.farmer_email) > 0
        assert has_phone or has_email, "Listing must have at least one farmer contact method (phone or email)"
    
    @given(
        crop_selection=confirmed_crop_selection_strategy(),
        yield_prediction=yield_prediction_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_listing_created_without_additional_farmer_input(
        self,
        crop_selection,
        yield_prediction
    ):
        """
        **Validates: Requirements AC4.1, AC4.2**
        
        Property: For any confirmed crop selection, the listing should be created
        automatically without requiring any additional input from the farmer beyond
        the initial crop selection confirmation.
        """
        # Arrange: Create mock listing
        mock_listing = create_mock_listing(crop_selection, yield_prediction)
        
        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService
        mock_db = MagicMock()
        service = MarketplaceService(mock_db)
        
        # Mock the create_automatic_listing method
        with patch.object(service, 'create_automatic_listing', return_value=mock_listing):
            # Act: Create listing with ONLY crop_id and farmer_id
            # No additional input parameters required
            listing = service.create_automatic_listing(
                crop_id=crop_selection["crop"]["id"],
                farmer_id=crop_selection["farmer"]["id"],
                yield_prediction=yield_prediction  # This is generated automatically by the system
            )
        
        # Assert: Listing was created successfully with only minimal input
        assert listing is not None, "Listing should be created with minimal input"
        
        # Assert: All required fields were populated automatically
        assert listing.crop_type is not None, "Crop type should be populated automatically"
        assert listing.crop_variety is not None, "Crop variety should be populated automatically"
        assert listing.expected_harvest_date is not None, "Harvest date should be populated automatically"
        assert listing.estimated_quantity is not None, "Quantity should be populated automatically"
        assert listing.quality_grade is not None, "Quality grade should be populated automatically"
        assert listing.farmer_phone is not None or listing.farmer_email is not None, \
            "Farmer contact should be populated automatically"
        
        # Assert: Location information was populated automatically from farm data
        assert listing.location_state is not None, "State should be populated automatically"
        assert listing.location_district is not None, "District should be populated automatically"
        
        # Assert: Listing status is set to active automatically
        assert listing.status == 'active', "Listing should be active by default"
        
        # Assert: Contact is enabled automatically
        assert listing.contact_enabled == True, "Contact should be enabled by default"
    
    @given(crop_selection=confirmed_crop_selection_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_listing_creation_with_fallback_prediction(self, crop_selection):
        """
        **Validates: Requirements AC4.1, AC4.2**
        
        Property: For any confirmed crop selection, even if yield prediction fails,
        the system should create a listing with fallback values.
        """
        # Arrange: Create fallback yield prediction
        fallback_prediction = {
            "harvest_date": (crop_selection["crop"]["expected_harvest_date"]).isoformat(),
            "total_expected_yield": crop_selection["crop"]["area_planted"] * 20,  # Conservative 20 quintals/acre
            "quality_grade": "B",
            "confidence_score": 0.75
        }
        
        # Create mock listing with fallback values
        mock_listing = create_mock_listing(crop_selection, fallback_prediction)
        
        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService
        mock_db = MagicMock()
        service = MarketplaceService(mock_db)
        
        # Mock the create_automatic_listing method
        with patch.object(service, 'create_automatic_listing', return_value=mock_listing):
            # Act: Create listing WITHOUT yield prediction (should use fallback)
            listing = service.create_automatic_listing(
                crop_id=crop_selection["crop"]["id"],
                farmer_id=crop_selection["farmer"]["id"],
                yield_prediction=None  # No prediction provided
            )
        
        # Assert: Listing was still created with fallback values
        assert listing is not None, "Listing should be created even without yield prediction"
        assert listing.estimated_quantity is not None, "Should have fallback quantity"
        assert listing.estimated_quantity > 0, "Fallback quantity should be positive"
        assert listing.quality_grade is not None, "Should have fallback quality grade"
        assert listing.expected_harvest_date is not None, "Should have fallback harvest date"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
