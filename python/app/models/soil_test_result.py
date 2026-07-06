from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SoilTestResult(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    farm_id: int
    plot_id: int | None = None
    test_date: datetime
    lab_name: str | None = None
    lab_reference_number: str | None = None
    nitrogen_kg_per_ha: int | None = None
    phosphorus_kg_per_ha: int | None = None
    potassium_kg_per_ha: int | None = None
    ph_level: int | None = None
    organic_carbon_percent: int | None = None
    organic_matter_percent: int | None = None
    electrical_conductivity: int | None = None
    sulfur_ppm: int | None = None
    zinc_ppm: int | None = None
    iron_ppm: int | None = None
    manganese_ppm: int | None = None
    copper_ppm: int | None = None
    boron_ppm: int | None = None
    soil_health_score: int | None = None
    test_method: str | None = None
    raw_data_json: str | None = None
    recommendations: str | None = None
    notes: str | None = None
    active_role_id: int
    active_role_id: int
