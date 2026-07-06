from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SupplyMatch(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    request_id: int
    listing_id: int | None = None
    farmer_id: int
    matched_quantity: int
    match_score: int | None = None
    price_offered: int | None = None
    status: str
    match_explanation: str | None = None
    is_aggregated: bool
    aggregation_group_id: str | None = None
    farmer_confirmation_status: str
    farmer_confirmed_at: datetime | None = None
    buyer_accepted_at: datetime | None = None
    delivery_status: str
    delivery_notes: str | None = None
    active_role_id: int
    active_role_id: int
    active_role_id: int
