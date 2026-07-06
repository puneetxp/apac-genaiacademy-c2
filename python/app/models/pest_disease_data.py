from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PestDiseaseData(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    name: str
    type: str
    scientific_name: str | None = None
    description: str
    affected_crops: str | None = None
    risk_stages: str | None = None
    temperature_min: int | None = None
    temperature_max: int | None = None
    humidity_min: int | None = None
    humidity_max: int | None = None
    rainfall_min: int | None = None
    severity: str
    organic_treatments: str | None = None
    chemical_treatments: str | None = None
    prevention_measures: str | None = None
    timing_instructions: str | None = None
    data_source: str | None = None
    last_updated: datetime | None = None
