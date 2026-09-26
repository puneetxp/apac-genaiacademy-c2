"""
Test Match Acceptance and Coordination System
Tests for Task 36.3 - Match acceptance workflow, farmer notifications, and coordination
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.supply_request_matching_service import SupplyRequestMatchingService


class TestMatchAcceptanceWorkflow:
    """Test buyer match acceptance and booking creation"""

    def test_accept_single_match_creates_booking(self):
        """Test that accepting a single match creates a booking and notifies farmer"""
        service = SupplyRequestMatchingService()

        # Mock data
        request_id = 1
        match_id = 10

        with (
            patch("app.services.supply_request_matching_service.SupplyMatch") as MockMatch,
            patch("app.services.supply_request_matching_service.SupplyRequest") as MockRequest,
            patch("app.services.supply_request_matching_service.AdvanceBooking") as MockBooking,
            patch("app.services.supply_request_matching_service.MarketplaceListing") as MockListing,
            patch(
                "app.services.supply_request_matching_service.get_notification_service"
            ) as MockNotification,
        ):

            # Setup mocks
            mock_match_instance = MockMatch.return_value
            mock_request_instance = MockRequest.return_value
            mock_booking_instance = MockBooking.return_value
            mock_listing_instance = MockListing.return_value
            mock_notification = MockNotification.return_value

            # Mock supply request
            mock_request_instance.find.return_value = {
                "id": request_id,
                "buyer_id": 100,
                "crop_type": "Wheat",
                "quantity_needed": 1000,
                "delivery_date_end": datetime.now() + timedelta(days=30),
                "quality_requirements": "Grade A",
            }

            # Mock match
            mock_match_instance.find.return_value = {
                "id": match_id,
                "request_id": request_id,
                "listing_id": 50,
                "farmer_id": 200,
                "matched_quantity": 1000,
                "price_offered": 25.50,
                "match_score": 85,
            }

            # Mock listing
            mock_listing_instance.find.return_value = {
                "id": 50,
                "farmer_id": 200,
                "crop_type": "Wheat",
                "farmer_contact_phone": "+919876543210",
                "farmer_contact_email": "farmer@example.com",
            }

            # Mock booking insert
            mock_booking_instance.insert.return_value = 1001

            # Mock notification
            mock_notification._send_notification.return_value = {
                "success": True,
                "message_id": "msg-123",
            }

            # Execute
            result = service.accept_match(request_id=request_id, match_id=match_id)

            # Verify
            assert result["success"] is True
            assert len(result["booking_ids"]) == 1
            assert result["booking_ids"][0] == 1001
            assert result["awaiting_farmer_confirmation"] is True
            assert "acceptance_timestamp" in result

            # Verify booking was created
            mock_booking_instance.insert.assert_called_once()
            booking_data = mock_booking_instance.insert.call_args[0][0]
            assert booking_data["buyer_id"] == 100
            assert booking_data["farmer_id"] == 200
            assert booking_data["quantity_booked"] == 1000
            assert booking_data["status"] == "pending_farmer_confirmation"

            # Verify match was updated
            mock_match_instance.update.assert_called_once()
            update_data = mock_match_instance.update.call_args[0][1]
            assert update_data["status"] == "buyer_accepted"
            assert update_data["farmer_confirmation_status"] == "pending"

            # Verify notification was sent
            mock_notification._send_notification.assert_called_once()

    def test_accept_aggregated_match_creates_multiple_bookings(self):
        """Test that accepting aggregated match creates multiple bookings"""
        service = SupplyRequestMatchingService()

        request_id = 1
        aggregation_group_id = "agg_1_0"

        with (
            patch("app.services.supply_request_matching_service.SupplyMatch") as MockMatch,
            patch("app.services.supply_request_matching_service.SupplyRequest") as MockRequest,
            patch("app.services.supply_request_matching_service.AdvanceBooking") as MockBooking,
            patch("app.services.supply_request_matching_service.MarketplaceListing") as MockListing,
            patch(
                "app.services.supply_request_matching_service.get_notification_service"
            ) as MockNotification,
        ):

            # Setup mocks
            mock_match_instance = MockMatch.return_value
            mock_request_instance = MockRequest.return_value
            mock_booking_instance = MockBooking.return_value
            mock_listing_instance = MockListing.return_value
            mock_notification = MockNotification.return_value

            # Mock supply request
            mock_request_instance.find.return_value = {
                "id": request_id,
                "buyer_id": 100,
                "crop_type": "Rice",
                "quantity_needed": 5000,
                "delivery_date_end": datetime.now() + timedelta(days=30),
            }

            # Mock aggregated matches (3 farmers)
            mock_match_instance.where.return_value.where.return_value.get.return_value = [
                {
                    "id": 11,
                    "request_id": request_id,
                    "listing_id": 51,
                    "farmer_id": 201,
                    "matched_quantity": 2000,
                    "price_offered": 30.00,
                    "aggregation_group_id": aggregation_group_id,
                },
                {
                    "id": 12,
                    "request_id": request_id,
                    "listing_id": 52,
                    "farmer_id": 202,
                    "matched_quantity": 1500,
                    "price_offered": 29.50,
                    "aggregation_group_id": aggregation_group_id,
                },
                {
                    "id": 13,
                    "request_id": request_id,
                    "listing_id": 53,
                    "farmer_id": 203,
                    "matched_quantity": 1500,
                    "price_offered": 30.50,
                    "aggregation_group_id": aggregation_group_id,
                },
            ]

            # Mock listings
            mock_listing_instance.find.side_effect = [
                {"id": 51, "farmer_id": 201, "farmer_contact_phone": "+919876543211"},
                {"id": 52, "farmer_id": 202, "farmer_contact_phone": "+919876543212"},
                {"id": 53, "farmer_id": 203, "farmer_contact_phone": "+919876543213"},
            ]

            # Mock booking inserts
            mock_booking_instance.insert.side_effect = [1001, 1002, 1003]

            # Mock notifications
            mock_notification._send_notification.return_value = {"success": True}

            # Execute
            result = service.accept_match(
                request_id=request_id, aggregation_group_id=aggregation_group_id
            )

            # Verify
            assert result["success"] is True
            assert len(result["booking_ids"]) == 3
            assert result["booking_ids"] == [1001, 1002, 1003]
            assert result["notifications_sent"] == 3

            # Verify 3 bookings were created
            assert mock_booking_instance.insert.call_count == 3

            # Verify 3 notifications were sent
            assert mock_notification._send_notification.call_count == 3


class TestFarmerConfirmationWorkflow:
    """Test farmer confirmation/rejection of matches"""

    def test_farmer_confirms_match(self):
        """Test farmer confirming a match"""
        service = SupplyRequestMatchingService()

        match_id = 10
        farmer_id = 200

        with (
            patch("app.services.supply_request_matching_service.SupplyMatch") as MockMatch,
            patch("app.services.supply_request_matching_service.AdvanceBooking") as MockBooking,
            patch("app.services.supply_request_matching_service.SupplyRequest") as MockRequest,
            patch(
                "app.services.supply_request_matching_service.get_notification_service"
            ) as MockNotification,
            patch.object(service, "_create_payment_milestones") as mock_create_milestones,
            patch.object(service, "_notify_buyer_of_farmer_confirmation") as mock_notify_buyer,
        ):

            # Setup mocks
            mock_match_instance = MockMatch.return_value
            mock_booking_instance = MockBooking.return_value
            mock_request_instance = MockRequest.return_value

            # Mock match
            mock_match_instance.find.return_value = {
                "id": match_id,
                "farmer_id": farmer_id,
                "request_id": 1,
                "farmer_confirmation_status": "pending",
                "listing_id": 50,
                "matched_quantity": 1000,
                "is_aggregated": False,
            }

            # Mock booking
            mock_booking_instance.where.return_value.where.return_value.where.return_value.first.return_value = {
                "id": 1001,
                "status": "pending_farmer_confirmation",
            }

            # Mock supply request
            mock_request_instance.find.return_value = {
                "id": 1,
                "buyer_id": 100,
                "crop_type": "Wheat",
            }

            # Execute
            result = service.farmer_confirm_match(
                match_id=match_id, farmer_id=farmer_id, confirmation=True, notes="Ready to deliver"
            )

            # Verify
            assert result["success"] is True
            assert result["status"] == "confirmed"
            assert "confirmation_timestamp" in result
            assert "next_steps" in result

            # Verify match was updated
            mock_match_instance.update.assert_called()
            update_data = mock_match_instance.update.call_args[0][1]
            assert update_data["farmer_confirmation_status"] == "confirmed"
            assert update_data["status"] == "confirmed"

            # Verify booking was updated
            mock_booking_instance.update.assert_called()

            # Verify payment milestones were created
            mock_create_milestones.assert_called_once()

            # Verify buyer was notified
            mock_notify_buyer.assert_called_once()

    def test_farmer_rejects_match(self):
        """Test farmer rejecting a match"""
        service = SupplyRequestMatchingService()

        match_id = 10
        farmer_id = 200

        with (
            patch("app.services.supply_request_matching_service.SupplyMatch") as MockMatch,
            patch("app.services.supply_request_matching_service.AdvanceBooking") as MockBooking,
            patch("app.services.supply_request_matching_service.SupplyRequest") as MockRequest,
            patch(
                "app.services.supply_request_matching_service.get_notification_service"
            ) as MockNotification,
            patch.object(service, "_notify_buyer_of_farmer_confirmation") as mock_notify_buyer,
        ):

            # Setup mocks
            mock_match_instance = MockMatch.return_value
            mock_booking_instance = MockBooking.return_value
            mock_request_instance = MockRequest.return_value

            # Mock match
            mock_match_instance.find.return_value = {
                "id": match_id,
                "farmer_id": farmer_id,
                "request_id": 1,
                "farmer_confirmation_status": "pending",
                "listing_id": 50,
                "is_aggregated": False,
            }

            # Mock booking
            mock_booking_instance.where.return_value.where.return_value.where.return_value.first.return_value = {
                "id": 1001,
                "status": "pending_farmer_confirmation",
            }

            # Mock supply request
            mock_request_instance.find.return_value = {"id": 1, "buyer_id": 100}

            # Execute
            result = service.farmer_confirm_match(
                match_id=match_id, farmer_id=farmer_id, confirmation=False, notes="Crop not ready"
            )

            # Verify
            assert result["success"] is True
            assert result["status"] == "rejected"
            assert result["reason"] == "Crop not ready"

            # Verify match was updated to rejected
            mock_match_instance.update.assert_called()
            update_data = mock_match_instance.update.call_args[0][1]
            assert update_data["farmer_confirmation_status"] == "rejected"
            assert update_data["status"] == "rejected"

            # Verify booking was cancelled
            mock_booking_instance.update.assert_called()
            booking_update = mock_booking_instance.update.call_args[0][1]
            assert booking_update["status"] == "cancelled"

            # Verify buyer was notified
            mock_notify_buyer.assert_called_once()


class TestCoordinationStatus:
    """Test coordination status tracking"""

    def test_get_coordination_status_single_match(self):
        """Test getting coordination status for single farmer match"""
        service = SupplyRequestMatchingService()

        request_id = 1

        with (
            patch("app.services.supply_request_matching_service.SupplyMatch") as MockMatch,
            patch("app.services.supply_request_matching_service.SupplyRequest") as MockRequest,
            patch("app.services.supply_request_matching_service.AdvanceBooking") as MockBooking,
            patch("app.services.supply_request_matching_service.PaymentMilestone") as MockMilestone,
        ):

            # Setup mocks
            mock_match_instance = MockMatch.return_value
            mock_request_instance = MockRequest.return_value
            mock_booking_instance = MockBooking.return_value
            mock_milestone_instance = MockMilestone.return_value

            # Mock supply request
            mock_request_instance.find.return_value = {
                "id": request_id,
                "status": "in_progress",
                "crop_type": "Wheat",
                "quantity_needed": 1000,
            }

            # Mock matches
            mock_match_instance.where.return_value.where.return_value.get.return_value = [
                {
                    "id": 10,
                    "farmer_id": 200,
                    "listing_id": 50,
                    "matched_quantity": 1000,
                    "farmer_confirmation_status": "confirmed",
                    "delivery_status": "pending",
                    "is_aggregated": False,
                }
            ]

            # Mock booking
            mock_booking_instance.where.return_value.where.return_value.first.return_value = {
                "id": 1001
            }

            # Mock milestones
            mock_milestone_instance.where.return_value.get.return_value = [
                {"status": "paid"},
                {"status": "pending"},
                {"status": "pending"},
            ]

            # Execute
            result = service.get_coordination_status(request_id)

            # Verify
            assert result["request_id"] == request_id
            assert result["request_status"] == "in_progress"
            assert len(result["single_farmer_matches"]) == 1

            match_status = result["single_farmer_matches"][0]
            assert match_status["farmer_id"] == 200
            assert match_status["farmer_confirmation"] == "confirmed"
            assert match_status["delivery_status"] == "pending"
            assert "1/3" in match_status["payment_status"]

    def test_get_coordination_status_aggregated(self):
        """Test getting coordination status for aggregated matches"""
        service = SupplyRequestMatchingService()

        request_id = 1
        group_id = "agg_1_0"

        with (
            patch("app.services.supply_request_matching_service.SupplyMatch") as MockMatch,
            patch("app.services.supply_request_matching_service.SupplyRequest") as MockRequest,
            patch("app.services.supply_request_matching_service.AdvanceBooking") as MockBooking,
            patch("app.services.supply_request_matching_service.PaymentMilestone") as MockMilestone,
        ):

            # Setup mocks
            mock_match_instance = MockMatch.return_value
            mock_request_instance = MockRequest.return_value
            mock_booking_instance = MockBooking.return_value
            mock_milestone_instance = MockMilestone.return_value

            # Mock supply request
            mock_request_instance.find.return_value = {
                "id": request_id,
                "status": "in_progress",
                "crop_type": "Rice",
                "quantity_needed": 5000,
            }

            # Mock aggregated matches
            mock_match_instance.where.return_value.where.return_value.get.return_value = [
                {
                    "id": 11,
                    "farmer_id": 201,
                    "listing_id": 51,
                    "matched_quantity": 2000,
                    "farmer_confirmation_status": "confirmed",
                    "delivery_status": "pending",
                    "is_aggregated": True,
                    "aggregation_group_id": group_id,
                },
                {
                    "id": 12,
                    "farmer_id": 202,
                    "listing_id": 52,
                    "matched_quantity": 1500,
                    "farmer_confirmation_status": "confirmed",
                    "delivery_status": "pending",
                    "is_aggregated": True,
                    "aggregation_group_id": group_id,
                },
                {
                    "id": 13,
                    "farmer_id": 203,
                    "listing_id": 53,
                    "matched_quantity": 1500,
                    "farmer_confirmation_status": "pending",
                    "delivery_status": "pending",
                    "is_aggregated": True,
                    "aggregation_group_id": group_id,
                },
            ]

            # Mock bookings
            mock_booking_instance.where.return_value.where.return_value.first.side_effect = [
                {"id": 1001},
                {"id": 1002},
                {"id": 1003},
            ]

            # Mock milestones
            mock_milestone_instance.where.return_value.get.return_value = []

            # Execute
            result = service.get_coordination_status(request_id)

            # Verify
            assert result["request_id"] == request_id
            assert len(result["aggregated_groups"]) == 1

            group = result["aggregated_groups"][0]
            assert group["group_id"] == group_id
            assert group["total_farmers"] == 3
            assert group["confirmed_farmers"] == 2
            assert group["total_quantity"] == 5000
            assert group["coordination_status"] == "pending_confirmations"


class TestDeliveryTracking:
    """Test delivery status tracking"""

    def test_update_delivery_status(self):
        """Test updating delivery status"""
        service = SupplyRequestMatchingService()

        match_id = 10

        with patch("app.services.supply_request_matching_service.SupplyMatch") as MockMatch:
            # Setup mocks
            mock_match_instance = MockMatch.return_value

            # Mock match
            mock_match_instance.find.return_value = {
                "id": match_id,
                "delivery_status": "pending",
                "delivery_notes": "",
            }

            # Execute
            result = service.update_delivery_status(
                match_id=match_id, delivery_status="in_transit", notes="Truck departed at 10:00 AM"
            )

            # Verify
            assert result["success"] is True
            assert result["delivery_status"] == "in_transit"

            # Verify match was updated
            mock_match_instance.update.assert_called_once()
            update_data = mock_match_instance.update.call_args[0][1]
            assert update_data["delivery_status"] == "in_transit"
            assert "Truck departed" in update_data["delivery_notes"]


class TestPaymentMilestones:
    """Test payment milestone creation"""

    def test_create_payment_milestones(self):
        """Test that payment milestones are created correctly"""
        service = SupplyRequestMatchingService()

        booking_id = 1001
        booking = {
            "id": booking_id,
            "total_amount": 30000,
            "expected_delivery_date": datetime.now() + timedelta(days=30),
        }

        with patch(
            "app.services.supply_request_matching_service.PaymentMilestone"
        ) as MockMilestone:
            # Setup mock
            mock_milestone_instance = MockMilestone.return_value

            # Execute
            service._create_payment_milestones(booking_id, booking)

            # Verify 3 milestones were created
            assert mock_milestone_instance.insert.call_count == 3

            # Verify milestone amounts
            calls = mock_milestone_instance.insert.call_args_list

            # Advance payment (30%)
            advance = calls[0][0][0]
            assert advance["milestone_type"] == "advance_payment"
            assert advance["amount"] == 9000  # 30% of 30000
            assert advance["status"] == "pending"

            # Quality verification (40%)
            quality = calls[1][0][0]
            assert quality["milestone_type"] == "quality_verification"
            assert quality["amount"] == 12000  # 40% of 30000

            # Delivery (30%)
            delivery = calls[2][0][0]
            assert delivery["milestone_type"] == "delivery"
            assert delivery["amount"] == 9000  # 30% of 30000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
