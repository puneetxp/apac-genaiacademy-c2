from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.farm_plot import FarmPlot
from app.services.farm_plot_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/farm_plot", tags=["islogin-farm_plot"])
service = get_service()

@router.get("/{item_id}", response_model=FarmPlot)
def show_islogin_farm_plot(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Farm_plot not found")
    return record

@router.post("/", response_model=FarmPlot, status_code=201)
def create_islogin_farm_plot(payload: FarmPlot):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=FarmPlot)
def update_islogin_farm_plot(item_id: int, payload: FarmPlot):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Farm_plot not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_farm_plot(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Farm_plot not found")
    return {"success": True}
