from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime


class ActiveRole(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    user_id: int
    role_id: int
    active_role_id: int
