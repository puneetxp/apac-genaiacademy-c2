from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.pest_disease_data import PestDiseaseData
from app.services.pest_disease_data_service import get_service


router = APIRouter(prefix="/islogin/pest_disease_data", tags=["islogin-pest_disease_data"])
service = get_service()

@router.get("/{item_id}", response_model=PestDiseaseData)
def show_islogin_pest_disease_data(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Pest_disease_data not found")
    return record
