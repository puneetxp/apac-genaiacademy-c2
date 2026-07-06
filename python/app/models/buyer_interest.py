from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BuyerInterest(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    listing_id: int
    buyer_name: str
    buyer_phone: str
    buyer_email: str | None = None
    buyer_type: str
    interested_quantity: int
    message: str | None = None
    status: str | None = None
    delivery_latitude: int | None = None
    delivery_longitude: int | None = None
    delivery_pincode: str | None = None
    delivery_state: str | None = None
    delivery_district: str | None = None
    delivery_village: str | None = None
    delivery_address_line: str | None = None
    active_role_id: int
