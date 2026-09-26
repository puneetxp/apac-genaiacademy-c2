"""
Unit and Integration Tests for Soil Moisture and Dynamic Settings Resolver
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_system_setting
from app.main import app

client = TestClient(app)


def test_settings_resolver_fallback():
    """Test get_system_setting falls back to environment variable if not in DB"""
    with patch("app.orm.system_setting.SystemSetting.find", return_value=None):
        with patch("os.getenv", return_value="env_secret_key"):
            val = get_system_setting("DATAGOV_MOISTURE_API_KEY")
            assert val == "env_secret_key"


def test_settings_resolver_database():
    """Test get_system_setting successfully retrieves key from database"""
    mock_setting = MagicMock()
    mock_setting.items = {"value": "db_secret_key", "enable": 1}

    with patch("app.orm.system_setting.SystemSetting.find", return_value=mock_setting):
        val = get_system_setting("DATAGOV_MOISTURE_API_KEY")
        assert val == "db_secret_key"


def test_api_get_soil_moisture_empty():
    """Test GET /api/v1/soil/moisture when database has no records"""
    mock_query_result = MagicMock()
    mock_query_result.items = []

    with patch("app.orm.soil_moisture_data.SoilMoistureData.where", return_value=mock_query_result):
        mock_query_result.paginate = MagicMock(return_value=mock_query_result)

        response = client.get("/api/v1/soil/moisture?state=Haryana&district=Gurgaon")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["data"] == []


def test_api_get_soil_moisture_records():
    """Test GET /api/v1/soil/moisture returns mock data records"""
    mock_records = [
        {
            "id": 1,
            "state": "Haryana",
            "district": "Gurgaon",
            "date": "2021-02-09",
            "year": 2021,
            "month": "02",
            "moisture_level": 8.9391,
            "agency_name": "NRSC VIC MODEL",
        }
    ]

    mock_query_result = MagicMock()
    mock_query_result.items = mock_records

    with patch("app.orm.soil_moisture_data.SoilMoistureData.where", return_value=mock_query_result):
        mock_query_result.paginate = MagicMock(return_value=mock_query_result)

        response = client.get("/api/v1/soil/moisture?state=Haryana&district=Gurgaon")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["moisture_level"] == 8.9391
