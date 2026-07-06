from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class SoilMoistureData(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    state: str
    district: str
    date: date
    year: int
    month: str
    moisture_level: Decimal
    agency_name: Optional[str] = None

    class Config:
        from_attributes = True
