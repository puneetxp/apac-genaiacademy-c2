from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    cognito_user_id: str | None = None
    firebase_id: str | None = None
    username: str
    name: str
    email: str | None = None
    phone: str | None = None
    google_id: str | None = None
    facebook_id: str | None = None
    password: str | None = None
    user_type: str | None = None
    preferred_language: str | None = None
    mfa_enabled: bool | None = None
    latitude: int | None = None
    longitude: int | None = None
    pincode: str | None = None
    state: str | None = None
    district: str | None = None
    village: str | None = None
    address_line: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
