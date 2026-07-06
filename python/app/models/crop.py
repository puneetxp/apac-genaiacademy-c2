from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Crop(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    farm_plot_id: int
    strategy_id: int | None = None
    crop_name: str
    crop_variety: str | None = None
    season: str
    planting_date: datetime
    expected_harvest_date: datetime
    area: int
    expected_yield: int | None = None
    expected_profit: int | None = None
    actual_yield: int | None = None
    actual_profit: int | None = None
    status: str | None = None
    active_role_id: int
    active_role_id: int
