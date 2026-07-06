from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.annual_strategy import AnnualStrategy
from app.services.annual_strategy_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/annual_strategy", tags=["islogin-annual_strategy"])
service = get_service()

@router.get("/{item_id}", response_model=AnnualStrategy)
def show_islogin_annual_strategy(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Annual_strategy not found")
    return record

@router.post("/", response_model=AnnualStrategy, status_code=201)
def create_islogin_annual_strategy(payload: AnnualStrategy):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=AnnualStrategy)
def update_islogin_annual_strategy(item_id: int, payload: AnnualStrategy):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Annual_strategy not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_annual_strategy(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Annual_strategy not found")
    return {"success": True}
