from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.active_role import ActiveRole
from app.services.active_role_service import get_service


router = APIRouter(prefix="/islogin/active-role", tags=["islogin-active-role"])
service = get_service()

@router.get("/{item_id}", response_model=ActiveRole)
def show_islogin_active-role(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Active_role not found")
    return record
