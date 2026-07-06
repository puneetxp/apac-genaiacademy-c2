from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SlusiMicrowatershedMap(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    state: str
    map_data: str
    file_size_bytes: int | None = None
    ingested_at: datetime
