from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.supply_request import SupplyRequest
from app.services.supply_request_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/supply_request", tags=["islogin-supply_request"])
service = get_service()

@router.get("/{item_id}", response_model=SupplyRequest)
def show_islogin_supply_request(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Supply_request not found")
    return record

@router.post("/", response_model=SupplyRequest, status_code=201)
def create_islogin_supply_request(payload: SupplyRequest):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=SupplyRequest)
def update_islogin_supply_request(item_id: int, payload: SupplyRequest):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Supply_request not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_supply_request(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Supply_request not found")
    return {"success": True}
