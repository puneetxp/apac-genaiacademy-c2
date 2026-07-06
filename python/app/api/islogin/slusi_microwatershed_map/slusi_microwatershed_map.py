from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.slusi_microwatershed_map import SlusiMicrowatershedMap
from app.services.slusi_microwatershed_map_service import get_service


router = APIRouter(prefix="/islogin/slusi_microwatershed_map", tags=["islogin-slusi_microwatershed_map"])
service = get_service()

@router.get("/{item_id}", response_model=SlusiMicrowatershedMap)
def show_islogin_slusi_microwatershed_map(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Slusi_microwatershed_map not found")
    return record
