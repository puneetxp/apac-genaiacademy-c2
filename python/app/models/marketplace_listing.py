from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MarketplaceListing(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    farm_id: int
    farmer_id: int
    crop_type: str
    crop_variety: str | None = None
    expected_harvest_date: datetime
    estimated_quantity: int
    available_quantity: int | None = None
    quality_grade: str | None = None
    location_state: str
    location_district: str
    farmer_contact_phone: str | None = None
    farmer_contact_email: str | None = None
    status: str | None = None
    delivery_latitude: int | None = None
    delivery_longitude: int | None = None
    delivery_pincode: str | None = None
    delivery_village: str | None = None
    delivery_address_line: str | None = None
    embedding: str | None = None
    embedding_cache_key: str | None = None
    price_per_unit: int | None = None
    active_role_id: int
