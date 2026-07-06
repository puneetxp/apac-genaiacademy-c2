from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SupplyRequest(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    buyer_id: int
    crop_type: str
    quantity_needed: int
    quality_requirements: str | None = None
    delivery_date_start: datetime
    delivery_date_end: datetime
    max_price_per_unit: int | None = None
    recurring: bool
    recurrence_pattern: str | None = None
    is_emergency: bool
    status: str
    delivery_address: str | None = None
    delivery_latitude: int | None = None
    delivery_longitude: int | None = None
    delivery_pincode: str | None = None
    delivery_state: str | None = None
    delivery_district: str | None = None
    notes: str | None = None
    embedding: str | None = None
    embedding_cache_key: str | None = None
    active_role_id: int
