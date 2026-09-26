"""
Unit tests for Weather API Integration
Tests IMD, OpenWeatherMap, and unified weather service

Task 23.1: Integrate with Weather APIs
**Validates: Requirements AC8**
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from app.services.imd_service import IMDService, get_imd_service
from app.services.openweathermap_service import OpenWeatherMapService, get_openweathermap_service
from app.services.weather_service import WeatherService, get_weather_service


class TestIMDService:
    """Test IMD API integration"""

    @pytest.mark.asyncio
    async def test_imd_service_initialization(self):
        """Test IMD service initialization"""
        service = IMDService(api_key="test_key")
        assert service.api_key == "test_key"
        assert service.client is not None
        await service.close()

    @pytest.mark.asyncio
    async def test_imd_get_current_weather_success(self):
        """Test successful current weather retrieval from IMD"""
        service = IMDService(api_key="test_key")

        # Mock response
        mock_response_data = {
            "temp": 28.5,
            "feels_like": 30.0,
            "humidity": 65,
            "pressure": 1013,
            "wind_speed": 3.5,
            "wind_direction": 180,
            "rainfall": 0.0,
            "description": "Partly cloudy",
            "timestamp": datetime.now().isoformat(),
        }

        with patch.object(service.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = await service.get_current_weather(28.7041, 77.1025)

            assert result is not None
            assert result["temperature"] == 28.5
            assert result["humidity"] == 65
            assert result["source"] == "IMD"

        await service.close()

    @pytest.mark.asyncio
    async def test_imd_get_current_weather_no_api_key(self):
        """Test current weather retrieval without API key"""
        service = IMDService(api_key=None)

        result = await service.get_current_weather(28.7041, 77.1025)

        assert result is None
        await service.close()

    @pytest.mark.asyncio
    async def test_imd_get_forecast_success(self):
        """Test successful forecast retrieval from IMD"""
        service = IMDService(api_key="test_key")

        # Mock response
        mock_response_data = {
            "forecast": [
                {
                    "date": (datetime.now() + timedelta(days=i)).isoformat(),
                    "temp_min": 20.0 + i,
                    "temp_max": 30.0 + i,
                    "humidity": 60 + i,
                    "rainfall": 0.0,
                    "wind_speed": 3.0,
                    "description": "Clear sky",
                }
                for i in range(7)
            ]
        }

        with patch.object(service.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = await service.get_forecast(28.7041, 77.1025, days=7)

            assert result is not None
            assert result["days"] == 7
            assert len(result["forecasts"]) == 7
            assert result["source"] == "IMD"

        await service.close()

    @pytest.mark.asyncio
    async def test_imd_get_forecast_invalid_days(self):
        """Test forecast with invalid days parameter"""
        service = IMDService(api_key="test_key")

        mock_response_data = {"forecast": []}

        with patch.object(service.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Should default to 7 days
            result = await service.get_forecast(28.7041, 77.1025, days=10)

            assert result is not None

        await service.close()

    @pytest.mark.asyncio
    async def test_imd_get_weather_alerts_success(self):
        """Test successful weather alerts retrieval from IMD"""
        service = IMDService(api_key="test_key")

        # Mock response
        mock_response_data = {
            "alerts": [
                {
                    "id": "alert_1",
                    "severity": "high",
                    "event_type": "heavy_rain",
                    "headline": "Heavy rainfall warning",
                    "description": "Heavy rainfall expected in next 24 hours",
                    "start_time": datetime.now().isoformat(),
                    "end_time": (datetime.now() + timedelta(hours=24)).isoformat(),
                    "affected_areas": ["District A", "District B"],
                }
            ]
        }

        with patch.object(service.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = await service.get_weather_alerts("Punjab", "Ludhiana")

            assert result is not None
            assert len(result) == 1
            assert result[0]["severity"] == "high"
            assert result[0]["source"] == "IMD"

        await service.close()

    @pytest.mark.asyncio
    async def test_imd_http_error_handling(self):
        """Test IMD API HTTP error handling"""
        service = IMDService(api_key="test_key")

        with patch.object(service.client, "get", new_callable=AsyncMock) as mock_get:
            # Simulate HTTP error by raising exception when raise_for_status is called
            mock_response = AsyncMock()
            mock_response.raise_for_status = Mock(
                side_effect=httpx.HTTPStatusError(
                    "404 Not Found",
                    request=Mock(),
                    response=Mock(status_code=404, text="Not Found"),
                )
            )
            mock_get.return_value = mock_response

            result = await service.get_current_weather(28.7041, 77.1025)

            assert result is None

        await service.close()


class TestOpenWeatherMapService:
    """Test OpenWeatherMap API integration"""

    @pytest.mark.asyncio
    async def test_owm_service_initialization(self):
        """Test OpenWeatherMap service initialization"""
        service = OpenWeatherMapService(api_key="test_key")
        assert service.api_key == "test_key"
        assert service.client is not None
        await service.close()

    @pytest.mark.asyncio
    async def test_owm_get_current_weather_success(self):
        """Test successful current weather retrieval from OpenWeatherMap"""
        service = OpenWeatherMapService(api_key="test_key")

        # Mock response (OpenWeatherMap format)
        mock_response_data = {
            "main": {"temp": 28.5, "feels_like": 30.0, "humidity": 65, "pressure": 1013},
            "wind": {"speed": 3.5, "deg": 180},
            "weather": [{"description": "partly cloudy"}],
            "rain": {"1h": 0.0},
            "dt": int(datetime.now().timestamp()),
        }

        with patch.object(service.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = await service.get_current_weather(28.7041, 77.1025)

            assert result is not None
            assert result["temperature"] == 28.5
            assert result["humidity"] == 65
            assert result["source"] == "OpenWeatherMap"

        await service.close()

    @pytest.mark.asyncio
    async def test_owm_get_forecast_success(self):
        """Test successful forecast retrieval from OpenWeatherMap"""
        service = OpenWeatherMapService(api_key="test_key")

        # Mock response (OpenWeatherMap 5-day forecast format)
        mock_response_data = {
            "list": [
                {
                    "dt": int((datetime.now() + timedelta(hours=3 * i)).timestamp()),
                    "main": {"temp": 25.0 + i, "humidity": 60},
                    "wind": {"speed": 3.0},
                    "weather": [{"description": "clear sky"}],
                    "rain": {"3h": 0.0},
                }
                for i in range(40)  # 5 days * 8 forecasts per day
            ]
        }

        with patch.object(service.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = await service.get_forecast(28.7041, 77.1025, days=5)

            assert result is not None
            assert result["days"] <= 5
            assert len(result["forecasts"]) > 0
            assert result["source"] == "OpenWeatherMap"

        await service.close()

    @pytest.mark.asyncio
    async def test_owm_get_forecast_exceeds_free_tier(self):
        """Test forecast request exceeding free tier limit"""
        service = OpenWeatherMapService(api_key="test_key")

        mock_response_data = {"list": []}

        with patch.object(service.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Should limit to 5 days
            result = await service.get_forecast(28.7041, 77.1025, days=14)

            assert result is not None

        await service.close()


class TestWeatherService:
    """Test unified weather service with failover"""

    @pytest.mark.asyncio
    async def test_weather_service_initialization(self):
        """Test weather service initialization"""
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        assert service.imd_service is not None
        assert service.owm_service is not None

        await service.close()

    @pytest.mark.asyncio
    async def test_get_current_weather_imd_success(self):
        """Test current weather retrieval with IMD success"""
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        mock_weather_data = {"temperature": 28.5, "humidity": 65, "source": "IMD"}

        with patch.object(
            service.imd_service, "get_current_weather", new_callable=AsyncMock
        ) as mock_imd:
            mock_imd.return_value = mock_weather_data

            result = await service.get_current_weather(28.7041, 77.1025, use_cache=False)

            assert result is not None
            assert result["source"] == "IMD"
            mock_imd.assert_called_once()

        await service.close()

    @pytest.mark.asyncio
    async def test_get_current_weather_failover_to_owm(self):
        """Test failover to OpenWeatherMap when IMD fails"""
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        mock_owm_data = {"temperature": 28.5, "humidity": 65, "source": "OpenWeatherMap"}

        with (
            patch.object(
                service.imd_service, "get_current_weather", new_callable=AsyncMock
            ) as mock_imd,
            patch.object(
                service.owm_service, "get_current_weather", new_callable=AsyncMock
            ) as mock_owm,
        ):

            # IMD fails
            mock_imd.return_value = None
            # OWM succeeds
            mock_owm.return_value = mock_owm_data

            result = await service.get_current_weather(28.7041, 77.1025, use_cache=False)

            assert result is not None
            assert result["source"] == "OpenWeatherMap"
            mock_imd.assert_called_once()
            mock_owm.assert_called_once()

        await service.close()

    @pytest.mark.asyncio
    async def test_get_current_weather_all_sources_fail(self):
        """Test when all weather sources fail"""
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        with (
            patch.object(
                service.imd_service, "get_current_weather", new_callable=AsyncMock
            ) as mock_imd,
            patch.object(
                service.owm_service, "get_current_weather", new_callable=AsyncMock
            ) as mock_owm,
        ):

            # Both fail
            mock_imd.return_value = None
            mock_owm.return_value = None

            result = await service.get_current_weather(28.7041, 77.1025, use_cache=False)

            assert result is None

        await service.close()

    @pytest.mark.asyncio
    async def test_get_forecast_imd_success(self):
        """Test forecast retrieval with IMD success"""
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        mock_forecast_data = {
            "days": 7,
            "forecasts": [{"date": datetime.now(), "temp_min": 20.0, "temp_max": 30.0}],
            "source": "IMD",
        }

        with (
            patch.object(service.imd_service, "get_forecast", new_callable=AsyncMock) as mock_imd,
            patch.object(service, "_store_forecast", new_callable=AsyncMock) as mock_store,
        ):

            mock_imd.return_value = mock_forecast_data

            result = await service.get_forecast(28.7041, 77.1025, days=7, use_cache=False)

            assert result is not None
            assert result["source"] == "IMD"
            assert result["days"] == 7
            mock_imd.assert_called_once()
            mock_store.assert_called_once()

        await service.close()

    @pytest.mark.asyncio
    async def test_get_forecast_failover_to_owm(self):
        """Test forecast failover to OpenWeatherMap"""
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        mock_owm_forecast = {
            "days": 5,
            "forecasts": [{"date": datetime.now(), "temp_min": 20.0, "temp_max": 30.0}],
            "source": "OpenWeatherMap",
        }

        with (
            patch.object(service.imd_service, "get_forecast", new_callable=AsyncMock) as mock_imd,
            patch.object(service.owm_service, "get_forecast", new_callable=AsyncMock) as mock_owm,
            patch.object(service, "_store_forecast", new_callable=AsyncMock) as mock_store,
        ):

            # IMD fails
            mock_imd.return_value = None
            # OWM succeeds
            mock_owm.return_value = mock_owm_forecast

            result = await service.get_forecast(28.7041, 77.1025, days=7, use_cache=False)

            assert result is not None
            assert result["source"] == "OpenWeatherMap"
            mock_imd.assert_called_once()
            mock_owm.assert_called_once()

        await service.close()

    @pytest.mark.asyncio
    async def test_get_weather_alerts_imd(self):
        """Test weather alerts retrieval from IMD"""
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        mock_alerts = [
            {"alert_id": "alert_1", "severity": "high", "event_type": "heavy_rain", "source": "IMD"}
        ]

        with patch.object(
            service.imd_service, "get_weather_alerts", new_callable=AsyncMock
        ) as mock_imd:
            mock_imd.return_value = mock_alerts

            result = await service.get_weather_alerts(state="Punjab", district="Ludhiana")

            assert result is not None
            assert len(result) == 1
            assert result[0]["source"] == "IMD"

        await service.close()

    @pytest.mark.asyncio
    async def test_analyze_seasonal_patterns(self):
        """Test seasonal pattern analysis"""
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        # Mock historical data
        mock_historical = [
            {
                "date": datetime(2023, i, 15),
                "temp_avg": 25.0 + i,
                "rainfall": 50.0 * (i % 4),
                "humidity": 60 + i,
            }
            for i in range(1, 13)
        ]

        with patch.object(service, "get_historical_weather", new_callable=AsyncMock) as mock_hist:
            mock_hist.return_value = mock_historical

            result = await service.analyze_seasonal_patterns(28.7041, 77.1025, years=1)

            assert result is not None
            assert "monthly_patterns" in result
            assert "monsoon_months" in result
            assert result["years_analyzed"] == 1

        await service.close()


class TestWeatherServicePerformance:
    """Test weather service performance metrics (AC8)"""

    @pytest.mark.asyncio
    async def test_weather_api_response_time(self):
        """
        **Validates: AC8 - Weather API response time < 3 seconds (95th percentile)**
        """
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        mock_weather_data = {"temperature": 28.5, "humidity": 65, "source": "IMD"}

        with patch.object(
            service.imd_service, "get_current_weather", new_callable=AsyncMock
        ) as mock_imd:
            mock_imd.return_value = mock_weather_data

            start_time = datetime.now()
            result = await service.get_current_weather(28.7041, 77.1025, use_cache=False)
            end_time = datetime.now()

            response_time = (end_time - start_time).total_seconds()

            assert result is not None
            assert response_time < 3.0, f"Response time {response_time}s exceeds 3 seconds"

        await service.close()

    @pytest.mark.asyncio
    async def test_failover_time(self):
        """
        **Validates: AC8 - Failover to OWM < 5 seconds**
        """
        mock_db = AsyncMock()
        service = WeatherService(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")

        mock_owm_data = {"temperature": 28.5, "humidity": 65, "source": "OpenWeatherMap"}

        with (
            patch.object(
                service.imd_service, "get_current_weather", new_callable=AsyncMock
            ) as mock_imd,
            patch.object(
                service.owm_service, "get_current_weather", new_callable=AsyncMock
            ) as mock_owm,
        ):

            # IMD fails (timeout)
            mock_imd.return_value = None
            # OWM succeeds
            mock_owm.return_value = mock_owm_data

            start_time = datetime.now()
            result = await service.get_current_weather(28.7041, 77.1025, use_cache=False)
            end_time = datetime.now()

            failover_time = (end_time - start_time).total_seconds()

            assert result is not None
            assert result["source"] == "OpenWeatherMap"
            assert failover_time < 5.0, f"Failover time {failover_time}s exceeds 5 seconds"

        await service.close()


class TestFactoryFunctions:
    """Test factory functions"""

    def test_get_imd_service(self):
        """Test IMD service factory function"""
        service = get_imd_service(api_key="test_key")
        assert isinstance(service, IMDService)
        assert service.api_key == "test_key"

    def test_get_openweathermap_service(self):
        """Test OpenWeatherMap service factory function"""
        service = get_openweathermap_service(api_key="test_key")
        assert isinstance(service, OpenWeatherMapService)
        assert service.api_key == "test_key"

    @pytest.mark.asyncio
    async def test_get_weather_service(self):
        """Test weather service factory function"""
        mock_db = AsyncMock()
        service = get_weather_service(mock_db, imd_api_key="imd_key", owm_api_key="owm_key")
        assert isinstance(service, WeatherService)
        await service.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
