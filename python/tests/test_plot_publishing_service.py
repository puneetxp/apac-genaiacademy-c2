"""
Unit tests for Plot Publishing Service

Task 27.1: Plot publishing API tests
"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.orm.farm_plot import FarmPlot
from app.orm.user import User
from app.services.plot_publishing_service import PlotPublishingService


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = AsyncMock()
    return db


@pytest.fixture
def mock_plot():
    """Mock farm plot"""
    plot = Mock(spec=FarmPlot)
    plot.id = 1
    plot.farm_id = 100
    plot.plot_name = "North Field"
    plot.area = Decimal("10.5")
    plot.soil_type = "loamy"
    plot.irrigation_type = "canal"
    plot.state = "Punjab"
    plot.district = "Ludhiana"
    plot.previous_crops = "[]"
    plot.investment_capacity = Decimal("20000")
    return plot


@pytest.fixture
def mock_farmer():
    """Mock farmer user"""
    farmer = Mock(spec=User)
    farmer.id = 1
    farmer.email = "farmer@example.com"
    farmer.phone_number = "+919876543210"
    return farmer


@pytest.mark.asyncio
async def test_publish_plot_success(mock_db, mock_plot, mock_farmer):
    """Test successful plot publishing"""

    service = PlotPublishingService(mock_db)

    # Mock database queries
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.side_effect = [mock_plot, mock_farmer]
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = Mock()

    # Mock plot analysis service
    with patch.object(service.plot_analysis_service, "analyze_plot") as mock_analyze:
        mock_analyze.return_value = {
            "recommended_crops": [
                {
                    "crop_name": "Rice",
                    "confidence_score": 0.85,
                    "quality_confidence": 0.80,
                    "suitability_score": 8.5,
                    "risk_probability": "medium",
                }
            ]
        }

        # Publish plot
        result = await service.publish_plot(
            plot_id=1,
            crop_name="Rice",
            crop_variety="Basmati 1121",
            expected_harvest_date="2024-10-15",
            quantity_quintals=50.0,
            quality_grade="A",
            price_per_quintal=2500.0,
            farmer_id=1,
        )

    # Verify result structure
    assert result["plot_id"] == 1
    assert result["plot_name"] == "North Field"
    assert result["status"] == "published"
    assert "listing_id" in result
    assert "crop_details" in result
    assert "plot_characteristics" in result
    assert "ai_predictions" in result
    assert "farmer_contact" in result
    assert "offering_terms" in result

    # Verify crop details
    assert result["crop_details"]["crop_name"] == "Rice"
    assert result["crop_details"]["crop_variety"] == "Basmati 1121"
    assert result["crop_details"]["quantity_quintals"] == 50.0
    assert result["crop_details"]["quantity_kg"] == 5000
    assert result["crop_details"]["quality_grade"] == "A"
    assert result["crop_details"]["price_per_quintal"] == 2500.0

    # Verify plot characteristics
    assert result["plot_characteristics"]["location"]["state"] == "Punjab"
    assert result["plot_characteristics"]["location"]["district"] == "Ludhiana"
    assert result["plot_characteristics"]["area_acres"] == 10.5
    assert result["plot_characteristics"]["soil_type"] == "loamy"
    assert result["plot_characteristics"]["irrigation_type"] == "canal"

    # Verify AI predictions
    assert "yield_confidence" in result["ai_predictions"]
    assert "quality_confidence" in result["ai_predictions"]
    assert "harvest_date_range" in result["ai_predictions"]
    assert result["ai_predictions"]["yield_confidence"] == 0.85
    assert result["ai_predictions"]["quality_confidence"] == 0.80

    # Verify offering terms
    assert result["offering_terms"]["price_per_quintal"] == 2500.0
    assert result["offering_terms"]["total_value"] == 125000.0  # 50 * 2500
    assert result["offering_terms"]["advance_booking_available"] is True


@pytest.mark.asyncio
async def test_publish_plot_not_found(mock_db):
    """Test publishing non-existent plot"""

    service = PlotPublishingService(mock_db)

    # Mock database query returning None
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    # Should raise ValueError
    with pytest.raises(ValueError, match="Plot 999 not found"):
        await service.publish_plot(
            plot_id=999,
            crop_name="Rice",
            crop_variety="Basmati 1121",
            expected_harvest_date="2024-10-15",
            quantity_quintals=50.0,
            quality_grade="A",
            price_per_quintal=2500.0,
            farmer_id=1,
        )


@pytest.mark.asyncio
async def test_generate_ai_predictions_with_analysis(mock_db, mock_plot):
    """Test AI prediction generation with plot analysis"""

    service = PlotPublishingService(mock_db)

    # Mock plot analysis
    with patch.object(service.plot_analysis_service, "analyze_plot") as mock_analyze:
        mock_analyze.return_value = {
            "recommended_crops": [
                {
                    "crop_name": "Rice",
                    "confidence_score": 0.87,
                    "quality_confidence": 0.82,
                    "suitability_score": 9.0,
                    "risk_probability": "low",
                }
            ]
        }

        predictions = await service._generate_ai_predictions(
            plot=mock_plot,
            crop_name="Rice",
            expected_harvest_date="2024-10-15",
            quantity_quintals=50.0,
            quality_grade="A",
        )

    # Verify predictions
    assert predictions["yield_confidence"] == 0.87
    assert predictions["quality_confidence"] == 0.82
    assert predictions["suitability_score"] == 9.0
    assert predictions["risk_level"] == "low"
    assert predictions["ai_analysis_available"] is True
    assert "harvest_date_range" in predictions
    assert "start" in predictions["harvest_date_range"]
    assert "end" in predictions["harvest_date_range"]


@pytest.mark.asyncio
async def test_generate_ai_predictions_fallback(mock_db, mock_plot):
    """Test AI prediction generation with fallback when analysis fails"""

    service = PlotPublishingService(mock_db)

    # Mock plot analysis to raise exception
    with patch.object(service.plot_analysis_service, "analyze_plot") as mock_analyze:
        mock_analyze.side_effect = Exception("Analysis failed")

        predictions = await service._generate_ai_predictions(
            plot=mock_plot,
            crop_name="Rice",
            expected_harvest_date="2024-10-15",
            quantity_quintals=50.0,
            quality_grade="A",
        )

    # Verify fallback predictions
    assert predictions["yield_confidence"] == 0.70
    assert predictions["quality_confidence"] == 0.75
    assert predictions["suitability_score"] == 7.0
    assert predictions["risk_level"] == "medium"
    assert predictions["ai_analysis_available"] is False


@pytest.mark.asyncio
async def test_generate_ai_predictions_crop_not_in_analysis(mock_db, mock_plot):
    """Test AI prediction when crop not found in analysis"""

    service = PlotPublishingService(mock_db)

    # Mock plot analysis with different crop
    with patch.object(service.plot_analysis_service, "analyze_plot") as mock_analyze:
        mock_analyze.return_value = {
            "recommended_crops": [
                {
                    "crop_name": "Wheat",  # Different crop
                    "confidence_score": 0.85,
                    "quality_confidence": 0.80,
                }
            ]
        }

        predictions = await service._generate_ai_predictions(
            plot=mock_plot,
            crop_name="Rice",  # Requesting Rice
            expected_harvest_date="2024-10-15",
            quantity_quintals=50.0,
            quality_grade="A",
        )

    # Should use fallback predictions
    assert predictions["yield_confidence"] == 0.70
    assert predictions["quality_confidence"] == 0.75
    assert predictions["ai_analysis_available"] is False


@pytest.mark.asyncio
async def test_harvest_date_range_calculation(mock_db, mock_plot):
    """Test harvest date range calculation"""

    service = PlotPublishingService(mock_db)

    with patch.object(service.plot_analysis_service, "analyze_plot") as mock_analyze:
        mock_analyze.return_value = {
            "recommended_crops": [
                {
                    "crop_name": "Rice",
                    "confidence_score": 0.85,
                    "quality_confidence": 0.80,
                    "suitability_score": 8.5,
                    "risk_probability": "medium",
                }
            ]
        }

        predictions = await service._generate_ai_predictions(
            plot=mock_plot,
            crop_name="Rice",
            expected_harvest_date="2024-10-15",
            quantity_quintals=50.0,
            quality_grade="A",
        )

    # Verify date range is ±7 days
    harvest_date = datetime(2024, 10, 15).date()
    expected_start = (harvest_date - timedelta(days=7)).isoformat()
    expected_end = (harvest_date + timedelta(days=7)).isoformat()

    assert predictions["harvest_date_range"]["start"] == expected_start
    assert predictions["harvest_date_range"]["end"] == expected_end


@pytest.mark.asyncio
async def test_quantity_conversion_quintals_to_kg(mock_db, mock_plot, mock_farmer):
    """Test quantity conversion from quintals to kg"""

    service = PlotPublishingService(mock_db)

    # Mock database
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.side_effect = [mock_plot, mock_farmer]
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = Mock()

    with patch.object(service.plot_analysis_service, "analyze_plot") as mock_analyze:
        mock_analyze.return_value = {
            "recommended_crops": [
                {
                    "crop_name": "Rice",
                    "confidence_score": 0.85,
                    "quality_confidence": 0.80,
                    "suitability_score": 8.5,
                    "risk_probability": "medium",
                }
            ]
        }

        result = await service.publish_plot(
            plot_id=1,
            crop_name="Rice",
            crop_variety="Basmati 1121",
            expected_harvest_date="2024-10-15",
            quantity_quintals=50.0,
            quality_grade="A",
            price_per_quintal=2500.0,
            farmer_id=1,
        )

    # Verify conversion: 50 quintals = 5000 kg
    assert result["crop_details"]["quantity_quintals"] == 50.0
    assert result["crop_details"]["quantity_kg"] == 5000


@pytest.mark.asyncio
async def test_season_detection_from_harvest_date(mock_db, mock_plot):
    """Test season detection from harvest date"""

    service = PlotPublishingService(mock_db)

    # Test Kharif season (October harvest)
    with patch.object(service.plot_analysis_service, "analyze_plot") as mock_analyze:
        mock_analyze.return_value = {"recommended_crops": []}

        await service._generate_ai_predictions(
            plot=mock_plot,
            crop_name="Rice",
            expected_harvest_date="2024-10-15",
            quantity_quintals=50.0,
            quality_grade="A",
        )

        # Verify analyze_plot was called with 'kharif' season
        mock_analyze.assert_called_once()
        call_args = mock_analyze.call_args[1]
        assert call_args["season"] == "kharif"

    # Test Rabi season (April harvest)
    with patch.object(service.plot_analysis_service, "analyze_plot") as mock_analyze:
        mock_analyze.return_value = {"recommended_crops": []}

        await service._generate_ai_predictions(
            plot=mock_plot,
            crop_name="Wheat",
            expected_harvest_date="2024-04-15",
            quantity_quintals=40.0,
            quality_grade="A",
        )

        call_args = mock_analyze.call_args[1]
        assert call_args["season"] == "rabi"

    # Test Zaid season (July harvest)
    with patch.object(service.plot_analysis_service, "analyze_plot") as mock_analyze:
        mock_analyze.return_value = {"recommended_crops": []}

        await service._generate_ai_predictions(
            plot=mock_plot,
            crop_name="Vegetables",
            expected_harvest_date="2024-07-15",
            quantity_quintals=30.0,
            quality_grade="B",
        )

        call_args = mock_analyze.call_args[1]
        assert call_args["season"] == "zaid"
