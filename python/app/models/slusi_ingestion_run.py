from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SlusiIngestionRun(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    lcc_records_ingested: int | None = None
    maps_ingested: int | None = None
    error_message: str | None = None
