"""
Livestock Listings API

REST API endpoints for livestock marketplace listings including creation,
search, filtering, analytics, and media upload management.

Compatible with Python 3.14.3, FastAPI 0.115.6
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.core.database import get_db
from app.schemas.livestock_listing import (
    LivestockListingCreate,
    LivestockListingUpdate,
    LivestockListingResponse,
    LivestockListingSearchFilters,
    LivestockListingAnalytics,
    MediaUploadRequest,
    MediaUploadResponse,
    SpeciesEnum,
    PurposeEnum,
    GenderEnum,
    HealthStatusEnum,
    VaccinationStatusEnum,
    ListingStatusEnum
)
from app.services.livestock_listing_service import LivestockListingService

router = APIRouter(prefix="/livestock-listings", tags=["livestock-listings"])


# Dependency to get current user ID (simplified for MVP)
async def get_current_user_id() -> int:
    """Get current authenticated user ID"""
    # TODO: Implement proper JWT authentication
    return 1


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_livestock_listing(
    listing: LivestockListingCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Create a new livestock listing.

    - **livestock_id**: ID of the livestock to list
    - **title**: Listing title (5-255 characters)
    - **species**: Livestock species (cattle, goat, sheep, poultry, buffalo)
    - **breed**: Breed name
    - **purpose**: Primary purpose (dairy, meat, breeding, draft, eggs)
    - **price**: Price in INR
    - **location_state**: State name
    - **location_district**: District name

    Returns the created listing with ID and timestamps.
    """
    service = LivestockListingService(db)
    try:
        listing_data = await service.create_listing(listing, user_id)
        return listing_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create listing: {str(e)}"
        )


@router.get("/{listing_id}", response_model=Dict[str, Any])
async def get_livestock_listing(
    listing_id: int,
    increment_views: bool = Query(False, description="Increment view count"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a livestock listing by ID.

    - **listing_id**: Listing ID
    - **increment_views**: Whether to increment view count (default: false)

    Returns the listing details including photos, videos, and analytics.
    """
    service = LivestockListingService(db)
    listing = await service.get_listing(listing_id, increment_views)

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    return listing


@router.put("/{listing_id}", response_model=Dict[str, Any])
async def update_livestock_listing(
    listing_id: int,
    listing: LivestockListingUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Update a livestock listing.

    Only the owner can update their listing. All fields are optional.

    Returns the updated listing data.
    """
    service = LivestockListingService(db)
    try:
        updated_listing = await service.update_listing(listing_id, listing, user_id)

        if not updated_listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )

        return updated_listing
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update listing: {str(e)}"
        )


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_livestock_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete (deactivate) a livestock listing.

    Only the owner can delete their listing. This is a soft delete that sets
    the status to 'inactive'.
    """
    service = LivestockListingService(db)
    try:
        deleted = await service.delete_listing(listing_id, user_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete listing: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
async def search_livestock_listings(
    species: SpeciesEnum = Query(None, description="Filter by species"),
    breed: str = Query(None, description="Filter by breed (partial match)"),
    purpose: PurposeEnum = Query(None, description="Filter by purpose"),
    min_price: float = Query(None, ge=0, description="Minimum price"),
    max_price: float = Query(None, ge=0, description="Maximum price"),
    min_age_months: int = Query(None, ge=0, description="Minimum age in months"),
    max_age_months: int = Query(None, ge=0, description="Maximum age in months"),
    gender: GenderEnum = Query(None, description="Filter by gender"),
    location_state: str = Query(None, description="Filter by state"),
    location_district: str = Query(None, description="Filter by district"),
    health_status: HealthStatusEnum = Query(None, description="Filter by health status"),
    vaccination_status: VaccinationStatusEnum = Query(None, description="Filter by vaccination status"),
    breeding_certified: bool = Query(None, description="Filter by breeding certification"),
    listing_status: ListingStatusEnum = Query(ListingStatusEnum.ACTIVE, description="Filter by listing status"),
    featured_only: bool = Query(False, description="Show only featured listings"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    sort_by: str = Query("created_at", regex="^(created_at|price|views_count|interest_count)$", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search livestock listings with filters.

    Supports filtering by:
    - Species, breed, purpose, gender
    - Price range, age range
    - Location (state, district)
    - Health and vaccination status
    - Breeding certification
    - Featured status

    Returns paginated results with total count.
    """
    filters = LivestockListingSearchFilters(
        species=species,
        breed=breed,
        purpose=purpose,
        min_price=min_price,
        max_price=max_price,
        min_age_months=min_age_months,
        max_age_months=max_age_months,
        gender=gender,
        location_state=location_state,
        location_district=location_district,
        health_status=health_status,
        vaccination_status=vaccination_status,
        breeding_certified=breeding_certified,
        status=listing_status,
        featured_only=featured_only,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )

    service = LivestockListingService(db)
    listings, total_count = await service.search_listings(filters)

    return {
        "listings": listings,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }


@router.get("/{listing_id}/analytics", response_model=LivestockListingAnalytics)
async def get_listing_analytics(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get analytics for a livestock listing.

    Only the owner can view analytics for their listing.

    Returns:
    - View counts (total, last 7 days, last 30 days)
    - Interest and inquiry counts
    - Average daily views
    - Conversion rate (interest to views ratio)
    """
    service = LivestockListingService(db)
    try:
        analytics = await service.get_listing_analytics(listing_id, user_id)

        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )

        return analytics
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.post("/{listing_id}/interest", status_code=status.HTTP_200_OK)
async def register_interest(
    listing_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Register interest in a livestock listing.

    Increments the interest count for the listing.
    """
    service = LivestockListingService(db)
    success = await service.increment_interest(listing_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not active"
        )

    return {"message": "Interest registered successfully"}


@router.post("/{listing_id}/inquiry", status_code=status.HTTP_200_OK)
async def register_inquiry(
    listing_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Register an inquiry for a livestock listing.

    Increments the inquiry count for the listing.
    """
    service = LivestockListingService(db)
    success = await service.increment_inquiry(listing_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not active"
        )

    return {"message": "Inquiry registered successfully"}


@router.post("/media/upload-url", response_model=MediaUploadResponse)
async def get_media_upload_url(
    request: MediaUploadRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a presigned S3 URL for uploading photos or videos.

    - **filename**: Original filename
    - **content_type**: MIME type (e.g., image/jpeg, video/mp4)
    - **file_size**: File size in bytes (max 10MB)

    Returns a presigned URL for direct upload to S3 and the final file URL.
    The presigned URL expires in 1 hour.
    """
    service = LivestockListingService(db)
    try:
        upload_data = service.generate_presigned_upload_url(
            request.filename,
            request.content_type,
            user_id
        )
        return MediaUploadResponse(**upload_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}"
        )


@router.get("/my-listings/dashboard", response_model=Dict[str, Any])
async def get_seller_dashboard(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get seller dashboard with listing management overview.

    Returns:
    - Total listings count
    - Active listings count
    - Total views, interests, and inquiries
    - Recent listings
    """
    from app.orm.livestock_listing import LivestockListing
    from sqlalchemy import select, func

    # Get listing counts
    active_count_query = select(func.count()).select_from(LivestockListing).where(
        LivestockListing.farmer_id == user_id,
        LivestockListing.status == 'active'
    )
    result = await db.execute(active_count_query)
    active_count = result.scalar()

    total_count_query = select(func.count()).select_from(LivestockListing).where(
        LivestockListing.farmer_id == user_id
    )
    result = await db.execute(total_count_query)
    total_count = result.scalar()

    # Get aggregate stats
    stats_query = select(
        func.sum(LivestockListing.views_count).label('total_views'),
        func.sum(LivestockListing.interest_count).label('total_interests'),
        func.sum(LivestockListing.inquiry_count).label('total_inquiries')
    ).where(LivestockListing.farmer_id == user_id)
    result = await db.execute(stats_query)
    stats = result.one()

    # Get recent listings
    recent_query = select(LivestockListing).where(
        LivestockListing.farmer_id == user_id
    ).order_by(LivestockListing.created_at.desc()).limit(5)
    result = await db.execute(recent_query)
    recent_listings = result.scalars().all()

    service = LivestockListingService(db)

    return {
        "total_listings": total_count,
        "active_listings": active_count,
        "total_views": int(stats.total_views or 0),
        "total_interests": int(stats.total_interests or 0),
        "total_inquiries": int(stats.total_inquiries or 0),
        "recent_listings": [service._format_listing_response(listing) for listing in recent_listings]
    }
