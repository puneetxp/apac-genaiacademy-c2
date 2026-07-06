from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.ai_usage_quota import AiUsageQuota
from app.services.ai_usage_quota_service import get_service


router = APIRouter(prefix="/islogin/ai_usage_quota", tags=["islogin-ai_usage_quota"])
service = get_service()

@router.get("/{item_id}", response_model=AiUsageQuota)
def show_islogin_ai_usage_quota(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Ai_usage_quota not found")
    return record
