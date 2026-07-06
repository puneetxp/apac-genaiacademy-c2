"""
Veterinary Services API
Task 28.2: Build veterinary services integration

Endpoints:
- POST /veterinary/symptom-check - Check symptoms and get triage
- POST /veterinary/remote-diagnosis - Get comprehensive remote diagnosis
- POST /veterinary/save-diagnosis - Save diagnosis as health record
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.veterinary_service import veterinary_service

router = APIRouter(prefix="/veterinary", tags=["veterinary"])


class SymptomCheckRequest(BaseModel):
    """Request model for symptom check"""
    livestock_id: int = Field(..., description="Livestock ID")
    symptoms: List[str] = Field(..., description="List of observed symptoms")
    duration_days: int = Field(..., ge=0, description="How long symptoms have been present")
    additional_info: Optional[str] = Field(None, description="Additional observations")


class RemoteDiagnosisRequest(BaseModel):
    """Request model for remote diagnosis"""
    livestock_id: int = Field(..., description="Livestock ID")
    symptoms: List[str] = Field(..., description="List of observed symptoms")
    duration_days: int = Field(..., ge=0, description="Duration of symptoms in days")
    temperature_celsius: Optional[float] = Field(None, ge=35.0, le=45.0, description="Body temperature")
    photos: Optional[List[str]] = Field(None, description="Photo URLs (future feature)")
    additional_info: Optional[str] = Field(None, description="Additional observations")


class SaveDiagnosisRequest(BaseModel):
    """Request model for saving diagnosis"""
    livestock_id: int = Field(..., description="Livestock ID")
    diagnosis: Dict[str, Any] = Field(..., description="Diagnosis results")
    veterinarian_name: Optional[str] = Field(None, description="Veterinarian name if consulted")


@router.get("/appointments", response_model=Dict[str, Any])
async def get_appointments_alias():
    """Registry alias for veterinary appointments"""
    return {
        "success": True,
        "message": "Veterinary appointments system operational",
        "appointments": []
    }


@router.post("/symptom-check", status_code=status.HTTP_200_OK)
async def check_symptoms(request: SymptomCheckRequest):
    """
    Check symptoms against disease database and perform AI triage
    
    Returns symptom analysis with:
    - Possible diseases matched from database
    - AI-powered diagnosis from Bedrock
    - Triage assessment (low/medium/high severity)
    - Recommended actions and timeframe
    """
    try:
        result = veterinary_service.check_symptoms(
            livestock_id=request.livestock_id,
            symptoms=request.symptoms,
            duration_days=request.duration_days,
            additional_info=request.additional_info
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Symptom check completed. Severity: {result['triage']['severity']}"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking symptoms: {str(e)}"
        )



@router.post("/remote-diagnosis", status_code=status.HTTP_200_OK)
async def get_remote_diagnosis(request: RemoteDiagnosisRequest):
    """
    Get comprehensive remote diagnosis with treatment recommendations
    
    Returns complete diagnosis including:
    - Symptom analysis and triage
    - AI-powered diagnosis with confidence level
    - Detailed treatment plan with medications
    - Follow-up schedule
    - Cost estimates
    - Telemedicine options (placeholder for partnerships)
    """
    try:
        result = veterinary_service.get_remote_diagnosis(
            livestock_id=request.livestock_id,
            symptoms=request.symptoms,
            duration_days=request.duration_days,
            temperature_celsius=request.temperature_celsius,
            photos=request.photos,
            additional_info=request.additional_info
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Remote diagnosis completed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting remote diagnosis: {str(e)}"
        )


@router.post("/save-diagnosis", status_code=status.HTTP_201_CREATED)
async def save_diagnosis(request: SaveDiagnosisRequest):
    """
    Save diagnosis results as health record
    
    Creates a health record entry with:
    - Diagnosis details
    - Treatment plan
    - Veterinarian information (if consulted)
    """
    try:
        result = veterinary_service.save_diagnosis_record(
            livestock_id=request.livestock_id,
            diagnosis=request.diagnosis,
            veterinarian_name=request.veterinarian_name
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Diagnosis saved successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving diagnosis: {str(e)}"
        )


@router.get("/diseases/{species}", status_code=status.HTTP_200_OK)
async def get_disease_database(species: str):
    """
    Get disease database for a specific species
    
    Returns list of common diseases with:
    - Disease name
    - Common symptoms
    - Severity level
    - Contagious status
    - Treatment information
    """
    try:
        species_lower = species.lower()
        diseases = veterinary_service.DISEASE_DATABASE.get(species_lower, [])
        
        if not diseases:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No disease database found for species: {species}"
            )
        
        return {
            "success": True,
            "data": {
                "species": species,
                "diseases": diseases,
                "total_diseases": len(diseases)
            },
            "message": f"Disease database retrieved for {species}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving disease database: {str(e)}"
        )
