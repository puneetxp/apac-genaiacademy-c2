from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MarketPrice(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    listing_id: int | None = None
    booking_id: int | None = None
    transaction_id: int | None = None
    item_type: str
    item_name: str
    variety: str | None = None
    price_per_unit: int
    quantity: int
    total_value: int
    quality_grade: str | None = None
    quality_premium_percent: int | None = None
    state: str
    district: str
    transaction_date: datetime
    season: str | None = None
    source: str
    active_role_id: int
