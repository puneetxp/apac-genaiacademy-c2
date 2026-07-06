"""
Unit tests for Plot Publishing API

Task 27.1: Plot publishing API endpoint tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.main import create_app


@pytest.fixture
def client():
    """Test client"""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication"""
    return {
        'user_id': 1,
        'email': 'farmer@example.com',
        'role': 'farmer'
    }


@pytest.fixture
def valid_publish_request():
    """Valid plot publish request"""
    return {
        "crop_name": "Rice",
        "crop_variety": "Basmati 1121",
        "expected_harvest_date": "2024-10-15",
        "quantity_quintals": 50.0,
        "quality_grade": "A",
        "price_per_quintal": 2500.0
    }


@pytest.fixture
def mock_listing_response():
    """Mock listing response"""
    return {
        "listing_id": 1,
        "plot_id": 1,
        "plot_name": "North Field",
        "status": "published",
        "created_at": datetime.now().isoformat(),
        "crop_details": {
            "crop_name": "Rice",
            "crop_variety": "Basmati 1121",
            "expected_harvest_date": "2024-10-15",
            "quantity_quintals": 50.0,
            "quantity_kg": 5000,
            "quality_grade": "A",
            "price_per_quintal": 2500.0
        },
        "plot_characteristics": {
            "location": {
                "state": "Punjab",
                "district": "Ludhiana"
            },
            "area_acres": 10.5,
            "soil_type": "loamy",
            "irrigation_type": "canal",
            "soil_health_score": None
        },
        "ai_predictions": {
            "yield_confidence": 0.85,
            "quality_confidence": 0.80,
            "harvest_date_range": {
                "start": "2024-10-08",
                "end": "2024-10-22"
            },
            "suitability_score": 8.5,
            "risk_level": "medium"
        },
        "farmer_contact": {
            "phone": "+919876543210",
            "email": "farmer@example.com"
        },
        "offering_terms": {
            "price_per_quintal": 2500.0,
            "total_value": 125000.0,
            "advance_booking_available": True,
            "minimum_booking_quantity": 5.0
        }
    }


def test_publish_plot_success(client, valid_publish_request, mock_listing_response, mock_auth):
    """Test successful plot publishing"""
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        with patch('app.api.v1.plot_publishing.PlotPublishingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.publish_plot = AsyncMock(return_value=mock_listing_response)
            mock_service_class.return_value = mock_service
            
            response = client.post(
                "/plots/1/publish",
                json=valid_publish_request
            )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert data['listing_id'] == 1
    assert data['plot_id'] == 1
    assert data['status'] == "published"
    assert 'crop_details' in data
    assert 'plot_characteristics' in data
    assert 'ai_predictions' in data
    assert 'farmer_contact' in data
    assert 'offering_terms' in data


def test_publish_plot_invalid_quality_grade(client, valid_publish_request, mock_auth):
    """Test publishing with invalid quality grade"""
    
    invalid_request = valid_publish_request.copy()
    invalid_request['quality_grade'] = "D"  # Invalid grade
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        response = client.post(
            "/plots/1/publish",
            json=invalid_request
        )
    
    assert response.status_code == 422  # Validation error


def test_publish_plot_invalid_harvest_date(client, valid_publish_request, mock_auth):
    """Test publishing with invalid harvest date format"""
    
    invalid_request = valid_publish_request.copy()
    invalid_request['expected_harvest_date'] = "15-10-2024"  # Wrong format
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        with patch('app.api.v1.plot_publishing.PlotPublishingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            response = client.post(
                "/plots/1/publish",
                json=invalid_request
            )
    
    assert response.status_code == 400
    assert "Invalid harvest date format" in response.json()['detail']


def test_publish_plot_not_found(client, valid_publish_request, mock_auth):
    """Test publishing non-existent plot"""
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        with patch('app.api.v1.plot_publishing.PlotPublishingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.publish_plot = AsyncMock(side_effect=ValueError("Plot 999 not found"))
            mock_service_class.return_value = mock_service
            
            response = client.post(
                "/plots/999/publish",
                json=valid_publish_request
            )
    
    assert response.status_code == 404
    assert "Plot 999 not found" in response.json()['detail']


def test_publish_plot_negative_quantity(client, valid_publish_request, mock_auth):
    """Test publishing with negative quantity"""
    
    invalid_request = valid_publish_request.copy()
    invalid_request['quantity_quintals'] = -10.0
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        response = client.post(
            "/plots/1/publish",
            json=invalid_request
        )
    
    assert response.status_code == 422  # Validation error


def test_publish_plot_negative_price(client, valid_publish_request, mock_auth):
    """Test publishing with negative price"""
    
    invalid_request = valid_publish_request.copy()
    invalid_request['price_per_quintal'] = -100.0
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        response = client.post(
            "/plots/1/publish",
            json=invalid_request
        )
    
    assert response.status_code == 422  # Validation error


def test_publish_plot_missing_required_fields(client, mock_auth):
    """Test publishing with missing required fields"""
    
    incomplete_request = {
        "crop_name": "Rice",
        # Missing other required fields
    }
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        response = client.post(
            "/plots/1/publish",
            json=incomplete_request
        )
    
    assert response.status_code == 422  # Validation error


def test_publish_plot_server_error(client, valid_publish_request, mock_auth):
    """Test handling of server errors"""
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        with patch('app.api.v1.plot_publishing.PlotPublishingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.publish_plot = AsyncMock(side_effect=Exception("Database error"))
            mock_service_class.return_value = mock_service
            
            response = client.post(
                "/plots/1/publish",
                json=valid_publish_request
            )
    
    assert response.status_code == 500
    assert "Plot publishing failed" in response.json()['detail']


def test_get_plot_listings_success(client, mock_auth):
    """Test getting plot listings"""
    
    mock_listings = [
        {
            "listing_id": 1,
            "crop_type": "Rice",
            "crop_variety": "Basmati 1121",
            "expected_harvest_date": "2024-10-15",
            "estimated_quantity": 5000,
            "quality_grade": "A",
            "status": "published",
            "created_at": "2024-01-15T10:00:00"
        },
        {
            "listing_id": 2,
            "crop_type": "Wheat",
            "crop_variety": "HD-2967",
            "expected_harvest_date": "2024-04-20",
            "estimated_quantity": 4000,
            "quality_grade": "B",
            "status": "completed",
            "created_at": "2024-01-10T09:00:00"
        }
    ]
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        with patch('app.api.v1.plot_publishing.select') as mock_select:
            # Mock database query
            mock_result = AsyncMock()
            mock_result.scalars.return_value.all.return_value = [
                Mock(
                    id=1,
                    crop_type="Rice",
                    crop_variety="Basmati 1121",
                    expected_harvest_date=datetime(2024, 10, 15).date(),
                    estimated_quantity=5000,
                    quality_grade="A",
                    status="published",
                    created_at=datetime(2024, 1, 15, 10, 0, 0)
                ),
                Mock(
                    id=2,
                    crop_type="Wheat",
                    crop_variety="HD-2967",
                    expected_harvest_date=datetime(2024, 4, 20).date(),
                    estimated_quantity=4000,
                    quality_grade="B",
                    status="completed",
                    created_at=datetime(2024, 1, 10, 9, 0, 0)
                )
            ]
            
            response = client.get("/plots/1/listings")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['plot_id'] == 1
    assert data['total_listings'] == 2
    assert len(data['listings']) == 2
    assert data['listings'][0]['crop_type'] == "Rice"
    assert data['listings'][1]['crop_type'] == "Wheat"


def test_get_plot_listings_empty(client, mock_auth):
    """Test getting listings for plot with no listings"""
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.return_value = mock_auth
        
        with patch('app.api.v1.plot_publishing.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.scalars.return_value.all.return_value = []
            
            response = client.get("/plots/1/listings")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['plot_id'] == 1
    assert data['total_listings'] == 0
    assert len(data['listings']) == 0


def test_publish_plot_unauthorized(client, valid_publish_request):
    """Test publishing without authentication"""
    
    with patch('app.api.v1.plot_publishing.get_current_user') as mock_get_user:
        mock_get_user.side_effect = Exception("Unauthorized")
        
        response = client.post(
            "/plots/1/publish",
            json=valid_publish_request
        )
    
    # Should fail due to authentication error
    assert response.status_code in [401, 500]
