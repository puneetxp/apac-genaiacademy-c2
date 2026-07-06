from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime


class Role(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    name: str
