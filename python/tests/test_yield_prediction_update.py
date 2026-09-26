"""
Tests for Real-Time Yield Prediction Update Service

Task 25.3: Implement real-time yield prediction updates
Validates: Requirements AC10 (Phase 6 - Required)
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.yield_prediction_update_service import (
    HARVEST_READINESS_THRESHOLD,
    QUALITY_GRADE_THRESHOLDS,
    YieldPredictionUpdateService,
)


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def mock_crop():
    """Mock crop record"""
    crop = Mock()
    crop.id = 1
    crop.crop_name = "Rice"
    crop.crop_variety = "Basmati"
    crop.planting_date = date.today() - timedelta(days=60)
    crop.expected_harvest_date = date.today() + timedelta(days=60)
    crop.expected_yield = 2500.0  # kg
    crop.area = 10.0  # acres
    return crop


@pytest.fixture
def service(mock_db):
    """Create service instance"""
    return YieldPredictionUpdateService(mock_db)


class TestYieldPredictionUpdate:
    """Test yield prediction update functionality"""

    def test_calculate_weather_impact_optimal(self, service):
        """Test weather impact calculation with optimal conditions"""
        weather_conditions = {
            "avg_temperature": 25.0,
            "total_rainfall": 150.0,
            "avg_humidity": 70,
            "extreme_events": 0,
        }

        impact = service._calculate_weather_impact(weather_conditions, "rice")

        # Optimal conditions should give impact close to 1.0
        assert 0.95 <= impact <= 1.05

    def test_calculate_weather_impact_suboptimal(self, service):
        """Test weather impact with suboptimal conditions"""
        weather_conditions = {
            "avg_temperature": 40.0,  # Too hot
            "total_rainfall": 50.0,  # Too dry
            "avg_humidity": 50,
            "extreme_events": 2,  # 2 extreme events
        }

        impact = service._calculate_weather_impact(weather_conditions, "rice")

        # Suboptimal conditions should reduce impact
        assert 0.5 <= impact < 0.9

    def test_calculate_care_impact_excellent(self, service):
        """Test care impact with excellent care"""
        care_metrics = {
            "fertilizer_applied": True,
            "fertilizer_timing_optimal": True,
            "pest_control_done": True,
            "irrigation_adequate": True,
            "weeding_done": True,
        }

        impact = service._calculate_care_impact(care_metrics)

        # Excellent care should give high impact
        assert 1.10 <= impact <= 1.15

    def test_calculate_care_impact_poor(self, service):
        """Test care impact with poor care"""
        care_metrics = {
            "fertilizer_applied": False,
            "fertilizer_timing_optimal": False,
            "pest_control_done": False,
            "irrigation_adequate": False,
            "weeding_done": False,
        }

        impact = service._calculate_care_impact(care_metrics)

        # Poor care should give low impact
        assert 0.7 <= impact <= 0.75

    def test_calculate_prediction_confidence_high(self, service):
        """Test confidence calculation with complete data"""
        confidence = service._calculate_prediction_confidence(
            has_weather=True, has_care_metrics=True, growth_rate_variance=0.05
        )

        # Complete data should give high confidence
        assert 0.90 <= confidence <= 0.95

    def test_calculate_prediction_confidence_low(self, service):
        """Test confidence calculation with incomplete data"""
        confidence = service._calculate_prediction_confidence(
            has_weather=False, has_care_metrics=False, growth_rate_variance=0.4
        )

        # Incomplete data should give lower confidence
        assert 0.60 <= confidence <= 0.75

    @pytest.mark.asyncio
    async def test_adjust_harvest_date_faster_growth(self, service):
        """Test harvest date adjustment with faster growth"""
        # Create crop dict instead of mock
        crop = {
            "id": 1,
            "crop_name": "Rice",
            "planting_date": date.today() - timedelta(days=60),
            "expected_harvest_date": date.today() + timedelta(days=60),
        }

        # Growth rate 1.2 = 20% faster than expected
        adjusted_date = await service._adjust_harvest_date(
            crop=crop,
            growth_rate=1.2,
            current_stage={"stage": "vegetative", "progress_percentage": 60},
        )

        # Should harvest earlier (max 3 days)
        days_diff = (crop["expected_harvest_date"] - adjusted_date).days
        assert 0 <= days_diff <= 3

    @pytest.mark.asyncio
    async def test_adjust_harvest_date_slower_growth(self, service):
        """Test harvest date adjustment with slower growth"""
        # Create crop dict instead of mock
        crop = {
            "id": 1,
            "crop_name": "Rice",
            "planting_date": date.today() - timedelta(days=60),
            "expected_harvest_date": date.today() + timedelta(days=60),
        }

        # Growth rate 0.8 = 20% slower than expected
        adjusted_date = await service._adjust_harvest_date(
            crop=crop,
            growth_rate=0.8,
            current_stage={"stage": "vegetative", "progress_percentage": 40},
        )

        # Should harvest later (max 3 days)
        days_diff = (adjusted_date - crop["expected_harvest_date"]).days
        assert 0 <= days_diff <= 3

    @pytest.mark.asyncio
    async def test_predict_quality_grade_A(self, service):
        """Test quality grade prediction for grade A"""
        quality = await service._predict_quality_grade(
            crop_id=1,
            growth_rate=1.0,
            weather_conditions={
                "avg_temperature": 25.0,
                "total_rainfall": 150.0,
                "avg_humidity": 70,
                "extreme_events": 0,
            },
            care_metrics={
                "fertilizer_applied": True,
                "fertilizer_timing_optimal": True,
                "pest_control_done": True,
                "irrigation_adequate": True,
                "weeding_done": True,
            },
        )

        assert quality["grade"] == "A"
        assert quality["confidence"] >= 0.85
        assert "factors" in quality
        assert "recommendations" in quality

    @pytest.mark.asyncio
    async def test_predict_quality_grade_C(self, service):
        """Test quality grade prediction for grade C"""
        quality = await service._predict_quality_grade(
            crop_id=1,
            growth_rate=0.7,
            weather_conditions={
                "avg_temperature": 40.0,
                "total_rainfall": 50.0,
                "avg_humidity": 50,
                "extreme_events": 2,
            },
            care_metrics={
                "fertilizer_applied": False,
                "pest_control_done": False,
                "irrigation_adequate": False,
                "weeding_done": False,
            },
        )

        assert quality["grade"] in ["C", "D"]
        assert len(quality["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_check_harvest_readiness_not_ready(self, service, mock_db):
        """Test harvest readiness check when not ready"""
        # Mock database query result
        mock_row = Mock()
        mock_row.id = 1
        mock_row.crop_name = "Rice"
        mock_row.planting_date = date.today() - timedelta(days=60)
        mock_row.expected_harvest_date = date.today() + timedelta(days=60)

        mock_result = Mock()
        mock_result.first.return_value = mock_row
        mock_db.execute.return_value = mock_result

        readiness = await service.check_harvest_readiness(1)

        # Should not be ready (only 50% through growing period)
        assert readiness["maturity_percentage"] < 90.0
        assert readiness["is_harvest_ready"] is False
        assert "alert" not in readiness

    @pytest.mark.asyncio
    async def test_check_harvest_readiness_ready(self, service, mock_db):
        """Test harvest readiness check when ready"""
        # Mock database query result for crop near harvest
        mock_row = Mock()
        mock_row.id = 1
        mock_row.crop_name = "Rice"
        mock_row.planting_date = date.today() - timedelta(days=110)
        mock_row.expected_harvest_date = date.today() + timedelta(days=10)

        mock_result = Mock()
        mock_result.first.return_value = mock_row
        mock_db.execute.return_value = mock_result

        readiness = await service.check_harvest_readiness(1)

        # Should be ready (>90% through growing period)
        assert readiness["maturity_percentage"] >= 90.0
        assert readiness["is_harvest_ready"] is True
        assert "alert" in readiness
        assert readiness["alert"]["type"] == "harvest_readiness"
        assert len(readiness["alert"]["recommendations"]) > 0


class TestQualityGradeThresholds:
    """Test quality grade threshold definitions"""

    def test_grade_thresholds_exist(self):
        """Test that all grade thresholds are defined"""
        assert "A" in QUALITY_GRADE_THRESHOLDS
        assert "B" in QUALITY_GRADE_THRESHOLDS
        assert "C" in QUALITY_GRADE_THRESHOLDS

    def test_grade_thresholds_descending(self):
        """Test that grade thresholds are in descending order"""
        assert (
            QUALITY_GRADE_THRESHOLDS["A"]["min_growth_rate"]
            > QUALITY_GRADE_THRESHOLDS["B"]["min_growth_rate"]
        )
        assert (
            QUALITY_GRADE_THRESHOLDS["B"]["min_growth_rate"]
            > QUALITY_GRADE_THRESHOLDS["C"]["min_growth_rate"]
        )

    def test_harvest_readiness_threshold(self):
        """Test harvest readiness threshold is 90%"""
        assert HARVEST_READINESS_THRESHOLD == 0.90


class TestWeeklyUpdateJob:
    """Test weekly update job functionality"""

    @pytest.mark.asyncio
    async def test_weekly_update_job_structure(self, service):
        """Test that weekly update job returns proper structure"""
        # Mock the database queries to return empty list
        with patch.object(service.db, "execute") as mock_execute:
            mock_result = Mock()
            mock_result.fetchall.return_value = []
            mock_execute.return_value = mock_result

            summary = await service.run_weekly_update_job()

            assert "crops_checked" in summary
            assert "predictions_updated" in summary
            assert "harvest_alerts_sent" in summary
            assert "errors" in summary
            assert summary["crops_checked"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
