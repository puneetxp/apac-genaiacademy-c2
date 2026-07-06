from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LivestockHealthRecord(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    livestock_id: int
    record_type: str
    record_date: datetime
    description: str
    veterinarian_name: str | None = None
    cost: int | None = None
    next_due_date: datetime | None = None
    notes: str | None = None
    active_role_id: int
