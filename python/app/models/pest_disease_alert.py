from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PestDiseaseAlert(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    crop_id: int
    farm_id: int
    pest_disease_name: str
    alert_type: str
    severity: str
    description: str
    crop_stage: str
    weather_conditions: str | None = None
    organic_recommendations: str | None = None
    chemical_recommendations: str | None = None
    prevention_measures: str | None = None
    timing_instructions: str | None = None
    notification_sent: bool | None = None
    notification_sent_at: datetime | None = None
    is_resolved: bool | None = None
    resolved_at: datetime | None = None
    active_role_id: int
