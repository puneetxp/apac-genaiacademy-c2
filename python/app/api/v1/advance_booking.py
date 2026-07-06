"""
Advance Booking API endpoints for pre-harvest booking system
Implements Task 27.2: Build advance booking system
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Dict, Any, Optional, Annotated
from decimal import Decimal
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import DB, CurrentUser
from app.services.advance_booking_service import get_advance_booking_service

router = APIRouter(prefix="/advance-bookings", tags=["Advance Booking"])


# Request/Response Schemas
class QualityStandards(BaseModel):
    """Quality standards specification"""
    grade: str = Field(..., description="Quality grade (A/B/C)")
    size: Optional[str] = Field(None, description="Size requirements")
    moisture_content: Optional[float] = Field(None, description="Maximum moisture content %")
    organic_certified: bool = Field(default=False, description="Organic certification required")
    defects_tolerance: Optional[float] = Field(None, description="Maximum defects tolerance %")


class ContractTerms(BaseModel):
    """Contract terms and conditions"""
    delivery_terms: str = Field(..., description="Delivery terms (FOB, CIF, etc.)")
    penalty_late_delivery: Optional[Decimal] = Field(None, description="Penalty for late delivery")
    penalty_quality_failure: Optional[Decimal] = Field(None, description="Penalty for quality failure")
    cancellation_terms: Optional[str] = Field(None, description="Cancellation policy")


class CreateAdvanceBookingRequest(BaseModel):
    """Request to create advance booking"""
    listing_id: str = Field(..., description="Marketplace listing UUID")
    buyer_id: str = Field(..., description="Buyer user UUID")
    quantity: Decimal = Field(..., description="Quantity to book (kg/quintal)", gt=0)
    price_per_unit: Decimal = Field(..., description="Price per unit", gt=0)
    advance_payment_percent: int = Field(
        default=20, 
        ge=20, 
        le=50, 
        description="Advance payment % (20-50%)"
    )
    expected_delivery_date: date = Field(..., description="Expected delivery date")
    quality_requirement: QualityStandards = Field(..., description="Quality requirements")
    contract_terms: ContractTerms = Field(..., description="Contract terms")


class ConfirmBookingRequest(BaseModel):
    """Request to confirm booking"""
    booking_id: str = Field(..., description="Booking UUID")


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_advance_booking(
    request: CreateAdvanceBookingRequest,
    db: DB
):
    """
    Create pre-harvest booking with quality standards and contract terms
    
    Task 27.2: Build advance booking system
    - Accept booking details (listing_id, buyer_id, quantity, advance_payment, quality_requirement)
    - Calculate advance payment amount based on percentage and quantity
    - Store booking with status "pending"
    - Validates: Requirements AC7 (Smart Land Plot Management)
    """
    try:
        service = get_advance_booking_service(db)
        
        # Create booking
        booking = service.create_booking(
            listing_id=request.listing_id,
            buyer_id=request.buyer_id,
            quantity_booked=request.quantity,
            price_per_unit=request.price_per_unit,
            advance_payment_percent=request.advance_payment_percent,
            expected_delivery_date=request.expected_delivery_date,
            quality_standards=request.quality_requirement.dict(),
            contract_terms=request.contract_terms.dict()
        )
        
        return {
            'success': True,
            'message': 'Advance booking created successfully',
            'booking': booking
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create advance booking: {str(e)}"
        )


@router.post("/{id}/confirm", response_model=Dict[str, Any])
async def confirm_booking(
    id: str,
    db: DB
):
    """
    Confirm booking and update listing available quantity
    
    Task 27.2: Build advance booking system
    - Update listing available quantity when booking confirmed
    - Validates: Requirements AC7 (Smart Land Plot Management)
    """
    try:
        service = get_advance_booking_service(db)
        
        # Confirm booking (this updates the listing's available quantity)
        result = service.confirm_booking(id)
        
        return {
            'success': True,
            'message': 'Booking confirmed successfully',
            'booking': result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm booking: {str(e)}"
        )


@router.post("/{id}/cancel", response_model=Dict[str, Any])
async def cancel_booking(
    id: str,
    db: DB
):
    """
    Cancel booking and restore listing available quantity
    
    Task 27.2: Build advance booking system
    - Restore listing available quantity when booking cancelled
    - Validates: Requirements AC7 (Smart Land Plot Management)
    """
    try:
        service = get_advance_booking_service(db)
        
        # Cancel booking (this restores the listing's available quantity)
        result = service.cancel_booking(id)
        
        return {
            'success': True,
            'message': 'Booking cancelled successfully',
            'booking': result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel booking: {str(e)}"
        )


@router.get("/{id}", response_model=Dict[str, Any])
async def get_booking(
    id: str,
    db: DB
):
    """Get booking details by ID"""
    try:
        service = get_advance_booking_service(db)
        booking = service.get_booking(id)
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        return {
            'success': True,
            'booking': booking
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get booking: {str(e)}"
        )


@router.post("/{id}/complete", response_model=Dict[str, Any])
async def complete_booking(
    id: str,
    db: DB,
    current_user: CurrentUser
):
    """Mark booking as complete (handover occurred)"""
    try:
        service = get_advance_booking_service(db)
        result = service.complete_booking(id)
        return {"success": True, "booking": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{id}/quality-verify", response_model=Dict[str, Any])
async def quality_verify(
    id: str,
    db: DB,
    current_user: CurrentUser
):
    """Verify quality grade of the crop before final payment"""
    try:
        service = get_advance_booking_service(db)
        result = service.verify_quality(id)
        return {"success": True, "booking": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
async def list_bookings(
    db: DB,
    buyer_id: Optional[str] = None,
    farmer_id: Optional[str] = None,
    status: Optional[str] = None
):
    """List bookings with optional filters"""
    try:
        service = get_advance_booking_service(db)
        bookings = service.list_bookings(
            buyer_id=buyer_id,
            farmer_id=farmer_id,
            status=status
        )
        
        return {
            'success': True,
            'count': len(bookings),
            'bookings': bookings
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list bookings: {str(e)}"
        )
