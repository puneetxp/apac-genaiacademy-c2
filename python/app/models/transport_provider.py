from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransportProvider(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    user_id: int
    company_name: str
    contact_person: str
    contact_phone: str
    contact_email: str | None = None
    service_areas: str
    vehicle_types: str
    livestock_specialization: str | None = None
    base_rate_per_km: int
    minimum_charge: int
    insurance_available: bool | None = None
    insurance_rate_percentage: int | None = None
    max_capacity_animals: int
    rating: int | None = None
    total_ratings: int | None = None
    completed_transports: int | None = None
    verified: bool | None = None
    verification_documents: str | None = None
    license_number: str | None = None
    status: str | None = None
    active_role_id: int
