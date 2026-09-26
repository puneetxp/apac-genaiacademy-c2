"""
Tests for Fertilizer Tracking Service

Tests:
- Recording fertilizer applications
- Updating soil response data
- Calculating effectiveness scores
- Retrieving application history
- Analyzing fertilizer effectiveness
- Generating usage reports

Validates: Requirements AC9 (Phase 6 - Required)
"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.orm.crop import Crop
from app.orm.farm import Farm
from app.orm.farm_plot import FarmPlot
from app.orm.fertilizer_application import FertilizerApplication
from app.orm.soil_test_result import SoilTestResult
from app.orm.user import User
from app.services.fertilizer_tracking_service import FertilizerTrackingService


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create test user"""
    user = User(
        cognito_user_id="test-user-123",
        email="farmer@test.com",
        phone="+919876543210",
        full_name="Test Farmer",
        user_type="farmer",
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
        soil_type="loamy",
    )
    db_session.add(farm)
    await db_session.commit()
    await db_session.refresh(farm)
    return farm


@pytest.fixture
async def test_plot(db_session: AsyncSession, test_farm):
    """Create test plot"""
    plot = FarmPlot(
        farm_id=test_farm.id, plot_name="Plot 1", area=Decimal("2.5"), soil_type="loamy"
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
        status="growing",
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
        organic_carbon_percent=Decimal("0.8"),
        soil_health_score=Decimal("65.0"),
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
        nitrogen_kg_per_ha=Decimal("200.0"),  # Improved by 50 kg/ha
        phosphorus_kg_per_ha=Decimal("35.0"),  # Improved by 15 kg/ha
        potassium_kg_per_ha=Decimal("220.0"),  # Improved by 40 kg/ha
        ph_level=Decimal("6.8"),
        organic_carbon_percent=Decimal("1.0"),
        soil_health_score=Decimal("72.0"),  # Improved by 7 points
    )
    db_session.add(soil_test)
    await db_session.commit()
    await db_session.refresh(soil_test)
    return soil_test


@pytest.mark.asyncio
async def test_record_application(db_session: AsyncSession, test_farm, test_plot, test_crop):
    """Test recording a fertilizer application"""
    service = FertilizerTrackingService(db_session)

    application = await service.record_application(
        farm_id=test_farm.id,
        application_date=datetime.now(),
        fertilizer_type="urea",
        category="chemical",
        quantity_kg=50.0,
        cost_total=1500.0,
        plot_id=test_plot.id,
        crop_id=test_crop.id,
        area_applied_hectares=1.0,
        nitrogen_kg=23.0,  # Urea is 46% N, so 50kg * 0.46 = 23kg N
        application_method="broadcast",
        growth_stage="vegetative",
        days_after_planting=30,
        recommended_by="system",
    )

    assert application.id is not None
    assert application.farm_id == test_farm.id
    assert application.fertilizer_type == "urea"
    assert application.category == "chemical"
    assert float(application.quantity_kg) == 50.0
    assert float(application.cost_total) == 1500.0
    assert float(application.cost_per_kg) == 30.0  # 1500 / 50
    assert float(application.quantity_per_hectare) == 50.0  # 50 / 1
    assert float(application.cost_per_hectare) == 1500.0  # 1500 / 1
    assert application.application_method == "broadcast"
    assert application.growth_stage == "vegetative"


@pytest.mark.asyncio
async def test_update_soil_response(
    db_session: AsyncSession, test_farm, test_plot, soil_test_before, soil_test_after
):
    """Test updating soil response after fertilizer application"""
    service = FertilizerTrackingService(db_session)

    # Create application with before soil test
    application = await service.record_application(
        farm_id=test_farm.id,
        application_date=datetime.now(),
        fertilizer_type="dap",
        category="chemical",
        quantity_kg=100.0,
        cost_total=3000.0,
        plot_id=test_plot.id,
        area_applied_hectares=2.5,
        nitrogen_kg=18.0,  # DAP is 18% N
        phosphorus_kg=46.0,  # DAP is 46% P2O5
        potassium_kg=0.0,
        soil_test_before_id=soil_test_before.id,
    )

    # Update with after soil test
    updated = await service.update_soil_response(
        application_id=application.id,
        soil_test_after_id=soil_test_after.id,
        soil_response_notes="Good crop response, healthy green color",
    )

    assert updated.soil_test_after_id == soil_test_after.id
    assert updated.soil_response_notes == "Good crop response, healthy green color"
    assert updated.effectiveness_score is not None
    assert float(updated.effectiveness_score) > 0
    # With good nutrient improvements, score should be decent
    assert float(updated.effectiveness_score) >= 50


@pytest.mark.asyncio
async def test_effectiveness_score_calculation(
    db_session: AsyncSession, test_farm, test_plot, soil_test_before, soil_test_after
):
    """Test effectiveness score calculation logic"""
    service = FertilizerTrackingService(db_session)

    # Create application with realistic NPK values
    application = await service.record_application(
        farm_id=test_farm.id,
        application_date=datetime.now(),
        fertilizer_type="npk_complex",
        category="chemical",
        quantity_kg=100.0,
        cost_total=4000.0,
        plot_id=test_plot.id,
        area_applied_hectares=2.5,
        nitrogen_kg=50.0,  # Applied 50 kg N
        phosphorus_kg=20.0,  # Applied 20 kg P
        potassium_kg=50.0,  # Applied 50 kg K
        soil_test_before_id=soil_test_before.id,
    )

    # Update with after soil test
    updated = await service.update_soil_response(
        application_id=application.id, soil_test_after_id=soil_test_after.id
    )

    # Verify effectiveness score is calculated
    assert updated.effectiveness_score is not None
    score = float(updated.effectiveness_score)

    # Score should be between 0 and 100
    assert 0 <= score <= 100

    # With improvements in N (50 kg), P (15 kg), K (40 kg), and health (7 points)
    # Score should be reasonably good
    assert score >= 40


@pytest.mark.asyncio
async def test_get_application_history(db_session: AsyncSession, test_farm, test_plot):
    """Test retrieving application history with filters"""
    service = FertilizerTrackingService(db_session)

    # Create multiple applications
    dates = [
        datetime.now() - timedelta(days=60),
        datetime.now() - timedelta(days=30),
        datetime.now() - timedelta(days=10),
    ]

    for i, date in enumerate(dates):
        await service.record_application(
            farm_id=test_farm.id,
            application_date=date,
            fertilizer_type="urea" if i % 2 == 0 else "dap",
            category="chemical",
            quantity_kg=50.0 + (i * 10),
            cost_total=1500.0 + (i * 500),
            plot_id=test_plot.id,
        )

    # Get all applications
    all_apps = await service.get_application_history(farm_id=test_farm.id)
    assert len(all_apps) == 3

    # Get applications by plot
    plot_apps = await service.get_application_history(farm_id=test_farm.id, plot_id=test_plot.id)
    assert len(plot_apps) == 3

    # Get applications by date range
    recent_apps = await service.get_application_history(
        farm_id=test_farm.id, start_date=datetime.now() - timedelta(days=40)
    )
    assert len(recent_apps) == 2

    # Get applications by fertilizer type
    urea_apps = await service.get_application_history(farm_id=test_farm.id, fertilizer_type="urea")
    assert len(urea_apps) == 2


@pytest.mark.asyncio
async def test_analyze_fertilizer_effectiveness(
    db_session: AsyncSession, test_farm, test_plot, soil_test_before, soil_test_after
):
    """Test fertilizer effectiveness analysis"""
    service = FertilizerTrackingService(db_session)

    # Create applications with different types and effectiveness
    app1 = await service.record_application(
        farm_id=test_farm.id,
        application_date=datetime.now() - timedelta(days=60),
        fertilizer_type="urea",
        category="chemical",
        quantity_kg=50.0,
        cost_total=1500.0,
        nitrogen_kg=23.0,
        soil_test_before_id=soil_test_before.id,
    )

    app2 = await service.record_application(
        farm_id=test_farm.id,
        application_date=datetime.now() - timedelta(days=30),
        fertilizer_type="vermicompost",
        category="organic",
        quantity_kg=200.0,
        cost_total=2000.0,
        nitrogen_kg=10.0,
        phosphorus_kg=5.0,
        potassium_kg=8.0,
    )

    # Update first application with effectiveness
    await service.update_soil_response(
        application_id=app1.id, soil_test_after_id=soil_test_after.id
    )

    # Analyze effectiveness
    analysis = await service.analyze_fertilizer_effectiveness(farm_id=test_farm.id)

    assert analysis["total_applications"] == 2
    assert analysis["total_cost"] > 0
    assert "by_fertilizer_type" in analysis
    assert "urea" in analysis["by_fertilizer_type"]
    assert "vermicompost" in analysis["by_fertilizer_type"]
    assert "by_category" in analysis
    assert "chemical" in analysis["by_category"]
    assert "organic" in analysis["by_category"]
    assert "recommendations" in analysis
    assert len(analysis["recommendations"]) > 0


@pytest.mark.asyncio
async def test_generate_usage_report(db_session: AsyncSession, test_farm, test_plot):
    """Test generating comprehensive usage report"""
    service = FertilizerTrackingService(db_session)

    # Create applications over several months
    base_date = datetime.now() - timedelta(days=180)

    for i in range(6):
        await service.record_application(
            farm_id=test_farm.id,
            application_date=base_date + timedelta(days=i * 30),
            fertilizer_type="urea" if i % 2 == 0 else "dap",
            category="chemical",
            quantity_kg=50.0 + (i * 5),
            cost_total=1500.0 + (i * 200),
            nitrogen_kg=20.0 + (i * 2),
            phosphorus_kg=10.0 if i % 2 == 1 else 0,
            potassium_kg=5.0,
        )

    # Generate report
    report = await service.generate_usage_report(
        farm_id=test_farm.id, start_date=base_date, end_date=datetime.now()
    )

    assert "report_period" in report
    assert "summary" in report
    assert report["summary"]["total_applications"] == 6
    assert report["summary"]["total_cost"] > 0
    assert "nutrients_applied" in report
    assert report["nutrients_applied"]["nitrogen_kg"] > 0
    assert "monthly_breakdown" in report
    assert len(report["monthly_breakdown"]) > 0
    assert "effectiveness_analysis" in report
    assert "cost_optimization_tips" in report
    assert len(report["cost_optimization_tips"]) > 0


@pytest.mark.asyncio
async def test_cost_optimization_tips(db_session: AsyncSession, test_farm):
    """Test cost optimization tips generation"""
    service = FertilizerTrackingService(db_session)

    # Create expensive chemical applications
    for i in range(3):
        await service.record_application(
            farm_id=test_farm.id,
            application_date=datetime.now() - timedelta(days=i * 20),
            fertilizer_type="expensive_chemical",
            category="chemical",
            quantity_kg=50.0,
            cost_total=5000.0,  # High cost
            nitrogen_kg=20.0,
        )

    # Create cheap organic application
    await service.record_application(
        farm_id=test_farm.id,
        application_date=datetime.now() - timedelta(days=10),
        fertilizer_type="vermicompost",
        category="organic",
        quantity_kg=100.0,
        cost_total=500.0,  # Low cost
        nitrogen_kg=5.0,
    )

    # Generate report
    report = await service.generate_usage_report(farm_id=test_farm.id)

    tips = report["cost_optimization_tips"]
    assert len(tips) > 0

    # Should recommend increasing organic fertilizer usage
    organic_tip_found = any("organic" in tip.lower() for tip in tips)
    assert organic_tip_found


@pytest.mark.asyncio
async def test_application_with_weather_data(db_session: AsyncSession, test_farm):
    """Test recording application with weather conditions"""
    service = FertilizerTrackingService(db_session)

    application = await service.record_application(
        farm_id=test_farm.id,
        application_date=datetime.now(),
        fertilizer_type="urea",
        category="chemical",
        quantity_kg=50.0,
        cost_total=1500.0,
        weather_conditions="Sunny, dry",
        temperature_celsius=28.5,
        rainfall_mm_24h=0.0,
    )

    assert application.weather_conditions == "Sunny, dry"
    assert float(application.temperature_celsius) == 28.5
    assert float(application.rainfall_mm_24h) == 0.0


@pytest.mark.asyncio
async def test_roi_score_calculation(
    db_session: AsyncSession, test_farm, soil_test_before, soil_test_after
):
    """Test ROI score calculation in effectiveness analysis"""
    service = FertilizerTrackingService(db_session)

    # Create high-effectiveness, low-cost application
    app1 = await service.record_application(
        farm_id=test_farm.id,
        application_date=datetime.now() - timedelta(days=30),
        fertilizer_type="efficient_fertilizer",
        category="chemical",
        quantity_kg=50.0,
        cost_total=1000.0,  # Low cost
        nitrogen_kg=25.0,
        phosphorus_kg=20.0,
        potassium_kg=40.0,
        soil_test_before_id=soil_test_before.id,
    )

    # Update with good effectiveness
    await service.update_soil_response(
        application_id=app1.id, soil_test_after_id=soil_test_after.id
    )

    # Analyze
    analysis = await service.analyze_fertilizer_effectiveness(farm_id=test_farm.id)

    # Check ROI score is calculated
    fert_data = analysis["by_fertilizer_type"]["efficient_fertilizer"]
    assert "roi_score" in fert_data
    assert fert_data["roi_score"] > 0
