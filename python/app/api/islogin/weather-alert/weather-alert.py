from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.weather_alert import WeatherAlert
from app.services.weather_alert_service import get_service


router = APIRouter(prefix="/islogin/weather-alert", tags=["islogin-weather-alert"])
service = get_service()

@router.get("/{item_id}", response_model=WeatherAlert)
def show_islogin_weather-alert(item_id: int):
    record = service.find(item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Weather_alert not found")
    return record
