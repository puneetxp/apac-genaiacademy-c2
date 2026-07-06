from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FarmPlot(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    farm_id: int
    plot_name: str
    area: int
    soil_type: str
    irrigation_type: str
    state: str
    district: str
    previous_crops: str | None = None
    investment_capacity: int | None = None
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
    active_role_id: int
