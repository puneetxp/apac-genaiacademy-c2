"""
Tests for Livestock Listing API

Tests the livestock marketplace listing endpoints including creation,
search, filtering, and analytics.

Compatible with Python 3.14.3, pytest, FastAPI 0.115.6
"""

import pytest
from datetime import datetime, date
from decimal import Decimal


def test_livestock_listing_schemas():
    """Test that livestock listing schemas are properly defined"""
    from app.schemas.livestock_listing import (
        LivestockListingCreate,
        LivestockListingUpdate,
        LivestockListingResponse,
        LivestockListingSearchFilters,
        SpeciesEnum,
        PurposeEnum,
        GenderEnum
    )
    
    # Test enum values
    assert SpeciesEnum.CATTLE == "cattle"
    assert SpeciesEnum.GOAT == "goat"
    assert SpeciesEnum.SHEEP == "sheep"
    assert SpeciesEnum.POULTRY == "poultry"
    assert SpeciesEnum.BUFFALO == "buffalo"
    
    assert PurposeEnum.DAIRY == "dairy"
    assert PurposeEnum.MEAT == "meat"
    assert PurposeEnum.BREEDING == "breeding"
    assert PurposeEnum.DRAFT == "draft"
    assert PurposeEnum.EGGS == "eggs"
    
    assert GenderEnum.MALE == "male"
    assert GenderEnum.FEMALE == "female"
    assert GenderEnum.MIXED == "mixed"
    
    # Test schema creation
    listing_data = {
        "livestock_id": 1,
        "farmer_id": 1,
        "title": "Test Livestock",
        "species": "cattle",
        "breed": "Holstein",
        "gender": "female",
        "quantity": 1,
        "purpose": "dairy",
        "price": 50000.0,
        "location_state": "Maharashtra",
        "location_district": "Pune"
    }
    
    listing = LivestockListingCreate(**listing_data)
    assert listing.title == "Test Livestock"
    assert listing.species == SpeciesEnum.CATTLE
    assert listing.price == 50000.0


def test_livestock_listing_service_initialization():
    """Test that livestock listing service can be initialized"""
    from app.services.livestock_listing_service import LivestockListingService
    
    # Service requires a database session, so we just test import
    assert LivestockListingService is not None


def test_livestock_listing_orm_model():
    """Test that livestock listing ORM model exists"""
    from app.orm.livestock_listing import LivestockListing
    
    assert LivestockListing is not None
    assert LivestockListing.table == 'livestock_listings'
    assert 'title' in LivestockListing.fillable
    assert 'species' in LivestockListing.fillable
    assert 'breed' in LivestockListing.fillable
    assert 'price' in LivestockListing.fillable


def test_livestock_transaction_orm_model():
    """Test that livestock transaction ORM model exists"""
    from app.orm.livestock_transaction import LivestockTransaction
    
    assert LivestockTransaction is not None
    assert LivestockTransaction.table == 'livestock_transactions'
    assert 'listing_id' in LivestockTransaction.fillable
    assert 'seller_id' in LivestockTransaction.fillable
    assert 'buyer_id' in LivestockTransaction.fillable
    assert 'transaction_type' in LivestockTransaction.fillable


def test_livestock_listing_api_router():
    """Test that livestock listing API router exists"""
    from app.api.v1.livestock_listings import router
    
    assert router is not None
    assert router.prefix == "/livestock-listings"
    assert "livestock-listings" in router.tags


def test_search_filters_validation():
    """Test search filters validation"""
    from app.schemas.livestock_listing import LivestockListingSearchFilters, SpeciesEnum
    
    # Test valid filters
    filters = LivestockListingSearchFilters(
        species=SpeciesEnum.CATTLE,
        min_price=10000.0,
        max_price=100000.0,
        location_state="Maharashtra",
        skip=0,
        limit=20
    )
    
    assert filters.species == SpeciesEnum.CATTLE
    assert filters.min_price == 10000.0
    assert filters.max_price == 100000.0
    assert filters.location_state == "Maharashtra"
    assert filters.skip == 0
    assert filters.limit == 20


def test_media_upload_request_validation():
    """Test media upload request validation"""
    from app.schemas.livestock_listing import MediaUploadRequest
    
    # Test valid request
    request = MediaUploadRequest(
        filename="cow_photo.jpg",
        content_type="image/jpeg",
        file_size=1024000  # 1MB
    )
    
    assert request.filename == "cow_photo.jpg"
    assert request.content_type == "image/jpeg"
    assert request.file_size == 1024000
    
    # Test file size validation
    with pytest.raises(Exception):
        MediaUploadRequest(
            filename="large_video.mp4",
            content_type="video/mp4",
            file_size=20971520  # 20MB - exceeds 10MB limit
        )


def test_listing_create_validation():
    """Test listing creation validation"""
    from app.schemas.livestock_listing import LivestockListingCreate
    
    # Test valid listing
    listing = LivestockListingCreate(
        livestock_id=1,
        farmer_id=1,
        title="Healthy Holstein Cow",
        species="cattle",
        breed="Holstein",
        age_years=3,
        age_months=6,
        gender="female",
        quantity=1,
        purpose="dairy",
        price=75000.0,
        location_state="Maharashtra",
        location_district="Pune"
    )
    
    assert listing.title == "Healthy Holstein Cow"
    assert listing.age_years == 3
    assert listing.age_months == 6
    
    # Test title length validation
    with pytest.raises(Exception):
        LivestockListingCreate(
            livestock_id=1,
            farmer_id=1,
            title="Cow",  # Too short (min 5 chars)
            species="cattle",
            breed="Holstein",
            gender="female",
            quantity=1,
            purpose="dairy",
            price=75000.0,
            location_state="Maharashtra",
            location_district="Pune"
        )


def test_listing_update_validation():
    """Test listing update validation"""
    from app.schemas.livestock_listing import LivestockListingUpdate
    
    # Test partial update
    update = LivestockListingUpdate(
        price=80000.0,
        price_negotiable=False
    )
    
    assert update.price == 80000.0
    assert update.price_negotiable == False
    
    # Test empty update (all fields optional)
    empty_update = LivestockListingUpdate()
    assert empty_update.price is None
    assert empty_update.title is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

