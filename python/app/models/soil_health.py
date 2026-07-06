"""
Soil Health Pydantic Models - STUB
TODO: These are temporary stubs to allow application startup.
Need to be properly implemented with full schemas.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SoilTest(BaseModel):
    """Pydantic model for soil test data - STUB"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FertilizerApplication(BaseModel):
    """Pydantic model for fertilizer application data - STUB"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SoilAmendment(BaseModel):
    """Pydantic model for soil amendment data - STUB"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
