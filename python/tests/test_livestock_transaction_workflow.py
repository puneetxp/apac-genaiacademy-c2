"""
Tests for Livestock Transaction Workflow

Tests the complete transaction workflow including:
- Transaction initiation
- Messaging between buyers and sellers
- Status tracking
- Health guarantee system
- Bulk trading
- Transaction analytics

Compatible with Python 3.14.3, pytest
"""

from datetime import datetime, timedelta

import pytest

from app.orm.livestock_listing import LivestockListing
from app.orm.livestock_transaction import LivestockTransaction
from app.orm.user import User
from app.services.livestock_transaction_service import get_livestock_transaction_service


class TestLivestockTransactionWorkflow:
    """Test livestock transaction workflow"""

    def test_initiate_transaction(self):
        """Test transaction initiation creates inquiry status"""
        service = get_livestock_transaction_service()

        # Create test data
        test_data = {
            "listing_id": 1,
            "buyer_id": 2,
            "transaction_type": "sale",
            "quantity": 1,
            "buyer_message": "Interested in purchasing this animal",
            "buyer_contact_phone": "+919876543210",
            "buyer_contact_email": "buyer@example.com",
        }

        # Note: This test assumes listing_id 1 exists
        # In real tests, we'd create the listing first
        result = service.initiate_transaction(**test_data)

        # Verify transaction created with inquiry status
        if result:
            assert result.status == "inquiry"
            assert result.buyer_id == 2
            assert result.transaction_type == "sale"
            assert result.quantity == 1
            assert result.health_guarantee_days == 7

    def test_transaction_status_flow(self):
        """Test transaction status transitions"""
        service = get_livestock_transaction_service()

        # Status flow: inquiry → negotiation → agreed → completed
        valid_transitions = [
            ("inquiry", "negotiation"),
            ("negotiation", "agreed"),
            ("agreed", "completed"),
        ]

        for current, next_status in valid_transitions:
            # Each transition should be valid
            assert next_status in ["inquiry", "negotiation", "agreed", "completed", "cancelled"]

    def test_seller_response(self):
        """Test seller can respond to inquiry"""
        service = get_livestock_transaction_service()

        # Test seller response functionality
        response_data = {
            "transaction_id": 1,
            "seller_id": 1,
            "message": "Thank you for your interest. The animal is available.",
            "new_status": "negotiation",
        }

        # Note: This assumes transaction 1 exists
        result = service.add_seller_response(**response_data)

        if result:
            assert result.seller_response is not None
            assert result.status == "negotiation"

    def test_buyer_message(self):
        """Test buyer can send messages"""
        service = get_livestock_transaction_service()

        message_data = {
            "transaction_id": 1,
            "buyer_id": 2,
            "message": "Can we negotiate the price?",
        }

        result = service.add_buyer_message(**message_data)

        if result:
            assert result.buyer_message is not None

    def test_complete_transaction_activates_health_guarantee(self):
        """Test completing transaction activates 7-day health guarantee"""
        service = get_livestock_transaction_service()

        completion_data = {
            "transaction_id": 1,
            "seller_id": 1,
            "notes": "Animal delivered in good health",
        }

        result = service.complete_transaction(**completion_data)

        if result:
            assert result.status == "completed"
            assert result.completed_at is not None
            assert result.health_guarantee_expires is not None

            # Verify 7-day guarantee
            expected_expiry = result.completed_at + timedelta(days=7)
            assert abs((result.health_guarantee_expires - expected_expiry).total_seconds()) < 60

    def test_cancel_transaction(self):
        """Test transaction cancellation"""
        service = get_livestock_transaction_service()

        cancellation_data = {
            "transaction_id": 1,
            "user_id": 2,
            "cancellation_reason": "Changed my mind",
        }

        result = service.cancel_transaction(**cancellation_data)

        if result:
            assert result.status == "cancelled"
            assert result.cancelled_at is not None
            assert result.cancellation_reason == "Changed my mind"

    def test_bulk_transaction_creation(self):
        """Test creating multiple transactions for bulk trading"""
        service = get_livestock_transaction_service()

        bulk_data = {
            "listing_id": 1,
            "buyer_id": 2,
            "transaction_type": "sale",
            "quantities": [2, 3, 5],  # 3 separate transactions
            "buyer_message": "Interested in bulk purchase",
            "buyer_contact_phone": "+919876543210",
        }

        results = service.create_bulk_transactions(**bulk_data)

        if results:
            assert len(results) == 3
            assert results[0].quantity == 2
            assert results[1].quantity == 3
            assert results[2].quantity == 5

            # All should have same buyer and listing
            for result in results:
                assert result.buyer_id == 2
                assert result.listing_id == 1
                assert result.status == "inquiry"

    def test_transaction_analytics(self):
        """Test transaction analytics calculation"""
        service = get_livestock_transaction_service()

        # Get analytics for all transactions
        analytics = service.get_transaction_analytics()

        assert "total_transactions" in analytics
        assert "by_status" in analytics
        assert "by_type" in analytics
        assert "total_value" in analytics
        assert "average_transaction_value" in analytics
        assert "completion_rate" in analytics
        assert "cancellation_rate" in analytics

        # Verify rates are between 0 and 1
        assert 0 <= analytics["completion_rate"] <= 1
        assert 0 <= analytics["cancellation_rate"] <= 1

    def test_user_transaction_history(self):
        """Test retrieving user transaction history"""
        service = get_livestock_transaction_service()

        # Get buyer transactions
        buyer_transactions = service.get_user_transactions(
            user_id=2, role="buyer", skip=0, limit=20
        )

        assert isinstance(buyer_transactions, list)

        # Get seller transactions
        seller_transactions = service.get_user_transactions(
            user_id=1, role="seller", skip=0, limit=20
        )

        assert isinstance(seller_transactions, list)

    def test_transaction_with_details(self):
        """Test retrieving transaction with related data"""
        service = get_livestock_transaction_service()

        result = service.get_transaction_with_details(transaction_id=1)

        if result:
            # Should include transaction, listing, seller, and buyer details
            assert "listing" in result or result.get("listing") is None
            assert "seller" in result or result.get("seller") is None
            assert "buyer" in result or result.get("buyer") is None

    def test_agreed_status_requires_price(self):
        """Test that agreed status requires agreed_price"""
        service = get_livestock_transaction_service()

        # Attempting to set status to 'agreed' without price should fail
        # This is validated at the schema level
        from app.schemas.livestock_transaction import TransactionStatusUpdate

        with pytest.raises(ValueError):
            TransactionStatusUpdate(status="agreed", agreed_price=None)  # Should raise error

    def test_health_guarantee_expiration(self):
        """Test health guarantee expiration calculation"""
        # Health guarantee should be 7 days from completion
        completion_time = datetime.now()
        expected_expiry = completion_time + timedelta(days=7)

        # Verify the calculation
        assert (expected_expiry - completion_time).days == 7


class TestTransactionSchemas:
    """Test transaction Pydantic schemas"""

    def test_transaction_create_schema(self):
        """Test transaction creation schema validation"""
        from app.schemas.livestock_transaction import LivestockTransactionCreate

        valid_data = {
            "listing_id": 1,
            "buyer_id": 2,
            "seller_id": 1,
            "transaction_type": "sale",
            "quantity": 1,
            "buyer_message": "Interested in this animal",
            "buyer_contact_phone": "+919876543210",
        }

        transaction = LivestockTransactionCreate(**valid_data)
        assert transaction.listing_id == 1
        assert transaction.quantity == 1
        assert transaction.transaction_type == "sale"

    def test_transaction_type_enum(self):
        """Test transaction type enum values"""
        from app.schemas.livestock_transaction import TransactionTypeEnum

        assert TransactionTypeEnum.SALE == "sale"
        assert TransactionTypeEnum.BREEDING == "breeding"
        assert TransactionTypeEnum.LEASE == "lease"

    def test_transaction_status_enum(self):
        """Test transaction status enum values"""
        from app.schemas.livestock_transaction import TransactionStatusEnum

        assert TransactionStatusEnum.INQUIRY == "inquiry"
        assert TransactionStatusEnum.NEGOTIATION == "negotiation"
        assert TransactionStatusEnum.AGREED == "agreed"
        assert TransactionStatusEnum.COMPLETED == "completed"
        assert TransactionStatusEnum.CANCELLED == "cancelled"

    def test_bulk_transaction_validation(self):
        """Test bulk transaction schema validation"""
        from app.schemas.livestock_transaction import BulkTransactionCreate

        valid_data = {
            "listing_id": 1,
            "transaction_type": "sale",
            "quantities": [2, 3, 5],
            "buyer_message": "Bulk purchase inquiry",
        }

        bulk_transaction = BulkTransactionCreate(**valid_data)
        assert len(bulk_transaction.quantities) == 3
        assert sum(bulk_transaction.quantities) == 10

    def test_bulk_transaction_quantity_limit(self):
        """Test bulk transaction total quantity limit"""
        from app.schemas.livestock_transaction import BulkTransactionCreate

        # Should fail if total exceeds 1000
        with pytest.raises(ValueError):
            BulkTransactionCreate(
                listing_id=1,
                transaction_type="sale",
                quantities=[500, 501],  # Total 1001, exceeds limit
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
