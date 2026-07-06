from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.shc_state_district_code import ShcStateDistrictCode
from app.services.shc_state_district_code_service import get_service


router = APIRouter(prefix="/islogin/shc_state_district_code", tags=["islogin-shc_state_district_code"])
service = get_service()

@router.get("/{item_id}", response_model=ShcStateDistrictCode)
def show_islogin_shc_state_district_code(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Shc_state_district_code not found")
    return record
