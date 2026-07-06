"""
Soil Testing API endpoints
Handles soil test result upload, parsing, and soil health analysis

Task 22.1: Integrate with soil testing laboratories
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
import logging

from app.core.database import get_db
from app.services.soil_testing_service import soil_testing_service
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/soil-testing", tags=["soil-testing"])


# Request/Response schemas
class SoilTestManualEntry(BaseModel):
    """Manual soil test entry schema"""
    farm_id: int = Field(..., description="Farm ID")
    plot_id: Optional[int] = Field(None, description="Optional plot ID")
    test_date: date = Field(..., description="Date of soil test")
    lab_name: Optional[str] = Field(None, max_length=255, description="Laboratory name")
    lab_reference_number: Optional[str] = Field(None, max_length=255, description="Lab reference number")
    
    # Macronutrients
    nitrogen_kg_per_ha: Optional[float] = Field(None, ge=0, description="Nitrogen (kg/ha)")
    phosphorus_kg_per_ha: Optional[float] = Field(None, ge=0, description="Phosphorus (kg/ha)")
    potassium_kg_per_ha: Optional[float] = Field(None, ge=0, description="Potassium (kg/ha)")
    
    # Soil properties
    ph_level: Optional[float] = Field(None, ge=0, le=14, description="pH level")
    organic_carbon_percent: Optional[float] = Field(None, ge=0, le=100, description="Organic carbon %")
    organic_matter_percent: Optional[float] = Field(None, ge=0, le=100, description="Organic matter %")
    electrical_conductivity: Optional[float] = Field(None, ge=0, description="EC (dS/m)")
    
    # Micronutrients
    sulfur_ppm: Optional[float] = Field(None, ge=0, description="Sulfur (ppm)")
    zinc_ppm: Optional[float] = Field(None, ge=0, description="Zinc (ppm)")
    iron_ppm: Optional[float] = Field(None, ge=0, description="Iron (ppm)")
    manganese_ppm: Optional[float] = Field(None, ge=0, description="Manganese (ppm)")
    copper_ppm: Optional[float] = Field(None, ge=0, description="Copper (ppm)")
    boron_ppm: Optional[float] = Field(None, ge=0, description="Boron (ppm)")
    
    # Metadata
    test_method: Optional[str] = Field(None, max_length=255, description="Testing method")
    recommendations: Optional[str] = Field(None, description="Lab recommendations")
    notes: Optional[str] = Field(None, description="Additional notes")


class SoilTestResponse(BaseModel):
    """Soil test response schema"""
    id: int
    farm_id: int
    plot_id: Optional[int]
    test_date: date
    lab_name: Optional[str]
    lab_reference_number: Optional[str]
    
    nitrogen_kg_per_ha: Optional[float]
    phosphorus_kg_per_ha: Optional[float]
    potassium_kg_per_ha: Optional[float]
    ph_level: Optional[float]
    organic_carbon_percent: Optional[float]
    organic_matter_percent: Optional[float]
    electrical_conductivity: Optional[float]
    
    sulfur_ppm: Optional[float]
    zinc_ppm: Optional[float]
    iron_ppm: Optional[float]
    manganese_ppm: Optional[float]
    copper_ppm: Optional[float]
    boron_ppm: Optional[float]
    
    soil_health_score: Optional[float]
    test_method: Optional[str]
    recommendations: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class SoilHealthAnalysis(BaseModel):
    """Soil health analysis response"""
    soil_health_score: float = Field(..., description="Soil health score (0-100)")
    rating: str = Field(..., description="Health rating: excellent/good/fair/poor")
    recommendations: List[dict] = Field(..., description="Improvement recommendations")
    parameter_scores: dict = Field(..., description="Individual parameter scores")


class SoilTestComparison(BaseModel):
    """Soil test comparison response"""
    previous_test_id: int
    current_test_id: int
    previous_test_date: date
    current_test_date: date
    days_between_tests: int
    changes: dict = Field(..., description="Parameter changes and trends")
    overall_trend: str = Field(..., description="Overall trend: improving/stable/declining")


@router.post("/tests", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_test_alias(
    test_data: SoilTestManualEntry,
    db: AsyncSession = Depends(get_db)
):
    """Registry alias for create soil test"""
    return await create_soil_test_manual_entry(test_data, db)


@router.post("/manual-entry", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_soil_test_manual_entry(
    test_data: SoilTestManualEntry,
    db: AsyncSession = Depends(get_db)
):
    """
    Create soil test result from manual entry
    
    Parses manually entered soil test data, calculates soil health score,
    and generates improvement recommendations.
    """
    try:
        logger.info(f"Creating manual soil test entry for farm {test_data.farm_id}")
        
        # Parse and validate test data
        parsed_data = soil_testing_service.parse_soil_test_manual_entry(test_data.dict())
        
        # Calculate soil health score
        soil_health_score = soil_testing_service.calculate_soil_health_score(parsed_data)
        parsed_data['soil_health_score'] = soil_health_score
        
        # Generate recommendations
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            parsed_data,
            soil_health_score
        )
        
        # Store in database
        from app.orm.soil_test_result import SoilTestResult
        import json
        
        soil_test = SoilTestResult(
            farm_id=test_data.farm_id,
            plot_id=test_data.plot_id,
            test_date=test_data.test_date,
            lab_name=parsed_data.get('lab_name'),
            lab_reference_number=parsed_data.get('lab_reference_number'),
            nitrogen_kg_per_ha=parsed_data.get('nitrogen_kg_per_ha'),
            phosphorus_kg_per_ha=parsed_data.get('phosphorus_kg_per_ha'),
            potassium_kg_per_ha=parsed_data.get('potassium_kg_per_ha'),
            ph_level=parsed_data.get('ph_level'),
            organic_carbon_percent=parsed_data.get('organic_carbon_percent'),
            organic_matter_percent=parsed_data.get('organic_matter_percent'),
            electrical_conductivity=parsed_data.get('electrical_conductivity'),
            sulfur_ppm=parsed_data.get('sulfur_ppm'),
            zinc_ppm=parsed_data.get('zinc_ppm'),
            iron_ppm=parsed_data.get('iron_ppm'),
            manganese_ppm=parsed_data.get('manganese_ppm'),
            copper_ppm=parsed_data.get('copper_ppm'),
            boron_ppm=parsed_data.get('boron_ppm'),
            soil_health_score=soil_health_score,
            test_method=parsed_data.get('test_method'),
            raw_data_json=json.dumps(parsed_data),
            recommendations=json.dumps(recommendations),
            notes=parsed_data.get('notes')
        )
        
        db.add(soil_test)
        await db.commit()
        await db.refresh(soil_test)
        
        # Prepare response
        response = {
            "message": "Soil test result created successfully",
            "id": soil_test.id,
            "soil_health_score": soil_health_score,
            "rating": _get_health_rating(soil_health_score),
            "recommendations": recommendations,
            "test_data": parsed_data
        }
        
        logger.info(f"Soil test created with ID {soil_test.id} and health score: {soil_health_score}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating soil test: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create soil test result"
        )


@router.post("/fetch-from-icar", response_model=dict)
async def fetch_soil_test_from_icar(
    lab_reference_number: str,
    farm_id: int,
    plot_id: Optional[int] = None,
    lab_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch soil test results from ICAR laboratory API
    
    Note: This is a placeholder endpoint. Actual ICAR API integration
    requires official API credentials and documentation.
    """
    try:
        logger.info(f"Fetching soil test from ICAR: {lab_reference_number}")
        
        # Attempt to fetch from ICAR API
        icar_data = await soil_testing_service.fetch_soil_test_from_icar(
            lab_reference_number,
            lab_name
        )
        
        if not icar_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Soil test result not found in ICAR database"
            )
        
        # Calculate soil health score
        soil_health_score = soil_testing_service.calculate_soil_health_score(icar_data)
        icar_data['soil_health_score'] = soil_health_score
        
        # Generate recommendations
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            icar_data,
            soil_health_score
        )
        
        # Store in database
        from app.orm.soil_test_result import SoilTestResult
        from datetime import date
        import json
        
        soil_test = SoilTestResult(
            farm_id=farm_id,
            plot_id=plot_id,
            test_date=icar_data.get('test_date', date.today()),
            lab_name=lab_name or icar_data.get('lab_name'),
            lab_reference_number=lab_reference_number,
            nitrogen_kg_per_ha=icar_data.get('nitrogen_kg_per_ha'),
            phosphorus_kg_per_ha=icar_data.get('phosphorus_kg_per_ha'),
            potassium_kg_per_ha=icar_data.get('potassium_kg_per_ha'),
            ph_level=icar_data.get('ph_level'),
            organic_carbon_percent=icar_data.get('organic_carbon_percent'),
            organic_matter_percent=icar_data.get('organic_matter_percent'),
            electrical_conductivity=icar_data.get('electrical_conductivity'),
            sulfur_ppm=icar_data.get('sulfur_ppm'),
            zinc_ppm=icar_data.get('zinc_ppm'),
            iron_ppm=icar_data.get('iron_ppm'),
            manganese_ppm=icar_data.get('manganese_ppm'),
            copper_ppm=icar_data.get('copper_ppm'),
            boron_ppm=icar_data.get('boron_ppm'),
            soil_health_score=soil_health_score,
            test_method=icar_data.get('test_method'),
            raw_data_json=json.dumps(icar_data),
            recommendations=json.dumps(recommendations),
            notes=icar_data.get('notes')
        )
        
        db.add(soil_test)
        await db.commit()
        await db.refresh(soil_test)
        
        response = {
            "message": "Soil test result fetched from ICAR successfully",
            "id": soil_test.id,
            "soil_health_score": soil_health_score,
            "rating": _get_health_rating(soil_health_score),
            "recommendations": recommendations,
            "test_data": icar_data
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching from ICAR: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch soil test from ICAR"
        )


@router.post("/upload-pdf", response_model=dict)
async def upload_soil_test_pdf(
    farm_id: int,
    file: UploadFile = File(...),
    plot_id: Optional[int] = None,
    lab_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse soil test PDF report
    
    Note: PDF parsing functionality is not yet implemented.
    This is a placeholder for future implementation.
    """
    try:
        logger.info(f"Uploading soil test PDF for farm {farm_id}")
        
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Read file content
        pdf_content = await file.read()
        
        # Parse PDF (not yet implemented)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF parsing will be implemented in future version. Please use manual entry for now."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload soil test PDF"
        )


@router.get("/farm/{farm_id}/latest", response_model=dict)
async def get_latest_soil_test(
    farm_id: int,
    plot_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get latest soil test result for a farm or plot
    """
    try:
        logger.info(f"Fetching latest soil test for farm {farm_id}")
        
        from app.orm.soil_test_result import SoilTestResult
        from sqlalchemy import select, desc, and_
        import json
        
        # Build query
        query = select(SoilTestResult).where(SoilTestResult.farm_id == farm_id)
        
        if plot_id:
            query = query.where(SoilTestResult.plot_id == plot_id)
        
        query = query.order_by(desc(SoilTestResult.test_date)).limit(1)
        
        # Execute query
        result = await db.execute(query)
        soil_test = result.scalar_one_or_none()
        
        if not soil_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No soil test results found for this farm"
            )
        
        # Parse recommendations
        recommendations = []
        if soil_test.recommendations:
            try:
                recommendations = json.loads(soil_test.recommendations)
            except:
                pass
        
        response = {
            "id": soil_test.id,
            "farm_id": soil_test.farm_id,
            "plot_id": soil_test.plot_id,
            "test_date": soil_test.test_date.isoformat() if soil_test.test_date else None,
            "lab_name": soil_test.lab_name,
            "lab_reference_number": soil_test.lab_reference_number,
            "nitrogen_kg_per_ha": float(soil_test.nitrogen_kg_per_ha) if soil_test.nitrogen_kg_per_ha else None,
            "phosphorus_kg_per_ha": float(soil_test.phosphorus_kg_per_ha) if soil_test.phosphorus_kg_per_ha else None,
            "potassium_kg_per_ha": float(soil_test.potassium_kg_per_ha) if soil_test.potassium_kg_per_ha else None,
            "ph_level": float(soil_test.ph_level) if soil_test.ph_level else None,
            "organic_carbon_percent": float(soil_test.organic_carbon_percent) if soil_test.organic_carbon_percent else None,
            "organic_matter_percent": float(soil_test.organic_matter_percent) if soil_test.organic_matter_percent else None,
            "electrical_conductivity": float(soil_test.electrical_conductivity) if soil_test.electrical_conductivity else None,
            "sulfur_ppm": float(soil_test.sulfur_ppm) if soil_test.sulfur_ppm else None,
            "zinc_ppm": float(soil_test.zinc_ppm) if soil_test.zinc_ppm else None,
            "iron_ppm": float(soil_test.iron_ppm) if soil_test.iron_ppm else None,
            "manganese_ppm": float(soil_test.manganese_ppm) if soil_test.manganese_ppm else None,
            "copper_ppm": float(soil_test.copper_ppm) if soil_test.copper_ppm else None,
            "boron_ppm": float(soil_test.boron_ppm) if soil_test.boron_ppm else None,
            "soil_health_score": float(soil_test.soil_health_score) if soil_test.soil_health_score else None,
            "rating": _get_health_rating(float(soil_test.soil_health_score)) if soil_test.soil_health_score else "unknown",
            "test_method": soil_test.test_method,
            "recommendations": recommendations,
            "notes": soil_test.notes,
            "created_at": soil_test.created_at.isoformat() if soil_test.created_at else None,
            "updated_at": soil_test.updated_at.isoformat() if soil_test.updated_at else None
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching soil test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch soil test result"
        )


@router.get("/tests", response_model=List[dict])
async def list_tests_alias(
    farm_id: int = Query(..., description="Farm ID"),
    db: AsyncSession = Depends(get_db)
):
    """Registry alias for listing tests"""
    return await get_soil_test_history(farm_id, db=db)


@router.get("/tests/{id}", response_model=dict)
async def get_test_alias(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """Registry alias for getting specific test"""
    # Using existing logic from get_latest_soil_test as base but for specific ID
    from app.orm.soil_test_result import SoilTestResult
    from sqlalchemy import select
    import json
    
    result = await db.execute(select(SoilTestResult).where(SoilTestResult.id == id))
    soil_test = result.scalar_one_or_none()
    
    if not soil_test:
        raise HTTPException(status_code=404, detail="Soil test not found")
        
    return {
        "id": soil_test.id,
        "farm_id": soil_test.farm_id,
        "test_date": soil_test.test_date.isoformat() if soil_test.test_date else None,
        "soil_health_score": float(soil_test.soil_health_score) if soil_test.soil_health_score else None,
        "recommendations": json.loads(soil_test.recommendations) if soil_test.recommendations else []
    }


@router.get("/farm/{farm_id}/history", response_model=List[dict])
async def get_soil_test_history(
    farm_id: int,
    plot_id: Optional[int] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get soil test history for a farm or plot
    """
    try:
        logger.info(f"Fetching soil test history for farm {farm_id}")
        
        # Use service method
        history = await soil_testing_service.get_soil_test_history(
            db, farm_id, plot_id, limit
        )
        
        return history
        
    except Exception as e:
        logger.error(f"Error fetching soil test history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch soil test history"
        )


@router.get("/compare/{previous_test_id}/{current_test_id}", response_model=SoilTestComparison)
async def compare_soil_tests(
    previous_test_id: int,
    current_test_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare two soil tests to track changes over time
    """
    try:
        logger.info(f"Comparing soil tests: {previous_test_id} vs {current_test_id}")
        
        from app.orm.soil_test_result import SoilTestResult
        from sqlalchemy import select
        
        # Fetch both tests
        result = await db.execute(
            select(SoilTestResult).where(SoilTestResult.id.in_([previous_test_id, current_test_id]))
        )
        tests = result.scalars().all()
        
        if len(tests) != 2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both soil test results not found"
            )
        
        # Identify which is previous and which is current
        test_dict = {test.id: test for test in tests}
        previous_test = test_dict[previous_test_id]
        current_test = test_dict[current_test_id]
        
        # Convert to dict for comparison
        previous_data = {
            'nitrogen_kg_per_ha': float(previous_test.nitrogen_kg_per_ha) if previous_test.nitrogen_kg_per_ha else None,
            'phosphorus_kg_per_ha': float(previous_test.phosphorus_kg_per_ha) if previous_test.phosphorus_kg_per_ha else None,
            'potassium_kg_per_ha': float(previous_test.potassium_kg_per_ha) if previous_test.potassium_kg_per_ha else None,
            'ph_level': float(previous_test.ph_level) if previous_test.ph_level else None,
            'organic_carbon_percent': float(previous_test.organic_carbon_percent) if previous_test.organic_carbon_percent else None,
            'electrical_conductivity': float(previous_test.electrical_conductivity) if previous_test.electrical_conductivity else None,
            'zinc_ppm': float(previous_test.zinc_ppm) if previous_test.zinc_ppm else None,
            'soil_health_score': float(previous_test.soil_health_score) if previous_test.soil_health_score else None
        }
        
        current_data = {
            'nitrogen_kg_per_ha': float(current_test.nitrogen_kg_per_ha) if current_test.nitrogen_kg_per_ha else None,
            'phosphorus_kg_per_ha': float(current_test.phosphorus_kg_per_ha) if current_test.phosphorus_kg_per_ha else None,
            'potassium_kg_per_ha': float(current_test.potassium_kg_per_ha) if current_test.potassium_kg_per_ha else None,
            'ph_level': float(current_test.ph_level) if current_test.ph_level else None,
            'organic_carbon_percent': float(current_test.organic_carbon_percent) if current_test.organic_carbon_percent else None,
            'electrical_conductivity': float(current_test.electrical_conductivity) if current_test.electrical_conductivity else None,
            'zinc_ppm': float(current_test.zinc_ppm) if current_test.zinc_ppm else None,
            'soil_health_score': float(current_test.soil_health_score) if current_test.soil_health_score else None
        }
        
        # Compare using service
        changes = soil_testing_service.compare_soil_tests(previous_data, current_data)
        
        # Determine overall trend
        if 'soil_health_score' in changes:
            overall_trend = changes['soil_health_score']['trend']
        else:
            # Count improving vs declining parameters
            improving = sum(1 for c in changes.values() if c.get('trend') == 'improving')
            declining = sum(1 for c in changes.values() if c.get('trend') == 'declining')
            if improving > declining:
                overall_trend = 'improving'
            elif declining > improving:
                overall_trend = 'declining'
            else:
                overall_trend = 'stable'
        
        days_between = (current_test.test_date - previous_test.test_date).days
        
        response = SoilTestComparison(
            previous_test_id=previous_test_id,
            current_test_id=current_test_id,
            previous_test_date=previous_test.test_date,
            current_test_date=current_test.test_date,
            days_between_tests=days_between,
            changes=changes,
            overall_trend=overall_trend
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing soil tests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare soil tests"
        )


@router.post("/calculate-health-score", response_model=SoilHealthAnalysis)
async def calculate_soil_health_score(
    soil_data: dict
):
    """
    Calculate soil health score from provided soil test data
    
    This is a utility endpoint for calculating scores without storing data.
    """
    try:
        logger.info("Calculating soil health score")
        
        # Calculate score
        soil_health_score = soil_testing_service.calculate_soil_health_score(soil_data)
        
        # Generate recommendations
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            soil_data,
            soil_health_score
        )
        
        response = SoilHealthAnalysis(
            soil_health_score=soil_health_score,
            rating=_get_health_rating(soil_health_score),
            recommendations=recommendations,
            parameter_scores={}  # Could add detailed parameter scores here
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error calculating soil health score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate soil health score"
        )


def _get_health_rating(score: float) -> str:
    """Get health rating from score"""
    if score >= 80:
        return "excellent"
    elif score >= 65:
        return "good"
    elif score >= 50:
        return "fair"
    else:
        return "poor"
