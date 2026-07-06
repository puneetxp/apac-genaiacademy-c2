"""
Unit tests for Plot Analysis API endpoints
Tests API endpoints for plot analysis and profitability comparison

Task 26.1: Comprehensive plot analysis API testing
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services.plot_analysis_service import PlotAnalysisService


@pytest.fixture
def mock_current_user():
    """Mock authenticated user"""
    return {
        "user_id": 1,
        "email": "farmer@example.com",
        "cognito_user_id": "test-user-123"
    }


@pytest.fixture
def sample_analysis_response():
    """Sample plot analysis response"""
    return {
        "plot_id": 1,
        "plot_name": "North Field",
        "analysis_date": "2024-02-28T10:30:00",
        "season": "kharif",
        "plot_characteristics": {
            "location": {"state": "Punjab", "district": "Ludhiana"},
            "area_acres": 5.0,
            "soil_data": {
                "type": "loamy",
                "ph": 7.2,
                "nitrogen": 280,
                "phosphorus": 15,
                "potassium": 250,
                "organic_matter": 1.8,
                "health_score": 85
            },
            "water_data": {
                "source": "Canal",
                "availability": "year-round",
                "quality": "good"
            }
        },
        "recommended_crops": [
            {
                "rank": 1,
                "crop_name": "Basmati Rice",
                "variety": "Pusa Basmati 1121",
                "suitability_score": 9.2,
                "investment_per_acre": 18000,
                "expected_yield_per_acre": "22-25 quintals",
                "market_price_per_quintal": 2500,
                "quality_grade": "A",
                "quality_confidence": 0.87,
                "demand_level": "High",
                "risk_probability": "Medium",
                "profitability": {
                    "per_acre": {
                        "investment": 18000,
                        "revenue": 58750,
                        "profit": 40750,
                        "roi_percentage": 226,
                        "breakeven_yield": "7.2 quintals"
                    },
                    "total_plot": {
                        "area_acres": 5.0,
                        "total_investment": 90000,
                        "total_yield": "117.5 quintals",
                        "total_revenue": 293750,
                        "total_profit": 203750
                    },
                    "investment_breakdown": {
                        "seeds": 2700,
                        "fertilizer": 6300,
                        "labor": 5400,
                        "irrigation": 2700,
                        "other": 900
                    }
                }
            }
        ],
        "annual_strategy": {
            "current_season_crop": "Basmati Rice",
            "next_season_crop": "Wheat",
            "total_annual_profit": 82000,
            "annual_roi": 273
        },
        "plot_health": {
            "soil_health_score": 85,
            "water_resource_score": 90,
            "overall_suitability_score": 87
        }
    }


class TestPlotAnalysisEndpoint:
    """Test suite for POST /plots/{plot_id}/analyze endpoint"""
    
    @pytest.mark.asyncio
    async def test_analyze_plot_success(
        self,
        mock_current_user,
        sample_analysis_response
    ):
        """Test successful plot analysis"""
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service
            mock_service = AsyncMock()
            mock_service.analyze_plot.return_value = sample_analysis_response
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute
            response = client.post(
                "/plots/1/analyze",
                json={
                    "season": "kharif",
                    "budget_per_acre": 20000,
                    "preferences": {
                        "risk_tolerance": "medium",
                        "market_focus": "local"
                    }
                },
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["plot_id"] == 1
            assert data["plot_name"] == "North Field"
            assert data["season"] == "kharif"
            assert len(data["recommended_crops"]) > 0
            assert "annual_strategy" in data
            assert "plot_health" in data
    
    @pytest.mark.asyncio
    async def test_analyze_plot_not_found(self, mock_current_user):
        """Test plot analysis with non-existent plot"""
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service to raise ValueError
            mock_service = AsyncMock()
            mock_service.analyze_plot.side_effect = ValueError("Plot 999 not found")
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute
            response = client.post(
                "/plots/999/analyze",
                json={"season": "kharif"},
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_analyze_plot_invalid_season(self, mock_current_user):
        """Test plot analysis with invalid season"""
        # Create test client
        client = TestClient(app)
        
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user):
            # Execute with invalid data
            response = client.post(
                "/plots/1/analyze",
                json={
                    "season": "",  # Empty season
                    "budget_per_acre": 20000
                },
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify validation error
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_analyze_plot_negative_budget(self, mock_current_user):
        """Test plot analysis with negative budget"""
        # Create test client
        client = TestClient(app)
        
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user):
            # Execute with invalid budget
            response = client.post(
                "/plots/1/analyze",
                json={
                    "season": "kharif",
                    "budget_per_acre": -5000  # Negative budget
                },
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify validation error
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_analyze_plot_without_auth(self):
        """Test plot analysis without authentication"""
        # Create test client
        client = TestClient(app)
        
        # Execute without auth header
        response = client.post(
            "/plots/1/analyze",
            json={"season": "kharif"}
        )
        
        # Verify unauthorized
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_analyze_plot_with_preferences(
        self,
        mock_current_user,
        sample_analysis_response
    ):
        """Test plot analysis with farmer preferences"""
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service
            mock_service = AsyncMock()
            mock_service.analyze_plot.return_value = sample_analysis_response
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute with preferences
            response = client.post(
                "/plots/1/analyze",
                json={
                    "season": "rabi",
                    "budget_per_acre": 25000,
                    "preferences": {
                        "risk_tolerance": "low",
                        "market_focus": "export",
                        "organic": "true"
                    }
                },
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify
            assert response.status_code == 200
            
            # Verify service was called with preferences
            mock_service.analyze_plot.assert_called_once()
            call_args = mock_service.analyze_plot.call_args
            assert call_args[1]["preferences"]["risk_tolerance"] == "low"
            assert call_args[1]["preferences"]["market_focus"] == "export"
    
    @pytest.mark.asyncio
    async def test_analyze_plot_server_error(self, mock_current_user):
        """Test plot analysis with server error"""
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service to raise exception
            mock_service = AsyncMock()
            mock_service.analyze_plot.side_effect = Exception("Database connection failed")
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute
            response = client.post(
                "/plots/1/analyze",
                json={"season": "kharif"},
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify
            assert response.status_code == 500
            assert "failed" in response.json()["detail"].lower()


class TestProfitabilityComparisonEndpoint:
    """Test suite for GET /plots/{plot_id}/profitability endpoint"""
    
    @pytest.mark.asyncio
    async def test_compare_profitability_success(
        self,
        mock_current_user,
        sample_analysis_response
    ):
        """Test successful profitability comparison"""
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service
            mock_service = AsyncMock()
            mock_service.analyze_plot.return_value = sample_analysis_response
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute
            response = client.get(
                "/plots/1/profitability?crops=rice,wheat&season=kharif",
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["plot_id"] == 1
            assert "crops" in data
            assert "recommendation" in data
            assert "best_for_profit" in data["recommendation"]
            assert "best_for_roi" in data["recommendation"]
            assert "ai_recommendation" in data["recommendation"]
    
    @pytest.mark.asyncio
    async def test_compare_profitability_missing_crops(self, mock_current_user):
        """Test profitability comparison without crops parameter"""
        # Create test client
        client = TestClient(app)
        
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user):
            # Execute without crops parameter
            response = client.get(
                "/plots/1/profitability?season=kharif",
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify validation error
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_compare_profitability_no_matching_crops(
        self,
        mock_current_user,
        sample_analysis_response
    ):
        """Test profitability comparison with no matching crops"""
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service with different crops
            response_data = sample_analysis_response.copy()
            response_data["recommended_crops"][0]["crop_name"] = "Cotton"
            
            mock_service = AsyncMock()
            mock_service.analyze_plot.return_value = response_data
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute with non-matching crops
            response = client.get(
                "/plots/1/profitability?crops=wheat,maize&season=kharif",
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify
            assert response.status_code == 404
            assert "no matching crops" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_compare_profitability_multiple_crops(
        self,
        mock_current_user
    ):
        """Test profitability comparison with multiple crops"""
        # Create analysis responses for different crops
        rice_response = {
            "analysis_date": "2024-02-28T10:30:00",
            "recommended_crops": [
                {
                    "crop_name": "Basmati Rice",
                    "suitability_score": 9.2,
                    "risk_probability": "Medium",
                    "demand_level": "High",
                    "profitability": {
                        "per_acre": {
                            "investment": 18000,
                            "revenue": 58750,
                            "profit": 40750,
                            "roi_percentage": 226
                        }
                    }
                }
            ]
        }
        
        wheat_response = {
            "analysis_date": "2024-02-28T10:30:00",
            "recommended_crops": [
                {
                    "crop_name": "Wheat",
                    "suitability_score": 8.5,
                    "risk_probability": "Low",
                    "demand_level": "High",
                    "profitability": {
                        "per_acre": {
                            "investment": 15000,
                            "revenue": 50000,
                            "profit": 35000,
                            "roi_percentage": 233
                        }
                    }
                }
            ]
        }
        
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service to return different responses
            mock_service = AsyncMock()
            mock_service.analyze_plot.side_effect = [rice_response, wheat_response]
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute
            response = client.get(
                "/plots/1/profitability?crops=basmati rice,wheat&season=kharif",
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify
            assert response.status_code == 200
            data = response.json()
            assert len(data["crops"]) == 2
            
            # Verify crops are compared
            crop_names = [c["crop_name"] for c in data["crops"]]
            assert "Basmati Rice" in crop_names
            assert "Wheat" in crop_names
            
            # Verify recommendation
            assert data["recommendation"]["best_for_profit"] in ["Basmati Rice", "Wheat"]
            assert data["recommendation"]["best_for_roi"] in ["Basmati Rice", "Wheat"]
    
    @pytest.mark.asyncio
    async def test_compare_profitability_without_auth(self):
        """Test profitability comparison without authentication"""
        # Create test client
        client = TestClient(app)
        
        # Execute without auth header
        response = client.get(
            "/plots/1/profitability?crops=rice,wheat&season=kharif"
        )
        
        # Verify unauthorized
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_compare_profitability_plot_not_found(self, mock_current_user):
        """Test profitability comparison with non-existent plot"""
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service to raise ValueError
            mock_service = AsyncMock()
            mock_service.analyze_plot.side_effect = ValueError("Plot 999 not found")
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute
            response = client.get(
                "/plots/999/profitability?crops=rice,wheat&season=kharif",
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify
            assert response.status_code == 404


class TestResponseValidation:
    """Test suite for response validation"""
    
    @pytest.mark.asyncio
    async def test_analysis_response_structure(
        self,
        mock_current_user,
        sample_analysis_response
    ):
        """Test that analysis response has correct structure"""
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service
            mock_service = AsyncMock()
            mock_service.analyze_plot.return_value = sample_analysis_response
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute
            response = client.post(
                "/plots/1/analyze",
                json={"season": "kharif"},
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify response structure
            assert response.status_code == 200
            data = response.json()
            
            # Required fields
            assert "plot_id" in data
            assert "plot_name" in data
            assert "analysis_date" in data
            assert "season" in data
            assert "plot_characteristics" in data
            assert "recommended_crops" in data
            assert "annual_strategy" in data
            assert "plot_health" in data
            
            # Crop structure
            crop = data["recommended_crops"][0]
            assert "rank" in crop
            assert "crop_name" in crop
            assert "suitability_score" in crop
            assert "profitability" in crop
            
            # Profitability structure
            prof = crop["profitability"]
            assert "per_acre" in prof
            assert "total_plot" in prof
            assert "investment_breakdown" in prof
    
    @pytest.mark.asyncio
    async def test_profitability_comparison_structure(
        self,
        mock_current_user,
        sample_analysis_response
    ):
        """Test that profitability comparison response has correct structure"""
        # Mock dependencies
        with patch('app.api.v1.plot_analysis.get_current_user', return_value=mock_current_user), \
             patch('app.api.v1.plot_analysis.PlotAnalysisService') as MockService:
            
            # Setup mock service
            mock_service = AsyncMock()
            mock_service.analyze_plot.return_value = sample_analysis_response
            MockService.return_value = mock_service
            
            # Create test client
            client = TestClient(app)
            
            # Execute
            response = client.get(
                "/plots/1/profitability?crops=basmati rice&season=kharif",
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify response structure
            assert response.status_code == 200
            data = response.json()
            
            # Required fields
            assert "plot_id" in data
            assert "comparison_date" in data
            assert "season" in data
            assert "crops" in data
            assert "recommendation" in data
            
            # Crop comparison structure
            if len(data["crops"]) > 0:
                crop = data["crops"][0]
                assert "crop_name" in crop
                assert "investment" in crop
                assert "revenue" in crop
                assert "profit" in crop
                assert "roi" in crop
                assert "risk_level" in crop
                assert "market_demand" in crop
                assert "suitability_score" in crop
            
            # Recommendation structure
            rec = data["recommendation"]
            assert "best_for_profit" in rec
            assert "best_for_roi" in rec
            assert "ai_recommendation" in rec
            assert "reason" in rec
