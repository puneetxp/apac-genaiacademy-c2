from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.livestock_listing import LivestockListing
from app.services.livestock_listing_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/livestock_listing", tags=["islogin-livestock_listing"])
service = get_service()

@router.get("/{item_id}", response_model=LivestockListing)
def show_islogin_livestock_listing(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Livestock_listing not found")
    return record

@router.post("/", response_model=LivestockListing, status_code=201)
def create_islogin_livestock_listing(payload: LivestockListing):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=LivestockListing)
def update_islogin_livestock_listing(item_id: int, payload: LivestockListing):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Livestock_listing not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_livestock_listing(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Livestock_listing not found")
    return {"success": True}
