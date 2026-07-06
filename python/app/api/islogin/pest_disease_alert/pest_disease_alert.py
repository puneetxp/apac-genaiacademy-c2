from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.pest_disease_alert import PestDiseaseAlert
from app.services.pest_disease_alert_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/pest_disease_alert", tags=["islogin-pest_disease_alert"])
service = get_service()

@router.get("/{item_id}", response_model=PestDiseaseAlert)
def show_islogin_pest_disease_alert(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Pest_disease_alert not found")
    return record

@router.post("/", response_model=PestDiseaseAlert, status_code=201)
def create_islogin_pest_disease_alert(payload: PestDiseaseAlert):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=PestDiseaseAlert)
def update_islogin_pest_disease_alert(item_id: int, payload: PestDiseaseAlert):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Pest_disease_alert not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_pest_disease_alert(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Pest_disease_alert not found")
    return {"success": True}
