from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.buyer_interest import BuyerInterest
from app.services.buyer_interest_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/buyer_interest", tags=["islogin-buyer_interest"])
service = get_service()

@router.get("/{item_id}", response_model=BuyerInterest)
def show_islogin_buyer_interest(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Buyer_interest not found")
    return record

@router.post("/", response_model=BuyerInterest, status_code=201)
def create_islogin_buyer_interest(payload: BuyerInterest):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=BuyerInterest)
def update_islogin_buyer_interest(item_id: int, payload: BuyerInterest):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Buyer_interest not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_buyer_interest(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Buyer_interest not found")
    return {"success": True}
