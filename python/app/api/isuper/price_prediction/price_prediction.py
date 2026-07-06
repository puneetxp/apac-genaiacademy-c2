from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.price_prediction import PricePrediction
from app.services.price_prediction_service import get_service
from typing import List, Dict


router = APIRouter(prefix="/isuper/price_prediction", tags=["isuper-price_prediction"])
service = get_service()

@router.get("/", response_model=List[PricePrediction])
def list_isuper_price_prediction():
    return service.all()

@router.get("/{item_id}", response_model=PricePrediction)
def show_isuper_price_prediction(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Price_prediction not found")
    return record

@router.post("/", response_model=PricePrediction, status_code=201)
def create_isuper_price_prediction(payload: PricePrediction):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=PricePrediction)
def update_isuper_price_prediction(item_id: int, payload: PricePrediction):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Price_prediction not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_isuper_price_prediction(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Price_prediction not found")
    return {"success": True}
