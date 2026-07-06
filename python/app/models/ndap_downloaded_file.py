from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime


class NdapDownloadedFile(BaseModel):
    """Pydantic model for storing raw downloaded NDAP dataset files in the DB"""
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    file_name: str
    file_hash: str
    file_content: bytes
