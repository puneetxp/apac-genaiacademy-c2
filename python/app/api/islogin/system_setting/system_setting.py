from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from app.models.system_setting import SystemSetting, SystemSettingInput
from app.services.system_setting_service import get_service
from app.core.auth import get_current_active_user
from typing import List


router = APIRouter(prefix="/islogin/system_setting", tags=["islogin-system_setting"])
service = get_service()

@router.get("/", response_model=List[SystemSetting])
def list_islogin_system_setting(current_user=Depends(get_current_active_user)):
    return service.all(owner=current_user)

@router.get("/{item_id}", response_model=SystemSetting)
def show_islogin_system_setting(item_id: int, current_user=Depends(get_current_active_user)):
    record = service.find(item_id, owner=current_user)
    if not record:
        raise HTTPException(status_code=404, detail="System_setting not found")
    return record
