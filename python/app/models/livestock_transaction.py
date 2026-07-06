from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LivestockTransaction(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    listing_id: int
    seller_id: int
    buyer_id: int
    transaction_type: str
    quantity: int
    agreed_price: int
    status: str | None = None
    buyer_message: str | None = None
    seller_response: str | None = None
    buyer_contact_phone: str | None = None
    buyer_contact_email: str | None = None
    delivery_required: bool | None = None
    delivery_address: str | None = None
    delivery_latitude: int | None = None
    delivery_longitude: int | None = None
    health_guarantee_days: int | None = None
    health_guarantee_expires: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    notes: str | None = None
    active_role_id: int
