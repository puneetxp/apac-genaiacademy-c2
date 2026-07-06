from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.payment_milestone import PaymentMilestone
from app.services.payment_milestone_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/payment-milestone", tags=["islogin-payment-milestone"])
service = get_service()

@router.get("/{item_id}", response_model=PaymentMilestone)
def show_islogin_payment-milestone(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Payment_milestone not found")
    return record

@router.post("/", response_model=PaymentMilestone, status_code=201)
def create_islogin_payment-milestone(payload: PaymentMilestone):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=PaymentMilestone)
def update_islogin_payment-milestone(item_id: int, payload: PaymentMilestone):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Payment_milestone not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_payment-milestone(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Payment_milestone not found")
    return {"success": True}
