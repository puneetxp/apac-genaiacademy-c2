from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.marketplace_listing import MarketplaceListing
from app.services.marketplace_listing_service import get_service
from typing import List, Dict


router = APIRouter(prefix="/isuper/marketplace-listing", tags=["isuper-marketplace-listing"])
service = get_service()

@router.get("/", response_model=List[MarketplaceListing])
def list_isuper_marketplace-listing():
    return service.all()

@router.get("/{item_id}", response_model=MarketplaceListing)
def show_isuper_marketplace-listing(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Marketplace_listing not found")
    return record

@router.post("/", response_model=MarketplaceListing, status_code=201)
def create_isuper_marketplace-listing(payload: MarketplaceListing):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=MarketplaceListing)
def update_isuper_marketplace-listing(item_id: int, payload: MarketplaceListing):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Marketplace_listing not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_isuper_marketplace-listing(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Marketplace_listing not found")
    return {"success": True}
