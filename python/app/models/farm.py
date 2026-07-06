from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


class Farm(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    name: str
    description: str | None = None
    location_state: str
    location_district: str
    location_block: str | None = None
    location_village: str | None = None
    latitude: int | None = None
    longitude: int | None = None
    total_area: int
    cultivable_area: int | None = None
    area_unit: str | None = None
    primary_soil_type: str | None = None
    soil_ph: int | None = None
    soil_characteristics: Dict[str, Any] | None = None
    irrigation_type: str | None = None
    water_availability: str | None = None
    previous_crops: str | None = None
    farming_experience_years: int | None = None
    investment_capacity_per_acre: int | None = None
    farm_profile_embedding: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    nitrogen: int | None = None
    phosphorus: int | None = None
    potassium: int | None = None
    ph_level: int | None = None
    organic_carbon: int | None = None
    electrical_conductivity: int | None = None
    sulfur: int | None = None
    zinc: int | None = None
    iron: int | None = None
    boron: int | None = None
    copper: int | None = None
    manganese: int | None = None
    soil_depth_class: str | None = None
    slope_class: str | None = None
    erosion_class: str | None = None
    soil_texture_class: str | None = None
    land_capability_class: str | None = None
    land_irrigability_class: str | None = None
    hydrological_soil_group: str | None = None
    shc_data_source: str | None = None
    shc_fetched_at: datetime | None = None
    shc_partial_data: bool | None = None
    shc_unavailable_styles: str | None = None
    user_id: int
    owner_id: int
