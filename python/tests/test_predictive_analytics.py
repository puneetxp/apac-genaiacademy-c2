"""
Unit Tests for Predictive Analytics Service

Tests for:
- Market price forecasting (30-90 day predictions with ±15% accuracy)
- Demand prediction based on buyer interest patterns
- Supply-demand matching algorithms
- Market opportunity alerts generation
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.predictive_analytics_service import (
    PredictiveAnalyticsService,
    get_predictive_analytics_service
)


# ==================== Fixtures ====================

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock(spec=AsyncSession)
    return db


@pytest.fixture
def service(mock_db):
    """Create predictive analytics service instance"""
    return PredictiveAnalyticsService(mock_db)


@pytest.fixture
def sample_price_data():
    """Sample historical price data"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = {
        'crop_name': ['wheat'] * 100,
        'price': np.random.uniform(20, 30, 100),
        'date': dates,
        'state': ['Maharashtra'] * 100,
        'district': ['Pune'] * 100,
        'season': ['Rabi'] * 100,
        'month': [d.month for d in dates],
        'year': [d.year for d in dates]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_buyer_interest_data():
    """Sample buyer interest data"""
    months = pd.date_range(start='2023-01-01', periods=12, freq='MS')
    data = {
        'crop_type': ['wheat'] * 12,
        'state': ['Maharashtra'] * 12,
        'district': ['Pune'] * 12,
        'interest_count': np.random.randint(10, 50, 12),
        'month': months,
        'month_num': [m.month for m in months],
        'year': [m.year for m in months]
    }
    return pd.DataFrame(data)


# ==================== Market Price Forecasting Tests ====================

@pytest.mark.asyncio
async def test_forecast_market_prices_success(service, sample_price_data):
    """Test successful price forecasting"""
    # Mock database query
    mock_result = Mock()
    mock_result.fetchall.return_value = [
        Mock(
            crop_name=row['crop_name'],
            price=row['price'],
            date=row['date'],
            state=row['state'],
            district=row['district'],
            season=row['season'],
            month=row['month'],
            year=row['year']
        )
        for _, row in sample_price_data.iterrows()
    ]
    service.db.execute = AsyncMock(return_value=mock_result)
    
    # Test forecast
    forecast = await service.forecast_market_prices(
        crop_name='wheat',
        region_state='Maharashtra',
        region_district='Pune',
        forecast_days=30
    )
    
    # Assertions
    assert forecast['crop_name'] == 'wheat'
    assert forecast['forecast_days'] == 30
    assert 'current_price' in forecast
    assert 'forecasted_price' in forecast
    assert 'confidence_interval' in forecast
    assert 'lower' in forecast['confidence_interval']
    assert 'upper' in forecast['confidence_interval']
    assert forecast['trend'] in ['increasing', 'decreasing', 'stable']
    assert 0 <= forecast['confidence_score'] <= 1
    assert forecast['data_points'] > 0


@pytest.mark.asyncio
async def test_forecast_market_prices_insufficient_data(service):
    """Test price forecasting with insufficient data"""
    # Mock database query with minimal data
    mock_result = Mock()
    mock_result.fetchall.return_value = []
    service.db.execute = AsyncMock(return_value=mock_result)
    
    forecast = await service.forecast_market_prices(
        crop_name='wheat',
        forecast_days=30
    )
    
    # Should return low confidence forecast
    assert forecast['confidence_score'] == 0.5
    assert 'warning' in forecast
    assert forecast['data_points'] == 0


@pytest.mark.asyncio
async def test_forecast_market_prices_different_horizons(service, sample_price_data):
    """Test price forecasting for different time horizons"""
    mock_result = Mock()
    mock_result.fetchall.return_value = [
        Mock(
            crop_name=row['crop_name'],
            price=row['price'],
            date=row['date'],
            state=row['state'],
            district=row['district'],
            season=row['season'],
            month=row['month'],
            year=row['year']
        )
        for _, row in sample_price_data.iterrows()
    ]
    service.db.execute = AsyncMock(return_value=mock_result)
    
    # Test 30, 60, 90 day forecasts
    for days in [30, 60, 90]:
        forecast = await service.forecast_market_prices(
            crop_name='wheat',
            forecast_days=days
        )
        assert forecast['forecast_days'] == days
        assert 'forecasted_price' in forecast


def test_prepare_price_features(service, sample_price_data):
    """Test price feature preparation"""
    features, prices = service._prepare_price_features(sample_price_data)
    
    # Check features are created
    assert 'days_since_start' in features.columns
    assert 'month_sin' in features.columns
    assert 'month_cos' in features.columns
    assert 'price_lag_1' in features.columns
    assert 'price_rolling_mean_7' in features.columns
    
    # Check no NaN values
    assert not features.isnull().any().any()
    
    # Check prices match
    assert len(prices) == len(sample_price_data)


def test_train_price_model(service, sample_price_data):
    """Test price model training"""
    features, prices = service._prepare_price_features(sample_price_data)
    model = service._train_price_model(features, prices)
    
    # Check model is trained
    assert model is not None
    assert hasattr(model, 'predict')
    
    # Test prediction
    prediction = model.predict(features.iloc[:1])
    assert len(prediction) == 1
    assert prediction[0] > 0


def test_generate_price_forecast(service, sample_price_data):
    """Test price forecast generation"""
    features, prices = service._prepare_price_features(sample_price_data)
    model = service._train_price_model(features, prices)
    
    forecast = service._generate_price_forecast(model, sample_price_data, 30)
    
    # Check forecast structure
    assert 'predicted_price' in forecast
    assert 'lower_bound' in forecast
    assert 'upper_bound' in forecast
    assert 'confidence' in forecast
    assert 'model_accuracy' in forecast
    
    # Check bounds are reasonable
    assert forecast['lower_bound'] < forecast['predicted_price']
    assert forecast['predicted_price'] < forecast['upper_bound']
    assert 0 <= forecast['confidence'] <= 1


# ==================== Demand Prediction Tests ====================

@pytest.mark.asyncio
async def test_predict_crop_demand_success(service, sample_buyer_interest_data):
    """Test successful demand prediction"""
    # Mock buyer interest data
    mock_result = Mock()
    mock_result.fetchall.return_value = [
        Mock(
            crop_type=row['crop_type'],
            state=row['state'],
            district=row['district'],
            interest_count=row['interest_count'],
            month=row['month'],
            month_num=row['month_num'],
            year=row['year']
        )
        for _, row in sample_buyer_interest_data.iterrows()
    ]
    service.db.execute = AsyncMock(return_value=mock_result)
    
    # Mock seasonal trends
    mock_seasonal = Mock()
    mock_seasonal.fetchall.return_value = []
    
    # Set up multiple execute calls
    service.db.execute = AsyncMock(side_effect=[mock_result, mock_seasonal])
    
    prediction = await service.predict_crop_demand(
        crop_name='wheat',
        region_state='Maharashtra',
        forecast_days=90
    )
    
    # Assertions
    assert 'demand_level' in prediction
    assert prediction['demand_level'] in ['high', 'medium', 'low', 'unknown']
    assert 'confidence_score' in prediction
    assert 'trend' in prediction
    assert prediction['trend'] in ['increasing', 'decreasing', 'stable', 'insufficient_data']
    assert 'predicted_interest_count' in prediction
    assert prediction['forecast_days'] == 90


@pytest.mark.asyncio
async def test_predict_crop_demand_no_data(service):
    """Test demand prediction with no data"""
    mock_result = Mock()
    mock_result.fetchall.return_value = []
    service.db.execute = AsyncMock(return_value=mock_result)
    
    prediction = await service.predict_crop_demand(crop_name='wheat')
    
    # Should return unknown demand
    assert prediction['demand_level'] == 'unknown'
    assert prediction['confidence_score'] == 0.0
    assert 'warning' in prediction


def test_analyze_demand_patterns_high_demand(service, sample_buyer_interest_data):
    """Test demand pattern analysis for high demand"""
    # Modify data for high demand
    sample_buyer_interest_data['interest_count'] = 60
    
    analysis = service._analyze_demand_patterns(
        sample_buyer_interest_data, {}, 90
    )
    
    assert analysis['demand_level'] == 'high'
    assert analysis['trend'] in ['increasing', 'decreasing', 'stable']
    assert analysis['predicted_interest_count'] > 0


def test_analyze_demand_patterns_low_demand(service, sample_buyer_interest_data):
    """Test demand pattern analysis for low demand"""
    # Modify data for low demand
    sample_buyer_interest_data['interest_count'] = 5
    
    analysis = service._analyze_demand_patterns(
        sample_buyer_interest_data, {}, 90
    )
    
    assert analysis['demand_level'] == 'low'


# ==================== Supply-Demand Matching Tests ====================

@pytest.mark.asyncio
async def test_match_supply_demand_success(service):
    """Test successful supply-demand matching"""
    # Mock supply forecast
    mock_supply = Mock()
    mock_supply.fetchall.return_value = [
        Mock(crop_name='wheat', expected_supply=1000, farm_count=10, avg_price=25)
    ]
    
    # Mock buyer interest for demand
    mock_demand = Mock()
    mock_demand.fetchall.return_value = [
        Mock(
            crop_type='wheat',
            state='Maharashtra',
            district='Pune',
            interest_count=30,
            month=datetime.now(UTC),
            month_num=1,
            year=2024
        )
    ]
    
    # Mock seasonal trends
    mock_seasonal = Mock()
    mock_seasonal.fetchall.return_value = []
    
    service.db.execute = AsyncMock(side_effect=[mock_supply, mock_demand, mock_seasonal])
    
    matches = await service.match_supply_demand(
        region_state='Maharashtra',
        forecast_days=90
    )
    
    # Assertions
    assert 'supply_forecast' in matches
    assert 'demand_forecast' in matches
    assert 'matches' in matches
    assert len(matches['matches']) > 0
    
    # Check match structure
    match = matches['matches'][0]
    assert 'crop' in match
    assert 'expected_supply' in match
    assert 'predicted_demand' in match
    assert 'status' in match
    assert match['status'] in ['oversupply', 'undersupply', 'balanced']
    assert 'recommendation' in match


@pytest.mark.asyncio
async def test_supply_forecast(service):
    """Test supply forecasting"""
    mock_result = Mock()
    mock_result.fetchall.return_value = [
        Mock(crop_name='wheat', expected_supply=1000, farm_count=10, avg_price=25),
        Mock(crop_name='rice', expected_supply=800, farm_count=8, avg_price=30)
    ]
    service.db.execute = AsyncMock(return_value=mock_result)
    
    supply = await service._get_supply_forecast(
        region_state='Maharashtra',
        region_district='Pune',
        forecast_days=90
    )
    
    assert 'wheat' in supply
    assert 'rice' in supply
    assert supply['wheat']['expected_supply'] == 1000
    assert supply['wheat']['farm_count'] == 10


def test_analyze_supply_demand_gaps_oversupply(service):
    """Test supply-demand gap analysis for oversupply"""
    supply = {
        'wheat': {'expected_supply': 1000, 'farm_count': 10, 'avg_price': 25}
    }
    demand = {
        'wheat': {'predicted_interest_count': 100, 'demand_level': 'low'}
    }
    
    matches = service._analyze_supply_demand_gaps(supply, demand)
    
    assert len(matches) == 1
    assert matches[0]['status'] == 'oversupply'
    assert 'recommendation' in matches[0]


def test_analyze_supply_demand_gaps_undersupply(service):
    """Test supply-demand gap analysis for undersupply"""
    supply = {
        'wheat': {'expected_supply': 100, 'farm_count': 2, 'avg_price': 25}
    }
    demand = {
        'wheat': {'predicted_interest_count': 500, 'demand_level': 'high'}
    }
    
    matches = service._analyze_supply_demand_gaps(supply, demand)
    
    assert len(matches) == 1
    assert matches[0]['status'] == 'undersupply'
    assert 'opportunity' in matches[0]['recommendation'].lower()


def test_analyze_supply_demand_gaps_balanced(service):
    """Test supply-demand gap analysis for balanced market"""
    supply = {
        'wheat': {'expected_supply': 1000, 'farm_count': 10, 'avg_price': 25}
    }
    demand = {
        'wheat': {'predicted_interest_count': 1200, 'demand_level': 'medium'}
    }
    
    matches = service._analyze_supply_demand_gaps(supply, demand)
    
    assert len(matches) == 1
    assert matches[0]['status'] == 'balanced'


# ==================== Market Opportunity Alerts Tests ====================

@pytest.mark.asyncio
async def test_generate_market_opportunities_success(service):
    """Test market opportunity generation"""
    # Mock supply-demand matching
    with patch.object(service, 'match_supply_demand') as mock_match:
        mock_match.return_value = {
            'matches': [
                {
                    'crop': 'wheat',
                    'status': 'undersupply',
                    'demand_level': 'high',
                    'recommendation': 'High demand opportunity',
                    'avg_price': 25
                }
            ]
        }
        
        # Mock price forecasting
        with patch.object(service, 'forecast_market_prices') as mock_forecast:
            mock_forecast.return_value = {
                'trend': 'increasing',
                'price_change_percentage': 15,
                'current_price': 25,
                'forecasted_price': 28.75,
                'confidence_score': 0.85
            }
            
            opportunities = await service.generate_market_opportunities(
                region_state='Maharashtra'
            )
    
    # Assertions
    assert len(opportunities) > 0
    assert opportunities[0]['type'] in ['high_demand_low_supply', 'price_spike']
    assert 'crop' in opportunities[0]
    assert 'priority' in opportunities[0]
    assert opportunities[0]['priority'] in ['high', 'medium', 'low']
    assert 'title' in opportunities[0]
    assert 'description' in opportunities[0]
    assert 'action' in opportunities[0]


@pytest.mark.asyncio
async def test_generate_market_opportunities_high_demand(service):
    """Test high demand opportunity detection"""
    with patch.object(service, 'match_supply_demand') as mock_match:
        mock_match.return_value = {
            'matches': [
                {
                    'crop': 'wheat',
                    'status': 'undersupply',
                    'demand_level': 'high',
                    'recommendation': 'Plant more wheat',
                    'avg_price': 25
                }
            ]
        }
        
        with patch.object(service, 'forecast_market_prices') as mock_forecast:
            mock_forecast.side_effect = Exception("No data")
            
            opportunities = await service.generate_market_opportunities()
    
    # Should have high demand opportunity
    high_demand_opps = [o for o in opportunities if o['type'] == 'high_demand_low_supply']
    assert len(high_demand_opps) > 0
    assert high_demand_opps[0]['priority'] == 'high'


@pytest.mark.asyncio
async def test_generate_market_opportunities_price_spike(service):
    """Test price spike opportunity detection"""
    with patch.object(service, 'match_supply_demand') as mock_match:
        mock_match.return_value = {'matches': []}
        
        with patch.object(service, 'forecast_market_prices') as mock_forecast:
            mock_forecast.return_value = {
                'trend': 'increasing',
                'price_change_percentage': 15,
                'current_price': 25,
                'forecasted_price': 28.75,
                'confidence_score': 0.85
            }
            
            opportunities = await service.generate_market_opportunities()
    
    # Should have price spike opportunity
    price_spike_opps = [o for o in opportunities if o['type'] == 'price_spike']
    assert len(price_spike_opps) > 0
    assert price_spike_opps[0]['priority'] == 'medium'


@pytest.mark.asyncio
async def test_generate_market_opportunities_sorted_by_priority(service):
    """Test opportunities are sorted by priority"""
    with patch.object(service, 'match_supply_demand') as mock_match:
        mock_match.return_value = {
            'matches': [
                {
                    'crop': 'wheat',
                    'status': 'undersupply',
                    'demand_level': 'high',
                    'recommendation': 'High priority',
                    'avg_price': 25
                }
            ]
        }
        
        with patch.object(service, 'forecast_market_prices') as mock_forecast:
            mock_forecast.return_value = {
                'trend': 'increasing',
                'price_change_percentage': 12,
                'current_price': 25,
                'forecasted_price': 28,
                'confidence_score': 0.8
            }
            
            opportunities = await service.generate_market_opportunities()
    
    # Check sorting (high priority first)
    if len(opportunities) > 1:
        priorities = [o['priority'] for o in opportunities]
        priority_values = {'high': 0, 'medium': 1, 'low': 2}
        priority_nums = [priority_values[p] for p in priorities]
        assert priority_nums == sorted(priority_nums)


# ==================== Helper Function Tests ====================

def test_get_predictive_analytics_service(mock_db):
    """Test service factory function"""
    service = get_predictive_analytics_service(mock_db)
    assert isinstance(service, PredictiveAnalyticsService)
    assert service.db == mock_db


# ==================== Integration Tests ====================

@pytest.mark.asyncio
async def test_end_to_end_price_forecast_workflow(service, sample_price_data):
    """Test complete price forecasting workflow"""
    # Mock database
    mock_result = Mock()
    mock_result.fetchall.return_value = [
        Mock(
            crop_name=row['crop_name'],
            price=row['price'],
            date=row['date'],
            state=row['state'],
            district=row['district'],
            season=row['season'],
            month=row['month'],
            year=row['year']
        )
        for _, row in sample_price_data.iterrows()
    ]
    service.db.execute = AsyncMock(return_value=mock_result)
    
    # Run forecast
    forecast = await service.forecast_market_prices(
        crop_name='wheat',
        region_state='Maharashtra',
        forecast_days=30
    )
    
    # Verify complete workflow
    assert forecast['crop_name'] == 'wheat'
    assert forecast['forecasted_price'] > 0
    assert forecast['confidence_interval']['lower'] < forecast['forecasted_price']
    assert forecast['forecasted_price'] < forecast['confidence_interval']['upper']
    assert forecast['model_accuracy'] >= 0.85  # Target accuracy


@pytest.mark.asyncio
async def test_end_to_end_demand_prediction_workflow(service, sample_buyer_interest_data):
    """Test complete demand prediction workflow"""
    # Mock database
    mock_result = Mock()
    mock_result.fetchall.return_value = [
        Mock(
            crop_type=row['crop_type'],
            state=row['state'],
            district=row['district'],
            interest_count=row['interest_count'],
            month=row['month'],
            month_num=row['month_num'],
            year=row['year']
        )
        for _, row in sample_buyer_interest_data.iterrows()
    ]
    
    mock_seasonal = Mock()
    mock_seasonal.fetchall.return_value = []
    
    service.db.execute = AsyncMock(side_effect=[mock_result, mock_seasonal])
    
    # Run prediction
    prediction = await service.predict_crop_demand(
        crop_name='wheat',
        forecast_days=90
    )
    
    # Verify complete workflow
    assert prediction['demand_level'] in ['high', 'medium', 'low']
    assert prediction['accuracy_estimate'] >= 0.80  # Target > 80%
    assert prediction['predicted_interest_count'] >= 0
