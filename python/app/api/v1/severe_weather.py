"""
Severe Weather Monitoring API Endpoints
Provides severe weather alerts, harvest window analysis, and emergency notifications

Task 23.2: Implement Severe Weather Monitoring
Validates: Requirements AC8 (Phase 6 - Required)
"""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.weather_service import get_weather_service
from app.services.severe_weather_service import get_severe_weather_service
from app.core.cache import get_cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/severe-weather", tags=["severe-weather"])


# Request/Response Models
class SevereWeatherAlert(BaseModel):
    """Severe weather alert"""
    alert_type: str = Field(..., description="Alert type (heavy_rain, extreme_heat, cyclone, etc.)")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    date: datetime = Field(..., description="Alert date/time")
    message: str = Field(..., description="Alert message")
    recommendation: str = Field(..., description="Recommended actions")
    rainfall: Optional[float] = Field(None, description="Rainfall amount (mm)")
    temperature: Optional[float] = Field(None, description="Temperature (°C)")
    wind_speed: Optional[float] = Field(None, description="Wind speed (m/s)")


class SevereWeatherResponse(BaseModel):
    """Severe weather detection response"""
    latitude: float
    longitude: float
    farm_id: Optional[int]
    alerts: List[SevereWeatherAlert]
    alert_count: int
    critical_alerts: int
    high_alerts: int


class DryPeriod(BaseModel):
    """Dry period for harvest window"""
    start_date: datetime = Field(..., description="Period start date")
    end_date: datetime = Field(..., description="Period end date")
    days: int = Field(..., description="Number of consecutive dry days")
    avg_temp: float = Field(..., description="Average temperature (°C)")
    avg_humidity: int = Field(..., description="Average humidity (%)")
    suitability_score: float = Field(..., description="Harvest suitability score (0-100)")


class HarvestWindowResponse(BaseModel):
    """Harvest window analysis response"""
    latitude: float
    longitude: float
    forecast_days: int
    dry_periods: List[DryPeriod]
    optimal_window: Optional[DryPeriod]
    recommendation: str


class EmergencyHarvestAlert(BaseModel):
    """Emergency harvest alert"""
    alert_type: str
    severity: str
    farm_id: int
    crop_id: int
    crop_type: str
    expected_harvest_date: datetime
    days_to_harvest: int
    severe_weather: List[SevereWeatherAlert]
    harvest_windows: HarvestWindowResponse
    message: str
    recommendation: str


class MicroclimateCharacteristics(BaseModel):
    """Farm microclimate characteristics"""
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    slope: Optional[float] = Field(None, description="Slope in degrees")
    soil_type: Optional[str] = Field(None, description="Soil type")


class AdjustedForecast(BaseModel):
    """Microclimate-adjusted forecast"""
    date: datetime
    temp_min: float
    temp_max: float
    humidity: int
    rainfall: float
    effective_rainfall: Optional[float] = None
    irrigation_need: Optional[str] = None


class MicroclimateResponse(BaseModel):
    """Microclimate prediction response"""
    latitude: float
    longitude: float
    farm_characteristics: Optional[dict]
    microclimate_forecast: List[dict]
    adjustments_applied: List[str]


@router.get("/detect", response_model=SevereWeatherResponse)
async def detect_severe_weather(
    latitude: float = Query(..., description="GPS latitude", ge=-90, le=90),
    longitude: float = Query(..., description="GPS longitude", ge=-180, le=180),
    farm_id: Optional[int] = Query(None, description="Farm ID"),
    state: Optional[str] = Query(None, description="State name"),
    district: Optional[str] = Query(None, description="District name"),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect severe weather conditions from forecast
    
    - **latitude**: GPS latitude (-90 to 90)
    - **longitude**: GPS longitude (-180 to 180)
    - **farm_id**: Farm ID (optional)
    - **state**: State name (optional)
    - **district**: District name (optional)
    
    Returns severe weather alerts including:
    - Heavy rain (> 50mm)
    - Extreme temperatures (> 40°C or < 5°C)
    - High winds (> 15 m/s)
    - Cyclone warnings
    
    Alert delivery latency: < 15 minutes from detection
    """
    try:
        cache_manager = get_cache_manager()
        weather_service = get_weather_service(db, cache_manager=cache_manager)
        severe_weather_service = get_severe_weather_service(db, weather_service)
        
        async with weather_service:
            alerts = await severe_weather_service.detect_severe_weather(
                latitude, longitude, farm_id, state, district
            )
        
        # Count alerts by severity
        critical_count = sum(1 for a in alerts if a["severity"] == "critical")
        high_count = sum(1 for a in alerts if a["severity"] == "high")
        
        return SevereWeatherResponse(
            latitude=latitude,
            longitude=longitude,
            farm_id=farm_id,
            alerts=[SevereWeatherAlert(**alert) for alert in alerts],
            alert_count=len(alerts),
            critical_alerts=critical_count,
            high_alerts=high_count
        )
    
    except Exception as e:
        logger.error(f"Error detecting severe weather: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/harvest-windows", response_model=HarvestWindowResponse)
async def analyze_harvest_windows(
    latitude: float = Query(..., description="GPS latitude", ge=-90, le=90),
    longitude: float = Query(..., description="GPS longitude", ge=-180, le=180),
    days_ahead: int = Query(14, description="Days to analyze", ge=7, le=14),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze weather forecast to identify optimal harvest windows
    
    - **latitude**: GPS latitude (-90 to 90)
    - **longitude**: GPS longitude (-180 to 180)
    - **days_ahead**: Number of days to analyze (7-14, default: 14)
    
    Returns harvest window analysis including:
    - Dry periods (consecutive days with < 5mm rain)
    - Optimal harvest window with suitability score
    - Temperature and humidity conditions
    - Harvest timing recommendations
    
    Used to plan harvest operations and avoid weather-related crop damage.
    """
    try:
        cache_manager = get_cache_manager()
        weather_service = get_weather_service(db, cache_manager=cache_manager)
        severe_weather_service = get_severe_weather_service(db, weather_service)
        
        async with weather_service:
            analysis = await severe_weather_service.analyze_harvest_windows(
                latitude, longitude, days_ahead
            )
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="No forecast data available for harvest window analysis"
            )
        
        return HarvestWindowResponse(**analysis)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing harvest windows: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/emergency-harvest/{farm_id}/{crop_id}", response_model=Optional[EmergencyHarvestAlert])
async def check_emergency_harvest(
    farm_id: int,
    crop_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if emergency harvest is needed due to severe weather
    
    - **farm_id**: Farm ID
    - **crop_id**: Crop ID
    
    Returns emergency harvest alert if:
    - Crop is within 14 days of expected harvest
    - Severe weather (high/critical) threatens crop
    - Optimal harvest window identified before weather arrives
    
    Alert includes:
    - Severity assessment
    - Harvest window recommendations
    - Specific action recommendations
    
    Notification latency: < 15 minutes from detection
    """
    try:
        cache_manager = get_cache_manager()
        weather_service = get_weather_service(db, cache_manager=cache_manager)
        severe_weather_service = get_severe_weather_service(db, weather_service)
        
        async with weather_service:
            alert = await severe_weather_service.check_emergency_harvest_alert(
                farm_id, crop_id
            )
        
        if alert:
            # TODO: Send emergency notification via SNS
            # background_tasks.add_task(send_emergency_notification, alert)
            return EmergencyHarvestAlert(**alert)
        
        return None
    
    except Exception as e:
        logger.error(f"Error checking emergency harvest: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/microclimate", response_model=MicroclimateResponse)
async def get_microclimate_prediction(
    latitude: float = Query(..., description="GPS latitude", ge=-90, le=90),
    longitude: float = Query(..., description="GPS longitude", ge=-180, le=180),
    characteristics: Optional[MicroclimateCharacteristics] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate microclimate predictions for individual farm
    
    - **latitude**: GPS latitude (-90 to 90)
    - **longitude**: GPS longitude (-180 to 180)
    - **characteristics**: Farm-specific characteristics (optional)
      - elevation: Elevation in meters
      - slope: Slope in degrees
      - soil_type: Soil type (sandy, clay, loam, etc.)
    
    Returns microclimate-adjusted forecast including:
    - Temperature adjustments based on elevation
    - Effective rainfall based on slope
    - Irrigation needs based on soil type
    - Farm-specific weather predictions
    
    Provides more accurate forecasts than regional weather data alone.
    """
    try:
        cache_manager = get_cache_manager()
        weather_service = get_weather_service(db, cache_manager=cache_manager)
        severe_weather_service = get_severe_weather_service(db, weather_service)
        
        farm_chars = characteristics.dict() if characteristics else None
        
        async with weather_service:
            prediction = await severe_weather_service.get_microclimate_prediction(
                latitude, longitude, farm_chars
            )
        
        if not prediction:
            raise HTTPException(
                status_code=404,
                detail="No forecast data available for microclimate prediction"
            )
        
        return MicroclimateResponse(**prediction)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating microclimate prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/alerts", response_model=List[SevereWeatherAlert])
async def get_alerts_alias(
    farm_id: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Registry alias for severe weather alerts"""
    return await get_active_alerts(farm_id=farm_id, state=state, district=district, db=db)


@router.get("/alerts/active", response_model=List[SevereWeatherAlert])
async def get_active_alerts(
    farm_id: Optional[int] = Query(None, description="Farm ID"),
    state: Optional[str] = Query(None, description="State name"),
    district: Optional[str] = Query(None, description="District name"),
    severity: Optional[str] = Query(None, description="Minimum severity (low, medium, high, critical)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get active weather alerts from database
    
    - **farm_id**: Filter by farm ID (optional)
    - **state**: Filter by state (optional)
    - **district**: Filter by district (optional)
    - **severity**: Minimum severity level (optional)
    
    Returns list of active weather alerts stored in database.
    Alerts are automatically stored when detected by the system.
    """
    try:
        from sqlalchemy import select, and_
        from app.orm.weather_alert import WeatherAlert
        
        # Build query
        conditions = [WeatherAlert.is_active == True]
        
        if farm_id:
            conditions.append(WeatherAlert.farm_id == farm_id)
        if state:
            conditions.append(WeatherAlert.state == state)
        if district:
            conditions.append(WeatherAlert.district == district)
        if severity:
            severity_order = ["low", "medium", "high", "critical"]
            min_index = severity_order.index(severity.lower())
            valid_severities = severity_order[min_index:]
            conditions.append(WeatherAlert.severity.in_(valid_severities))
        
        # Execute query
        result = await db.execute(
            select(WeatherAlert).where(and_(*conditions))
        )
        alerts = result.scalars().all()
        
        # Convert to response format
        return [
            SevereWeatherAlert(
                alert_type=alert.alert_type,
                severity=alert.severity,
                date=alert.valid_from,
                message=alert.message,
                recommendation=alert.recommendation or ""
            )
            for alert in alerts
        ]
    
    except Exception as e:
        logger.error(f"Error fetching active alerts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
