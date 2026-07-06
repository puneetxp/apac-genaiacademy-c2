from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LivestockListing(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    livestock_id: int
    farmer_id: int
    title: str
    description: str | None = None
    species: str
    breed: str
    age_years: int | None = None
    age_months: int | None = None
    gender: str
    quantity: int
    purpose: str
    price: int
    price_negotiable: bool | None = None
    weight_kg: int | None = None
    health_status: str | None = None
    vaccination_status: str | None = None
    last_vaccination_date: datetime | None = None
    milk_production_liters: int | None = None
    breeding_certified: bool | None = None
    breeding_certification_number: str | None = None
    genetic_lineage: str | None = None
    photos: str | None = None
    videos: str | None = None
    location_state: str
    location_district: str
    location_village: str | None = None
    latitude: int | None = None
    longitude: int | None = None
    pincode: str | None = None
    address_line: str | None = None
    farmer_contact_phone: str | None = None
    farmer_contact_email: str | None = None
    status: str | None = None
    views_count: int | None = None
    interest_count: int | None = None
    inquiry_count: int | None = None
    featured: bool | None = None
    featured_until: datetime | None = None
    active_role_id: int
