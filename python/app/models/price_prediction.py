from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PricePrediction(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    item_type: str
    item_name: str
    variety: str | None = None
    state: str
    district: str | None = None
    prediction_date: datetime
    target_date: datetime
    predicted_price: int
    confidence_score: int
    price_range_min: int | None = None
    price_range_max: int | None = None
    trend: str | None = None
    demand_forecast: str | None = None
    supply_forecast: str | None = None
    season: str | None = None
    model_version: str | None = None
    factors: str | None = None
