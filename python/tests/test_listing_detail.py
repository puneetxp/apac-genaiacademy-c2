"""
Test for listing detail view endpoint (Task 8.7)
"""

import sys
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

# Import test models from conftest
from tests.conftest import Crop, Farm, FarmPlot, MarketplaceListing, User

# Monkey patch the imports in marketplace_service to use test models
sys.path.insert(0, str(Path(__file__).parent))
import conftest

sys.modules["app.models.user"] = type("module", (), {"User": conftest.User})()
sys.modules["app.models.farm"] = type("module", (), {"Farm": conftest.Farm})()
sys.modules["app.models.farm_plot"] = type("module", (), {"FarmPlot": conftest.FarmPlot})()
sys.modules["app.models.crop"] = type("module", (), {"Crop": conftest.Crop})()
sys.modules["app.models.marketplace_listing"] = type(
    "module", (), {"MarketplaceListing": conftest.MarketplaceListing}
)()
sys.modules["app.models.crop_market_data"] = type(
    "module", (), {"CropMarketData": conftest.CropMarketData}
)()

from app.services.marketplace_service import MarketplaceService


def test_get_listing_detail_returns_all_required_fields(db_session):
    """
    Test that get_listing_detail returns all required fields

    Validates: AC4 - Listing detail view with comprehensive information
    """
    # Create test user (farmer)
    farmer = User(
        id=uuid.uuid4(),
        email="farmer@test.com",
        phone_number="+919876543210",
        full_name="Test Farmer",
        user_type="farmer",
    )
    db_session.add(farmer)

    # Create test farm
    farm = Farm(
        id=uuid.uuid4(),
        farmer_id=farmer.id,
        name="Test Farm",
        location_state="Karnataka",
        location_district="Bangalore Rural",
        location_block="Devanahalli",
        total_area=Decimal("10.0"),
    )
    db_session.add(farm)

    # Create test plot
    plot = FarmPlot(
        id=uuid.uuid4(),
        farm_id=farm.id,
        plot_number="P1",
        area=Decimal("5.0"),
        soil_type="loamy",
        irrigation_type="borewell",
    )
    db_session.add(plot)

    # Create test crop
    crop = Crop(
        id=uuid.uuid4(),
        plot_id=plot.id,
        planting_date=date.today() - timedelta(days=60),
        expected_harvest_date=date.today() + timedelta(days=60),
        area_planted=Decimal("5.0"),
        growth_stage="vegetative",
    )
    db_session.add(crop)

    # Create test listing
    listing = MarketplaceListing(
        id=uuid.uuid4(),
        crop_id=crop.id,
        farmer_id=farmer.id,
        title="Rice (IR64) - Bangalore Rural, Karnataka",
        description="High-quality rice available for advance booking",
        crop_type="rice",
        crop_variety="IR64",
        estimated_quantity=Decimal("100.0"),
        quantity_unit="quintals",
        quality_grade="A",
        quality_confidence=Decimal("0.90"),
        quality_description="Expected A grade based on AI prediction",
        expected_harvest_date=date.today() + timedelta(days=60),
        harvest_date_confidence=Decimal("0.85"),
        harvest_window_start=date.today() + timedelta(days=53),
        harvest_window_end=date.today() + timedelta(days=67),
        asking_price_per_unit=Decimal("2000.0"),
        price_negotiable=True,
        currency="INR",
        location_state="Karnataka",
        location_district="Bangalore Rural",
        location_block="Devanahalli",
        contact_enabled=True,
        farmer_phone="+919876543210",
        farmer_email="farmer@test.com",
        preferred_contact_method="phone",
        market_demand_score=Decimal("0.75"),
        price_trend="stable",
        yoy_price_growth=Decimal("5.0"),
        status="active",
        advance_booking_allowed=True,
        view_count=0,
        interest_count=0,
    )
    db_session.add(listing)
    db_session.commit()

    # Test get_listing_detail
    marketplace_service = MarketplaceService(db_session)
    listing_detail = marketplace_service.get_listing_detail(listing.id)

    # Verify all required fields are present
    assert listing_detail is not None
    assert listing_detail["id"] == str(listing.id)
    assert listing_detail["title"] == listing.title
    assert listing_detail["crop_type"] == "rice"
    assert listing_detail["crop_variety"] == "IR64"

    # Verify production predictions
    assert "production_predictions" in listing_detail
    prod_pred = listing_detail["production_predictions"]
    assert "estimated_yield" in prod_pred
    assert prod_pred["estimated_yield"]["quantity"] == 100.0
    assert prod_pred["estimated_yield"]["unit"] == "quintals"
    assert "quality_prediction" in prod_pred
    assert prod_pred["quality_prediction"]["grade"] == "A"
    assert "harvest_timing" in prod_pred
    assert "expected_date" in prod_pred["harvest_timing"]

    # Verify farmer contact options
    assert "contact" in listing_detail
    assert listing_detail["contact"]["enabled"] is True
    assert listing_detail["contact"]["phone"] == "+919876543210"
    assert listing_detail["contact"]["email"] == "farmer@test.com"

    # Verify interest registration link
    assert "interest_registration" in listing_detail
    assert listing_detail["interest_registration"]["allowed"] is True
    assert listing_detail["interest_registration"]["endpoint"] == "/marketplace/buyer-interest"
    assert listing_detail["interest_registration"]["listing_id"] == str(listing.id)

    # Verify market intelligence context
    assert "market_intelligence" in listing_detail
    market_intel = listing_detail["market_intelligence"]
    assert "demand_score" in market_intel
    assert "demand_trend" in market_intel
    assert "price_trend" in market_intel
    assert "yoy_growth" in market_intel

    # Verify view count was incremented
    db_session.refresh(listing)
    assert listing.view_count == 1


def test_get_listing_detail_with_market_intelligence(db_session):
    """
    Test that market intelligence includes YoY growth and demand trends

    Validates: AC4 - Market intelligence context from crop_market_data
    """
    # Create minimal test data
    farmer = User(
        id=uuid.uuid4(),
        email="farmer2@test.com",
        phone_number="+919876543211",
        full_name="Test Farmer 2",
        user_type="farmer",
    )
    db_session.add(farmer)

    farm = Farm(
        id=uuid.uuid4(),
        farmer_id=farmer.id,
        name="Test Farm 2",
        location_state="Punjab",
        location_district="Ludhiana",
        total_area=Decimal("20.0"),
    )
    db_session.add(farm)

    plot = FarmPlot(
        id=uuid.uuid4(),
        farm_id=farm.id,
        plot_number="P1",
        area=Decimal("10.0"),
        soil_type="clay",
        irrigation_type="canal",
    )
    db_session.add(plot)

    crop = Crop(
        id=uuid.uuid4(),
        plot_id=plot.id,
        planting_date=date.today() - timedelta(days=30),
        expected_harvest_date=date.today() + timedelta(days=90),
        area_planted=Decimal("10.0"),
    )
    db_session.add(crop)

    listing = MarketplaceListing(
        id=uuid.uuid4(),
        crop_id=crop.id,
        farmer_id=farmer.id,
        title="Wheat (HD2967) - Ludhiana, Punjab",
        description="Premium wheat available",
        crop_type="wheat",
        crop_variety="HD2967",
        estimated_quantity=Decimal("200.0"),
        quantity_unit="quintals",
        quality_grade="A",
        expected_harvest_date=date.today() + timedelta(days=90),
        harvest_window_start=date.today() + timedelta(days=83),
        harvest_window_end=date.today() + timedelta(days=97),
        asking_price_per_unit=Decimal("2100.0"),
        location_state="Punjab",
        location_district="Ludhiana",
        contact_enabled=True,
        farmer_phone="+919876543211",
        farmer_email="farmer2@test.com",
        status="active",
        advance_booking_allowed=True,
    )
    db_session.add(listing)
    db_session.commit()

    # Test get_listing_detail
    marketplace_service = MarketplaceService(db_session)
    listing_detail = marketplace_service.get_listing_detail(listing.id)

    # Verify market intelligence is present
    assert "market_intelligence" in listing_detail
    market_intel = listing_detail["market_intelligence"]

    # Verify required market intelligence fields
    assert "demand_score" in market_intel
    assert isinstance(market_intel["demand_score"], (int, float))

    assert "demand_trend" in market_intel
    assert market_intel["demand_trend"] in ["increasing", "stable", "decreasing"]

    assert "price_trend" in market_intel
    assert market_intel["price_trend"] in ["increasing", "stable", "decreasing"]

    # YoY growth may be None if no historical data
    assert "yoy_growth" in market_intel
    assert "yoy_growth_description" in market_intel

    # Verify price range information
    assert "price_range" in market_intel
    assert "market_context" in market_intel


def test_get_listing_detail_not_found(db_session):
    """
    Test that get_listing_detail returns None for non-existent listing
    """
    marketplace_service = MarketplaceService(db_session)
    listing_detail = marketplace_service.get_listing_detail(uuid.uuid4())

    assert listing_detail is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
