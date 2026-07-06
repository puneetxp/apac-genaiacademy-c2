from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdvanceBooking(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    listing_id: int
    buyer_id: int
    farmer_id: int
    quantity_booked: int
    price_per_unit: int
    total_amount: int
    advance_payment_percent: int
    advance_payment_amount: int
    booking_date: datetime
    expected_delivery_date: datetime
    status: str
    quality_standards: str | None = None
    contract_terms: str | None = None
    active_role_id: int
