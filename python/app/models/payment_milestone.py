from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentMilestone(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    booking_id: int
    milestone_type: str
    amount: int
    due_date: datetime
    paid_date: datetime | None = None
    status: str
    payment_method: str | None = None
    transaction_id: str | None = None
    active_role_id: int
