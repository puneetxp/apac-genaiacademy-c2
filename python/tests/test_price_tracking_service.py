"""
Unit tests for Price Tracking Service
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.price_tracking_service import PriceTrackingService


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def service(mock_db):
    """Create service instance with mock db"""
    return PriceTrackingService(mock_db)


@pytest.mark.asyncio
async def test_collect_price_from_listing_success(service, mock_db):
    """Test collecting price data from a marketplace listing"""
    # Mock listing data
    mock_listing = {
        "id": 1,
        "crop_type": "Wheat",
        "crop_variety": "HD-2967",
        "price_per_unit": 25.50,
        "estimated_quantity": 1000,
        "quality_grade": "A",
        "location_state": "Punjab",
        "location_district": "Ludhiana",
        "expected_harvest_date": datetime(2024, 4, 15),
    }

    # Mock MarketplaceListing.find
    with patch("app.services.price_tracking_service.MarketplaceListing") as mock_listing_class:
        mock_listing_class.find = AsyncMock(return_value=mock_listing)

        # Mock MarketPrice.create
        with patch("app.services.price_tracking_service.MarketPrice") as mock_price_class:
            mock_price_class.create = AsyncMock(return_value={"id": 1, "item_name": "Wheat"})

            result = await service.collect_price_from_listing(1)

            assert result is not None
            assert result["item_name"] == "Wheat"
            mock_price_class.create.assert_called_once()


@pytest.mark.asyncio
async def test_collect_price_from_listing_no_price(service, mock_db):
    """Test collecting price from listing without price data"""
    mock_listing = {"id": 1, "crop_type": "Wheat", "price_per_unit": None}  # No price

    with patch("app.services.price_tracking_service.MarketplaceListing") as mock_listing_class:
        mock_listing_class.find = AsyncMock(return_value=mock_listing)

        result = await service.collect_price_from_listing(1)

        assert result is None


@pytest.mark.asyncio
async def test_collect_price_from_booking_with_premium(service, mock_db):
    """Test collecting price from booking with quality premium"""
    mock_booking = {
        "id": 1,
        "listing_id": 1,
        "price_per_unit": 30.00,
        "quantity_booked": 500,
        "total_amount": 15000,
        "booking_date": datetime.now(),
        "expected_delivery_date": datetime(2024, 4, 20),
    }

    mock_listing = {
        "id": 1,
        "crop_type": "Wheat",
        "crop_variety": "HD-2967",
        "price_per_unit": 25.00,  # Base price
        "quality_grade": "A",
        "location_state": "Punjab",
        "location_district": "Ludhiana",
    }

    with patch("app.services.price_tracking_service.AdvanceBooking") as mock_booking_class:
        mock_booking_class.find = AsyncMock(return_value=mock_booking)

        with patch("app.services.price_tracking_service.MarketplaceListing") as mock_listing_class:
            mock_listing_class.find = AsyncMock(return_value=mock_listing)

            with patch("app.services.price_tracking_service.MarketPrice") as mock_price_class:
                mock_price_class.create = AsyncMock(return_value={"id": 1})

                result = await service.collect_price_from_booking(1)

                assert result is not None
                # Verify quality premium was calculated
                call_args = mock_price_class.create.call_args[0][0]
                assert "quality_premium_percent" in call_args
                # Premium should be 20% ((30-25)/25 * 100)
                assert call_args["quality_premium_percent"] == 20.0


@pytest.mark.asyncio
async def test_get_price_trends_with_data(service, mock_db):
    """Test getting price trends with sufficient data"""
    # Mock price data over 90 days
    mock_prices = []
    base_date = datetime.now() - timedelta(days=90)

    for i in range(30):
        mock_prices.append(
            {
                "price_per_unit": 25.0 + (i * 0.5),  # Increasing trend
                "quantity": 100,
                "transaction_date": base_date + timedelta(days=i * 3),
            }
        )

    with patch("app.services.price_tracking_service.MarketPrice") as mock_price_class:
        mock_price_class.where = AsyncMock(return_value=mock_prices)

        result = await service.get_price_trends(
            item_type="crop", item_name="Wheat", state="Punjab", days=90
        )

        assert result["data_points"] == 30
        assert result["trend"] == "up"  # Prices are increasing
        assert result["avg_price"] > 0
        assert result["min_price"] <= result["avg_price"] <= result["max_price"]
        assert "time_series" in result
        assert len(result["time_series"]) > 0


@pytest.mark.asyncio
async def test_get_price_trends_insufficient_data(service, mock_db):
    """Test getting price trends with no data"""
    with patch("app.services.price_tracking_service.MarketPrice") as mock_price_class:
        mock_price_class.where = AsyncMock(return_value=[])

        result = await service.get_price_trends(item_type="crop", item_name="Wheat", days=90)

        assert result["data_points"] == 0
        assert result["trend"] == "insufficient_data"


@pytest.mark.asyncio
async def test_get_quality_premiums(service, mock_db):
    """Test getting quality premium analysis"""
    mock_prices = [
        {
            "quality_grade": "A",
            "price_per_unit": 30.0,
            "quality_premium_percent": 20.0,
            "transaction_date": datetime.now(),
        },
        {
            "quality_grade": "A",
            "price_per_unit": 32.0,
            "quality_premium_percent": 25.0,
            "transaction_date": datetime.now(),
        },
        {
            "quality_grade": "B",
            "price_per_unit": 25.0,
            "quality_premium_percent": 0.0,
            "transaction_date": datetime.now(),
        },
        {
            "quality_grade": "C",
            "price_per_unit": 20.0,
            "quality_premium_percent": -10.0,
            "transaction_date": datetime.now(),
        },
    ]

    with patch("app.services.price_tracking_service.MarketPrice") as mock_price_class:
        mock_price_class.where = AsyncMock(return_value=mock_prices)

        result = await service.get_quality_premiums(
            item_type="crop", item_name="Wheat", state="Punjab", days=90
        )

        assert result["data_points"] == 4
        assert "A" in result["grades"]
        assert "B" in result["grades"]
        assert "C" in result["grades"]

        # Grade A should have highest average price
        assert result["grades"]["A"]["avg_price"] == 31.0
        assert result["grades"]["A"]["avg_premium_percent"] == 22.5
        assert result["grades"]["A"]["transactions"] == 2


@pytest.mark.asyncio
async def test_get_demand_forecast_high_demand(service, mock_db):
    """Test demand forecast with increasing demand"""
    # Mock booking data showing increasing trend
    mock_bookings = []
    base_date = datetime.now() - timedelta(days=90)

    # Older bookings: lower volume
    for i in range(20):
        mock_bookings.append(
            {
                "quantity": 50,
                "transaction_date": base_date + timedelta(days=i * 2),
                "source": "booking",
            }
        )

    # Recent bookings: higher volume
    for i in range(20):
        mock_bookings.append(
            {
                "quantity": 100,
                "transaction_date": datetime.now() - timedelta(days=30 - i),
                "source": "booking",
            }
        )

    with patch("app.services.price_tracking_service.MarketPrice") as mock_price_class:
        mock_price_class.where = AsyncMock(return_value=mock_bookings)

        result = await service.get_demand_forecast(
            item_type="crop", item_name="Wheat", state="Punjab", days_ahead=30
        )

        assert result["demand_level"] == "high"
        assert result["confidence"] > 0.7
        assert result["forecasted_volume"] > 0


@pytest.mark.asyncio
async def test_determine_season_kharif(service):
    """Test season determination for Kharif season"""
    # July is Kharif season
    date = datetime(2024, 7, 15)
    season = service._determine_season(date)
    assert season == "Kharif"


@pytest.mark.asyncio
async def test_determine_season_rabi(service):
    """Test season determination for Rabi season"""
    # December is Rabi season
    date = datetime(2024, 12, 15)
    season = service._determine_season(date)
    assert season == "Rabi"


@pytest.mark.asyncio
async def test_determine_season_zaid(service):
    """Test season determination for Zaid season"""
    # April is Zaid season
    date = datetime(2024, 4, 15)
    season = service._determine_season(date)
    assert season == "Zaid"


@pytest.mark.asyncio
async def test_collect_price_from_livestock_transaction(service, mock_db):
    """Test collecting price from livestock transaction"""
    mock_transaction = {
        "id": 1,
        "listing_id": 1,
        "status": "completed",
        "agreed_price": 50000,
        "quantity": 2,
        "completed_at": datetime.now(),
    }

    mock_listing = {
        "id": 1,
        "species": "Cattle",
        "breed": "Holstein",
        "location_state": "Punjab",
        "location_district": "Ludhiana",
    }

    with patch("app.services.price_tracking_service.LivestockTransaction") as mock_trans_class:
        mock_trans_class.find = AsyncMock(return_value=mock_transaction)

        with patch("app.services.price_tracking_service.LivestockListing") as mock_listing_class:
            mock_listing_class.find = AsyncMock(return_value=mock_listing)

            with patch("app.services.price_tracking_service.MarketPrice") as mock_price_class:
                mock_price_class.create = AsyncMock(return_value={"id": 1})

                result = await service.collect_price_from_livestock_transaction(1)

                assert result is not None
                call_args = mock_price_class.create.call_args[0][0]
                assert call_args["item_type"] == "livestock"
                assert call_args["item_name"] == "Cattle"
                assert call_args["price_per_unit"] == 25000  # 50000 / 2


@pytest.mark.asyncio
async def test_collect_price_from_livestock_transaction_not_completed(service, mock_db):
    """Test collecting price from incomplete livestock transaction"""
    mock_transaction = {"id": 1, "status": "inquiry", "agreed_price": 50000}  # Not completed

    with patch("app.services.price_tracking_service.LivestockTransaction") as mock_trans_class:
        mock_trans_class.find = AsyncMock(return_value=mock_transaction)

        result = await service.collect_price_from_livestock_transaction(1)

        assert result is None
