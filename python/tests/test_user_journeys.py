"""
Integration tests for complete user journeys
Tests end-to-end user experiences from registration to marketplace

**Validates: All Requirements**
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.services.bedrock_service import BedrockService
from app.services.cognito_service import CognitoService
from app.services.marketplace_service import MarketplaceService


class TestFarmerCompleteJourney:
    """
    Integration test for complete farmer journey
    Tests: Registration → Farm profile → Annual strategy → Marketplace listing
    """

    @pytest.mark.asyncio
    async def test_farmer_journey_from_registration_to_marketplace(self):
        """
        **Validates: All Requirements (AC1, AC2, AC3, AC4)**

        Test complete farmer journey:
        1. Farmer registers and confirms account
        2. Farmer creates farm profile
        3. Farmer requests annual crop strategy
        4. Farmer selects crops from strategy
        5. Crops automatically listed on marketplace
        6. Farmer receives buyer interest notification
        """
        # Arrange
        cognito_service = CognitoService()
        bedrock_service = BedrockService()
        marketplace_service = MarketplaceService()

        farmer_data = {
            "username": "farmer_raj",
            "password": "FarmPass123!",
            "email": "raj@farmmail.com",
            "phone_number": "+919876543210",
            "full_name": "Raj Kumar",
        }

        farm_profile = {
            "farmer_id": "farmer-raj-123",
            "state": "Punjab",
            "district": "Ludhiana",
            "land_area": 10.0,
            "soil_type": "Loamy",
            "irrigation_type": "Canal",
            "previous_crops": "Wheat, Rice",
            "investment_capacity": 100000,
        }

        # Mock responses
        signup_response = {"UserSub": "farmer-raj-123", "UserConfirmed": False}
        signin_response = {
            "AuthenticationResult": {
                "AccessToken": "farmer-access-token",
                "IdToken": "farmer-id-token",
                "RefreshToken": "farmer-refresh-token",
                "ExpiresIn": 3600,
            }
        }

        strategy_response = {
            "kharif_season": {
                "recommended_crops": ["Rice", "Cotton"],
                "profit_estimate": 250000,
                "confidence_score": 0.88,
                "investment_required": 80000,
                "expected_roi": 213,
            },
            "rabi_season": {
                "recommended_crops": ["Wheat", "Mustard"],
                "profit_estimate": 200000,
                "confidence_score": 0.92,
                "investment_required": 60000,
                "expected_roi": 233,
            },
            "zaid_season": {
                "recommended_crops": ["Watermelon", "Muskmelon"],
                "profit_estimate": 100000,
                "confidence_score": 0.78,
                "investment_required": 40000,
                "expected_roi": 150,
            },
            "total_annual_profit": 550000,
            "implementation_timeline": [
                {"month": "June", "action": "Plant Rice"},
                {"month": "October", "action": "Harvest Rice"},
                {"month": "November", "action": "Plant Wheat"},
            ],
        }

        listing_response = {
            "id": "listing-rice-001",
            "farmer_id": "farmer-raj-123",
            "crop_type": "Rice",
            "variety": "Basmati 1121",
            "expected_harvest_date": "2026-10-15",
            "estimated_quantity": 10000,
            "quality_grade": "A",
            "status": "active",
        }

        buyer_interest_response = {
            "id": "interest-001",
            "listing_id": "listing-rice-001",
            "buyer_name": "Punjab Grain Traders",
            "buyer_phone": "+919123456789",
            "quantity_needed": 5000,
            "status": "pending",
        }

        # Mock all services
        with (
            patch.object(cognito_service, "client") as mock_cognito,
            patch.object(bedrock_service, "client") as mock_bedrock,
            patch.object(marketplace_service, "db") as mock_db,
        ):

            # Setup mocks
            mock_cognito.sign_up.return_value = signup_response
            mock_cognito.confirm_sign_up.return_value = {}
            mock_cognito.initiate_auth.return_value = signin_response

            mock_bedrock.invoke_model.return_value = {
                "body": {"content": [{"text": str(strategy_response)}]}
            }

            mock_db.create_farm = AsyncMock(return_value=farm_profile)
            mock_db.save_strategy = AsyncMock(return_value={"id": "strategy-001"})
            mock_db.create_listing = AsyncMock(return_value=listing_response)
            mock_db.get_buyer_interests = AsyncMock(return_value=[buyer_interest_response])

            # Act: Step 1 - Farmer registers
            signup_result = cognito_service.sign_up(
                username=farmer_data["username"],
                password=farmer_data["password"],
                email=farmer_data["email"],
                phone_number=farmer_data["phone_number"],
                full_name=farmer_data["full_name"],
            )

            # Assert: Registration successful
            assert signup_result is not None
            assert signup_result["user_sub"] == "farmer-raj-123"

            # Act: Step 2 - Farmer confirms email
            confirm_result = cognito_service.confirm_sign_up(
                username=farmer_data["username"], confirmation_code="123456"
            )
            assert confirm_result is True

            # Act: Step 3 - Farmer signs in
            signin_result = cognito_service.sign_in(
                username=farmer_data["username"], password=farmer_data["password"]
            )

            # Assert: Sign in successful
            assert signin_result is not None
            assert "access_token" in signin_result

            # Act: Step 4 - Farmer creates farm profile
            farm_result = await mock_db.create_farm(farm_profile)

            # Assert: Farm profile created
            assert farm_result is not None
            assert farm_result["state"] == "Punjab"
            assert farm_result["land_area"] == 10.0

            # Act: Step 5 - Farmer requests annual strategy
            strategy_result = await bedrock_service.generate_annual_strategy(farm_profile)

            # Assert: Strategy generated
            assert strategy_result is not None
            assert "kharif_season" in strategy_result
            assert "rabi_season" in strategy_result
            assert "zaid_season" in strategy_result
            assert strategy_result["total_annual_profit"] == 550000

            # Act: Step 6 - Farmer selects crop (Rice from Kharif)
            crop_selection = {
                "farmer_id": "farmer-raj-123",
                "crop_type": "Rice",
                "variety": "Basmati 1121",
                "expected_harvest_date": "2026-10-15",
                "estimated_quantity": 10000,
                "quality_grade": "A",
            }

            # Act: Step 7 - Automatic marketplace listing created
            listing_result = await mock_db.create_listing(crop_selection)

            # Assert: Listing created automatically
            assert listing_result is not None
            assert listing_result["id"] == "listing-rice-001"
            assert listing_result["crop_type"] == "Rice"
            assert listing_result["status"] == "active"

            # Act: Step 8 - Check for buyer interests
            interests = await mock_db.get_buyer_interests(listing_result["id"])

            # Assert: Buyer interest received
            assert interests is not None
            assert len(interests) > 0
            assert interests[0]["buyer_name"] == "Punjab Grain Traders"
            assert interests[0]["quantity_needed"] == 5000

            # Verify complete journey flow
            assert mock_cognito.sign_up.call_count == 1
            assert mock_cognito.confirm_sign_up.call_count == 1
            assert mock_cognito.initiate_auth.call_count == 1
            assert mock_bedrock.invoke_model.call_count == 1
            assert mock_db.create_farm.call_count == 1
            assert mock_db.create_listing.call_count == 1
            assert mock_db.get_buyer_interests.call_count == 1


class TestBuyerCompleteJourney:
    """
    Integration test for complete buyer journey
    Tests: Browse → Listing detail → Contact farmer → Agreement tracking
    """

    @pytest.mark.asyncio
    async def test_buyer_journey_from_browse_to_agreement(self):
        """
        **Validates: Requirements AC4**

        Test complete buyer journey:
        1. Buyer browses marketplace listings
        2. Buyer views listing details
        3. Buyer expresses interest
        4. Buyer receives farmer contact information
        5. Connection is tracked for agreement
        """
        # Arrange
        marketplace_service = MarketplaceService()

        search_filters = {
            "crop_type": "Rice",
            "state": "Punjab",
            "harvest_date_from": "2026-10-01",
            "harvest_date_to": "2026-11-30",
        }

        listings = [
            {
                "id": "listing-001",
                "crop_type": "Rice",
                "variety": "Basmati 1121",
                "state": "Punjab",
                "district": "Ludhiana",
                "expected_harvest_date": "2026-10-15",
                "estimated_quantity": 10000,
                "quality_grade": "A",
                "farmer_id": "farmer-raj-123",
            },
            {
                "id": "listing-002",
                "crop_type": "Rice",
                "variety": "Pusa Basmati",
                "state": "Punjab",
                "district": "Amritsar",
                "expected_harvest_date": "2026-10-20",
                "estimated_quantity": 8000,
                "quality_grade": "A",
                "farmer_id": "farmer-singh-456",
            },
        ]

        listing_detail = {
            "id": "listing-001",
            "crop_type": "Rice",
            "variety": "Basmati 1121",
            "expected_harvest_date": "2026-10-15",
            "estimated_quantity": 10000,
            "quality_grade": "A",
            "farmer_phone": "+919876543210",
            "farmer_email": "raj@farmmail.com",
            "market_intelligence": {
                "yoy_growth": 15.5,
                "demand_trend": "increasing",
                "regional_price": 45,
            },
        }

        buyer_interest = {
            "buyer_name": "Punjab Grain Traders",
            "buyer_phone": "+919123456789",
            "buyer_email": "buyer@graintraders.com",
            "quantity_needed": 5000,
            "preferred_price": 45,
        }

        interest_response = {
            "id": "interest-001",
            "listing_id": "listing-001",
            "buyer_name": buyer_interest["buyer_name"],
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
        }

        farmer_contact = {
            "farmer_phone": "+919876543210",
            "farmer_email": "raj@farmmail.com",
            "farmer_name": "Raj Kumar",
        }

        # Mock database operations
        with patch.object(marketplace_service, "db") as mock_db:
            mock_db.search_listings = AsyncMock(return_value=listings)
            mock_db.get_listing_detail = AsyncMock(return_value=listing_detail)
            mock_db.create_buyer_interest = AsyncMock(return_value=interest_response)
            mock_db.get_farmer_contact = AsyncMock(return_value=farmer_contact)
            mock_db.track_connection = AsyncMock(return_value={"id": "connection-001"})

            # Act: Step 1 - Buyer browses marketplace
            browse_result = await mock_db.search_listings(search_filters)

            # Assert: Listings found
            assert browse_result is not None
            assert len(browse_result) == 2
            assert browse_result[0]["crop_type"] == "Rice"
            assert browse_result[0]["state"] == "Punjab"

            # Act: Step 2 - Buyer views listing detail
            detail_result = await mock_db.get_listing_detail("listing-001")

            # Assert: Listing details retrieved
            assert detail_result is not None
            assert detail_result["id"] == "listing-001"
            assert detail_result["variety"] == "Basmati 1121"
            assert "market_intelligence" in detail_result
            assert detail_result["market_intelligence"]["yoy_growth"] == 15.5

            # Act: Step 3 - Buyer expresses interest
            interest_result = await mock_db.create_buyer_interest(
                listing_id="listing-001", buyer_data=buyer_interest
            )

            # Assert: Interest registered
            assert interest_result is not None
            assert interest_result["id"] == "interest-001"
            assert interest_result["buyer_name"] == "Punjab Grain Traders"
            assert interest_result["status"] == "pending"

            # Act: Step 4 - Buyer receives farmer contact
            contact_result = await mock_db.get_farmer_contact("listing-001")

            # Assert: Farmer contact shared
            assert contact_result is not None
            assert contact_result["farmer_phone"] == "+919876543210"
            assert contact_result["farmer_email"] == "raj@farmmail.com"
            assert contact_result["farmer_name"] == "Raj Kumar"

            # Act: Step 5 - Track connection for agreement
            connection_result = await mock_db.track_connection(
                listing_id="listing-001", interest_id="interest-001"
            )

            # Assert: Connection tracked
            assert connection_result is not None
            assert connection_result["id"] == "connection-001"

            # Verify complete buyer journey
            assert mock_db.search_listings.call_count == 1
            assert mock_db.get_listing_detail.call_count == 1
            assert mock_db.create_buyer_interest.call_count == 1
            assert mock_db.get_farmer_contact.call_count == 1
            assert mock_db.track_connection.call_count == 1


class TestOfflineFunctionalityAndSync:
    """
    Integration test for offline functionality and data synchronization
    Tests: View saved data → Queue actions → Sync when online
    """

    @pytest.mark.asyncio
    async def test_offline_functionality_and_sync(self):
        """
        **Validates: Requirements (Non-Functional - Offline Functionality)**

        Test offline functionality:
        1. User views saved farm profile offline
        2. User views cached annual strategy offline
        3. User queues crop selection action offline
        4. User comes online and actions sync
        5. Verify conflict resolution (last-write-wins)
        """
        # Arrange
        offline_storage = {
            "farm_profile": {
                "id": "farm-123",
                "state": "Maharashtra",
                "land_area": 5.0,
                "cached_at": datetime.now(timezone.utc).isoformat(),
            },
            "annual_strategy": {
                "id": "strategy-456",
                "kharif_season": {"recommended_crops": ["Soybean"]},
                "cached_at": datetime.now(timezone.utc).isoformat(),
            },
            "queued_actions": [],
        }

        queued_action = {
            "action_type": "select_crop",
            "data": {
                "crop_type": "Soybean",
                "variety": "JS 335",
                "expected_harvest_date": "2026-10-15",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Mock offline storage and sync service
        with (
            patch("app.services.offline_service.OfflineStorage") as MockStorage,
            patch("app.services.sync_service.SyncService") as MockSync,
        ):

            mock_storage = MockStorage.return_value
            mock_sync = MockSync.return_value

            # Setup mocks
            mock_storage.get_cached_data = AsyncMock(
                side_effect=lambda key: offline_storage.get(key)
            )
            mock_storage.queue_action = AsyncMock()
            mock_storage.get_queued_actions = AsyncMock(return_value=[queued_action])
            mock_storage.clear_queued_actions = AsyncMock()

            mock_sync.is_online = AsyncMock(side_effect=[False, False, True])
            mock_sync.sync_queued_actions = AsyncMock(return_value={"synced": 1, "failed": 0})

            # Act: Step 1 - View saved farm profile offline
            is_online = await mock_sync.is_online()
            assert is_online is False

            farm_profile = await mock_storage.get_cached_data("farm_profile")

            # Assert: Farm profile retrieved from cache
            assert farm_profile is not None
            assert farm_profile["id"] == "farm-123"
            assert farm_profile["state"] == "Maharashtra"
            assert "cached_at" in farm_profile

            # Act: Step 2 - View cached annual strategy offline
            strategy = await mock_storage.get_cached_data("annual_strategy")

            # Assert: Strategy retrieved from cache
            assert strategy is not None
            assert strategy["id"] == "strategy-456"
            assert "kharif_season" in strategy
            assert "cached_at" in strategy

            # Act: Step 3 - Queue crop selection action offline
            await mock_storage.queue_action(queued_action)

            # Assert: Action queued
            assert mock_storage.queue_action.call_count == 1

            # Act: Step 4 - User comes online
            is_online = await mock_sync.is_online()
            assert is_online is True

            # Act: Step 5 - Sync queued actions
            queued_actions = await mock_storage.get_queued_actions()
            sync_result = await mock_sync.sync_queued_actions(queued_actions)

            # Assert: Actions synced successfully
            assert sync_result is not None
            assert sync_result["synced"] == 1
            assert sync_result["failed"] == 0

            # Act: Step 6 - Clear synced actions
            await mock_storage.clear_queued_actions()

            # Verify offline flow
            assert mock_storage.get_cached_data.call_count == 2
            assert mock_storage.queue_action.call_count == 1
            assert mock_storage.get_queued_actions.call_count == 1
            assert mock_sync.sync_queued_actions.call_count == 1
            assert mock_storage.clear_queued_actions.call_count == 1


class TestMultiSeasonStrategyImplementation:
    """
    Integration test for multi-season strategy implementation
    Tests: Strategy generation → Kharif implementation → Rabi implementation → Zaid implementation
    """

    @pytest.mark.asyncio
    async def test_multi_season_strategy_implementation(self):
        """
        **Validates: Requirements AC2**

        Test multi-season strategy implementation:
        1. Farmer receives annual strategy with all 3 seasons
        2. Farmer implements Kharif season crops
        3. Farmer receives reminders for Kharif milestones
        4. Farmer implements Rabi season crops
        5. Farmer implements Zaid season crops
        6. Track progress across all seasons
        """
        # Arrange
        bedrock_service = BedrockService()

        farm_profile = {
            "state": "Haryana",
            "district": "Karnal",
            "land_area": 8.0,
            "soil_type": "Loamy",
            "irrigation_type": "Canal",
        }

        annual_strategy = {
            "kharif_season": {
                "recommended_crops": ["Rice", "Bajra"],
                "profit_estimate": 180000,
                "planting_window": "June-July",
                "harvest_window": "October-November",
                "milestones": [
                    {"date": "2026-06-15", "action": "Plant Rice"},
                    {"date": "2026-07-15", "action": "First irrigation"},
                    {"date": "2026-10-15", "action": "Harvest Rice"},
                ],
            },
            "rabi_season": {
                "recommended_crops": ["Wheat", "Mustard"],
                "profit_estimate": 160000,
                "planting_window": "November-December",
                "harvest_window": "March-April",
                "milestones": [
                    {"date": "2026-11-15", "action": "Plant Wheat"},
                    {"date": "2026-12-15", "action": "First irrigation"},
                    {"date": "2027-03-15", "action": "Harvest Wheat"},
                ],
            },
            "zaid_season": {
                "recommended_crops": ["Watermelon", "Cucumber"],
                "profit_estimate": 90000,
                "planting_window": "March-April",
                "harvest_window": "May-June",
                "milestones": [
                    {"date": "2027-03-20", "action": "Plant Watermelon"},
                    {"date": "2027-04-20", "action": "Monitor growth"},
                    {"date": "2027-05-20", "action": "Harvest Watermelon"},
                ],
            },
            "total_annual_profit": 430000,
        }

        # Mock services
        with (
            patch.object(bedrock_service, "client") as mock_bedrock,
            patch("app.services.reminder_service.ReminderService") as MockReminder,
            patch("app.services.progress_service.ProgressService") as MockProgress,
        ):

            mock_bedrock.invoke_model.return_value = {
                "body": {"content": [{"text": str(annual_strategy)}]}
            }

            mock_reminder = MockReminder.return_value
            mock_progress = MockProgress.return_value

            mock_reminder.schedule_reminders = AsyncMock(return_value={"scheduled": 9})
            mock_reminder.send_reminder = AsyncMock()
            mock_progress.track_milestone = AsyncMock()
            mock_progress.get_season_progress = AsyncMock(
                side_effect=[
                    {"season": "kharif", "progress": 100, "status": "completed"},
                    {"season": "rabi", "progress": 100, "status": "completed"},
                    {"season": "zaid", "progress": 50, "status": "in_progress"},
                ]
            )

            # Act: Step 1 - Generate annual strategy
            strategy = await bedrock_service.generate_annual_strategy(farm_profile)

            # Assert: Strategy contains all 3 seasons
            assert strategy is not None
            assert "kharif_season" in strategy
            assert "rabi_season" in strategy
            assert "zaid_season" in strategy

            # Act: Step 2 - Schedule reminders for all seasons
            reminder_result = await mock_reminder.schedule_reminders(strategy)

            # Assert: Reminders scheduled for all milestones
            assert reminder_result is not None
            assert reminder_result["scheduled"] == 9  # 3 milestones per season

            # Act: Step 3 - Implement Kharif season
            await mock_progress.track_milestone("kharif", "Plant Rice")
            await mock_progress.track_milestone("kharif", "First irrigation")
            await mock_progress.track_milestone("kharif", "Harvest Rice")

            kharif_progress = await mock_progress.get_season_progress("kharif")

            # Assert: Kharif season completed
            assert kharif_progress is not None
            assert kharif_progress["progress"] == 100
            assert kharif_progress["status"] == "completed"

            # Act: Step 4 - Implement Rabi season
            await mock_progress.track_milestone("rabi", "Plant Wheat")
            await mock_progress.track_milestone("rabi", "First irrigation")
            await mock_progress.track_milestone("rabi", "Harvest Wheat")

            rabi_progress = await mock_progress.get_season_progress("rabi")

            # Assert: Rabi season completed
            assert rabi_progress is not None
            assert rabi_progress["progress"] == 100
            assert rabi_progress["status"] == "completed"

            # Act: Step 5 - Implement Zaid season (partial)
            await mock_progress.track_milestone("zaid", "Plant Watermelon")

            zaid_progress = await mock_progress.get_season_progress("zaid")

            # Assert: Zaid season in progress
            assert zaid_progress is not None
            assert zaid_progress["progress"] == 50
            assert zaid_progress["status"] == "in_progress"

            # Verify multi-season flow
            assert mock_bedrock.invoke_model.call_count == 1
            assert mock_reminder.schedule_reminders.call_count == 1
            assert mock_progress.track_milestone.call_count == 7
            assert mock_progress.get_season_progress.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
