"""
Tests for booking notification functionality
"""

import pytest
from datetime import datetime, timedelta, date
from unittest.mock import Mock, patch

from app.services.notification_service import NotificationService
from app.services.booking_reminder_service import BookingReminderService


class TestBookingNotifications:
    """Test booking notification methods"""
    
    def test_send_booking_created_notification_buyer(self):
        """Test booking created notification for buyer"""
        service = NotificationService()
        
        result = service.send_booking_created_notification(
            recipient_phone="+919876543210",
            recipient_email="buyer@example.com",
            recipient_name="John Buyer",
            recipient_role="buyer",
            booking_id=123,
            crop_type="Wheat",
            quantity=100.0,
            total_amount=50000.0,
            expected_delivery_date=datetime.now() + timedelta(days=90),
            other_party_name="Farmer Ram"
        )
        
        # Should return result (success depends on SNS configuration)
        assert 'notification_type' in result
        assert result['notification_type'] == 'booking_created'
    
    def test_send_payment_reminder_notification(self):
        """Test payment reminder notification"""
        service = NotificationService()
        
        result = service.send_payment_reminder_notification(
            recipient_phone="+919876543210",
            recipient_email="buyer@example.com",
            recipient_name="John Buyer",
            booking_id=123,
            milestone_type="quality_check",
            amount=10000.0,
            due_date=datetime.now() + timedelta(days=7),
            crop_type="Wheat",
            days_until_due=7
        )
        
        assert 'notification_type' in result
        assert result['notification_type'] == 'payment_reminder'

    def test_send_payment_overdue_notification(self):
        """Test payment overdue notification"""
        service = NotificationService()
        
        result = service.send_payment_overdue_notification(
            recipient_phone="+919876543210",
            recipient_email="buyer@example.com",
            recipient_name="John Buyer",
            booking_id=123,
            milestone_type="advance",
            amount=10000.0,
            due_date=datetime.now() - timedelta(days=3),
            crop_type="Wheat",
            days_overdue=3
        )
        
        assert 'notification_type' in result
        assert result['notification_type'] == 'payment_overdue'
    
    def test_send_quality_verification_reminder(self):
        """Test quality verification reminder"""
        service = NotificationService()
        
        result = service.send_quality_verification_reminder(
            recipient_phone="+919876543210",
            recipient_email="farmer@example.com",
            recipient_name="Farmer Ram",
            booking_id=123,
            crop_type="Wheat",
            expected_delivery_date=datetime.now() + timedelta(days=3),
            days_until_delivery=3
        )
        
        assert 'notification_type' in result
        assert result['notification_type'] == 'quality_verification_reminder'
    
    def test_send_booking_status_update_notification(self):
        """Test booking status update notification"""
        service = NotificationService()
        
        result = service.send_booking_status_update_notification(
            recipient_phone="+919876543210",
            recipient_email="buyer@example.com",
            recipient_name="John Buyer",
            recipient_role="buyer",
            booking_id=123,
            crop_type="Wheat",
            old_status="pending",
            new_status="confirmed",
            notes="Booking confirmed by farmer"
        )
        
        assert 'notification_type' in result
        assert result['notification_type'] == 'booking_status_update'
    
    def test_notification_history_tracking(self):
        """Test that notifications are tracked in history"""
        service = NotificationService()
        
        initial_count = len(service.notification_history)
        
        service.send_booking_created_notification(
            recipient_phone="+919876543210",
            recipient_email="buyer@example.com",
            recipient_name="John Buyer",
            recipient_role="buyer",
            booking_id=123,
            crop_type="Wheat",
            quantity=100.0,
            total_amount=50000.0,
            expected_delivery_date=datetime.now() + timedelta(days=90),
            other_party_name="Farmer Ram"
        )
        
        # History should have one more entry
        assert len(service.notification_history) == initial_count + 1
        
        # Latest entry should be booking_created
        latest = service.notification_history[-1]
        assert latest['notification_type'] == 'booking_created'
        assert 'timestamp' in latest
        assert 'metadata' in latest
