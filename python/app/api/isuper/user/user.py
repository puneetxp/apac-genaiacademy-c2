from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.user import User
from app.services.user_service import get_service
from typing import List, Dict


router = APIRouter(prefix="/isuper/user", tags=["isuper-user"])
service = get_service()

@router.get("/", response_model=List[User])
def list_isuper_user():
    return service.all()

@router.get("/{item_id}", response_model=User)
def show_isuper_user(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="User not found")
    return record

@router.post("/", response_model=User, status_code=201)
def create_isuper_user(payload: User):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=User)
def update_isuper_user(item_id: int, payload: User):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_isuper_user(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}
