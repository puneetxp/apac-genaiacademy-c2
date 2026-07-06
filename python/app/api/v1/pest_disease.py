"""
Pest and Disease Early Warning API
Provides pest/disease risk monitoring and management recommendations

Validates: Requirements AC10 (Phase 6 - Required)
Task 25.2: Build pest and disease early warning system
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.pest_disease_service import get_pest_disease_service
from app.services.weather_service import get_weather_service
from app.services.crop_milestone_service import get_service as get_crop_milestone_service

router = APIRouter(prefix="/pest-disease", tags=["pest-disease"])


class WeatherConditions(BaseModel):
    """Weather conditions for risk assessment"""
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: int = Field(..., ge=0, le=100, description="Humidity percentage")
    rainfall: float = Field(default=0.0, ge=0, description="Rainfall in mm")


class RiskCheckRequest(BaseModel):
    """Request to check pest/disease risk"""
    crop_id: int = Field(..., description="Crop ID")
    weather_data: WeatherConditions
    current_stage: str = Field(..., description="Current growth stage")


class ManagementRecommendation(BaseModel):
    """Pest/disease management recommendation"""
    pest_disease: str
    timing: str
    prevention: List[str]
    organic_options: Optional[List[str]] = None
    chemical_options: Optional[List[str]] = None


class RiskAlert(BaseModel):
    """Pest/disease risk alert"""
    pest_disease: str
    severity: str
    description: str
    current_conditions: dict
    management: dict
    detected_at: str


@router.post("/identify", response_model=List[RiskAlert])
async def identify_risks_alias(
    request: RiskCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """Registry alias for pest/disease identification"""
    return await check_pest_disease_risk(request, db)


@router.post("/check-risk", response_model=List[RiskAlert])
async def check_pest_disease_risk(
    request: RiskCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Check for pest and disease risks based on weather and crop stage
    
    Validates: AC10.3 - Early warning alerts based on weather and crop stage
    """
    try:
        service = get_pest_disease_service(db)
        
        risks = await service.check_pest_disease_risk(
            crop_id=request.crop_id,
            weather_data=request.weather_data.model_dump(),
            current_stage=request.current_stage
        )
        
        return risks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/treatments", response_model=List[dict])
async def get_treatments_alias(
    pest_disease: str = Query(..., description="Pest or disease name"),
    preference: str = Query(default="both", pattern="^(organic|chemical|both)$"),
    db: AsyncSession = Depends(get_db)
):
    """Registry alias for treatments"""
    res = await get_management_recommendations(pest_disease, preference, db)
    return [res] if isinstance(res, dict) else res


@router.get("/management/{pest_disease}", response_model=ManagementRecommendation)
async def get_management_recommendations(
    pest_disease: str,
    preference: str = Query(default="both", pattern="^(organic|chemical|both)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pest/disease management recommendations
    
    Args:
        pest_disease: Name of pest or disease (e.g., 'aphids', 'fungal_diseases')
        preference: Treatment preference ('organic', 'chemical', or 'both')
    
    Validates: AC10.3 - Pest management recommendations with organic and chemical options
    """
    try:
        service = get_pest_disease_service(db)
        
        recommendations = await service.get_management_recommendations(
            pest_disease=pest_disease,
            preference=preference
        )
        
        if 'error' in recommendations:
            raise HTTPException(status_code=404, detail=recommendations['error'])
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crop-risks/{crop_id}")
async def get_crop_specific_risks(
    crop_id: int,
    current_stage: str = Query(..., description="Current growth stage"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get common pest/disease risks for specific crop and stage
    
    Validates: AC10.3 - Crop-specific pest/disease information
    """
    try:
        service = get_pest_disease_service(db)
        
        # Get crop details to determine crop name
        from app.orm.crop import Crop
        from sqlalchemy import select
        
        result = await db.execute(select(Crop).where(Crop.id == crop_id))
        crop = result.scalar_one_or_none()
        
        if not crop:
            raise HTTPException(status_code=404, detail="Crop not found")
        
        risks = await service.get_crop_specific_risks(
            crop_name=crop.crop_name,
            current_stage=current_stage
        )
        
        return {
            'crop_id': crop_id,
            'crop_name': crop.crop_name,
            'current_stage': current_stage,
            'risks': risks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prevention-guidance/{crop_id}")
async def get_prevention_guidance(
    crop_id: int,
    current_stage: str = Query(..., description="Current growth stage"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get disease prevention guidance for current crop stage
    
    Validates: AC10.3 - Disease prevention guidance with timing and application instructions
    """
    try:
        service = get_pest_disease_service(db)
        
        guidance = await service.get_prevention_guidance(
            crop_id=crop_id,
            current_stage=current_stage
        )
        
        return guidance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor-all")
async def monitor_all_crops(
    db: AsyncSession = Depends(get_db)
):
    """
    Background job endpoint to monitor all active crops for pest/disease risks
    
    This endpoint should be called by a scheduled job (cron/celery)
    
    Validates: AC10.3 - Automated pest/disease monitoring
    """
    try:
        service = get_pest_disease_service(db)
        weather_service = get_weather_service(db)
        milestone_service = get_crop_milestone_service(db)
        
        summary = await service.monitor_crops_for_risks(
            weather_service=weather_service,
            milestone_service=milestone_service
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-pests")
async def get_available_pests():
    """
    Get list of all pests and diseases tracked by the system
    
    Returns list of pest/disease names with descriptions
    """
    from app.services.pest_disease_service import PEST_DISEASE_THRESHOLDS
    
    pests = []
    for pest_disease, data in PEST_DISEASE_THRESHOLDS.items():
        pests.append({
            'name': pest_disease,
            'description': data['description'],
            'severity': data['severity'],
            'risk_stages': data['risk_stages']
        })
    
    return {
        'total': len(pests),
        'pests_diseases': pests
    }


@router.get("/history/{crop_id}")
async def get_pest_disease_history(
    crop_id: int,
    db: AsyncSession = Depends(get_db)
):
    """ Get historical pest/disease records for a specific crop """
    try:
        from app.orm.pest_disease_alert import PestDiseaseAlert
        from sqlalchemy import select
        
        result = await db.execute(
            select(PestDiseaseAlert).where(PestDiseaseAlert.crop_id == crop_id).order_by(PestDiseaseAlert.created_at.desc())
        )
        alerts = result.scalars().all()
        
        return {
            'crop_id': crop_id,
            'history': [alert.to_dict() for alert in alerts]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[dict])
async def get_all_alerts_alias(
    farm_id: Optional[int] = Query(None),
    crop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Registry alias for alerts"""
    if crop_id:
        res = await get_crop_alerts(crop_id, db=db)
        return res.get('alerts', [])
    if farm_id:
        res = await get_farm_alerts(farm_id, db=db)
        return res.get('alerts', [])
    return []


@router.get("/alerts/{crop_id}")
async def get_crop_alerts(
    crop_id: int,
    include_resolved: bool = Query(default=False, description="Include resolved alerts"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pest/disease alerts for a specific crop
    
    Args:
        crop_id: Crop ID
        include_resolved: Whether to include resolved alerts
    
    Returns:
        List of alerts for the crop
    """
    try:
        from app.orm.pest_disease_alert import PestDiseaseAlert
        from sqlalchemy import select, and_
        
        # Build query
        conditions = [PestDiseaseAlert.crop_id == crop_id]
        if not include_resolved:
            conditions.append(PestDiseaseAlert.is_resolved == False)
        
        result = await db.execute(
            select(PestDiseaseAlert).where(and_(*conditions)).order_by(PestDiseaseAlert.created_at.desc())
        )
        alerts = result.scalars().all()
        
        return {
            'crop_id': crop_id,
            'total_alerts': len(alerts),
            'alerts': [alert.to_dict() for alert in alerts]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a pest/disease alert as resolved
    
    Args:
        alert_id: Alert ID
    
    Returns:
        Updated alert
    """
    try:
        from app.orm.pest_disease_alert import PestDiseaseAlert
        from sqlalchemy import select
        from datetime import datetime
        
        result = await db.execute(
            select(PestDiseaseAlert).where(PestDiseaseAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_resolved = True
        alert.resolved_at = datetime.now()
        await alert.save(db)
        
        return {
            'success': True,
            'message': 'Alert marked as resolved',
            'alert': alert.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/farm/{farm_id}")
async def get_farm_alerts(
    farm_id: int,
    include_resolved: bool = Query(default=False, description="Include resolved alerts"),
    limit: int = Query(default=50, le=100, description="Maximum number of alerts"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pest/disease alerts for a specific farm
    
    Args:
        farm_id: Farm ID
        include_resolved: Whether to include resolved alerts
        limit: Maximum number of alerts to return
    
    Returns:
        List of alerts for the farm
    """
    try:
        from app.orm.pest_disease_alert import PestDiseaseAlert
        from sqlalchemy import select, and_
        
        # Build query
        conditions = [PestDiseaseAlert.farm_id == farm_id]
        if not include_resolved:
            conditions.append(PestDiseaseAlert.is_resolved == False)
        
        result = await db.execute(
            select(PestDiseaseAlert)
            .where(and_(*conditions))
            .order_by(PestDiseaseAlert.created_at.desc())
            .limit(limit)
        )
        alerts = result.scalars().all()
        
        return {
            'farm_id': farm_id,
            'total_alerts': len(alerts),
            'alerts': [alert.to_dict() for alert in alerts]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
