from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FertilizerApplication(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    farm_id: int
    plot_id: int | None = None
    crop_id: int | None = None
    application_date: datetime
    fertilizer_type: str
    category: str
    quantity_kg: int
    quantity_per_hectare: int | None = None
    area_applied_hectares: int | None = None
    nitrogen_kg: int | None = None
    phosphorus_kg: int | None = None
    potassium_kg: int | None = None
    cost_total: int | None = None
    cost_per_kg: int | None = None
    cost_per_hectare: int | None = None
    application_method: str | None = None
    growth_stage: str | None = None
    days_after_planting: int | None = None
    soil_test_before_id: int | None = None
    soil_test_after_id: int | None = None
    effectiveness_score: int | None = None
    soil_response_notes: str | None = None
    weather_conditions: str | None = None
    temperature_celsius: int | None = None
    rainfall_mm_24h: int | None = None
    recommended_by: str | None = None
    recommendation_id: str | None = None
    notes: str | None = None
    active_role_id: int
