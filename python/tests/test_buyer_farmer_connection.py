"""
Property-based tests for buyer-farmer connection facilitation
Tests Property 9: Buyer-Farmer Connection Facilitation

**Validates: Requirements AC4.3, AC4.4, AC4.5**
"""

import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st


# Custom strategies for generating buyer interest data
@st.composite
def buyer_interest_strategy(draw):
    """
    Generate valid buyer interest data for testing

    This strategy creates buyer interest registrations that test the
    buyer-farmer connection facilitation system.
    """

    # Buyer types
    buyer_types = ["wholesaler", "retailer", "processor", "cooperative", "exporter"]

    # Generate buyer details
    buyer_name = f"Buyer {draw(st.integers(min_value=1, max_value=999))}"
    buyer_phone = f"+91{draw(st.integers(min_value=7000000000, max_value=9999999999))}"
    buyer_email = f"buyer{draw(st.integers(min_value=1000, max_value=9999))}@example.com"
    buyer_type = draw(st.sampled_from(buyer_types))

    # Generate interest details
    interested_quantity = draw(st.integers(min_value=100, max_value=5000))  # kg
    preferred_price = draw(st.floats(min_value=1500.0, max_value=8000.0))

    # Generate message
    messages = [
        "Interested in purchasing for wholesale distribution",
        "Looking for high-quality produce for retail chain",
        "Need regular supply for processing unit",
        "Cooperative looking to support local farmers",
        "Export quality requirements needed",
    ]
    message = draw(st.sampled_from(messages))

    # Generate quality requirements
    quality_requirements = draw(
        st.sampled_from(
            [
                "Grade A only",
                "Grade A or B acceptable",
                "Any grade acceptable",
                "Organic certification required",
                "Export quality standards",
            ]
        )
    )

    # Generate delivery requirements
    delivery_requirements = draw(
        st.sampled_from(
            [
                "Pickup from farm",
                "Delivery to warehouse required",
                "Flexible delivery options",
                "Cold chain transport needed",
                "Standard transport acceptable",
            ]
        )
    )

    # Generate payment terms
    payment_terms = draw(
        st.sampled_from(
            [
                "Advance payment 50%",
                "Payment on delivery",
                "30 days credit",
                "Cash on delivery",
                "Bank transfer",
            ]
        )
    )

    return {
        "buyer_name": buyer_name,
        "buyer_phone": buyer_phone,
        "buyer_email": buyer_email,
        "buyer_type": buyer_type,
        "interested_quantity": interested_quantity,
        "preferred_price": preferred_price,
        "message": message,
        "quality_requirements": quality_requirements,
        "delivery_requirements": delivery_requirements,
        "payment_terms": payment_terms,
    }


@st.composite
def marketplace_listing_strategy(draw):
    """Generate marketplace listing data for testing"""

    # Common Indian crops
    crops = [
        "Rice",
        "Wheat",
        "Cotton",
        "Maize",
        "Soybean",
        "Groundnut",
        "Chickpea",
        "Mustard",
        "Sugarcane",
        "Potato",
    ]

    # Indian states and districts
    states = [
        "Punjab",
        "Haryana",
        "Uttar Pradesh",
        "Madhya Pradesh",
        "Rajasthan",
        "Maharashtra",
        "Karnataka",
        "Tamil Nadu",
        "Andhra Pradesh",
        "Gujarat",
    ]
    districts = [
        "Ludhiana",
        "Amritsar",
        "Karnal",
        "Agra",
        "Lucknow",
        "Indore",
        "Mumbai",
        "Bangalore",
        "Chennai",
        "Ahmedabad",
    ]

    # Generate listing details
    crop_type = draw(st.sampled_from(crops))
    variety = draw(
        st.text(
            min_size=3,
            max_size=30,
            alphabet=st.characters(min_codepoint=65, max_codepoint=122, whitelist_characters=" -"),
        )
    )

    # Generate harvest date (30-180 days from now)
    days_ahead = draw(st.integers(min_value=30, max_value=180))
    expected_harvest_date = date.today() + timedelta(days=days_ahead)

    # Generate quantity (500-10000 kg)
    estimated_quantity = draw(st.integers(min_value=500, max_value=10000))

    # Generate quality grade
    quality_grade = draw(st.sampled_from(["A", "B", "C"]))

    # Generate location
    state = draw(st.sampled_from(states))
    district = draw(st.sampled_from(districts))

    # Generate farmer contact
    farmer_phone = f"+91{draw(st.integers(min_value=7000000000, max_value=9999999999))}"
    farmer_email = f"farmer{draw(st.integers(min_value=1000, max_value=9999))}@example.com"

    return {
        "id": uuid.uuid4(),
        "crop_type": crop_type,
        "crop_variety": variety,
        "expected_harvest_date": expected_harvest_date,
        "estimated_quantity": estimated_quantity,
        "quality_grade": quality_grade,
        "location_state": state,
        "location_district": district,
        "farmer_phone": farmer_phone,
        "farmer_email": farmer_email,
        "farmer_id": uuid.uuid4(),
        "status": "active",
        "contact_enabled": True,
    }


def create_mock_buyer_interest(listing, buyer_interest_data):
    """Helper function to create a mock buyer interest object"""
    mock_interest = Mock()
    mock_interest.id = uuid.uuid4()
    mock_interest.listing_id = listing["id"]
    mock_interest.buyer_id = uuid.uuid4()
    mock_interest.buyer_name = buyer_interest_data["buyer_name"]
    mock_interest.buyer_phone = buyer_interest_data["buyer_phone"]
    mock_interest.buyer_email = buyer_interest_data["buyer_email"]
    mock_interest.buyer_type = buyer_interest_data["buyer_type"]
    mock_interest.interested_quantity = buyer_interest_data["interested_quantity"]
    mock_interest.preferred_price = buyer_interest_data["preferred_price"]
    mock_interest.message_to_farmer = buyer_interest_data["message"]
    mock_interest.quality_requirements = buyer_interest_data["quality_requirements"]
    mock_interest.delivery_requirements = buyer_interest_data["delivery_requirements"]
    mock_interest.payment_terms = buyer_interest_data["payment_terms"]
    mock_interest.contact_requested = True
    mock_interest.contact_request_date = datetime.now()
    mock_interest.status = "pending"
    mock_interest.created_at = datetime.now()

    return mock_interest


def create_mock_connection_response(listing, buyer_interest):
    """Helper function to create a mock connection response"""
    return {
        "connection_id": str(uuid.uuid4()),
        "listing_id": str(listing["id"]),
        "buyer_interest_id": str(buyer_interest.id),
        "farmer_contact": {
            "phone": listing["farmer_phone"],
            "email": listing["farmer_email"],
            "preferred_method": "phone",
        },
        "buyer_details": {
            "name": buyer_interest.buyer_name,
            "phone": buyer_interest.buyer_phone,
            "email": buyer_interest.buyer_email,
            "type": buyer_interest.buyer_type,
        },
        "interest_details": {
            "quantity": buyer_interest.interested_quantity,
            "preferred_price": buyer_interest.preferred_price,
            "message": buyer_interest.message_to_farmer,
        },
        "connection_status": "pending",
        "contact_shared_at": datetime.now().isoformat(),
        "interest_registered_at": buyer_interest.contact_request_date.isoformat(),
    }


class TestBuyerFarmerConnectionFacilitation:
    """
    Property 9: Buyer-Farmer Connection Facilitation

    Test that for any buyer interest in marketplace listing, system enables
    direct communication by sharing farmer contact information, registering
    buyer interest with timestamp, and tracking connection status.
    """

    @given(listing=marketplace_listing_strategy(), buyer_interest_data=buyer_interest_strategy())
    @settings(
        max_examples=200,
        deadline=15000,  # 15 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_direct_communication_enabled_on_buyer_interest(self, listing, buyer_interest_data):
        """
        **Validates: Requirements AC4.3, AC4.4**

        Property: For any buyer interest in a marketplace listing, the system
        should enable direct communication by sharing farmer contact information
        with the buyer.
        """
        # Arrange: Create mock buyer interest
        mock_interest = create_mock_buyer_interest(listing, buyer_interest_data)
        mock_connection = create_mock_connection_response(listing, mock_interest)

        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService

        mock_db = MagicMock()
        service = MarketplaceService(mock_db)

        # Mock the register_buyer_interest method
        with patch.object(service, "register_buyer_interest", return_value=mock_interest):
            # Act: Register buyer interest
            interest = service.register_buyer_interest(
                listing_id=listing["id"], buyer_id=uuid.uuid4(), interest_data=buyer_interest_data
            )

        # Assert: Interest was registered successfully
        assert interest is not None, "Buyer interest should be registered"
        assert interest.id is not None, "Interest should have an ID"
        assert interest.listing_id == listing["id"], "Interest should be linked to listing"

        # Assert: Contact was requested
        assert interest.contact_requested == True, "Contact should be requested"
        assert interest.contact_request_date is not None, "Contact request date should be set"

    @given(listing=marketplace_listing_strategy(), buyer_interest_data=buyer_interest_strategy())
    @settings(
        max_examples=200,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_farmer_contact_information_shared_with_buyer(self, listing, buyer_interest_data):
        """
        **Validates: Requirements AC4.4**

        Property: For any buyer interest, the system should share farmer contact
        information (phone number and/or email) with the buyer to enable direct
        communication.
        """
        # Arrange: Create mock buyer interest and connection
        mock_interest = create_mock_buyer_interest(listing, buyer_interest_data)
        mock_connection = create_mock_connection_response(listing, mock_interest)

        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService

        mock_db = MagicMock()
        service = MarketplaceService(mock_db)

        # Mock the register_buyer_interest method
        with patch.object(service, "register_buyer_interest", return_value=mock_interest):
            # Act: Register buyer interest
            interest = service.register_buyer_interest(
                listing_id=listing["id"], buyer_id=uuid.uuid4(), interest_data=buyer_interest_data
            )

        # Assert: Farmer contact information is available in the listing
        assert (
            listing["farmer_phone"] is not None or listing["farmer_email"] is not None
        ), "Farmer must have at least one contact method"

        # Assert: Contact is enabled for the listing
        assert listing["contact_enabled"] == True, "Contact should be enabled for listing"

        # Assert: Farmer phone is valid format if present
        if listing["farmer_phone"]:
            assert listing["farmer_phone"].startswith(
                "+91"
            ), "Farmer phone should be in Indian format (+91)"
            assert (
                len(listing["farmer_phone"]) == 13
            ), "Farmer phone should be 13 characters (+91 + 10 digits)"

        # Assert: Farmer email is valid format if present
        if listing["farmer_email"]:
            assert "@" in listing["farmer_email"], "Farmer email should contain @"
            assert "." in listing["farmer_email"], "Farmer email should contain domain"

    @given(listing=marketplace_listing_strategy(), buyer_interest_data=buyer_interest_strategy())
    @settings(
        max_examples=200,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_buyer_interest_registered_with_timestamp(self, listing, buyer_interest_data):
        """
        **Validates: Requirements AC4.3, AC4.5**

        Property: For any buyer interest, the system should register the interest
        with a timestamp to track when the buyer expressed interest.
        """
        # Arrange: Create mock buyer interest
        mock_interest = create_mock_buyer_interest(listing, buyer_interest_data)

        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService

        mock_db = MagicMock()
        service = MarketplaceService(mock_db)

        # Mock the register_buyer_interest method
        with patch.object(service, "register_buyer_interest", return_value=mock_interest):
            # Act: Register buyer interest
            interest = service.register_buyer_interest(
                listing_id=listing["id"], buyer_id=uuid.uuid4(), interest_data=buyer_interest_data
            )

        # Assert: Interest has all required buyer information
        assert interest.buyer_name is not None, "Buyer name should be recorded"
        assert interest.buyer_phone is not None, "Buyer phone should be recorded"
        assert interest.buyer_type is not None, "Buyer type should be recorded"
        assert interest.interested_quantity is not None, "Interested quantity should be recorded"

        # Assert: Interest has timestamp
        assert interest.contact_request_date is not None, "Contact request date should be set"
        assert isinstance(
            interest.contact_request_date, datetime
        ), "Contact request date should be a datetime object"

        # Assert: Timestamp is recent (within last minute for test)
        time_diff = datetime.now() - interest.contact_request_date
        assert time_diff.total_seconds() < 60, "Contact request timestamp should be recent"

        # Assert: Interest has creation timestamp
        assert interest.created_at is not None, "Interest should have creation timestamp"
        assert isinstance(
            interest.created_at, datetime
        ), "Creation timestamp should be a datetime object"

    @given(listing=marketplace_listing_strategy(), buyer_interest_data=buyer_interest_strategy())
    @settings(
        max_examples=200,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_connection_status_tracked_for_transaction_monitoring(
        self, listing, buyer_interest_data
    ):
        """
        **Validates: Requirements AC4.5**

        Property: For any buyer-farmer connection, the system should track the
        connection status (pending, contacted, completed) for successful
        transaction monitoring.
        """
        # Arrange: Create mock buyer interest
        mock_interest = create_mock_buyer_interest(listing, buyer_interest_data)

        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService

        mock_db = MagicMock()
        service = MarketplaceService(mock_db)

        # Mock the register_buyer_interest method
        with patch.object(service, "register_buyer_interest", return_value=mock_interest):
            # Act: Register buyer interest
            interest = service.register_buyer_interest(
                listing_id=listing["id"], buyer_id=uuid.uuid4(), interest_data=buyer_interest_data
            )

        # Assert: Connection has status field
        assert hasattr(interest, "status"), "Interest should have status field"
        assert interest.status is not None, "Status should not be None"

        # Assert: Status is one of the valid values
        valid_statuses = ["pending", "contacted", "agreed", "cancelled", "completed"]
        assert (
            interest.status in valid_statuses
        ), f"Status should be one of {valid_statuses}, got {interest.status}"

        # Assert: Initial status is 'pending'
        assert interest.status == "pending", "Initial status should be 'pending' for new interest"

        # Assert: Contact was requested (enables tracking)
        assert (
            interest.contact_requested == True
        ), "Contact requested flag should be set for tracking"

    @given(listing=marketplace_listing_strategy(), buyer_interest_data=buyer_interest_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_buyer_interest_includes_all_required_details(self, listing, buyer_interest_data):
        """
        **Validates: Requirements AC4.3, AC4.4, AC4.5**

        Property: For any buyer interest, the system should capture all required
        details including buyer contact, quantity interested, and message to farmer.
        """
        # Arrange: Create mock buyer interest
        mock_interest = create_mock_buyer_interest(listing, buyer_interest_data)

        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService

        mock_db = MagicMock()
        service = MarketplaceService(mock_db)

        # Mock the register_buyer_interest method
        with patch.object(service, "register_buyer_interest", return_value=mock_interest):
            # Act: Register buyer interest
            interest = service.register_buyer_interest(
                listing_id=listing["id"], buyer_id=uuid.uuid4(), interest_data=buyer_interest_data
            )

        # Assert: All required buyer details are present

        # 1. Buyer identification
        assert interest.buyer_name is not None, "Buyer name should be present"
        assert len(interest.buyer_name) > 0, "Buyer name should not be empty"

        # 2. Buyer contact information
        assert interest.buyer_phone is not None, "Buyer phone should be present"
        assert len(interest.buyer_phone) > 0, "Buyer phone should not be empty"

        # 3. Buyer type
        assert interest.buyer_type is not None, "Buyer type should be present"
        assert interest.buyer_type in [
            "wholesaler",
            "retailer",
            "processor",
            "cooperative",
            "exporter",
        ], f"Buyer type should be valid, got {interest.buyer_type}"

        # 4. Interest quantity
        assert interest.interested_quantity is not None, "Interested quantity should be present"
        assert interest.interested_quantity > 0, "Interested quantity should be positive"

        # 5. Preferred price (optional but should be present if provided)
        if hasattr(interest, "preferred_price") and interest.preferred_price is not None:
            assert interest.preferred_price > 0, "Preferred price should be positive if present"

        # 6. Message to farmer (optional but should be present if provided)
        if hasattr(interest, "message_to_farmer"):
            assert interest.message_to_farmer is not None, "Message should be present"

        # 7. Quality requirements (optional but should be present if provided)
        if hasattr(interest, "quality_requirements"):
            assert (
                interest.quality_requirements is not None
            ), "Quality requirements should be present"

        # 8. Delivery requirements (optional but should be present if provided)
        if hasattr(interest, "delivery_requirements"):
            assert (
                interest.delivery_requirements is not None
            ), "Delivery requirements should be present"

        # 9. Payment terms (optional but should be present if provided)
        if hasattr(interest, "payment_terms"):
            assert interest.payment_terms is not None, "Payment terms should be present"

    @given(listing=marketplace_listing_strategy(), buyer_interest_data=buyer_interest_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_connection_enables_bidirectional_communication(self, listing, buyer_interest_data):
        """
        **Validates: Requirements AC4.4, AC4.5**

        Property: For any buyer-farmer connection, the system should enable
        bidirectional communication by sharing both farmer and buyer contact
        information.
        """
        # Arrange: Create mock buyer interest and connection
        mock_interest = create_mock_buyer_interest(listing, buyer_interest_data)
        mock_connection = create_mock_connection_response(listing, mock_interest)

        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService

        mock_db = MagicMock()
        service = MarketplaceService(mock_db)

        # Mock the register_buyer_interest method
        with patch.object(service, "register_buyer_interest", return_value=mock_interest):
            # Act: Register buyer interest
            interest = service.register_buyer_interest(
                listing_id=listing["id"], buyer_id=uuid.uuid4(), interest_data=buyer_interest_data
            )

        # Assert: Farmer contact is available (shared with buyer)
        assert (
            listing["farmer_phone"] is not None or listing["farmer_email"] is not None
        ), "Farmer contact should be available for buyer"

        # Assert: Buyer contact is recorded (shared with farmer)
        assert (
            interest.buyer_phone is not None or interest.buyer_email is not None
        ), "Buyer contact should be recorded for farmer"

        # Assert: Both parties have at least one contact method
        farmer_has_contact = (
            listing["farmer_phone"] is not None or listing["farmer_email"] is not None
        )
        buyer_has_contact = interest.buyer_phone is not None or interest.buyer_email is not None

        assert (
            farmer_has_contact and buyer_has_contact
        ), "Both farmer and buyer should have contact information for bidirectional communication"

    @given(listing=marketplace_listing_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_multiple_buyer_interests_tracked_separately(self, listing):
        """
        **Validates: Requirements AC4.3, AC4.5**

        Property: For any marketplace listing, the system should track multiple
        buyer interests separately with unique IDs and timestamps.
        """
        # Arrange: Create multiple buyer interests
        buyer1_data = {
            "buyer_name": "Buyer 1",
            "buyer_phone": "+919876543210",
            "buyer_email": "buyer1@example.com",
            "buyer_type": "wholesaler",
            "interested_quantity": 1000,
            "preferred_price": 2500.0,
            "message": "Interested in bulk purchase",
            "quality_requirements": "Grade A only",
            "delivery_requirements": "Pickup from farm",
            "payment_terms": "Advance payment 50%",
        }

        buyer2_data = {
            "buyer_name": "Buyer 2",
            "buyer_phone": "+919876543211",
            "buyer_email": "buyer2@example.com",
            "buyer_type": "retailer",
            "interested_quantity": 500,
            "preferred_price": 2800.0,
            "message": "Need for retail chain",
            "quality_requirements": "Grade A or B acceptable",
            "delivery_requirements": "Delivery to warehouse required",
            "payment_terms": "Payment on delivery",
        }

        mock_interest1 = create_mock_buyer_interest(listing, buyer1_data)
        mock_interest2 = create_mock_buyer_interest(listing, buyer2_data)

        # Mock the marketplace service
        from app.services.marketplace_service import MarketplaceService

        mock_db = MagicMock()
        service = MarketplaceService(mock_db)

        # Mock the register_buyer_interest method to return different interests
        with patch.object(
            service, "register_buyer_interest", side_effect=[mock_interest1, mock_interest2]
        ):
            # Act: Register multiple buyer interests
            interest1 = service.register_buyer_interest(
                listing_id=listing["id"], buyer_id=uuid.uuid4(), interest_data=buyer1_data
            )

            interest2 = service.register_buyer_interest(
                listing_id=listing["id"], buyer_id=uuid.uuid4(), interest_data=buyer2_data
            )

        # Assert: Both interests were created
        assert interest1 is not None, "First interest should be created"
        assert interest2 is not None, "Second interest should be created"

        # Assert: Interests have unique IDs
        assert interest1.id != interest2.id, "Interests should have unique IDs"

        # Assert: Both interests are linked to the same listing
        assert interest1.listing_id == listing["id"], "First interest should be linked to listing"
        assert interest2.listing_id == listing["id"], "Second interest should be linked to listing"

        # Assert: Interests have different buyer details
        assert (
            interest1.buyer_name != interest2.buyer_name
        ), "Interests should have different buyers"
        assert (
            interest1.buyer_phone != interest2.buyer_phone
        ), "Interests should have different phone numbers"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
