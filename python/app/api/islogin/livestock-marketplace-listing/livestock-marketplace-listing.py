from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.livestock_marketplace_listing import LivestockMarketplaceListing
from app.services.livestock_marketplace_listing_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/livestock-marketplace-listing", tags=["islogin-livestock-marketplace-listing"])
service = get_service()

@router.get("/{item_id}", response_model=LivestockMarketplaceListing)
def show_islogin_livestock-marketplace-listing(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Livestock_marketplace_listing not found")
    return record

@router.post("/", response_model=LivestockMarketplaceListing, status_code=201)
def create_islogin_livestock-marketplace-listing(payload: LivestockMarketplaceListing):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=LivestockMarketplaceListing)
def update_islogin_livestock-marketplace-listing(item_id: int, payload: LivestockMarketplaceListing):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Livestock_marketplace_listing not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_livestock-marketplace-listing(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Livestock_marketplace_listing not found")
    return {"success": True}
