from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.price_prediction import PricePrediction
from app.services.price_prediction_service import get_service


router = APIRouter(prefix="/islogin/price_prediction", tags=["islogin-price_prediction"])
service = get_service()

@router.get("/{item_id}", response_model=PricePrediction)
def show_islogin_price_prediction(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Price_prediction not found")
    return record
