"""
Unit tests for Predictive Analytics Service
"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.predictive_analytics_service import PredictiveAnalyticsService
from app.orm.market_price import MarketPrice
from app.orm.price_prediction import PricePrediction
from app.orm.buyer_interest import BuyerInterest
from app.orm.marketplace_listing import MarketplaceListing
from app.orm.advance_booking import AdvanceBooking


@pytest.fixture
def mock_db():
    """Create mock database session"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def service(mock_db):
    """Create PredictiveAnalyticsService instance"""
    with patch('app.services.predictive_analytics_service.boto3'):
        return PredictiveAnalyticsService(mock_db)


@pytest.mark.asyncio
async def test_predict_price_success(service, mock_db):
    """Test successful price prediction"""
    # Mock historical data
    historical_prices = [
        MarketPrice(
            item_type="crop",
            item_name="Wheat",
            state="Punjab",
            district="Ludhiana",
            price_per_unit=Decimal("25.00"),
            quantity=Decimal("100"),
            total_value=Decimal("2500"),
            transaction_date=datetime.now() - timedelta(days=i),
            season="Rabi",
            source="marketplace"
        )
        for i in range(30)
    ]
    
    # Mock database queries
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = historical_prices
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Mock Bedrock response
    bedrock_response = {
        "predicted_price": 27.50,
        "confidence_score": 0.85,
        "price_range_min": 26.00,
        "price_range_max": 29.00,
        "trend": "up",
        "demand_forecast": "high",
        "supply_forecast": "medium",
        "factors": ["Seasonal demand increase", "Limited supply"],
        "reasoning": "Price expected to rise due to high demand"
    }
    
    service._invoke_bedrock_price_prediction = AsyncMock(return_value=bedrock_response)
    
    # Test prediction
    result = await service.predict_price(
        item_type="crop",
        item_name="Wheat",
        state="Punjab",
        district="Ludhiana",
        forecast_days=30
    )
    
    assert result["success"] is True
    assert result["data"]["predicted_price"] == 27.50
    assert result["data"]["confidence_score"] == 0.85
    assert result["data"]["trend"] == "up"



@pytest.mark.asyncio
async def test_predict_price_insufficient_data(service, mock_db):
    """Test price prediction with insufficient historical data"""
    # Mock empty historical data
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    result = await service.predict_price(
        item_type="crop",
        item_name="Wheat",
        state="Punjab",
        forecast_days=30
    )
    
    assert result["success"] is False
    assert "Insufficient historical data" in result["error"]


@pytest.mark.asyncio
async def test_predict_price_invalid_forecast_days(service):
    """Test price prediction with invalid forecast days"""
    with pytest.raises(ValueError, match="Forecast days must be between 30 and 90"):
        await service.predict_price(
            item_type="crop",
            item_name="Wheat",
            state="Punjab",
            forecast_days=20  # Too short
        )


@pytest.mark.asyncio
async def test_predict_demand_high(service, mock_db):
    """Test demand prediction with high growth"""
    # Mock buyer interests
    buyer_interests = [
        BuyerInterest(
            listing_id=1,
            buyer_name="Buyer 1",
            buyer_phone="1234567890",
            buyer_type="wholesaler",
            interested_quantity=100,
            status="pending",
            created_at=datetime.now() - timedelta(days=i)
        )
        for i in range(20)  # Recent interests
    ]
    
    # Mock marketplace listings
    listing = MarketplaceListing(
        id=1,
        item_type="crop",
        item_name="Wheat",
        state="Punjab",
        district="Ludhiana",
        status="active"
    )
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.side_effect = [buyer_interests, [listing]]
    mock_result.scalar_one_or_none.return_value = listing
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    result = await service.predict_demand(
        item_type="crop",
        item_name="Wheat",
        state="Punjab",
        district="Ludhiana",
        forecast_days=30
    )
    
    assert result["success"] is True
    assert result["data"]["demand_level"] in ["high", "medium", "low"]
    assert "forecasted_volume" in result["data"]
    assert "confidence" in result["data"]


@pytest.mark.asyncio
async def test_identify_supply_demand_gaps(service, mock_db):
    """Test supply-demand gap identification"""
    # Mock marketplace listings (supply)
    listings = [
        MarketplaceListing(
            id=1,
            item_type="crop",
            item_name="Wheat",
            state="Punjab",
            district="Ludhiana",
            quantity=Decimal("1000"),
            status="active"
        ),
        MarketplaceListing(
            id=2,
            item_type="crop",
            item_name="Rice",
            state="Punjab",
            district="Ludhiana",
            quantity=Decimal("500"),
            status="active"
        )
    ]
    
    # Mock buyer interests (demand)
    interests = [
        BuyerInterest(
            listing_id=1,
            buyer_name="Buyer 1",
            buyer_phone="1234567890",
            buyer_type="wholesaler",
            interested_quantity=1500,  # More than supply
            status="pending"
        )
    ]
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.side_effect = [listings, interests]
    mock_result.scalar_one_or_none.return_value = listings[0]
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    result = await service.identify_supply_demand_gaps(
        state="Punjab",
        district="Ludhiana"
    )
    
    assert result["success"] is True
    assert "gaps" in result["data"]
    assert result["data"]["total_items"] > 0



@pytest.mark.asyncio
async def test_calculate_opportunity_score(service, mock_db):
    """Test opportunity score calculation"""
    # Mock historical prices
    historical_prices = [
        MarketPrice(
            item_type="crop",
            item_name="Wheat",
            state="Punjab",
            price_per_unit=Decimal("25.00"),
            quantity=Decimal("100"),
            total_value=Decimal("2500"),
            transaction_date=datetime.now() - timedelta(days=i),
            season="Rabi",
            source="marketplace"
        )
        for i in range(60)
    ]
    
    # Mock buyer interests
    buyer_interests = [
        BuyerInterest(
            listing_id=1,
            buyer_name="Buyer 1",
            buyer_phone="1234567890",
            buyer_type="wholesaler",
            interested_quantity=100,
            status="pending",
            created_at=datetime.now() - timedelta(days=i)
        )
        for i in range(15)
    ]
    
    # Mock marketplace listing
    listing = MarketplaceListing(
        id=1,
        item_type="crop",
        item_name="Wheat",
        state="Punjab",
        district="Ludhiana",
        quantity=Decimal("500"),
        status="active"
    )
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.side_effect = [
        historical_prices,  # For price trend
        buyer_interests,    # For demand
        [listing],          # For supply
        [],                 # For gaps
        []                  # For quality premiums
    ]
    mock_result.scalar_one_or_none.return_value = listing
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # Mock predict_demand
    service.predict_demand = AsyncMock(return_value={
        "success": True,
        "data": {"demand_level": "high"}
    })
    
    # Mock identify_supply_demand_gaps
    service.identify_supply_demand_gaps = AsyncMock(return_value={
        "success": True,
        "data": {
            "gaps": [{
                "item_name": "Wheat",
                "gap_type": "shortage",
                "gap_percent": 30
            }]
        }
    })
    
    result = await service.calculate_opportunity_score(
        item_type="crop",
        item_name="Wheat",
        state="Punjab",
        district="Ludhiana"
    )
    
    assert result["success"] is True
    assert "opportunity_score" in result["data"]
    assert 0 <= result["data"]["opportunity_score"] <= 100
    assert "opportunity_level" in result["data"]
    assert "score_components" in result["data"]
    assert "recommendation" in result["data"]


@pytest.mark.asyncio
async def test_generate_market_opportunity_alert(service, mock_db):
    """Test market opportunity alert generation"""
    # Mock regional crops
    crops = [{"name": "Wheat"}, {"name": "Rice"}]
    service._get_regional_crops = AsyncMock(return_value=crops)
    
    # Mock opportunity scores
    high_score_result = {
        "success": True,
        "data": {
            "item_name": "Wheat",
            "opportunity_score": 85,
            "opportunity_level": "excellent",
            "recommendation": "Strong opportunity",
            "score_components": {
                "price_trend": {"score": 25, "max": 30},
                "demand_level": {"score": 28, "max": 30, "level": "high"},
                "supply_demand_gap": {"score": 18, "max": 20},
                "profitability": {"score": 14, "max": 20}
            }
        }
    }
    
    low_score_result = {
        "success": True,
        "data": {
            "item_name": "Rice",
            "opportunity_score": 45,
            "opportunity_level": "moderate",
            "recommendation": "Moderate opportunity"
        }
    }
    
    service.calculate_opportunity_score = AsyncMock(
        side_effect=[high_score_result, low_score_result]
    )
    
    # Mock SNS client
    service.sns_client.publish = Mock(return_value={"MessageId": "msg-123"})
    
    result = await service.generate_market_opportunity_alert(
        farmer_id=1,
        state="Punjab",
        district="Ludhiana",
        min_score=70
    )
    
    assert result["success"] is True
    assert result["data"]["alerts_generated"] >= 1
    assert "opportunities" in result["data"]
    assert "sns_messages" in result["data"]


@pytest.mark.asyncio
async def test_get_buyer_supply_planning_data(service, mock_db):
    """Test buyer supply planning data"""
    # Mock upcoming listings
    future_listings = [
        MarketplaceListing(
            id=1,
            item_type="crop",
            item_name="Wheat",
            state="Punjab",
            district="Ludhiana",
            quantity=Decimal("1000"),
            price_per_unit=Decimal("25.00"),
            quality_grade="A",
            expected_harvest_date=date.today() + timedelta(days=30),
            status="active"
        ),
        MarketplaceListing(
            id=2,
            item_type="crop",
            item_name="Wheat",
            state="Punjab",
            district="Ludhiana",
            quantity=Decimal("800"),
            price_per_unit=Decimal("24.00"),
            quality_grade="B",
            expected_harvest_date=date.today() + timedelta(days=60),
            status="active"
        )
    ]
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = future_listings
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # Mock price predictions
    service.predict_price = AsyncMock(return_value={
        "success": True,
        "data": {
            "predicted_price": 26.00,
            "confidence_score": 0.8,
            "trend": "up"
        }
    })
    
    result = await service.get_buyer_supply_planning_data(
        item_type="crop",
        item_name="Wheat",
        state="Punjab",
        district="Ludhiana",
        months_ahead=3
    )
    
    assert result["success"] is True
    assert "supply_by_month" in result["data"]
    assert "total_upcoming_supply" in result["data"]
    assert "price_forecasts" in result["data"]
    assert result["data"]["total_upcoming_supply"] > 0


@pytest.mark.asyncio
async def test_fallback_prediction(service):
    """Test fallback prediction when Bedrock fails"""
    fallback = service._create_fallback_prediction(25.00)
    
    assert fallback["predicted_price"] == 25.00
    assert fallback["confidence_score"] == 0.5
    assert fallback["trend"] == "stable"
    assert fallback["model_version"] == "fallback-v1"
    assert "Insufficient data" in fallback["factors"]
