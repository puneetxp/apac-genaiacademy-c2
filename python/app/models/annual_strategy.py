from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnnualStrategy(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    farm_id: int
    farmer_id: int
    year: int
    kharif_crop: str | None = None
    kharif_profit_estimate: int | None = None
    kharif_confidence_score: int | None = None
    rabi_crop: str | None = None
    rabi_profit_estimate: int | None = None
    rabi_confidence_score: int | None = None
    zaid_crop: str | None = None
    zaid_profit_estimate: int | None = None
    zaid_confidence_score: int | None = None
    total_annual_profit: int | None = None
    implementation_timeline: str | None = None
    alternative_options: str | None = None
    risk_mitigation: str | None = None
    bedrock_response: str | None = None
    status: str | None = None
    active_role_id: int
