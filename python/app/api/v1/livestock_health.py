"""
Livestock Health Record API Endpoints
Handles health record management, vaccination schedules, and health reports
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import logging

from app.core.database import get_db
from app.schemas.livestock_health_record import (
    HealthRecordCreate,
    HealthRecordUpdate,
    HealthRecordResponse,
    VaccinationSchedule,
    HealthRecordReport
)
from app.services.livestock_health_service import get_health_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/livestock-health", tags=["livestock-health"])


@router.get("/{id}")
def get_health_summary_alias(id: int, db: Session = Depends(get_db)):
    """Registry alias for health report"""
    return get_health_report(id, db)


@router.get("/vaccinations")
def list_vaccinations_alias(db: Session = Depends(get_db)):
    """Registry alias for vaccination list"""
    return list_health_records(record_type='vaccination', db=db)


@router.get("/veterinary/appointments")
def list_veterinary_appointments_alias(db: Session = Depends(get_db)):
    """Registry alias for veterinary appointments (checkups)"""
    return list_health_records(record_type='checkup', db=db)


@router.post("/records", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
def create_health_record(
    record: HealthRecordCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new health record
    
    Creates a health record for vaccinations, treatments, checkups, breeding, or observations.
    Supports tracking medications, dosages, outcomes, and next due dates.
    """
    try:
        service = get_health_service()
        
        # Prepare record data
        record_data = record.model_dump()
        
        # Create health record
        result = service.create_health_record(record_data)
        
        logger.info(f"Created health record {result['id']} for livestock {record.livestock_id}")
        
        return HealthRecordResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error creating health record: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating health record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create health record: {str(e)}"
        )


@router.get("/records/{record_id}", response_model=HealthRecordResponse)
def get_health_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Get health record by ID
    """
    try:
        service = get_health_service()
        record = service.get_health_record(record_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health record not found"
            )
        
        return HealthRecordResponse(**record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching health record {record_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch health record: {str(e)}"
        )


@router.put("/records/{record_id}", response_model=HealthRecordResponse)
def update_health_record(
    record_id: int,
    record: HealthRecordUpdate,
    db: Session = Depends(get_db)
):
    """
    Update health record
    
    Allows updating health record details including descriptions, costs, outcomes, and next due dates.
    """
    try:
        service = get_health_service()
        
        # Prepare update data
        update_data = record.model_dump(exclude_unset=True)
        
        # Update health record
        result = service.update_health_record(record_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health record not found"
            )
        
        logger.info(f"Updated health record {record_id}")
        
        return HealthRecordResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating health record {record_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update health record: {str(e)}"
        )


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete health record (soft delete)
    """
    try:
        service = get_health_service()
        
        success = service.delete_health_record(record_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health record not found"
            )
        
        logger.info(f"Deleted health record {record_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting health record {record_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete health record: {str(e)}"
        )


@router.get("/records", response_model=List[HealthRecordResponse])
def list_health_records(
    livestock_id: Optional[int] = Query(None, description="Filter by livestock ID"),
    record_type: Optional[str] = Query(None, description="Filter by record type"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List health records with optional filters
    
    Supports filtering by livestock ID, record type, and date range.
    Returns records sorted by date (most recent first).
    """
    try:
        service = get_health_service()
        
        records = service.list_health_records(
            livestock_id=livestock_id,
            record_type=record_type,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        return [HealthRecordResponse(**record) for record in records]
        
    except Exception as e:
        logger.error(f"Error listing health records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list health records: {str(e)}"
        )


@router.get("/livestock/{livestock_id}/vaccination-schedule", response_model=VaccinationSchedule)
def get_vaccination_schedule(
    livestock_id: int,
    db: Session = Depends(get_db)
):
    """
    Get vaccination schedule for livestock
    
    Returns:
    - Upcoming vaccinations with due dates
    - Completed vaccinations with history
    - Overdue vaccinations requiring immediate attention
    
    Vaccination schedules are based on species-specific requirements and regional guidelines.
    """
    try:
        service = get_health_service()
        
        schedule = service.get_vaccination_schedule(livestock_id)
        
        return VaccinationSchedule(**schedule)
        
    except ValueError as e:
        logger.error(f"Validation error getting vaccination schedule: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting vaccination schedule for livestock {livestock_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vaccination schedule: {str(e)}"
        )


@router.get("/livestock/{livestock_id}/health-report", response_model=HealthRecordReport)
def get_health_report(
    livestock_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive health report for livestock
    
    Provides complete health history including:
    - All vaccinations, treatments, checkups, and observations
    - Total health costs
    - Last checkup date
    - Upcoming vaccinations
    - Health summary with recommendations
    
    Ideal for veterinary consultations and health monitoring.
    """
    try:
        service = get_health_service()
        
        report = service.generate_health_report(livestock_id)
        
        # Convert records to response models
        report['vaccinations'] = [HealthRecordResponse(**r) for r in report['vaccinations']]
        report['treatments'] = [HealthRecordResponse(**r) for r in report['treatments']]
        report['checkups'] = [HealthRecordResponse(**r) for r in report['checkups']]
        report['observations'] = [HealthRecordResponse(**r) for r in report['observations']]
        
        return HealthRecordReport(**report)
        
    except ValueError as e:
        logger.error(f"Validation error generating health report: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating health report for livestock {livestock_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate health report: {str(e)}"
        )


@router.get("/livestock/{livestock_id}/treatment-history")
def get_treatment_history(
    livestock_id: int,
    days: int = Query(90, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Get treatment history for livestock
    
    Returns all treatments within the specified time period with:
    - Medication names and dosages
    - Treatment outcomes
    - Costs
    - Veterinarian information
    """
    try:
        service = get_health_service()
        
        from datetime import timedelta
        start_date = date.today() - timedelta(days=days)
        
        treatments = service.list_health_records(
            livestock_id=livestock_id,
            record_type='treatment',
            start_date=start_date,
            limit=1000
        )
        
        return {
            'livestock_id': livestock_id,
            'period_days': days,
            'start_date': start_date,
            'end_date': date.today(),
            'total_treatments': len(treatments),
            'treatments': [HealthRecordResponse(**t) for t in treatments]
        }
        
    except Exception as e:
        logger.error(f"Error getting treatment history for livestock {livestock_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get treatment history: {str(e)}"
        )
