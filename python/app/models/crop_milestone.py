from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CropMilestone(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    crop_id: int
    stage: str
    expected_start_date: datetime
    expected_end_date: datetime
    actual_start_date: datetime | None = None
    actual_end_date: datetime | None = None
    status: str | None = None
    progress_percentage: int | None = None
    recommendations: str | None = None
    notes: str | None = None
    alert_sent: bool | None = None
    active_role_id: int
