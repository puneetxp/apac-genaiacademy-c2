from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime


class AiUsageQuota(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    user_id: int
    date: datetime
    gps_enhanced_requests: int
    pincode_requests: int
    last_reset: datetime
    quota_limit: int
    active_role_id: int
