from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.user import User
from app.services.user_service import get_service


router = APIRouter(prefix="/islogin/user", tags=["islogin-user"])
service = get_service()

@router.get("/{item_id}", response_model=User)
def show_islogin_user(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="User not found")
    return record

@router.put("/{item_id}", response_model=User)
def update_islogin_user(item_id: int, payload: User):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated
