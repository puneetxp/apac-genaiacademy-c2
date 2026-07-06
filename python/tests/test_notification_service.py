"""
Tests for Notification Service
Tests all notification triggers and delivery tracking
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

from app.services.notification_service import NotificationService, get_notification_service


class TestNotificationService:
    """Test suite for NotificationService"""
    
    @pytest.fixture
    def notification_service(self):
        """Create notification service instance for testing"""
        with patch('app.services.notification_service.settings') as mock_settings:
            mock_settings.SNS_ENABLED = True
            mock_settings.AWS_REGION = 'ap-south-1'
            mock_settings.AWS_ACCESS_KEY_ID = 'test-key'
            mock_settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
            mock_settings.SNS_TOPIC_ARN_BUYER_INTEREST = 'arn:aws:sns:ap-south-1:123456789:buyer-interest'
            mock_settings.SNS_TOPIC_ARN_STRATEGY_REMINDERS = 'arn:aws:sns:ap-south-1:123456789:strategy-reminders'
            mock_settings.SNS_TOPIC_ARN_WEATHER_ALERTS = 'arn:aws:sns:ap-south-1:123456789:weather-alerts'
            mock_settings.SNS_TOPIC_ARN_HARVEST_REMINDERS = 'arn:aws:sns:ap-south-1:123456789:harvest-reminders'
            
            with patch('boto3.client') as mock_boto_client:
                mock_sns = MagicMock()
                mock_boto_client.return_value = mock_sns
                
                service = NotificationService()
                service.sns_client = mock_sns
                
                yield service
    
    @pytest.fixture
    def mock_sns_success_response(self):
        """Mock successful SNS response"""
        return {
            'MessageId': 'test-message-id-12345',
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            }
        }
    
    def test_send_buyer_interest_notification_success(self, notification_service, mock_sns_success_response):
        """Test successful buyer interest notification"""
        # Setup
        notification_service.sns_client.publish.return_value = mock_sns_success_response
        
        # Execute
        result = notification_service.send_buyer_interest_notification(
            farmer_phone='+919876543210',
            farmer_email='farmer@example.com',
            buyer_name='Raj Traders',
            crop_type='Wheat',
            quantity_interested=50.0,
            listing_id='listing-123',
            buyer_contact='+919123456789'
        )
        
        # Verify
        assert result['success'] is True
        assert result['message_id'] == 'test-message-id-12345'
        assert result['notification_type'] == 'buyer_interest'
        assert notification_service.sns_client.publish.called
        
        # Verify SNS publish call
        call_args = notification_service.sns_client.publish.call_args
        assert 'TopicArn' in call_args[1]
        assert 'Subject' in call_args[1]
        assert 'Wheat' in call_args[1]['Subject']
        assert 'Message' in call_args[1]
        assert 'Raj Traders' in call_args[1]['Message']
    
    def test_send_buyer_interest_notification_formats_message_correctly(self, notification_service, mock_sns_success_response):
        """Test buyer interest notification message formatting"""
        # Setup
        notification_service.sns_client.publish.return_value = mock_sns_success_response
        
        # Execute
        result = notification_service.send_buyer_interest_notification(
            farmer_phone='+919876543210',
            farmer_email='farmer@example.com',
            buyer_name='Raj Traders',
            crop_type='Cotton',
            quantity_interested=100.0,
            listing_id='listing-456',
            buyer_contact='+919123456789'
        )
        
        # Verify message content
        call_args = notification_service.sns_client.publish.call_args
        message = call_args[1]['Message']
        
        assert 'Raj Traders' in message
        assert 'Cotton' in message
        assert '100.00 quintals' in message
        assert '+919123456789' in message
        assert 'CropSense AI' in message
    
    def test_send_strategy_reminder_success(self, notification_service, mock_sns_success_response):
        """Test successful strategy reminder notification"""
        # Setup
        notification_service.sns_client.publish.return_value = mock_sns_success_response
        
        action_items = [
            'Apply first dose of fertilizer',
            'Check irrigation system',
            'Monitor for pests'
        ]
        
        # Execute
        result = notification_service.send_strategy_reminder(
            farmer_phone='+919876543210',
            farmer_email='farmer@example.com',
            farmer_name='Ramesh Kumar',
            strategy_id='strategy-789',
            reminder_type='fertilizer_application',
            action_items=action_items,
            due_date=datetime.now() + timedelta(days=7)
        )
        
        # Verify
        assert result['success'] is True
        assert result['message_id'] == 'test-message-id-12345'
        assert result['notification_type'] == 'strategy_reminder'
        
        # Verify message content
        call_args = notification_service.sns_client.publish.call_args
        message = call_args[1]['Message']
        
        assert 'Ramesh Kumar' in message
        assert 'fertilizer' in message.lower()
        assert 'Apply first dose of fertilizer' in message
        assert 'Check irrigation system' in message
        assert 'Monitor for pests' in message
    
    def test_send_weather_alert_success(self, notification_service, mock_sns_success_response):
        """Test successful weather alert notification"""
        # Setup
        notification_service.sns_client.publish.return_value = mock_sns_success_response
        
        # Execute
        result = notification_service.send_weather_alert(
            farmer_phone='+919876543210',
            farmer_email='farmer@example.com',
            alert_type='heavy_rainfall',
            severity='high',
            message='Heavy rainfall expected in next 24 hours',
            recommendation='Ensure proper drainage, protect crops from waterlogging',
            valid_until=datetime.now() + timedelta(hours=24),
            affected_crops=['Rice', 'Cotton']
        )
        
        # Verify
        assert result['success'] is True
        assert result['message_id'] == 'test-message-id-12345'
        assert result['notification_type'] == 'weather_alert'
        
        # Verify message content
        call_args = notification_service.sns_client.publish.call_args
        message = call_args[1]['Message']
        subject = call_args[1]['Subject']
        
        assert '⚠️' in subject
        assert 'HIGH' in subject
        assert 'Heavy rainfall' in message
        assert 'drainage' in message
        assert 'Rice' in message
        assert 'Cotton' in message
    
    def test_send_harvest_reminder_success(self, notification_service, mock_sns_success_response):
        """Test successful harvest reminder notification"""
        # Setup
        notification_service.sns_client.publish.return_value = mock_sns_success_response
        
        harvest_date = datetime.now() + timedelta(days=7)
        preparation_tasks = [
            'Arrange harvesting labor',
            'Prepare storage facilities',
            'Contact buyers'
        ]
        
        # Execute
        result = notification_service.send_harvest_reminder(
            farmer_phone='+919876543210',
            farmer_email='farmer@example.com',
            farmer_name='Suresh Patel',
            crop_type='Wheat',
            expected_harvest_date=harvest_date,
            estimated_yield=150.0,
            preparation_tasks=preparation_tasks
        )
        
        # Verify
        assert result['success'] is True
        assert result['message_id'] == 'test-message-id-12345'
        assert result['notification_type'] == 'harvest_reminder'
        
        # Verify message content
        call_args = notification_service.sns_client.publish.call_args
        message = call_args[1]['Message']
        
        assert 'Suresh Patel' in message
        assert 'Wheat' in message
        assert '150.00 quintals' in message
        assert 'days' in message  # Check for days mention (could be 6 or 7 depending on timing)
        assert 'Arrange harvesting labor' in message
        assert 'Prepare storage facilities' in message
    
    def test_notification_retry_on_throttling(self, notification_service):
        """Test notification retry logic on throttling error"""
        # Setup - First call fails with throttling, second succeeds
        error_response = {
            'Error': {
                'Code': 'Throttling',
                'Message': 'Rate exceeded'
            }
        }
        
        notification_service.sns_client.publish.side_effect = [
            ClientError(error_response, 'Publish'),
            {'MessageId': 'test-message-id-retry'}
        ]
        
        # Execute
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = notification_service.send_buyer_interest_notification(
                farmer_phone='+919876543210',
                farmer_email='farmer@example.com',
                buyer_name='Test Buyer',
                crop_type='Rice',
                quantity_interested=25.0,
                listing_id='listing-retry'
            )
        
        # Verify - Should succeed after retry
        assert result['success'] is True
        assert result['attempts'] == 2
        assert notification_service.sns_client.publish.call_count == 2
    
    def test_notification_fails_after_max_retries(self, notification_service):
        """Test notification fails after maximum retries"""
        # Setup - All calls fail
        error_response = {
            'Error': {
                'Code': 'ServiceUnavailable',
                'Message': 'Service temporarily unavailable'
            }
        }
        
        notification_service.sns_client.publish.side_effect = ClientError(error_response, 'Publish')
        
        # Execute
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = notification_service.send_buyer_interest_notification(
                farmer_phone='+919876543210',
                farmer_email='farmer@example.com',
                buyer_name='Test Buyer',
                crop_type='Rice',
                quantity_interested=25.0,
                listing_id='listing-fail'
            )
        
        # Verify - Should fail after 3 attempts
        assert result['success'] is False
        assert result['attempts'] == 3
        assert 'ServiceUnavailable' in result['error']
        assert notification_service.sns_client.publish.call_count == 3
        
        # Verify added to retry queue
        assert len(notification_service.retry_queue) == 1
        assert notification_service.retry_queue[0]['notification_type'] == 'buyer_interest'
    
    def test_notification_tracking_in_history(self, notification_service, mock_sns_success_response):
        """Test notification tracking in history"""
        # Setup
        notification_service.sns_client.publish.return_value = mock_sns_success_response
        
        # Execute - Send multiple notifications
        notification_service.send_buyer_interest_notification(
            farmer_phone='+919876543210',
            farmer_email='farmer@example.com',
            buyer_name='Buyer 1',
            crop_type='Wheat',
            quantity_interested=50.0,
            listing_id='listing-1'
        )
        
        notification_service.send_weather_alert(
            farmer_phone='+919876543210',
            farmer_email='farmer@example.com',
            alert_type='storm',
            severity='high',
            message='Storm warning'
        )
        
        # Verify history
        history = notification_service.get_notification_history()
        assert len(history) == 2
        assert history[0]['notification_type'] == 'buyer_interest'
        assert history[1]['notification_type'] == 'weather_alert'
        
        # Verify filtered history
        buyer_history = notification_service.get_notification_history(notification_type='buyer_interest')
        assert len(buyer_history) == 1
        assert buyer_history[0]['notification_type'] == 'buyer_interest'
    
    def test_sns_disabled_logs_warning(self, caplog):
        """Test that disabled SNS logs warning instead of sending"""
        # Setup
        with patch('app.services.notification_service.settings') as mock_settings:
            mock_settings.SNS_ENABLED = False
            
            service = NotificationService()
            
            # Execute
            result = service.send_buyer_interest_notification(
                farmer_phone='+919876543210',
                farmer_email='farmer@example.com',
                buyer_name='Test Buyer',
                crop_type='Rice',
                quantity_interested=25.0,
                listing_id='listing-disabled'
            )
            
            # Verify
            assert result['success'] is False
            assert result['error'] == 'SNS disabled'
            assert 'SNS disabled' in caplog.text
    
    def test_missing_topic_arn_logs_warning(self, notification_service, caplog):
        """Test that missing topic ARN logs warning"""
        # Setup - Clear topic ARN
        notification_service.topic_buyer_interest = None
        
        # Execute
        result = notification_service.send_buyer_interest_notification(
            farmer_phone='+919876543210',
            farmer_email='farmer@example.com',
            buyer_name='Test Buyer',
            crop_type='Rice',
            quantity_interested=25.0,
            listing_id='listing-no-topic'
        )
        
        # Verify
        assert result['success'] is False
        assert result['error'] == 'Topic ARN not configured'
        assert 'Topic ARN not configured' in caplog.text
    
    def test_retry_failed_notifications_success(self, notification_service, mock_sns_success_response):
        """Test retrying failed notifications from queue"""
        # Setup - Add failed notification to retry queue
        failed_notification = {
            'notification_type': 'buyer_interest',
            'subject': 'Test Subject',
            'message': 'Test Message',
            'phone_number': '+919876543210',
            'email': 'test@example.com',
            'metadata': {'listing_id': 'test-123'},
            'attempts': 3
        }
        notification_service.retry_queue.append(failed_notification)
        
        notification_service.sns_client.publish.return_value = mock_sns_success_response
        
        # Execute
        result = notification_service.retry_failed_notifications()
        
        # Verify
        assert result['total'] == 1
        assert result['retried'] == 1
        assert result['success'] == 1
        assert result['failed'] == 0
        assert len(notification_service.retry_queue) == 0
    
    def test_get_singleton_instance(self):
        """Test getting singleton notification service instance"""
        service1 = get_notification_service()
        service2 = get_notification_service()
        
        assert service1 is service2
    
    def test_message_attributes_include_metadata(self, notification_service, mock_sns_success_response):
        """Test that SNS message attributes include notification metadata"""
        # Setup
        notification_service.sns_client.publish.return_value = mock_sns_success_response
        
        # Execute
        notification_service.send_buyer_interest_notification(
            farmer_phone='+919876543210',
            farmer_email='farmer@example.com',
            buyer_name='Test Buyer',
            crop_type='Rice',
            quantity_interested=25.0,
            listing_id='listing-attrs'
        )
        
        # Verify message attributes
        call_args = notification_service.sns_client.publish.call_args
        message_attrs = call_args[1]['MessageAttributes']
        
        assert 'notification_type' in message_attrs
        assert message_attrs['notification_type']['StringValue'] == 'buyer_interest'
        assert 'phone_number' in message_attrs
        assert message_attrs['phone_number']['StringValue'] == '+919876543210'
        assert 'email' in message_attrs
        assert message_attrs['email']['StringValue'] == 'farmer@example.com'


class TestNotificationMessageFormatting:
    """Test notification message formatting"""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing"""
        with patch('app.services.notification_service.settings') as mock_settings:
            mock_settings.SNS_ENABLED = False
            return NotificationService()
    
    def test_buyer_interest_message_format(self, service):
        """Test buyer interest message formatting"""
        message = service._format_buyer_interest_message(
            buyer_name='Raj Traders',
            crop_type='Wheat',
            quantity_interested=50.0,
            buyer_contact='+919123456789'
        )
        
        assert 'Raj Traders' in message
        assert 'Wheat' in message
        assert '50.00 quintals' in message
        assert '+919123456789' in message
        assert 'CropSense AI' in message
    
    def test_strategy_reminder_message_format(self, service):
        """Test strategy reminder message formatting"""
        action_items = ['Task 1', 'Task 2', 'Task 3']
        due_date = datetime(2024, 3, 15)
        
        message = service._format_strategy_reminder_message(
            farmer_name='Ramesh Kumar',
            reminder_type='planting',
            action_items=action_items,
            due_date=due_date
        )
        
        assert 'Ramesh Kumar' in message
        assert 'Planting' in message
        assert 'Task 1' in message
        assert 'Task 2' in message
        assert 'Task 3' in message
        assert 'March 15, 2024' in message
    
    def test_weather_alert_message_format(self, service):
        """Test weather alert message formatting"""
        valid_until = datetime(2024, 3, 15, 18, 0)
        
        message = service._format_weather_alert_message(
            alert_type='heavy_rainfall',
            severity='high',
            message='Heavy rain expected',
            recommendation='Ensure drainage',
            valid_until=valid_until,
            affected_crops=['Rice', 'Cotton']
        )
        
        assert '⚠️' in message
        assert 'Heavy Rainfall' in message
        assert 'HIGH' in message
        assert 'Heavy rain expected' in message
        assert 'Ensure drainage' in message
        assert 'Rice' in message
        assert 'Cotton' in message
        assert 'March 15, 2024' in message
    
    def test_harvest_reminder_message_format(self, service):
        """Test harvest reminder message formatting"""
        harvest_date = datetime.now() + timedelta(days=7)
        preparation_tasks = ['Task A', 'Task B']
        
        message = service._format_harvest_reminder_message(
            farmer_name='Suresh Patel',
            crop_type='Wheat',
            expected_harvest_date=harvest_date,
            estimated_yield=150.0,
            preparation_tasks=preparation_tasks
        )
        
        assert 'Suresh Patel' in message
        assert 'Wheat' in message
        assert '150.00 quintals' in message
        assert 'days' in message  # Check for days mention (could be 6 or 7 depending on timing)
        assert 'Task A' in message
        assert 'Task B' in message
        assert 'labor' in message.lower()
        assert 'storage' in message.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
