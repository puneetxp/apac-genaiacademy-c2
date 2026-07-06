from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WeatherAlert(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    farm_id: int | None = None
    state: str
    district: str | None = None
    alert_type: str
    severity: str
    message: str
    recommendation: str | None = None
    valid_from: datetime
    valid_until: datetime
    is_active: bool | None = None
    active_role_id: int
