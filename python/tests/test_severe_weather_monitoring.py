"""
Tests for Severe Weather Monitoring System
Task 23.2: Implement Severe Weather Monitoring
Validates: Requirements AC8 (Phase 6 - Required)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.severe_weather_service import SevereWeatherService
from app.services.weather_service import WeatherService


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    return db


@pytest.fixture
def mock_weather_service():
    """Mock weather service"""
    service = AsyncMock(spec=WeatherService)
    return service


@pytest.fixture
def severe_weather_service(mock_db, mock_weather_service):
    """Create severe weather service instance"""
    return SevereWeatherService(db=mock_db, weather_service=mock_weather_service)


class TestSevereWeatherDetection:
    """Test severe weather detection functionality"""
    
    @pytest.mark.asyncio
    async def test_detect_heavy_rain(self, severe_weather_service, mock_weather_service):
        """Test detection of heavy rainfall (> 50mm)"""
        # Mock forecast with heavy rain
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "rainfall": 75.0,
                    "temp_max": 30.0,
                    "temp_min": 22.0,
                    "humidity": 85,
                    "wind_speed": 10.0
                }
            ]
        }
        
        mock_weather_service.get_weather_alerts.return_value = []
        
        # Detect severe weather
        alerts = await severe_weather_service.detect_severe_weather(
            latitude=28.6139, longitude=77.2090
        )
        
        # Verify heavy rain alert
        assert len(alerts) > 0
        heavy_rain_alerts = [a for a in alerts if a["alert_type"] == "heavy_rain"]
        assert len(heavy_rain_alerts) == 1
        assert heavy_rain_alerts[0]["rainfall"] == 75.0
        assert heavy_rain_alerts[0]["severity"] in ["medium", "high"]
    
    @pytest.mark.asyncio
    async def test_detect_extreme_heat(self, severe_weather_service, mock_weather_service):
        """Test detection of extreme heat (> 40°C)"""
        # Mock forecast with extreme heat
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=2),
                    "rainfall": 0.0,
                    "temp_max": 43.0,
                    "temp_min": 28.0,
                    "humidity": 40,
                    "wind_speed": 8.0
                }
            ]
        }
        
        mock_weather_service.get_weather_alerts.return_value = []
        
        # Detect severe weather
        alerts = await severe_weather_service.detect_severe_weather(
            latitude=28.6139, longitude=77.2090
        )
        
        # Verify extreme heat alert
        assert len(alerts) > 0
        heat_alerts = [a for a in alerts if a["alert_type"] == "extreme_heat"]
        assert len(heat_alerts) == 1
        assert heat_alerts[0]["temperature"] == 43.0
        assert heat_alerts[0]["severity"] in ["medium", "high"]
    
    @pytest.mark.asyncio
    async def test_detect_extreme_cold(self, severe_weather_service, mock_weather_service):
        """Test detection of extreme cold (< 5°C)"""
        # Mock forecast with extreme cold
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "rainfall": 0.0,
                    "temp_max": 10.0,
                    "temp_min": 3.0,
                    "humidity": 60,
                    "wind_speed": 5.0
                }
            ]
        }
        
        mock_weather_service.get_weather_alerts.return_value = []
        
        # Detect severe weather
        alerts = await severe_weather_service.detect_severe_weather(
            latitude=28.6139, longitude=77.2090
        )
        
        # Verify extreme cold alert
        assert len(alerts) > 0
        cold_alerts = [a for a in alerts if a["alert_type"] == "extreme_cold"]
        assert len(cold_alerts) == 1
        assert cold_alerts[0]["temperature"] == 3.0
        assert cold_alerts[0]["severity"] == "high"
    
    @pytest.mark.asyncio
    async def test_detect_high_winds(self, severe_weather_service, mock_weather_service):
        """Test detection of high winds (> 15 m/s)"""
        # Mock forecast with high winds
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "rainfall": 10.0,
                    "temp_max": 28.0,
                    "temp_min": 20.0,
                    "humidity": 70,
                    "wind_speed": 18.0
                }
            ]
        }
        
        mock_weather_service.get_weather_alerts.return_value = []
        
        # Detect severe weather
        alerts = await severe_weather_service.detect_severe_weather(
            latitude=28.6139, longitude=77.2090
        )
        
        # Verify storm alert
        assert len(alerts) > 0
        storm_alerts = [a for a in alerts if a["alert_type"] == "storm"]
        assert len(storm_alerts) == 1
        assert storm_alerts[0]["wind_speed"] == 18.0
    
    @pytest.mark.asyncio
    async def test_detect_cyclone_warning(self, severe_weather_service, mock_weather_service):
        """Test detection of cyclone warnings"""
        # Mock forecast
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "rainfall": 20.0,
                    "temp_max": 30.0,
                    "temp_min": 24.0,
                    "humidity": 85,
                    "wind_speed": 12.0
                }
            ]
        }
        
        # Mock cyclone alert
        mock_weather_service.get_weather_alerts.return_value = [
            {
                "event_type": "cyclone",
                "start_time": datetime.now() + timedelta(days=1),
                "headline": "Cyclone Warning",
                "description": "Severe cyclone approaching coastal areas"
            }
        ]
        
        # Detect severe weather
        alerts = await severe_weather_service.detect_severe_weather(
            latitude=13.0827, longitude=80.2707, state="Tamil Nadu"
        )
        
        # Verify cyclone alert
        assert len(alerts) > 0
        cyclone_alerts = [a for a in alerts if a["alert_type"] == "cyclone"]
        assert len(cyclone_alerts) == 1
        assert cyclone_alerts[0]["severity"] == "critical"
    
    @pytest.mark.asyncio
    async def test_multiple_severe_conditions(self, severe_weather_service, mock_weather_service):
        """Test detection of multiple severe weather conditions"""
        # Mock forecast with multiple severe conditions
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "rainfall": 80.0,  # Heavy rain
                    "temp_max": 42.0,  # Extreme heat
                    "temp_min": 28.0,
                    "humidity": 90,
                    "wind_speed": 20.0  # High winds
                }
            ]
        }
        
        mock_weather_service.get_weather_alerts.return_value = []
        
        # Detect severe weather
        alerts = await severe_weather_service.detect_severe_weather(
            latitude=28.6139, longitude=77.2090
        )
        
        # Verify multiple alerts
        assert len(alerts) >= 3
        alert_types = [a["alert_type"] for a in alerts]
        assert "heavy_rain" in alert_types
        assert "extreme_heat" in alert_types
        assert "storm" in alert_types


class TestHarvestWindowAnalysis:
    """Test harvest window analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_identify_dry_periods(self, severe_weather_service, mock_weather_service):
        """Test identification of dry periods for harvest"""
        # Mock 14-day forecast with dry period
        forecasts = []
        for i in range(14):
            rainfall = 0.0 if 3 <= i <= 7 else 15.0  # 5-day dry period
            forecasts.append({
                "date": datetime.now() + timedelta(days=i),
                "rainfall": rainfall,
                "temp_max": 30.0,
                "temp_min": 20.0,
                "humidity": 60,
                "wind_speed": 8.0
            })
        
        mock_weather_service.get_forecast.return_value = {
            "forecasts": forecasts
        }
        
        # Analyze harvest windows
        analysis = await severe_weather_service.analyze_harvest_windows(
            latitude=28.6139, longitude=77.2090, days_ahead=14
        )
        
        # Verify dry period identified
        assert "dry_periods" in analysis
        assert len(analysis["dry_periods"]) > 0
        assert analysis["dry_periods"][0]["days"] == 5
        assert analysis["optimal_window"] is not None
    
    @pytest.mark.asyncio
    async def test_harvest_suitability_scoring(self, severe_weather_service, mock_weather_service):
        """Test harvest window suitability scoring"""
        # Mock forecast with multiple dry periods
        forecasts = []
        for i in range(14):
            # First period: 3 days, good conditions
            if 1 <= i <= 3:
                rainfall = 0.0
                temp = 28.0
                humidity = 55
            # Second period: 5 days, excellent conditions
            elif 7 <= i <= 11:
                rainfall = 0.0
                temp = 25.0
                humidity = 50
            else:
                rainfall = 20.0
                temp = 30.0
                humidity = 75
            
            forecasts.append({
                "date": datetime.now() + timedelta(days=i),
                "rainfall": rainfall,
                "temp_max": temp,
                "temp_min": temp - 8,
                "humidity": humidity,
                "wind_speed": 8.0
            })
        
        mock_weather_service.get_forecast.return_value = {
            "forecasts": forecasts
        }
        
        # Analyze harvest windows
        analysis = await severe_weather_service.analyze_harvest_windows(
            latitude=28.6139, longitude=77.2090, days_ahead=14
        )
        
        # Verify optimal window is the longer, better-condition period
        assert analysis["optimal_window"]["days"] == 5
        assert analysis["optimal_window"]["suitability_score"] > 70
    
    @pytest.mark.asyncio
    async def test_no_suitable_harvest_windows(self, severe_weather_service, mock_weather_service):
        """Test when no suitable harvest windows exist"""
        # Mock forecast with continuous rain
        forecasts = []
        for i in range(14):
            forecasts.append({
                "date": datetime.now() + timedelta(days=i),
                "rainfall": 25.0,  # Continuous rain
                "temp_max": 28.0,
                "temp_min": 22.0,
                "humidity": 85,
                "wind_speed": 10.0
            })
        
        mock_weather_service.get_forecast.return_value = {
            "forecasts": forecasts
        }
        
        # Analyze harvest windows
        analysis = await severe_weather_service.analyze_harvest_windows(
            latitude=28.6139, longitude=77.2090, days_ahead=14
        )
        
        # Verify no suitable windows
        assert len(analysis["dry_periods"]) == 0
        assert analysis["optimal_window"] is None
        assert "No suitable harvest windows" in analysis["recommendation"]


class TestEmergencyHarvestAlerts:
    """Test emergency harvest alert functionality"""
    
    @pytest.mark.skip(reason="Requires ORM setup - tested via integration tests")
    @pytest.mark.asyncio
    async def test_emergency_harvest_near_harvest_date(
        self, severe_weather_service, mock_weather_service, mock_db
    ):
        """Test emergency harvest alert when crop is near harvest and severe weather threatens"""
        pass
    
    @pytest.mark.skip(reason="Requires ORM setup - tested via integration tests")
    @pytest.mark.asyncio
    async def test_no_emergency_harvest_far_from_harvest(
        self, severe_weather_service, mock_weather_service, mock_db
    ):
        """Test no emergency alert when harvest is far away"""
        pass


class TestMicroclimatePredictions:
    """Test microclimate prediction functionality"""
    
    @pytest.mark.asyncio
    async def test_elevation_adjustment(self, severe_weather_service, mock_weather_service):
        """Test temperature adjustment based on elevation"""
        # Mock base forecast
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "rainfall": 5.0,
                    "temp_max": 30.0,
                    "temp_min": 20.0,
                    "humidity": 60,
                    "wind_speed": 8.0
                }
            ]
        }
        
        # Get microclimate prediction with elevation
        prediction = await severe_weather_service.get_microclimate_prediction(
            latitude=28.6139,
            longitude=77.2090,
            farm_characteristics={"elevation": 500}  # 500m elevation
        )
        
        # Verify temperature adjustment (should be ~3°C cooler)
        assert "microclimate_forecast" in prediction
        adjusted = prediction["microclimate_forecast"][0]
        assert adjusted["temp_max"] < 30.0
        assert adjusted["temp_min"] < 20.0
        assert "elevation" in prediction["adjustments_applied"]
    
    @pytest.mark.asyncio
    async def test_slope_adjustment(self, severe_weather_service, mock_weather_service):
        """Test rainfall adjustment based on slope"""
        # Mock base forecast
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "rainfall": 50.0,
                    "temp_max": 30.0,
                    "temp_min": 20.0,
                    "humidity": 60,
                    "wind_speed": 8.0
                }
            ]
        }
        
        # Get microclimate prediction with steep slope
        prediction = await severe_weather_service.get_microclimate_prediction(
            latitude=28.6139,
            longitude=77.2090,
            farm_characteristics={"slope": 10}  # 10 degree slope
        )
        
        # Verify effective rainfall adjustment
        assert "microclimate_forecast" in prediction
        adjusted = prediction["microclimate_forecast"][0]
        assert "effective_rainfall" in adjusted
        assert adjusted["effective_rainfall"] < 50.0  # Reduced due to runoff
        assert "slope" in prediction["adjustments_applied"]
    
    @pytest.mark.asyncio
    async def test_soil_type_irrigation_need(self, severe_weather_service, mock_weather_service):
        """Test irrigation need based on soil type"""
        # Mock base forecast
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "rainfall": 10.0,
                    "temp_max": 30.0,
                    "temp_min": 20.0,
                    "humidity": 60,
                    "wind_speed": 8.0
                }
            ]
        }
        
        # Test sandy soil (high irrigation need)
        prediction_sandy = await severe_weather_service.get_microclimate_prediction(
            latitude=28.6139,
            longitude=77.2090,
            farm_characteristics={"soil_type": "sandy"}
        )
        
        assert prediction_sandy["microclimate_forecast"][0]["irrigation_need"] == "high"
        
        # Test clay soil (low irrigation need)
        prediction_clay = await severe_weather_service.get_microclimate_prediction(
            latitude=28.6139,
            longitude=77.2090,
            farm_characteristics={"soil_type": "clay"}
        )
        
        assert prediction_clay["microclimate_forecast"][0]["irrigation_need"] == "low"


class TestAlertNotificationLatency:
    """Test alert notification latency requirements (< 15 minutes)"""
    
    @pytest.mark.asyncio
    async def test_alert_detection_performance(self, severe_weather_service, mock_weather_service):
        """Test that severe weather detection completes within acceptable time"""
        import time
        
        # Mock forecast
        mock_weather_service.get_forecast.return_value = {
            "forecasts": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "rainfall": 75.0,
                    "temp_max": 42.0,
                    "temp_min": 28.0,
                    "humidity": 85,
                    "wind_speed": 18.0
                }
            ]
        }
        
        mock_weather_service.get_weather_alerts.return_value = []
        
        # Measure detection time
        start_time = time.time()
        alerts = await severe_weather_service.detect_severe_weather(
            latitude=28.6139, longitude=77.2090
        )
        detection_time = time.time() - start_time
        
        # Verify detection completes quickly (< 5 seconds for processing)
        assert detection_time < 5.0
        assert len(alerts) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
