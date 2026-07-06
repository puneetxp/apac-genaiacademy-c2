from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NdapIngestionRun(BaseModel):
    """Pydantic model for NDAP email dataset ingestion runs"""
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    file_name: str
    file_hash: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    records_ingested: Optional[int] = None
    error_message: Optional[str] = None
