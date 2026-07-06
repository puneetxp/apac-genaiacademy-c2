from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.fertilizer_application import FertilizerApplication
from app.services.fertilizer_application_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/fertilizer_application", tags=["islogin-fertilizer_application"])
service = get_service()

@router.get("/{item_id}", response_model=FertilizerApplication)
def show_islogin_fertilizer_application(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Fertilizer_application not found")
    return record

@router.post("/", response_model=FertilizerApplication, status_code=201)
def create_islogin_fertilizer_application(payload: FertilizerApplication):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=FertilizerApplication)
def update_islogin_fertilizer_application(item_id: int, payload: FertilizerApplication):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Fertilizer_application not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_fertilizer_application(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Fertilizer_application not found")
    return {"success": True}
