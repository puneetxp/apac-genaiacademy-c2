from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransportBooking(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    transaction_id: int
    provider_id: int
    requester_id: int
    pickup_address: str
    pickup_latitude: int | None = None
    pickup_longitude: int | None = None
    delivery_address: str
    delivery_latitude: int | None = None
    delivery_longitude: int | None = None
    distance_km: int
    livestock_type: str
    livestock_count: int
    animal_value: int
    transport_cost: int
    insurance_opted: bool | None = None
    insurance_cost: int | None = None
    total_cost: int
    scheduled_pickup_date: datetime
    estimated_delivery_date: datetime
    actual_pickup_date: datetime | None = None
    actual_delivery_date: datetime | None = None
    status: str | None = None
    tracking_updates: str | None = None
    special_instructions: str | None = None
    rating: int | None = None
    review: str | None = None
    reviewed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    active_role_id: int
    active_role_id: int
    active_role_id: int
