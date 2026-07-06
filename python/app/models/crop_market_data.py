from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CropMarketData(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    crop_name: str
    state: str
    district: str | None = None
    price_per_kg: int
    date: datetime
    season: str
    yoy_growth: int | None = None
    demand_level: str | None = None
