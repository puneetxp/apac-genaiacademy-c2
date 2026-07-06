"""
Transport coordination API endpoints for livestock marketplace.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.database import get_async_db
from app.services.transport_service import TransportService


router = APIRouter(prefix="/transport", tags=["transport"])


# Request/Response Models

class TransportProviderCreate(BaseModel):
    """Request model for registering a transport provider."""
    user_id: int
    company_name: str = Field(..., min_length=1, max_length=255)
    contact_person: str = Field(..., min_length=1, max_length=255)
    contact_phone: str = Field(..., min_length=10, max_length=20)
    contact_email: Optional[str] = None
    service_areas: List[str] = Field(..., min_items=1, description="States/districts served")
    vehicle_types: List[str] = Field(..., min_items=1, description="truck, tempo, mini_truck, specialized_livestock")
    livestock_specialization: Optional[List[str]] = Field(None, description="cattle, goat, sheep, poultry, buffalo")
    base_rate_per_km: float = Field(..., gt=0, description="Base rate in INR per kilometer")
    minimum_charge: float = Field(..., gt=0, description="Minimum charge in INR")
    max_capacity_animals: int = Field(..., gt=0, description="Maximum animals per trip")
    insurance_available: bool = False
    insurance_rate_percentage: Optional[float] = Field(None, ge=0, le=100)
    license_number: Optional[str] = None
    verification_documents: Optional[List[str]] = None


class TransportProviderUpdate(BaseModel):
    """Request model for updating transport provider."""
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    service_areas: Optional[List[str]] = None
    vehicle_types: Optional[List[str]] = None
    livestock_specialization: Optional[List[str]] = None
    base_rate_per_km: Optional[float] = Field(None, gt=0)
    minimum_charge: Optional[float] = Field(None, gt=0)
    max_capacity_animals: Optional[int] = Field(None, gt=0)
    insurance_available: Optional[bool] = None
    insurance_rate_percentage: Optional[float] = Field(None, ge=0, le=100)
    license_number: Optional[str] = None
    verification_documents: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|suspended)$")


class TransportProviderResponse(BaseModel):
    """Response model for transport provider."""
    id: int
    user_id: int
    company_name: str
    contact_person: str
    contact_phone: str
    contact_email: Optional[str]
    service_areas: str  # JSON string
    vehicle_types: str  # JSON string
    livestock_specialization: Optional[str]  # JSON string
    base_rate_per_km: float
    minimum_charge: float
    insurance_available: bool
    insurance_rate_percentage: Optional[float]
    max_capacity_animals: int
    rating: float
    total_ratings: int
    completed_transports: int
    verified: bool
    license_number: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CostEstimateRequest(BaseModel):
    """Request model for transport cost estimate."""
    provider_id: int
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    livestock_type: str = Field(..., pattern="^(cattle|goat|sheep|poultry|buffalo)$")
    livestock_count: int = Field(..., gt=0)
    animal_value: float = Field(..., gt=0)
    insurance_opted: bool = False


class CostEstimateResponse(BaseModel):
    """Response model for transport cost estimate."""
    distance_km: float
    transport_cost: float
    insurance_cost: float
    total_cost: float
    provider_name: str
    estimated_travel_hours: float


class TransportBookingCreate(BaseModel):
    """Request model for creating transport booking."""
    transaction_id: int
    provider_id: int
    requester_id: int
    pickup_address: str = Field(..., min_length=10)
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    delivery_address: str = Field(..., min_length=10)
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    livestock_type: str = Field(..., pattern="^(cattle|goat|sheep|poultry|buffalo)$")
    livestock_count: int = Field(..., gt=0)
    animal_value: float = Field(..., gt=0)
    scheduled_pickup_date: datetime
    insurance_opted: bool = False
    special_instructions: Optional[str] = None


class TransportBookingResponse(BaseModel):
    """Response model for transport booking."""
    id: int
    transaction_id: int
    provider_id: int
    requester_id: int
    pickup_address: str
    pickup_latitude: Optional[float]
    pickup_longitude: Optional[float]
    delivery_address: str
    delivery_latitude: Optional[float]
    delivery_longitude: Optional[float]
    distance_km: float
    livestock_type: str
    livestock_count: int
    animal_value: float
    transport_cost: float
    insurance_opted: bool
    insurance_cost: Optional[float]
    total_cost: float
    scheduled_pickup_date: datetime
    estimated_delivery_date: datetime
    actual_pickup_date: Optional[datetime]
    actual_delivery_date: Optional[datetime]
    status: str
    tracking_updates: Optional[str]  # JSON string
    special_instructions: Optional[str]
    rating: Optional[int]
    review: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    """Request model for updating booking status."""
    status: str = Field(..., pattern="^(pending|confirmed|in_transit|delivered|cancelled)$")
    message: Optional[str] = None
    actual_pickup_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None


class RatingReview(BaseModel):
    """Request model for adding rating and review."""
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None


class CancellationRequest(BaseModel):
    """Request model for cancelling booking."""
    cancellation_reason: str = Field(..., min_length=10)


# Transport Provider Endpoints

@router.post("/providers", response_model=TransportProviderResponse, status_code=status.HTTP_201_CREATED)
async def register_provider(
    provider_data: TransportProviderCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Register a new transport provider."""
    service = TransportService(db)
    
    try:
        provider = await service.register_provider(
            user_id=provider_data.user_id,
            company_name=provider_data.company_name,
            contact_person=provider_data.contact_person,
            contact_phone=provider_data.contact_phone,
            contact_email=provider_data.contact_email,
            service_areas=provider_data.service_areas,
            vehicle_types=provider_data.vehicle_types,
            livestock_specialization=provider_data.livestock_specialization,
            base_rate_per_km=provider_data.base_rate_per_km,
            minimum_charge=provider_data.minimum_charge,
            max_capacity_animals=provider_data.max_capacity_animals,
            insurance_available=provider_data.insurance_available,
            insurance_rate_percentage=provider_data.insurance_rate_percentage,
            license_number=provider_data.license_number,
            verification_documents=provider_data.verification_documents
        )
        return provider
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to register provider: {str(e)}"
        )


@router.get("/providers/{provider_id}", response_model=TransportProviderResponse)
async def get_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get transport provider details."""
    service = TransportService(db)
    provider = await service.get_provider(provider_id)
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transport provider {provider_id} not found"
        )
    
    return provider


@router.get("/providers", response_model=List[TransportProviderResponse])
async def search_providers(
    state: Optional[str] = None,
    district: Optional[str] = None,
    livestock_type: Optional[str] = None,
    min_capacity: Optional[int] = None,
    insurance_required: bool = False,
    verified_only: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    """Search for transport providers based on criteria."""
    service = TransportService(db)
    providers = await service.search_providers(
        state=state,
        district=district,
        livestock_type=livestock_type,
        min_capacity=min_capacity,
        insurance_required=insurance_required,
        verified_only=verified_only
    )
    return providers


@router.put("/providers/{provider_id}", response_model=TransportProviderResponse)
async def update_provider(
    provider_id: int,
    updates: TransportProviderUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update transport provider details."""
    service = TransportService(db)
    
    # Convert to dict and remove None values
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    
    provider = await service.update_provider(provider_id, **update_data)
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transport provider {provider_id} not found"
        )
    
    return provider


# Cost Estimation Endpoint

@router.post("/cost-estimate", response_model=CostEstimateResponse)
async def estimate_transport_cost(
    estimate_request: CostEstimateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Calculate transport cost estimate."""
    service = TransportService(db)
    
    # Get provider
    provider = await service.get_provider(estimate_request.provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transport provider {estimate_request.provider_id} not found"
        )
    
    # Calculate distance
    distance_km = service.calculate_distance(
        estimate_request.pickup_latitude,
        estimate_request.pickup_longitude,
        estimate_request.delivery_latitude,
        estimate_request.delivery_longitude
    )
    
    # Calculate costs
    costs = service.calculate_transport_cost(
        provider,
        distance_km,
        estimate_request.livestock_type,
        estimate_request.livestock_count,
        estimate_request.animal_value,
        estimate_request.insurance_opted
    )
    
    # Estimate travel time
    estimated_travel_hours = distance_km / 50  # Assume 50 km/hour average
    
    return CostEstimateResponse(
        distance_km=distance_km,
        transport_cost=costs['transport_cost'],
        insurance_cost=costs['insurance_cost'],
        total_cost=costs['total_cost'],
        provider_name=provider.company_name,
        estimated_travel_hours=round(estimated_travel_hours, 2)
    )


# Transport Booking Endpoints

@router.post("/bookings", response_model=TransportBookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: TransportBookingCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new transport booking."""
    service = TransportService(db)
    
    try:
        booking = await service.create_booking(
            transaction_id=booking_data.transaction_id,
            provider_id=booking_data.provider_id,
            requester_id=booking_data.requester_id,
            pickup_address=booking_data.pickup_address,
            pickup_latitude=booking_data.pickup_latitude,
            pickup_longitude=booking_data.pickup_longitude,
            delivery_address=booking_data.delivery_address,
            delivery_latitude=booking_data.delivery_latitude,
            delivery_longitude=booking_data.delivery_longitude,
            livestock_type=booking_data.livestock_type,
            livestock_count=booking_data.livestock_count,
            animal_value=booking_data.animal_value,
            scheduled_pickup_date=booking_data.scheduled_pickup_date,
            insurance_opted=booking_data.insurance_opted,
            special_instructions=booking_data.special_instructions
        )
        return booking
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("/tracking/{booking_id}", response_model=TransportBookingResponse)
async def track_booking_by_id_alias(booking_id: int, db: AsyncSession = Depends(get_async_db)):
    """Registry alias for tracking booking by booking_id"""
    return await get_booking(booking_id, db)


@router.get("/tracking/{id}", response_model=TransportBookingResponse)
async def track_booking_alias(id: int, db: AsyncSession = Depends(get_async_db)):
    """Registry alias for tracking booking"""
    return await get_booking(id, db)


@router.get("/bookings/{id}", response_model=TransportBookingResponse)
async def get_booking(
    id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get transport booking details."""
    service = TransportService(db)
    booking = await service.get_booking(id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transport booking {id} not found"
        )
    
    return booking


@router.get("/bookings/transaction/{transaction_id}", response_model=List[TransportBookingResponse])
async def get_transaction_bookings(
    transaction_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get all transport bookings for a transaction."""
    service = TransportService(db)
    bookings = await service.get_bookings_for_transaction(transaction_id)
    return bookings


@router.get("/bookings/provider/{provider_id}", response_model=List[TransportBookingResponse])
async def get_provider_bookings(
    provider_id: int,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get all bookings for a provider."""
    service = TransportService(db)
    bookings = await service.get_provider_bookings(provider_id, status)
    return bookings


@router.put("/bookings/{booking_id}/status", response_model=TransportBookingResponse)
async def update_booking_status(
    booking_id: int,
    status_update: StatusUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update transport booking status."""
    service = TransportService(db)
    
    booking = await service.update_booking_status(
        booking_id,
        status_update.status,
        status_update.message,
        status_update.actual_pickup_date,
        status_update.actual_delivery_date
    )
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transport booking {booking_id} not found"
        )
    
    return booking


@router.post("/bookings/{booking_id}/review", response_model=TransportBookingResponse)
async def add_rating_review(
    booking_id: int,
    rating_review: RatingReview,
    db: AsyncSession = Depends(get_async_db)
):
    """Add rating and review for completed transport."""
    service = TransportService(db)
    
    booking = await service.add_rating_and_review(
        booking_id,
        rating_review.rating,
        rating_review.review
    )
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transport booking {booking_id} not found or not delivered"
        )
    
    return booking


@router.post("/bookings/{booking_id}/cancel", response_model=TransportBookingResponse)
async def cancel_booking(
    booking_id: int,
    cancellation: CancellationRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Cancel a transport booking."""
    service = TransportService(db)
    
    booking = await service.cancel_booking(
        booking_id,
        cancellation.cancellation_reason
    )
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transport booking {booking_id} not found or cannot be cancelled"
        )
    
    return booking
