"""
Tests for Fertilizer Tracking API Endpoints

Tests:
- POST /fertilizer-tracking/applications - Record application
- PUT /fertilizer-tracking/applications/{id}/soil-response - Update soil response
- GET /fertilizer-tracking/applications - Get application history
- GET /fertilizer-tracking/effectiveness-analysis - Analyze effectiveness
- GET /fertilizer-tracking/usage-report - Generate usage report

Validates: Requirements AC9 (Phase 6 - Required)
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.orm.farm import Farm
from app.orm.farm_plot import FarmPlot
from app.orm.crop import Crop
from app.orm.soil_test_result import SoilTestResult
from app.orm.user import User


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create test user"""
    user = User(
        cognito_user_id="test-user-123",
        email="farmer@test.com",
        phone="+919876543210",
        full_name="Test Farmer",
        user_type="farmer"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_farm(db_session: AsyncSession, test_user):
    """Create test farm"""
    farm = Farm(
        farmer_id=test_user.id,
        name="Test Farm",
        state="Maharashtra",
        district="Pune",
        pincode="411001",
        village="Test Village",
        total_area=Decimal("10.0"),
        soil_type="loamy"
    )
    db_session.add(farm)
    await db_session.commit()
    await db_session.refresh(farm)
    return farm


@pytest.fixture
async def test_plot(db_session: AsyncSession, test_farm):
    """Create test plot"""
    plot = FarmPlot(
        farm_id=test_farm.id,
        plot_name="Plot 1",
        area=Decimal("2.5"),
        soil_type="loamy"
    )
    db_session.add(plot)
    await db_session.commit()
    await db_session.refresh(plot)
    return plot


@pytest.fixture
async def test_crop(db_session: AsyncSession, test_plot):
    """Create test crop"""
    crop = Crop(
        farm_plot_id=test_plot.id,
        crop_name="Wheat",
        season="rabi",
        planting_date=datetime.now() - timedelta(days=30),
        expected_harvest_date=datetime.now() + timedelta(days=90),
        area=Decimal("2.5"),
        status="growing"
    )
    db_session.add(crop)
    await db_session.commit()
    await db_session.refresh(crop)
    return crop


@pytest.fixture
async def soil_test_before(db_session: AsyncSession, test_farm, test_plot):
    """Create soil test before fertilizer application"""
    soil_test = SoilTestResult(
        farm_id=test_farm.id,
        plot_id=test_plot.id,
        test_date=datetime.now() - timedelta(days=5),
        nitrogen_kg_per_ha=Decimal("150.0"),
        phosphorus_kg_per_ha=Decimal("20.0"),
        potassium_kg_per_ha=Decimal("180.0"),
        ph_level=Decimal("6.5"),
        soil_health_score=Decimal("65.0")
    )
    db_session.add(soil_test)
    await db_session.commit()
    await db_session.refresh(soil_test)
    return soil_test


@pytest.fixture
async def soil_test_after(db_session: AsyncSession, test_farm, test_plot):
    """Create soil test after fertilizer application"""
    soil_test = SoilTestResult(
        farm_id=test_farm.id,
        plot_id=test_plot.id,
        test_date=datetime.now() + timedelta(days=30),
        nitrogen_kg_per_ha=Decimal("200.0"),
        phosphorus_kg_per_ha=Decimal("35.0"),
        potassium_kg_per_ha=Decimal("220.0"),
        ph_level=Decimal("6.8"),
        soil_health_score=Decimal("72.0")
    )
    db_session.add(soil_test)
    await db_session.commit()
    await db_session.refresh(soil_test)
    return soil_test


@pytest.mark.asyncio
async def test_record_fertilizer_application(
    async_client: AsyncClient,
    test_farm,
    test_plot,
    test_crop
):
    """Test POST /fertilizer-tracking/applications"""
    application_data = {
        "farm_id": test_farm.id,
        "application_date": datetime.now().isoformat(),
        "fertilizer_type": "urea",
        "category": "chemical",
        "quantity_kg": 50.0,
        "cost_total": 1500.0,
        "plot_id": test_plot.id,
        "crop_id": test_crop.id,
        "area_applied_hectares": 1.0,
        "nitrogen_kg": 23.0,
        "application_method": "broadcast",
        "growth_stage": "vegetative",
        "days_after_planting": 30,
        "recommended_by": "system"
    }
    
    response = await async_client.post(
        "/fertilizer-tracking/applications",
        json=application_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["farm_id"] == test_farm.id
    assert data["fertilizer_type"] == "urea"
    assert data["category"] == "chemical"
    assert data["quantity_kg"] == 50.0
    assert data["cost_total"] == 1500.0
    assert data["cost_per_kg"] == 30.0
    assert data["quantity_per_hectare"] == 50.0
    assert data["application_method"] == "broadcast"


@pytest.mark.asyncio
async def test_update_soil_response(
    async_client: AsyncClient,
    test_farm,
    test_plot,
    soil_test_before,
    soil_test_after
):
    """Test PUT /fertilizer-tracking/applications/{id}/soil-response"""
    # First create an application
    application_data = {
        "farm_id": test_farm.id,
        "application_date": datetime.now().isoformat(),
        "fertilizer_type": "dap",
        "category": "chemical",
        "quantity_kg": 100.0,
        "cost_total": 3000.0,
        "plot_id": test_plot.id,
        "area_applied_hectares": 2.5,
        "nitrogen_kg": 18.0,
        "phosphorus_kg": 46.0,
        "soil_test_before_id": soil_test_before.id
    }
    
    create_response = await async_client.post(
        "/fertilizer-tracking/applications",
        json=application_data
    )
    assert create_response.status_code == 201
    application_id = create_response.json()["id"]
    
    # Update with soil response
    response_data = {
        "soil_test_after_id": soil_test_after.id,
        "soil_response_notes": "Good crop response observed"
    }
    
    response = await async_client.put(
        f"/fertilizer-tracking/applications/{application_id}/soil-response",
        json=response_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["soil_test_after_id"] == soil_test_after.id
    assert data["soil_response_notes"] == "Good crop response observed"
    assert data["effectiveness_score"] is not None
    assert data["effectiveness_score"] > 0


@pytest.mark.asyncio
async def test_get_application_history(
    async_client: AsyncClient,
    test_farm,
    test_plot
):
    """Test GET /fertilizer-tracking/applications"""
    # Create multiple applications
    for i in range(3):
        application_data = {
            "farm_id": test_farm.id,
            "application_date": (datetime.now() - timedelta(days=i * 20)).isoformat(),
            "fertilizer_type": "urea" if i % 2 == 0 else "dap",
            "category": "chemical",
            "quantity_kg": 50.0 + (i * 10),
            "cost_total": 1500.0 + (i * 500),
            "plot_id": test_plot.id
        }
        
        response = await async_client.post(
            "/fertilizer-tracking/applications",
            json=application_data
        )
        assert response.status_code == 201
    
    # Get all applications
    response = await async_client.get(
        f"/fertilizer-tracking/applications?farm_id={test_farm.id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(app["farm_id"] == test_farm.id for app in data)


@pytest.mark.asyncio
async def test_get_application_history_with_filters(
    async_client: AsyncClient,
    test_farm,
    test_plot
):
    """Test GET /fertilizer-tracking/applications with filters"""
    # Create applications with different types
    urea_data = {
        "farm_id": test_farm.id,
        "application_date": datetime.now().isoformat(),
        "fertilizer_type": "urea",
        "category": "chemical",
        "quantity_kg": 50.0,
        "cost_total": 1500.0,
        "plot_id": test_plot.id
    }
    
    dap_data = {
        "farm_id": test_farm.id,
        "application_date": datetime.now().isoformat(),
        "fertilizer_type": "dap",
        "category": "chemical",
        "quantity_kg": 100.0,
        "cost_total": 3000.0,
        "plot_id": test_plot.id
    }
    
    await async_client.post("/fertilizer-tracking/applications", json=urea_data)
    await async_client.post("/fertilizer-tracking/applications", json=dap_data)
    
    # Filter by fertilizer type
    response = await async_client.get(
        f"/fertilizer-tracking/applications?farm_id={test_farm.id}&fertilizer_type=urea"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["fertilizer_type"] == "urea"


@pytest.mark.asyncio
async def test_analyze_fertilizer_effectiveness(
    async_client: AsyncClient,
    test_farm,
    test_plot,
    soil_test_before,
    soil_test_after
):
    """Test GET /fertilizer-tracking/effectiveness-analysis"""
    # Create applications
    app1_data = {
        "farm_id": test_farm.id,
        "application_date": (datetime.now() - timedelta(days=60)).isoformat(),
        "fertilizer_type": "urea",
        "category": "chemical",
        "quantity_kg": 50.0,
        "cost_total": 1500.0,
        "nitrogen_kg": 23.0,
        "soil_test_before_id": soil_test_before.id
    }
    
    app2_data = {
        "farm_id": test_farm.id,
        "application_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "fertilizer_type": "vermicompost",
        "category": "organic",
        "quantity_kg": 200.0,
        "cost_total": 2000.0,
        "nitrogen_kg": 10.0
    }
    
    # Create first application
    create_response = await async_client.post(
        "/fertilizer-tracking/applications",
        json=app1_data
    )
    app1_id = create_response.json()["id"]
    
    # Create second application
    await async_client.post(
        "/fertilizer-tracking/applications",
        json=app2_data
    )
    
    # Update first with effectiveness
    await async_client.put(
        f"/fertilizer-tracking/applications/{app1_id}/soil-response",
        json={"soil_test_after_id": soil_test_after.id}
    )
    
    # Get effectiveness analysis
    response = await async_client.get(
        f"/fertilizer-tracking/effectiveness-analysis?farm_id={test_farm.id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_applications"] == 2
    assert data["total_cost"] > 0
    assert "by_fertilizer_type" in data
    assert "urea" in data["by_fertilizer_type"]
    assert "vermicompost" in data["by_fertilizer_type"]
    assert "by_category" in data
    assert "chemical" in data["by_category"]
    assert "organic" in data["by_category"]
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0


@pytest.mark.asyncio
async def test_generate_usage_report(
    async_client: AsyncClient,
    test_farm,
    test_plot
):
    """Test GET /fertilizer-tracking/usage-report"""
    # Create applications over time
    base_date = datetime.now() - timedelta(days=180)
    
    for i in range(4):
        application_data = {
            "farm_id": test_farm.id,
            "application_date": (base_date + timedelta(days=i * 45)).isoformat(),
            "fertilizer_type": "urea" if i % 2 == 0 else "dap",
            "category": "chemical",
            "quantity_kg": 50.0 + (i * 5),
            "cost_total": 1500.0 + (i * 200),
            "nitrogen_kg": 20.0 + (i * 2),
            "phosphorus_kg": 10.0 if i % 2 == 1 else 0.0,
            "potassium_kg": 5.0
        }
        
        response = await async_client.post(
            "/fertilizer-tracking/applications",
            json=application_data
        )
        assert response.status_code == 201
    
    # Generate usage report
    response = await async_client.get(
        f"/fertilizer-tracking/usage-report?farm_id={test_farm.id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "report_period" in data
    assert "summary" in data
    assert data["summary"]["total_applications"] == 4
    assert data["summary"]["total_cost"] > 0
    assert "nutrients_applied" in data
    assert data["nutrients_applied"]["nitrogen_kg"] > 0
    assert "monthly_breakdown" in data
    assert "effectiveness_analysis" in data
    assert "cost_optimization_tips" in data
    assert len(data["cost_optimization_tips"]) > 0


@pytest.mark.asyncio
async def test_usage_report_with_date_range(
    async_client: AsyncClient,
    test_farm
):
    """Test usage report with custom date range"""
    # Create applications
    old_date = datetime.now() - timedelta(days=400)
    recent_date = datetime.now() - timedelta(days=30)
    
    old_app = {
        "farm_id": test_farm.id,
        "application_date": old_date.isoformat(),
        "fertilizer_type": "urea",
        "category": "chemical",
        "quantity_kg": 50.0,
        "cost_total": 1500.0
    }
    
    recent_app = {
        "farm_id": test_farm.id,
        "application_date": recent_date.isoformat(),
        "fertilizer_type": "dap",
        "category": "chemical",
        "quantity_kg": 100.0,
        "cost_total": 3000.0
    }
    
    await async_client.post("/fertilizer-tracking/applications", json=old_app)
    await async_client.post("/fertilizer-tracking/applications", json=recent_app)
    
    # Get report for last 60 days only
    start_date = (datetime.now() - timedelta(days=60)).isoformat()
    end_date = datetime.now().isoformat()
    
    response = await async_client.get(
        f"/fertilizer-tracking/usage-report"
        f"?farm_id={test_farm.id}&start_date={start_date}&end_date={end_date}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only include recent application
    assert data["summary"]["total_applications"] == 1


@pytest.mark.asyncio
async def test_invalid_application_id(async_client: AsyncClient, soil_test_after):
    """Test updating non-existent application"""
    response = await async_client.put(
        "/fertilizer-tracking/applications/99999/soil-response",
        json={"soil_test_after_id": soil_test_after.id}
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_application_with_all_fields(
    async_client: AsyncClient,
    test_farm,
    test_plot,
    test_crop,
    soil_test_before
):
    """Test creating application with all optional fields"""
    application_data = {
        "farm_id": test_farm.id,
        "application_date": datetime.now().isoformat(),
        "fertilizer_type": "npk_complex",
        "category": "chemical",
        "quantity_kg": 100.0,
        "cost_total": 4000.0,
        "plot_id": test_plot.id,
        "crop_id": test_crop.id,
        "area_applied_hectares": 2.5,
        "nitrogen_kg": 20.0,
        "phosphorus_kg": 20.0,
        "potassium_kg": 20.0,
        "application_method": "banding",
        "growth_stage": "flowering",
        "days_after_planting": 60,
        "soil_test_before_id": soil_test_before.id,
        "weather_conditions": "Sunny, dry",
        "temperature_celsius": 28.5,
        "rainfall_mm_24h": 0.0,
        "recommended_by": "agronomist",
        "recommendation_id": "REC-2024-001",
        "notes": "Applied during optimal conditions"
    }
    
    response = await async_client.post(
        "/fertilizer-tracking/applications",
        json=application_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["fertilizer_type"] == "npk_complex"
    assert data["application_method"] == "banding"
    assert data["growth_stage"] == "flowering"
    assert data["weather_conditions"] == "Sunny, dry"
    assert data["temperature_celsius"] == 28.5
    assert data["recommended_by"] == "agronomist"
    assert data["notes"] == "Applied during optimal conditions"
