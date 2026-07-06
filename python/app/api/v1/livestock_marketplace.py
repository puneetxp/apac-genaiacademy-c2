"""
Livestock Marketplace API Endpoints
Handles livestock marketplace listings, ROI calculations, and buyer-seller connections
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.orm.user import User
from app.services.livestock_marketplace_listing_service import LivestockMarketplaceListingService
from app.services.livestock_roi_service import get_roi_calculator
from app.schemas.livestock_marketplace_listing import (
    LivestockMarketplaceListingCreate,
    LivestockMarketplaceListingUpdate,
    LivestockMarketplaceListingResponse,
    LivestockMarketplaceListingList
)
from pydantic import BaseModel, Field

router = APIRouter(prefix="/livestock-marketplace", tags=["livestock-marketplace"])


class ROICalculationRequest(BaseModel):
    """Request model for ROI calculation"""
    species: str = Field(..., description="Animal species (cattle, buffalo, goat, poultry)")
    purpose: str = Field(..., description="Purpose (dairy, meat, breeding, eggs)")
    purchase_price: float = Field(..., gt=0, description="Initial purchase price")
    current_age_months: int = Field(..., gt=0, description="Current age in months")
    total_investment: float = Field(..., gt=0, description="Total investment including feed, healthcare")
    total_revenue: float = Field(default=0, ge=0, description="Total revenue generated so far")
    milk_production_liters_per_day: Optional[float] = Field(None, ge=0, description="Daily milk production (for dairy)")


class ROICalculationResponse(BaseModel):
    """Response model for ROI calculation"""
    current_roi_percentage: float
    net_profit: float
    break_even_achieved: bool
    break_even_date: Optional[str]
    projected_annual_profit: float
    monthly_costs: float
    monthly_revenue: float
    monthly_cash_flow: float
    payback_period_months: Optional[int]
    investment_summary: dict
    recommendations: Optional[List[str]] = None


@router.post("/listings", response_model=LivestockMarketplaceListingResponse)
async def create_livestock_listing(
    listing_data: LivestockMarketplaceListingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new livestock marketplace listing with automatic ROI calculation
    """
    service = LivestockMarketplaceListingService(db)
    roi_calculator = get_roi_calculator()
    
    # Get livestock details to calculate ROI
    from app.services.livestock_service import LivestockService
    livestock_service = LivestockService(db)
    livestock = await livestock_service.get(listing_data.livestock_id)
    
    if not livestock:
        raise HTTPException(status_code=404, detail="Livestock not found")
    
    # Verify ownership
    if livestock.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to list this livestock")
    
    # Calculate ROI metrics
    roi_metrics = roi_calculator.calculate_roi(
        species=livestock.species,
        purpose=livestock.purpose,
        purchase_price=float(livestock.purchase_price),
        current_age_months=listing_data.current_age_months,
        total_investment=float(listing_data.total_investment),
        total_revenue=float(listing_data.total_revenue),
        milk_production_liters_per_day=float(listing_data.milk_production_liters_per_day) if listing_data.milk_production_liters_per_day else None
    )
    
    # Update listing data with calculated ROI
    listing_dict = listing_data.model_dump()
    listing_dict['farmer_id'] = current_user.id
    listing_dict['current_roi_percentage'] = roi_metrics['current_roi_percentage']
    listing_dict['break_even_achieved'] = roi_metrics['break_even_achieved']
    listing_dict['break_even_date'] = roi_metrics['break_even_date']
    listing_dict['projected_annual_profit'] = roi_metrics['projected_annual_profit']
    
    # Create listing
    listing = await service.create(listing_dict)
    
    return listing


@router.get("/listings", response_model=LivestockMarketplaceListingList)
async def get_livestock_listings(
    species: Optional[str] = Query(None, description="Filter by species"),
    listing_type: Optional[str] = Query(None, description="Filter by listing type"),
    state: Optional[str] = Query(None, description="Filter by state"),
    district: Optional[str] = Query(None, description="Filter by district"),
    min_price: Optional[float] = Query(None, description="Minimum asking price"),
    max_price: Optional[float] = Query(None, description="Maximum asking price"),
    min_roi: Optional[float] = Query(None, description="Minimum ROI percentage"),
    health_status: Optional[str] = Query(None, description="Filter by health status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Browse livestock marketplace listings with filters
    """
    service = LivestockMarketplaceListingService(db)
    
    # Build filters
    filters = {}
    if species:
        filters['species'] = species
    if listing_type:
        filters['listing_type'] = listing_type
    if state:
        filters['location_state'] = state
    if district:
        filters['location_district'] = district
    if health_status:
        filters['health_status'] = health_status
    
    # Get listings with pagination
    listings = await service.get_all(
        filters=filters,
        skip=(page - 1) * page_size,
        limit=page_size
    )
    
    # Apply additional filters (price, ROI)
    filtered_listings = []
    for listing in listings:
        if min_price and listing.asking_price < min_price:
            continue
        if max_price and listing.asking_price > max_price:
            continue
        if min_roi and (listing.current_roi_percentage is None or listing.current_roi_percentage < min_roi):
            continue
        filtered_listings.append(listing)
    
    return {
        "listings": filtered_listings,
        "total": len(filtered_listings),
        "page": page,
        "page_size": page_size,
        "total_pages": (len(filtered_listings) + page_size - 1) // page_size
    }


@router.get("/listings/{listing_id}", response_model=LivestockMarketplaceListingResponse)
async def get_livestock_listing_detail(
    listing_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a livestock listing
    """
    service = LivestockMarketplaceListingService(db)
    listing = await service.get(listing_id)
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Increment view count
    await service.update(listing_id, {"views_count": listing.views_count + 1})
    
    return listing


@router.post("/calculate-roi", response_model=ROICalculationResponse)
async def calculate_livestock_roi(
    request: ROICalculationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate ROI for livestock investment (standalone calculator)
    """
    roi_calculator = get_roi_calculator()
    
    roi_metrics = roi_calculator.calculate_roi(
        species=request.species,
        purpose=request.purpose,
        purchase_price=request.purchase_price,
        current_age_months=request.current_age_months,
        total_investment=request.total_investment,
        total_revenue=request.total_revenue,
        milk_production_liters_per_day=request.milk_production_liters_per_day
    )
    
    # Generate recommendations
    livestock_data = {
        'species': request.species,
        'purpose': request.purpose,
        'current_age_months': request.current_age_months
    }
    recommendations = roi_calculator._generate_recommendations(roi_metrics, livestock_data)
    roi_metrics['recommendations'] = recommendations
    
    return roi_metrics


@router.get("/listings/{listing_id}/roi-report")
async def get_livestock_roi_report(
    listing_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive ROI report for a livestock listing
    """
    service = LivestockMarketplaceListingService(db)
    listing = await service.get(listing_id)
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Get livestock details
    from app.services.livestock_service import LivestockService
    livestock_service = LivestockService(db)
    livestock = await livestock_service.get(listing.livestock_id)
    
    if not livestock:
        raise HTTPException(status_code=404, detail="Livestock not found")
    
    # Calculate current ROI metrics
    roi_calculator = get_roi_calculator()
    roi_metrics = roi_calculator.calculate_roi(
        species=livestock.species,
        purpose=livestock.purpose,
        purchase_price=float(livestock.purchase_price),
        current_age_months=listing.current_age_months,
        total_investment=float(listing.total_investment),
        total_revenue=float(listing.total_revenue),
        milk_production_liters_per_day=float(listing.milk_production_liters_per_day) if listing.milk_production_liters_per_day else None
    )
    
    # Generate comprehensive report
    livestock_data = {
        'species': livestock.species,
        'breed': livestock.breed,
        'purpose': livestock.purpose,
        'current_age_months': listing.current_age_months
    }
    
    report = roi_calculator.generate_roi_report(livestock_data, roi_metrics)
    
    return report


@router.put("/listings/{listing_id}", response_model=LivestockMarketplaceListingResponse)
async def update_livestock_listing(
    listing_id: int,
    listing_data: LivestockMarketplaceListingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a livestock marketplace listing
    """
    service = LivestockMarketplaceListingService(db)
    listing = await service.get(listing_id)
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Verify ownership
    if listing.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")
    
    # Update listing
    updated_listing = await service.update(listing_id, listing_data.model_dump(exclude_unset=True))
    
    return updated_listing


@router.delete("/listings/{listing_id}")
async def delete_livestock_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a livestock marketplace listing
    """
    service = LivestockMarketplaceListingService(db)
    listing = await service.get(listing_id)
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Verify ownership
    if listing.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    
    # Delete listing
    await service.delete(listing_id)
    
    return {"message": "Listing deleted successfully"}
