from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LivestockMarketplaceListing(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    livestock_id: int
    farmer_id: int
    listing_type: str
    asking_price: int
    current_age_months: int
    current_weight_kg: int | None = None
    milk_production_liters_per_day: int | None = None
    breeding_history: str | None = None
    health_status: str | None = None
    vaccination_status: str | None = None
    total_investment: int
    total_revenue: int | None = None
    current_roi_percentage: int | None = None
    break_even_achieved: bool | None = None
    break_even_date: datetime | None = None
    projected_annual_profit: int | None = None
    location_state: str
    location_district: str
    farmer_contact_phone: str
    farmer_contact_email: str | None = None
    listing_status: str | None = None
    views_count: int | None = None
    bedrock_analysis: str | None = None
    active_role_id: int
