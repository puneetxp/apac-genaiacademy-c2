"""
Tests for Analytics Service
Validates farmer analytics, platform analytics, market analytics, and executive reports
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics_service import AnalyticsService
from app.orm.user import User
from app.orm.farm import Farm
from app.orm.crop import Crop
from app.orm.annual_strategy import AnnualStrategy
from app.orm.marketplace_listing import MarketplaceListing
from app.orm.buyer_interest import BuyerInterest


@pytest.fixture
async def analytics_service(db_session: AsyncSession):
    """Create analytics service instance"""
    return AnalyticsService(db_session)


@pytest.fixture
async def sample_farmer(db_session: AsyncSession):
    """Create sample farmer user"""
    user = User()
    user.email = "farmer@test.com"
    user.phone = "+919876543210"
    user.full_name = "Test Farmer"
    user.user_type = "farmer"
    user.created_at = datetime.now()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_farm(db_session: AsyncSession, sample_farmer):
    """Create sample farm"""
    farm = Farm()
    farm.farmer_id = sample_farmer.id
    farm.name = "Test Farm"
    farm.location_state = "Maharashtra"
    farm.location_district = "Pune"
    farm.total_area = 10.0
    farm.created_at = datetime.now()
    db_session.add(farm)
    await db_session.commit()
    await db_session.refresh(farm)
    return farm



@pytest.fixture
async def sample_crops(db_session: AsyncSession, sample_farm):
    """Create sample crops with actual and expected data"""
    crops = []
    for i in range(5):
        crop = Crop()
        crop.farm_plot_id = sample_farm.id
        crop.crop_name = f"Wheat_{i}"
        crop.season = "Rabi" if i % 2 == 0 else "Kharif"
        crop.planting_date = datetime.now() - timedelta(days=90 - i * 10)
        crop.expected_harvest_date = datetime.now() + timedelta(days=30 + i * 5)
        crop.expected_yield = 100.0 + i * 10
        crop.actual_yield = 95.0 + i * 10
        crop.expected_profit = 10000.0 + i * 1000
        crop.actual_profit = 9500.0 + i * 1000
        crop.status = "harvested"
        crop.created_at = datetime.now() - timedelta(days=90 - i * 10)
        db_session.add(crop)
        crops.append(crop)
    
    await db_session.commit()
    for crop in crops:
        await db_session.refresh(crop)
    return crops


@pytest.fixture
async def sample_strategy(db_session: AsyncSession, sample_farmer, sample_farm):
    """Create sample annual strategy"""
    strategy = AnnualStrategy()
    strategy.farmer_id = sample_farmer.id
    strategy.farm_id = sample_farm.id
    strategy.year = 2024
    strategy.kharif_crop = "Rice"
    strategy.kharif_profit_estimate = 50000.0
    strategy.rabi_crop = "Wheat"
    strategy.rabi_profit_estimate = 45000.0
    strategy.zaid_crop = "Vegetables"
    strategy.zaid_profit_estimate = 30000.0
    strategy.total_annual_profit = 125000.0
    strategy.created_at = datetime.now() - timedelta(days=180)
    db_session.add(strategy)
    await db_session.commit()
    await db_session.refresh(strategy)
    return strategy


@pytest.mark.asyncio
async def test_get_farmer_analytics(analytics_service, sample_farmer, sample_farm, sample_crops, sample_strategy):
    """Test farmer analytics generation"""
    analytics = await analytics_service.get_farmer_analytics(sample_farmer.id)
    
    assert analytics is not None
    assert analytics["farmer_id"] == sample_farmer.id
    assert "crop_performance" in analytics
    assert "profit_trends" in analytics
    assert "roi_tracking" in analytics
    assert "regional_comparison" in analytics
    
    # Verify crop performance metrics
    crop_perf = analytics["crop_performance"]
    assert crop_perf["total_crops"] == 5
    assert crop_perf["total_actual_yield"] > 0
    assert crop_perf["total_expected_yield"] > 0
    assert crop_perf["yield_accuracy_percentage"] > 0
    assert crop_perf["profit_accuracy_percentage"] > 0


@pytest.mark.asyncio
async def test_crop_performance_metrics(analytics_service, sample_farmer, sample_crops):
    """Test crop performance calculation accuracy"""
    analytics = await analytics_service.get_farmer_analytics(sample_farmer.id)
    crop_perf = analytics["crop_performance"]
    
    # Verify yield accuracy calculation
    expected_total_yield = sum(float(c.expected_yield) for c in sample_crops)
    actual_total_yield = sum(float(c.actual_yield) for c in sample_crops)
    expected_accuracy = (actual_total_yield / expected_total_yield * 100)
    
    assert abs(crop_perf["yield_accuracy_percentage"] - expected_accuracy) < 1.0
    assert crop_perf["total_crops"] == len(sample_crops)



@pytest.mark.asyncio
async def test_profit_trends(analytics_service, sample_farmer, sample_crops):
    """Test profit trends calculation"""
    analytics = await analytics_service.get_farmer_analytics(sample_farmer.id)
    profit_trends = analytics["profit_trends"]
    
    assert "monthly_trends" in profit_trends
    assert "total_actual_profit" in profit_trends
    assert profit_trends["total_actual_profit"] > 0
    
    # Verify monthly trends structure
    if profit_trends["monthly_trends"]:
        trend = profit_trends["monthly_trends"][0]
        assert "month" in trend
        assert "expected" in trend
        assert "actual" in trend
        assert "count" in trend


@pytest.mark.asyncio
async def test_roi_tracking(analytics_service, sample_farmer, sample_strategy, sample_crops):
    """Test ROI tracking calculation"""
    analytics = await analytics_service.get_farmer_analytics(sample_farmer.id)
    roi = analytics["roi_tracking"]
    
    assert "total_investment_estimate" in roi
    assert "total_expected_returns" in roi
    assert "total_actual_returns" in roi
    assert "roi_percentage" in roi
    assert "profit_margin" in roi
    
    assert roi["total_expected_returns"] > 0
    assert roi["roi_percentage"] >= 0


@pytest.mark.asyncio
async def test_regional_comparison(analytics_service, sample_farmer, sample_farm, sample_crops):
    """Test regional comparison calculation"""
    analytics = await analytics_service.get_farmer_analytics(sample_farmer.id)
    regional = analytics["regional_comparison"]
    
    assert "regional_average_profit" in regional
    assert "farmer_average_profit" in regional
    assert "performance" in regional
    assert regional["performance"] in ["Above Average", "Below Average"]


@pytest.mark.asyncio
async def test_platform_analytics(analytics_service, sample_farmer):
    """Test platform analytics generation"""
    analytics = await analytics_service.get_platform_analytics()
    
    assert analytics is not None
    assert "user_adoption" in analytics
    assert "feature_usage" in analytics
    assert "prediction_accuracy" in analytics
    
    # Verify user adoption metrics
    user_adoption = analytics["user_adoption"]
    assert "total_users" in user_adoption
    assert "new_users_period" in user_adoption
    assert "active_users_period" in user_adoption
    assert "retention_rate_percentage" in user_adoption


@pytest.mark.asyncio
async def test_feature_usage_statistics(analytics_service, sample_strategy):
    """Test feature usage statistics"""
    analytics = await analytics_service.get_platform_analytics()
    feature_usage = analytics["feature_usage"]
    
    assert "annual_strategies_created" in feature_usage
    assert "marketplace_listings_created" in feature_usage
    assert "buyer_interests_registered" in feature_usage
    assert "most_used_feature" in feature_usage
    assert feature_usage["annual_strategies_created"] >= 1


@pytest.mark.asyncio
async def test_prediction_accuracy(analytics_service, sample_crops):
    """Test prediction accuracy calculation"""
    analytics = await analytics_service.get_platform_analytics()
    accuracy = analytics["prediction_accuracy"]
    
    assert "overall_accuracy_percentage" in accuracy
    assert "yield_accuracy_percentage" in accuracy
    assert "profit_accuracy_percentage" in accuracy
    assert "samples_analyzed" in accuracy
    
    assert 0 <= accuracy["overall_accuracy_percentage"] <= 100
    assert accuracy["samples_analyzed"] >= 0



@pytest.mark.asyncio
async def test_market_analytics(analytics_service, sample_crops):
    """Test market analytics generation"""
    analytics = await analytics_service.get_market_analytics()
    
    assert analytics is not None
    assert "price_trends" in analytics
    assert "demand_patterns" in analytics
    assert "supply_forecast" in analytics


@pytest.mark.asyncio
async def test_price_trends(analytics_service, sample_crops):
    """Test price trends calculation"""
    analytics = await analytics_service.get_market_analytics()
    price_trends = analytics["price_trends"]
    
    assert "crop_price_trends" in price_trends
    
    # Verify price trend structure
    if price_trends["crop_price_trends"]:
        trend = price_trends["crop_price_trends"][0]
        assert "crop" in trend
        assert "average_price" in trend
        assert "min_price" in trend
        assert "max_price" in trend
        assert "samples" in trend


@pytest.mark.asyncio
async def test_demand_patterns(analytics_service, db_session, sample_farm, sample_farmer):
    """Test demand patterns calculation"""
    # Create marketplace listing
    listing = MarketplaceListing()
    listing.farm_id = sample_farm.id
    listing.farmer_id = sample_farmer.id
    listing.crop_type = "Wheat"
    listing.crop_variety = "HD-2967"
    listing.expected_harvest_date = datetime.now() + timedelta(days=30)
    listing.estimated_quantity = 1000.0
    listing.location_state = "Maharashtra"
    listing.location_district = "Pune"
    listing.created_at = datetime.now()
    db_session.add(listing)
    await db_session.commit()
    await db_session.refresh(listing)
    
    # Create buyer interest
    interest = BuyerInterest()
    interest.listing_id = listing.id
    interest.buyer_name = "Test Buyer"
    interest.buyer_phone = "+919876543211"
    interest.buyer_email = "buyer@test.com"
    interest.buyer_type = "wholesaler"
    interest.interested_quantity = 500.0
    interest.created_at = datetime.now()
    db_session.add(interest)
    await db_session.commit()
    
    analytics = await analytics_service.get_market_analytics()
    demand = analytics["demand_patterns"]
    
    assert "top_demanded_crops" in demand
    assert "top_demand_regions" in demand
    assert "total_buyer_interests" in demand
    assert demand["total_buyer_interests"] >= 1


@pytest.mark.asyncio
async def test_supply_forecast(analytics_service, db_session, sample_farm):
    """Test supply forecasting"""
    # Create future crop
    future_crop = Crop()
    future_crop.farm_plot_id = sample_farm.id
    future_crop.crop_name = "Rice"
    future_crop.season = "Kharif"
    future_crop.planting_date = datetime.now() - timedelta(days=30)
    future_crop.expected_harvest_date = datetime.now() + timedelta(days=60)
    future_crop.expected_yield = 200.0
    future_crop.status = "planted"
    future_crop.created_at = datetime.now() - timedelta(days=30)
    db_session.add(future_crop)
    await db_session.commit()
    
    analytics = await analytics_service.get_market_analytics()
    supply = analytics["supply_forecast"]
    
    assert "upcoming_harvests_90_days" in supply
    assert "total_upcoming_crops" in supply
    assert supply["total_upcoming_crops"] >= 1


@pytest.mark.asyncio
async def test_executive_report(analytics_service, sample_farmer, sample_crops, sample_strategy):
    """Test executive report generation"""
    report = await analytics_service.generate_executive_report()
    
    assert report is not None
    assert "report_generated_at" in report
    assert "period" in report
    assert "key_metrics" in report
    assert "insights" in report
    assert "recommendations" in report
    
    # Verify key metrics
    metrics = report["key_metrics"]
    assert "total_users" in metrics
    assert "active_users" in metrics
    assert "prediction_accuracy" in metrics
    assert "total_buyer_interests" in metrics
    
    # Verify insights and recommendations are lists
    assert isinstance(report["insights"], list)
    assert isinstance(report["recommendations"], list)
    assert len(report["insights"]) > 0
    assert len(report["recommendations"]) > 0


@pytest.mark.asyncio
async def test_analytics_with_date_range(analytics_service, sample_farmer, sample_crops):
    """Test analytics with custom date range"""
    start_date = datetime.now() - timedelta(days=60)
    end_date = datetime.now()
    
    analytics = await analytics_service.get_farmer_analytics(sample_farmer.id, start_date, end_date)
    
    assert analytics is not None
    assert analytics["period"]["start_date"] == start_date.isoformat()
    assert analytics["period"]["end_date"] == end_date.isoformat()


@pytest.mark.asyncio
async def test_analytics_empty_data(analytics_service):
    """Test analytics with no data"""
    # Test with non-existent farmer
    analytics = await analytics_service.get_farmer_analytics(99999)
    
    assert analytics is not None
    assert analytics["crop_performance"]["total_crops"] == 0


@pytest.mark.asyncio
async def test_insights_generation(analytics_service):
    """Test insights generation logic"""
    platform_analytics = {
        "user_adoption": {"retention_rate_percentage": 75.0},
        "prediction_accuracy": {"overall_accuracy_percentage": 88.0},
        "feature_usage": {"most_used_feature": "annual_strategy"}
    }
    market_analytics = {
        "demand_patterns": {"top_demanded_crops": [{"crop": "Wheat", "interest_count": 10}]}
    }
    
    insights = analytics_service._generate_insights(platform_analytics, market_analytics)
    
    assert isinstance(insights, list)
    assert len(insights) > 0
    assert any("retention" in insight.lower() for insight in insights)


@pytest.mark.asyncio
async def test_recommendations_generation(analytics_service):
    """Test recommendations generation logic"""
    platform_analytics = {
        "user_adoption": {"retention_rate_percentage": 55.0},
        "prediction_accuracy": {"overall_accuracy_percentage": 82.0},
        "feature_usage": {"annual_strategies_created": 100}
    }
    market_analytics = {
        "demand_patterns": {
            "top_demanded_crops": [{"crop": "Wheat", "interest_count": 10}],
            "total_buyer_interests": 30
        }
    }
    
    recommendations = analytics_service._generate_recommendations(platform_analytics, market_analytics)
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert any("improve" in rec.lower() or "increase" in rec.lower() for rec in recommendations)
