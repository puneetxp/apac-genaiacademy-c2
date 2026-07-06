from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QualityVerification(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    booking_id: int
    verification_date: datetime
    verifier_type: str
    quality_grade: str
    quality_metrics: str | None = None
    photos: str | None = None
    passed: bool
    notes: str | None = None
    active_role_id: int
