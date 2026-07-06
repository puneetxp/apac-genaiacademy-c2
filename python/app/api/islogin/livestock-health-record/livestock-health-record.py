from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.livestock_health_record import LivestockHealthRecord
from app.services.livestock_health_record_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/livestock-health-record", tags=["islogin-livestock-health-record"])
service = get_service()

@router.get("/{item_id}", response_model=LivestockHealthRecord)
def show_islogin_livestock-health-record(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Livestock_health_record not found")
    return record

@router.post("/", response_model=LivestockHealthRecord, status_code=201)
def create_islogin_livestock-health-record(payload: LivestockHealthRecord):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=LivestockHealthRecord)
def update_islogin_livestock-health-record(item_id: int, payload: LivestockHealthRecord):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Livestock_health_record not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_livestock-health-record(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Livestock_health_record not found")
    return {"success": True}
