"""
Livestock Transaction API Endpoints

RESTful API for livestock transaction workflow including:
- Transaction initiation (buyer inquiry)
- Messaging between buyers and sellers
- Status tracking and updates
- Transaction completion and cancellation
- Bulk trading support
- Transaction history and analytics

Compatible with Python 3.14.3, FastAPI 0.115.6
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from app.schemas.livestock_transaction import (
    LivestockTransactionCreate,
    LivestockTransactionUpdate,
    LivestockTransactionResponse,
    LivestockTransactionWithDetails,
    TransactionMessageCreate,
    TransactionStatusUpdate,
    TransactionCancellation,
    TransactionCompletion,
    TransactionSearchFilters,
    TransactionAnalytics,
    BulkTransactionCreate,
    TransactionHistoryResponse,
    TransactionTypeEnum,
    TransactionStatusEnum
)
from app.services.livestock_transaction_service import get_livestock_transaction_service
from app.services.notification_service import get_notification_service


router = APIRouter(prefix="/livestock-transactions", tags=["livestock-transactions"])


@router.post("", response_model=LivestockTransactionResponse, status_code=201)
async def create_transaction(transaction: LivestockTransactionCreate):
    """
    Initiate a new livestock transaction (buyer inquiry)
    
    Creates a transaction in 'inquiry' status and notifies the seller.
    """
    service = get_livestock_transaction_service()
    
    result = service.initiate_transaction(
        listing_id=transaction.listing_id,
        buyer_id=transaction.buyer_id,
        transaction_type=transaction.transaction_type,
        quantity=transaction.quantity,
        buyer_message=transaction.buyer_message,
        buyer_contact_phone=transaction.buyer_contact_phone,
        buyer_contact_email=transaction.buyer_contact_email,
        delivery_required=transaction.delivery_required,
        delivery_address=transaction.delivery_address,
        delivery_latitude=transaction.delivery_latitude,
        delivery_longitude=transaction.delivery_longitude
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Send notification to seller
    try:
        notification_service = get_notification_service()
        notification_service.send_livestock_transaction_notification(
            transaction_id=result.id,
            seller_id=result.seller_id,
            buyer_id=transaction.buyer_id,
            listing_id=transaction.listing_id,
            notification_type='new_inquiry'
        )
    except Exception as e:
        # Log error but don't fail the transaction
        print(f"Failed to send notification: {e}")
    
    return result


@router.post("/bulk", response_model=List[LivestockTransactionResponse], status_code=201)
async def create_bulk_transactions(bulk_request: BulkTransactionCreate):
    """
    Create multiple transactions for bulk trading
    
    Useful when buying multiple animals from the same listing.
    """
    service = get_livestock_transaction_service()
    
    results = service.create_bulk_transactions(
        listing_id=bulk_request.listing_id,
        buyer_id=bulk_request.buyer_id,
        transaction_type=bulk_request.transaction_type,
        quantities=bulk_request.quantities,
        buyer_message=bulk_request.buyer_message,
        buyer_contact_phone=bulk_request.buyer_contact_phone,
        buyer_contact_email=bulk_request.buyer_contact_email,
        delivery_required=bulk_request.delivery_required,
        delivery_address=bulk_request.delivery_address,
        delivery_latitude=bulk_request.delivery_latitude,
        delivery_longitude=bulk_request.delivery_longitude
    )
    
    if not results:
        raise HTTPException(status_code=404, detail="Listing not found or bulk creation failed")
    
    # Send notification to seller for bulk inquiry
    try:
        notification_service = get_notification_service()
        notification_service.send_livestock_transaction_notification(
            transaction_id=results[0].id,
            seller_id=results[0].seller_id,
            buyer_id=bulk_request.buyer_id,
            listing_id=bulk_request.listing_id,
            notification_type='bulk_inquiry',
            extra_data={'total_quantity': sum(bulk_request.quantities)}
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    return results


@router.get("/{id}", response_model=LivestockTransactionWithDetails)
async def get_transaction(id: int):
    """
    Get transaction details with listing and user information
    """
    service = get_livestock_transaction_service()
    
    result = service.get_transaction_with_details(id)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return result


@router.get("", response_model=List[LivestockTransactionResponse])
async def list_transactions(
    listing_id: Optional[int] = Query(None),
    seller_id: Optional[int] = Query(None),
    buyer_id: Optional[int] = Query(None),
    transaction_type: Optional[TransactionTypeEnum] = Query(None),
    status: Optional[TransactionStatusEnum] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    List transactions with optional filters
    """
    service = get_livestock_transaction_service()
    
    filters = {}
    if listing_id:
        filters['listing_id'] = listing_id
    if seller_id:
        filters['seller_id'] = seller_id
    if buyer_id:
        filters['buyer_id'] = buyer_id
    if transaction_type:
        filters['transaction_type'] = transaction_type
    if status:
        filters['status'] = status
    
    if filters:
        results = service.where(filters)
    else:
        results = service.all()
    
    # Apply pagination
    return results[skip:skip + limit]


@router.put("/{id}", response_model=LivestockTransactionResponse)
async def update_transaction(
    id: int,
    update: LivestockTransactionUpdate,
    user_id: int = Query(..., description="User ID (buyer or seller)")
):
    """
    Update transaction details (Agreed price/status)
    """
    service = get_livestock_transaction_service()
    
    result = service.update_status(
        transaction_id=id,
        user_id=user_id,
        new_status=update.status,
        agreed_price=update.agreed_price,
        message=update.message 
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found or user not authorized")
    
    return result


@router.put("/{id}/status", response_model=LivestockTransactionResponse)
async def update_transaction_status(
    id: int,
    status_update: TransactionStatusUpdate,
    user_id: int = Query(..., description="User ID (buyer or seller)")
):
    """
    Update transaction status
    
    Status flow: inquiry → negotiation → agreed → completed
    Can also move to cancelled from any status.
    """
    service = get_livestock_transaction_service()
    
    result = service.update_status(
        transaction_id=id,
        user_id=user_id,
        new_status=status_update.status,
        agreed_price=status_update.agreed_price,
        message=status_update.message
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found or user not authorized"
        )
    
    # Send notification about status change
    try:
        notification_service = get_notification_service()
        notification_service.send_livestock_transaction_notification(
            transaction_id=transaction_id,
            seller_id=result.seller_id,
            buyer_id=result.buyer_id,
            listing_id=result.listing_id,
            notification_type='status_update',
            extra_data={'new_status': status_update.status}
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    return result


@router.post("/{transaction_id}/seller-response", response_model=LivestockTransactionResponse)
async def add_seller_response(
    transaction_id: int,
    seller_id: int = Query(..., description="Seller ID"),
    message: str = Query(..., min_length=10, max_length=2000),
    new_status: Optional[TransactionStatusEnum] = Query(None)
):
    """
    Add seller response message to a transaction
    
    Optionally update status (e.g., from inquiry to negotiation).
    """
    service = get_livestock_transaction_service()
    
    result = service.add_seller_response(
        transaction_id=transaction_id,
        seller_id=seller_id,
        message=message,
        new_status=new_status
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found or seller not authorized"
        )
    
    # Notify buyer of seller response
    try:
        notification_service = get_notification_service()
        notification_service.send_livestock_transaction_notification(
            transaction_id=transaction_id,
            seller_id=result.seller_id,
            buyer_id=result.buyer_id,
            listing_id=result.listing_id,
            notification_type='seller_response'
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    return result


@router.post("/{transaction_id}/buyer-message", response_model=LivestockTransactionResponse)
async def add_buyer_message(
    transaction_id: int,
    buyer_id: int = Query(..., description="Buyer ID"),
    message: str = Query(..., min_length=10, max_length=2000)
):
    """
    Add buyer message to a transaction
    """
    service = get_livestock_transaction_service()
    
    result = service.add_buyer_message(
        transaction_id=transaction_id,
        buyer_id=buyer_id,
        message=message
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found or buyer not authorized"
        )
    
    # Notify seller of buyer message
    try:
        notification_service = get_notification_service()
        notification_service.send_livestock_transaction_notification(
            transaction_id=transaction_id,
            seller_id=result.seller_id,
            buyer_id=result.buyer_id,
            listing_id=result.listing_id,
            notification_type='buyer_message'
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    return result


@router.post("/{transaction_id}/complete", response_model=LivestockTransactionResponse)
async def complete_transaction(
    transaction_id: int,
    completion: TransactionCompletion,
    seller_id: int = Query(..., description="Seller ID")
):
    """
    Complete a transaction (seller confirms delivery/handover)
    
    Activates 7-day health guarantee period.
    """
    service = get_livestock_transaction_service()
    
    result = service.complete_transaction(
        transaction_id=transaction_id,
        seller_id=seller_id,
        notes=completion.notes
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found, seller not authorized, or transaction not in 'agreed' status"
        )
    
    # Notify buyer of completion
    try:
        notification_service = get_notification_service()
        notification_service.send_livestock_transaction_notification(
            transaction_id=transaction_id,
            seller_id=result.seller_id,
            buyer_id=result.buyer_id,
            listing_id=result.listing_id,
            notification_type='completed',
            extra_data={'health_guarantee_expires': result.health_guarantee_expires.isoformat()}
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    return result


@router.post("/{id}/cancel", response_model=LivestockTransactionResponse)
async def cancel_transaction_alias(
    id: int,
    cancellation: TransactionCancellation,
    user_id: int = Query(..., description="User ID (buyer or seller)")
):
    """Registry alias for cancel transaction"""
    return await cancel_transaction(id, cancellation, user_id)


@router.post("/{transaction_id}/cancel", response_model=LivestockTransactionResponse)
async def cancel_transaction(
    transaction_id: int,
    cancellation: TransactionCancellation,
    user_id: int = Query(..., description="User ID (buyer or seller)")
):
    """
    Cancel a transaction
    
    Can be done by either buyer or seller.
    """
    service = get_livestock_transaction_service()
    
    result = service.cancel_transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        cancellation_reason=cancellation.cancellation_reason
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found or user not authorized"
        )
    
    # Notify other party of cancellation
    try:
        notification_service = get_notification_service()
        notification_service.send_livestock_transaction_notification(
            transaction_id=transaction_id,
            seller_id=result.seller_id,
            buyer_id=result.buyer_id,
            listing_id=result.listing_id,
            notification_type='cancelled',
            extra_data={'cancellation_reason': cancellation.cancellation_reason}
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    return result


@router.get("/user/{user_id}/history", response_model=TransactionHistoryResponse)
async def get_user_transaction_history(
    user_id: int,
    role: str = Query(..., pattern="^(buyer|seller)$"),
    status: Optional[TransactionStatusEnum] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get transaction history for a user (as buyer or seller)
    """
    service = get_livestock_transaction_service()
    
    transactions = service.get_user_transactions(
        user_id=user_id,
        role=role,
        status=status,
        skip=skip,
        limit=limit
    )
    
    # Calculate summary statistics
    total_count = len(transactions)
    total_value = sum(float(t.agreed_price or 0) for t in transactions)
    completed_count = sum(1 for t in transactions if t.status == 'completed')
    cancelled_count = sum(1 for t in transactions if t.status == 'cancelled')
    active_count = sum(1 for t in transactions if t.status in ['inquiry', 'negotiation', 'agreed'])
    
    return {
        'user_id': user_id,
        'role': role,
        'transactions': transactions,
        'total_count': total_count,
        'total_value': total_value,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'active_count': active_count
    }


@router.get("/analytics", response_model=TransactionAnalytics)
async def get_transaction_analytics(
    user_id: Optional[int] = Query(None),
    role: Optional[str] = Query(None, pattern="^(buyer|seller)$")
):
    """
    Get transaction analytics
    
    If user_id and role provided, returns analytics for that user.
    Otherwise returns platform-wide analytics.
    """
    service = get_livestock_transaction_service()
    
    analytics = service.get_transaction_analytics(user_id=user_id, role=role)
    
    return analytics
