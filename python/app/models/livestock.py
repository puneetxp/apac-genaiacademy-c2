from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Livestock(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    farm_id: int
    farmer_id: int
    species: str
    breed: str
    quantity: int
    purchase_price: int
    purchase_date: datetime
    purpose: str
    expected_roi: int | None = None
    break_even_date: datetime | None = None
    status: str | None = None
    latitude: int | None = None
    longitude: int | None = None
    pincode: str | None = None
    state: str | None = None
    district: str | None = None
    village: str | None = None
    address_line: str | None = None
    active_role_id: int
