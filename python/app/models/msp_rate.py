from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class MspRate(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    crop_name: str
    year: int
    season: str
    msp_per_quintal: Decimal
    msp_per_kg: Optional[Decimal] = None
    increase_over_previous: Optional[Decimal] = None
    cost_of_production: Optional[Decimal] = None
    return_over_cost_percent: Optional[Decimal] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True
