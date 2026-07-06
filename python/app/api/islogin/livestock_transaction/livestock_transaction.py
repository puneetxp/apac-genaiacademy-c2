from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.livestock_transaction import LivestockTransaction
from app.services.livestock_transaction_service import get_service
from typing import Dict


router = APIRouter(prefix="/islogin/livestock_transaction", tags=["islogin-livestock_transaction"])
service = get_service()

@router.get("/{item_id}", response_model=LivestockTransaction)
def show_islogin_livestock_transaction(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Livestock_transaction not found")
    return record

@router.post("/", response_model=LivestockTransaction, status_code=201)
def create_islogin_livestock_transaction(payload: LivestockTransaction):
    return service.create(payload.dict(exclude_unset=True))

@router.put("/{item_id}", response_model=LivestockTransaction)
def update_islogin_livestock_transaction(item_id: int, payload: LivestockTransaction):
    updated = service.update(item_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Livestock_transaction not found")
    return updated

@router.delete("/{item_id}", response_model=Dict[str, bool])
def delete_islogin_livestock_transaction(item_id: int):
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Livestock_transaction not found")
    return {"success": True}
