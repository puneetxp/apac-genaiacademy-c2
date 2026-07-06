from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CropExpense(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    crop_id: int
    category: str
    amount: int
    description: str | None = None
    expense_date: datetime
    active_role_id: int
