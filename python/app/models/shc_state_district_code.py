from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime


class ShcStateDistrictCode(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    state_name: str
    state_code: int
    district_name: str
    district_code: int
