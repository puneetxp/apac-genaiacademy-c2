from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.slusi_lcc_report import SlusiLccReport
from app.services.slusi_lcc_report_service import get_service


router = APIRouter(prefix="/islogin/slusi_lcc_report", tags=["islogin-slusi_lcc_report"])
service = get_service()

@router.get("/{item_id}", response_model=SlusiLccReport)
def show_islogin_slusi_lcc_report(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Slusi_lcc_report not found")
    return record
