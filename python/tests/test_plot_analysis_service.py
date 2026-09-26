"""
Unit tests for Plot Analysis Service
Tests comprehensive plot analysis with Bedrock AI integration

Task 26.1: Comprehensive plot analysis API testing
"""

import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.orm.farm_plot import FarmPlot
from app.orm.soil_test_result import SoilTestResult
from app.services.plot_analysis_service import PlotAnalysisService


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_cache_manager():
    """Mock cache manager"""
    cache = Mock()
    cache.enabled = True
    cache.get = Mock(return_value=None)
    cache.set = Mock(return_value=True)
    cache._generate_cache_key = Mock(return_value="test_cache_key")
    return cache


@pytest.fixture
def sample_plot():
    """Sample plot data"""
    plot = Mock(spec=FarmPlot)
    plot.id = 1
    plot.plot_name = "North Field"
    plot.area = Decimal("5.0")
    plot.soil_type = "loamy"
    plot.irrigation_type = "Canal"
    plot.state = "Punjab"
    plot.district = "Ludhiana"
    plot.previous_crops = json.dumps(
        [
            {"crop_name": "Wheat", "year": 2023, "yield": "20 quintals/acre"},
            {"crop_name": "Rice", "year": 2022, "yield": "22 quintals/acre"},
        ]
    )
    return plot


@pytest.fixture
def sample_soil_test():
    """Sample soil test data"""
    soil = Mock(spec=SoilTestResult)
    soil.ph_level = Decimal("7.2")
    soil.nitrogen_kg_per_ha = Decimal("280")
    soil.phosphorus_kg_per_ha = Decimal("15")
    soil.potassium_kg_per_ha = Decimal("250")
    soil.organic_matter_percent = Decimal("1.8")
    soil.soil_health_score = Decimal("85")
    soil.test_date = datetime(2024, 1, 15)
    return soil


@pytest.fixture
def sample_bedrock_response():
    """Sample Bedrock AI response"""
    return {
        "recommended_crops": [
            {
                "rank": 1,
                "crop_name": "Basmati Rice",
                "variety": "Pusa Basmati 1121",
                "suitability_score": 9.2,
                "soil_compatibility": 9.0,
                "water_match": 9.5,
                "climate_suitability": 9.0,
                "investment_per_acre": 18000,
                "expected_yield_per_acre": "22-25 quintals",
                "market_price_per_quintal": 2500,
                "expected_revenue_per_acre": 58750,
                "expected_profit_per_acre": 40750,
                "roi_percentage": 226,
                "breakeven_yield": "7.2 quintals",
                "planting_window": "June 15 - July 15",
                "harvest_window": "October 20 - November 10",
                "duration_days": 120,
                "water_requirement": "High",
                "labor_requirement": "Medium",
                "quality_grade": "A",
                "quality_confidence": 0.87,
                "quality_factors": ["Good soil health", "Adequate water"],
                "demand_level": "High",
                "price_trend": "Stable",
                "export_potential": True,
                "local_market_size": "Large",
                "risk_factors": ["Heavy rainfall during harvest"],
                "risk_probability": "Medium",
                "mitigation_strategies": ["Plan harvest before monsoon withdrawal"],
                "seasonal_weather_pattern": "Monsoon rainfall 700-900mm",
                "planting_timing": "After first good monsoon rains",
                "harvest_timing": "Complete by October",
                "weather_alerts": ["Heavy rainfall possible"],
                "soil_preparation": ["Add organic matter", "Apply lime"],
                "fertilizer_recommendations": ["Nitrogen: 120 kg/ha", "Phosphorus: 60 kg/ha"],
                "irrigation_schedule": "Weekly during dry spells",
                "confidence_score": 0.87,
            }
        ],
        "annual_strategy": {
            "current_season_crop": "Basmati Rice",
            "next_season_crop": "Wheat",
            "total_annual_profit": 82000,
            "annual_roi": 273,
        },
        "plot_health": {
            "soil_health_score": 85,
            "water_resource_score": 90,
            "overall_suitability_score": 87,
        },
        "soil_recommendations": ["Add organic matter", "Test pH regularly"],
        "water_recommendations": ["Maintain irrigation schedule", "Check drainage"],
    }


class TestPlotAnalysisService:
    """Test suite for PlotAnalysisService"""

    @pytest.mark.asyncio
    async def test_analyze_plot_success(
        self, mock_db, mock_cache_manager, sample_plot, sample_soil_test, sample_bedrock_response
    ):
        """Test successful plot analysis"""
        # Setup
        service = PlotAnalysisService(mock_db)
        service.cache_manager = mock_cache_manager

        # Mock database queries
        with (
            patch.object(service, "_get_plot_details", return_value=sample_plot),
            patch.object(service, "_get_latest_soil_test", return_value=sample_soil_test),
            patch.object(service, "_analyze_with_bedrock", return_value=sample_bedrock_response),
        ):

            # Execute
            result = await service.analyze_plot(
                plot_id=1,
                season="kharif",
                budget_per_acre=20000,
                preferences={"risk_tolerance": "medium"},
            )

            # Verify
            assert result is not None
            assert result["plot_id"] == 1
            assert result["plot_name"] == "North Field"
            assert result["season"] == "kharif"
            assert "recommended_crops" in result
            assert len(result["recommended_crops"]) > 0
            assert "annual_strategy" in result
            assert "plot_health" in result

            # Verify cache was set
            mock_cache_manager.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_plot_cache_hit(
        self, mock_db, mock_cache_manager, sample_bedrock_response
    ):
        """Test plot analysis with cache hit"""
        # Setup
        service = PlotAnalysisService(mock_db)
        service.cache_manager = mock_cache_manager

        # Mock cache hit
        cached_result = {
            "plot_id": 1,
            "plot_name": "North Field",
            "season": "kharif",
            **sample_bedrock_response,
        }
        mock_cache_manager.get.return_value = cached_result

        # Execute
        result = await service.analyze_plot(plot_id=1, season="kharif", budget_per_acre=20000)

        # Verify
        assert result == cached_result
        mock_cache_manager.get.assert_called_once()
        # Should not call database or Bedrock
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_analyze_plot_not_found(self, mock_db, mock_cache_manager):
        """Test plot analysis with non-existent plot"""
        # Setup
        service = PlotAnalysisService(mock_db)
        service.cache_manager = mock_cache_manager

        # Mock plot not found
        with patch.object(service, "_get_plot_details", return_value=None):
            # Execute and verify
            with pytest.raises(ValueError, match="Plot 999 not found"):
                await service.analyze_plot(plot_id=999, season="kharif")

    @pytest.mark.asyncio
    async def test_build_plot_profile_with_soil_data(self, mock_db, sample_plot, sample_soil_test):
        """Test building plot profile with soil test data"""
        # Setup
        service = PlotAnalysisService(mock_db)

        # Execute
        profile = service._build_plot_profile(sample_plot, sample_soil_test)

        # Verify
        assert profile["location"]["state"] == "Punjab"
        assert profile["location"]["district"] == "Ludhiana"
        assert profile["area_acres"] == 5.0
        assert profile["soil_data"]["type"] == "loamy"
        assert profile["soil_data"]["ph"] == 7.2
        assert profile["soil_data"]["nitrogen"] == 280
        assert profile["soil_data"]["phosphorus"] == 15
        assert profile["soil_data"]["potassium"] == 250
        assert profile["soil_data"]["organic_matter"] == 1.8
        assert profile["soil_data"]["health_score"] == 85
        assert profile["water_data"]["source"] == "Canal"
        assert len(profile["historical_crops"]) == 2

    @pytest.mark.asyncio
    async def test_build_plot_profile_without_soil_data(self, mock_db, sample_plot):
        """Test building plot profile without soil test data"""
        # Setup
        service = PlotAnalysisService(mock_db)

        # Execute
        profile = service._build_plot_profile(sample_plot, None)

        # Verify
        assert profile["location"]["state"] == "Punjab"
        assert profile["area_acres"] == 5.0
        assert profile["soil_data"]["type"] == "loamy"
        assert profile["soil_data"]["ph"] is None
        assert profile["soil_data"]["nitrogen"] is None
        assert profile["soil_data"]["health_score"] is None

    @pytest.mark.asyncio
    async def test_calculate_profitability(self, mock_db):
        """Test profitability calculation"""
        # Setup
        service = PlotAnalysisService(mock_db)

        crop = {
            "crop_name": "Rice",
            "investment_per_acre": 18000,
            "expected_yield_per_acre": "22-25 quintals",
            "market_price_per_quintal": 2500,
        }

        # Execute
        profitability = await service._calculate_profitability(
            crop=crop, area=5.0, budget_per_acre=20000
        )

        # Verify per-acre metrics
        assert profitability["per_acre"]["investment"] == 18000
        assert profitability["per_acre"]["average_yield"] == 23.5  # Average of 22-25
        assert profitability["per_acre"]["market_price"] == 2500

        # Calculate expected values
        expected_revenue = 23.5 * 2500  # 58750
        expected_profit = expected_revenue - 18000  # 40750
        expected_roi = (expected_profit / 18000) * 100  # 226.39%

        assert abs(profitability["per_acre"]["revenue"] - expected_revenue) < 1
        assert abs(profitability["per_acre"]["profit"] - expected_profit) < 1
        assert abs(profitability["per_acre"]["roi_percentage"] - expected_roi) < 1

        # Verify total plot metrics
        assert profitability["total_plot"]["area_acres"] == 5.0
        assert abs(profitability["total_plot"]["total_investment"] - 90000) < 1
        assert abs(profitability["total_plot"]["total_profit"] - 203750) < 1

        # Verify investment breakdown
        breakdown = profitability["investment_breakdown"]
        assert abs(breakdown["seeds"] - 2700) < 1  # 15%
        assert abs(breakdown["fertilizer"] - 6300) < 1  # 35%
        assert abs(breakdown["labor"] - 5400) < 1  # 30%
        assert abs(breakdown["irrigation"] - 2700) < 1  # 15%
        assert abs(breakdown["other"] - 900) < 1  # 5%

    def test_parse_yield_range(self, mock_db):
        """Test yield range parsing"""
        service = PlotAnalysisService(mock_db)

        # Test range format
        assert service._parse_yield_range("22-25 quintals") == 23.5
        assert service._parse_yield_range("20-30 quintals") == 25.0

        # Test single value
        assert service._parse_yield_range("25 quintals") == 25.0
        assert service._parse_yield_range("20") == 20.0

        # Test invalid format (should return default)
        assert service._parse_yield_range("invalid") == 20.0

    @pytest.mark.asyncio
    async def test_analyze_with_bedrock_success(self, mock_db, sample_bedrock_response):
        """Test Bedrock AI analysis"""
        # Setup
        service = PlotAnalysisService(mock_db)

        plot_profile = {
            "location": {"state": "Punjab", "district": "Ludhiana"},
            "area_acres": 5.0,
            "soil_data": {
                "type": "loamy",
                "ph": 7.2,
                "nitrogen": 280,
                "phosphorus": 15,
                "potassium": 250,
                "organic_matter": 1.8,
                "texture": "Medium",
                "health_score": 85,
            },
            "water_data": {"source": "Canal", "availability": "year-round", "quality": "good"},
            "historical_crops": [],
        }

        # Mock Bedrock service
        with patch("app.services.plot_analysis_service.bedrock_service") as mock_bedrock:
            mock_bedrock._invoke_claude.return_value = json.dumps(sample_bedrock_response)

            # Execute
            result = await service._analyze_with_bedrock(
                plot_profile=plot_profile,
                season="kharif",
                budget_per_acre=20000,
                preferences={"risk_tolerance": "medium"},
            )

            # Verify
            assert result == sample_bedrock_response
            mock_bedrock._invoke_claude.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_with_bedrock_fallback(self, mock_db):
        """Test Bedrock fallback when API fails"""
        # Setup
        service = PlotAnalysisService(mock_db)

        plot_profile = {
            "location": {"state": "Punjab", "district": "Ludhiana"},
            "area_acres": 5.0,
            "soil_data": {"type": "loamy"},
            "water_data": {"source": "Canal"},
            "historical_crops": [],
        }

        # Mock Bedrock service failure
        with patch("app.services.plot_analysis_service.bedrock_service") as mock_bedrock:
            mock_bedrock._invoke_claude.return_value = "Invalid JSON response"

            # Execute
            result = await service._analyze_with_bedrock(
                plot_profile=plot_profile, season="kharif", budget_per_acre=20000, preferences={}
            )

            # Verify fallback response
            assert "recommended_crops" in result
            assert len(result["recommended_crops"]) > 0
            assert "annual_strategy" in result
            assert "plot_health" in result

    @pytest.mark.asyncio
    async def test_create_fallback_analysis(self, mock_db):
        """Test fallback analysis creation"""
        # Setup
        service = PlotAnalysisService(mock_db)

        plot_profile = {
            "location": {"state": "Punjab", "district": "Ludhiana"},
            "area_acres": 5.0,
            "soil_data": {"type": "loamy"},
            "water_data": {"source": "Canal"},
            "historical_crops": [],
        }

        # Execute
        result = service._create_fallback_analysis(plot_profile, "kharif")

        # Verify
        assert "recommended_crops" in result
        assert len(result["recommended_crops"]) > 0
        assert result["recommended_crops"][0]["crop_name"] in ["Rice", "Cotton"]
        assert "annual_strategy" in result
        assert "plot_health" in result
        assert result["plot_health"]["soil_health_score"] == 70

    @pytest.mark.asyncio
    async def test_profitability_with_different_areas(self, mock_db):
        """Test profitability calculation with different plot areas"""
        service = PlotAnalysisService(mock_db)

        crop = {
            "investment_per_acre": 15000,
            "expected_yield_per_acre": "20 quintals",
            "market_price_per_quintal": 2000,
        }

        # Test with 1 acre
        result_1 = await service._calculate_profitability(crop, 1.0, 15000)
        assert result_1["total_plot"]["area_acres"] == 1.0
        assert result_1["total_plot"]["total_investment"] == 15000

        # Test with 10 acres
        result_10 = await service._calculate_profitability(crop, 10.0, 15000)
        assert result_10["total_plot"]["area_acres"] == 10.0
        assert result_10["total_plot"]["total_investment"] == 150000

        # ROI should be same regardless of area
        assert (
            abs(result_1["per_acre"]["roi_percentage"] - result_10["per_acre"]["roi_percentage"])
            < 0.1
        )

    @pytest.mark.asyncio
    async def test_cache_disabled(
        self, mock_db, sample_plot, sample_soil_test, sample_bedrock_response
    ):
        """Test plot analysis with caching disabled"""
        # Setup
        service = PlotAnalysisService(mock_db)
        service.cache_manager = None

        # Mock database queries
        with (
            patch.object(service, "_get_plot_details", return_value=sample_plot),
            patch.object(service, "_get_latest_soil_test", return_value=sample_soil_test),
            patch.object(service, "_analyze_with_bedrock", return_value=sample_bedrock_response),
        ):

            # Execute
            result = await service.analyze_plot(plot_id=1, season="kharif")

            # Verify
            assert result is not None
            assert result["plot_id"] == 1
            # Should work without cache


class TestProfitabilityCalculations:
    """Test suite for profitability calculation accuracy"""

    @pytest.mark.asyncio
    async def test_roi_calculation_accuracy(self, mock_db):
        """Test ROI = (profit / investment) * 100"""
        service = PlotAnalysisService(mock_db)

        crop = {
            "investment_per_acre": 10000,
            "expected_yield_per_acre": "20 quintals",
            "market_price_per_quintal": 2000,
        }

        result = await service._calculate_profitability(crop, 1.0, 10000)

        # Manual calculation
        revenue = 20 * 2000  # 40000
        profit = revenue - 10000  # 30000
        expected_roi = (profit / 10000) * 100  # 300%

        assert abs(result["per_acre"]["roi_percentage"] - expected_roi) < 0.01

    @pytest.mark.asyncio
    async def test_profit_margin_calculation(self, mock_db):
        """Test profit margin = (profit / revenue) * 100"""
        service = PlotAnalysisService(mock_db)

        crop = {
            "investment_per_acre": 15000,
            "expected_yield_per_acre": "25 quintals",
            "market_price_per_quintal": 2500,
        }

        result = await service._calculate_profitability(crop, 1.0, 15000)

        # Manual calculation
        revenue = 25 * 2500  # 62500
        profit = revenue - 15000  # 47500
        expected_margin = (profit / revenue) * 100  # 76%

        assert abs(result["per_acre"]["profit_margin"] - expected_margin) < 0.01

    @pytest.mark.asyncio
    async def test_breakeven_yield_calculation(self, mock_db):
        """Test breakeven yield = investment / market_price"""
        service = PlotAnalysisService(mock_db)

        crop = {
            "investment_per_acre": 18000,
            "expected_yield_per_acre": "20 quintals",
            "market_price_per_quintal": 2000,
        }

        result = await service._calculate_profitability(crop, 1.0, 18000)

        # Manual calculation
        expected_breakeven = 18000 / 2000  # 9.0 quintals

        breakeven_str = result["per_acre"]["breakeven_yield"]
        breakeven_value = float(breakeven_str.split()[0])

        assert abs(breakeven_value - expected_breakeven) < 0.1

    @pytest.mark.asyncio
    async def test_investment_breakdown_totals(self, mock_db):
        """Test investment breakdown sums to total investment"""
        service = PlotAnalysisService(mock_db)

        crop = {
            "investment_per_acre": 20000,
            "expected_yield_per_acre": "20 quintals",
            "market_price_per_quintal": 2000,
        }

        result = await service._calculate_profitability(crop, 1.0, 20000)

        breakdown = result["investment_breakdown"]
        total = (
            breakdown["seeds"]
            + breakdown["fertilizer"]
            + breakdown["labor"]
            + breakdown["irrigation"]
            + breakdown["other"]
        )

        # Should sum to investment_per_acre
        assert abs(total - 20000) < 1

        # Verify percentages
        assert abs(breakdown["seeds"] - 3000) < 1  # 15%
        assert abs(breakdown["fertilizer"] - 7000) < 1  # 35%
        assert abs(breakdown["labor"] - 6000) < 1  # 30%
        assert abs(breakdown["irrigation"] - 3000) < 1  # 15%
        assert abs(breakdown["other"] - 1000) < 1  # 5%
