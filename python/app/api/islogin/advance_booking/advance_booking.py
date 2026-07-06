from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.advance_booking import AdvanceBooking
from app.services.advance_booking_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/advance_booking", tags=["islogin-advance_booking"])
service = get_service()

@router.get("/{item_id}", response_model=AdvanceBooking)
def show_islogin_advance_booking(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Advance_booking not found")
    return record

@router.post("/", response_model=AdvanceBooking, status_code=201)
def create_islogin_advance_booking(payload: AdvanceBooking):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=AdvanceBooking)
def update_islogin_advance_booking(item_id: int, payload: AdvanceBooking):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Advance_booking not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_advance_booking(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Advance_booking not found")
    return {"success": True}
