"""
Tests for CloudWatch Alerting Service
Task 20.4: Configure alerting

Tests cover:
- SNS topic creation and subscription
- CloudWatch alarm creation
- Alarm configuration validation
- Error handling

Validates: Requirements (Non-Functional - Reliability)
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.alerting import AlarmSeverity, AlertingService


@pytest.fixture
def mock_boto_clients():
    """Mock boto3 clients"""
    with patch("boto3.client") as mock_client:
        mock_cloudwatch = Mock()
        mock_sns = Mock()

        def client_factory(service_name, **kwargs):
            if service_name == "cloudwatch":
                return mock_cloudwatch
            elif service_name == "sns":
                return mock_sns
            return Mock()

        mock_client.side_effect = client_factory

        yield {"cloudwatch": mock_cloudwatch, "sns": mock_sns}


@pytest.fixture
def alerting_service(mock_boto_clients):
    """Create alerting service with mocked clients"""
    service = AlertingService(region="ap-south-1", namespace="TestNamespace", enabled=True)
    return service


class TestAlertingServiceInitialization:
    """Test alerting service initialization"""

    def test_initialization_success(self, mock_boto_clients):
        """Test successful initialization"""
        service = AlertingService(region="us-east-1", namespace="TestApp", enabled=True)

        assert service.region == "us-east-1"
        assert service.namespace == "TestApp"
        assert service.enabled is True

    def test_initialization_disabled(self):
        """Test initialization with alerting disabled"""
        service = AlertingService(enabled=False)

        assert service.enabled is False

    def test_initialization_failure(self):
        """Test initialization with boto3 failure"""
        with patch("boto3.client", side_effect=Exception("AWS error")):
            service = AlertingService(enabled=True)

            # Should disable alerting on failure
            assert service.enabled is False


class TestSNSTopicManagement:
    """Test SNS topic creation and subscription"""

    def test_create_sns_topic_success(self, alerting_service, mock_boto_clients):
        """Test successful SNS topic creation"""
        mock_boto_clients["sns"].create_topic.return_value = {
            "TopicArn": "arn:aws:sns:ap-south-1:123456789012:test-topic"
        }

        topic_arn = alerting_service.create_sns_topic(
            topic_name="test-topic", display_name="Test Topic"
        )

        assert topic_arn == "arn:aws:sns:ap-south-1:123456789012:test-topic"
        mock_boto_clients["sns"].create_topic.assert_called_once()

    def test_create_sns_topic_already_exists(self, alerting_service, mock_boto_clients):
        """Test SNS topic creation when topic already exists"""
        error_response = {"Error": {"Code": "TopicAlreadyExists"}}
        mock_boto_clients["sns"].create_topic.side_effect = [
            ClientError(error_response, "CreateTopic"),
            {"TopicArn": "arn:aws:sns:ap-south-1:123456789012:existing-topic"},
        ]

        topic_arn = alerting_service.create_sns_topic(
            topic_name="existing-topic", display_name="Existing Topic"
        )

        assert topic_arn == "arn:aws:sns:ap-south-1:123456789012:existing-topic"

    def test_create_sns_topic_failure(self, alerting_service, mock_boto_clients):
        """Test SNS topic creation failure"""
        error_response = {"Error": {"Code": "AccessDenied"}}
        mock_boto_clients["sns"].create_topic.side_effect = ClientError(
            error_response, "CreateTopic"
        )

        topic_arn = alerting_service.create_sns_topic(
            topic_name="test-topic", display_name="Test Topic"
        )

        assert topic_arn is None

    def test_subscribe_email_success(self, alerting_service, mock_boto_clients):
        """Test successful email subscription"""
        topic_arn = "arn:aws:sns:ap-south-1:123456789012:test-topic"
        email = "test@example.com"

        result = alerting_service.subscribe_email(topic_arn, email)

        assert result is True
        mock_boto_clients["sns"].subscribe.assert_called_once_with(
            TopicArn=topic_arn, Protocol="email", Endpoint=email
        )

    def test_subscribe_sms_success(self, alerting_service, mock_boto_clients):
        """Test successful SMS subscription"""
        topic_arn = "arn:aws:sns:ap-south-1:123456789012:test-topic"
        phone = "+919876543210"

        result = alerting_service.subscribe_sms(topic_arn, phone)

        assert result is True
        mock_boto_clients["sns"].subscribe.assert_called_once_with(
            TopicArn=topic_arn, Protocol="sms", Endpoint=phone
        )

    def test_subscribe_email_failure(self, alerting_service, mock_boto_clients):
        """Test email subscription failure"""
        error_response = {"Error": {"Code": "InvalidParameter"}}
        mock_boto_clients["sns"].subscribe.side_effect = ClientError(error_response, "Subscribe")

        result = alerting_service.subscribe_email(
            "arn:aws:sns:ap-south-1:123456789012:test-topic", "invalid-email"
        )

        assert result is False


class TestAlarmCreation:
    """Test CloudWatch alarm creation"""

    def test_create_alarm_success(self, alerting_service, mock_boto_clients):
        """Test successful alarm creation"""
        result = alerting_service.create_alarm(
            alarm_name="test-alarm",
            alarm_description="Test alarm",
            metric_name="TestMetric",
            comparison_operator="GreaterThanThreshold",
            threshold=100.0,
            evaluation_periods=2,
            period=300,
            statistic="Average",
            sns_topic_arn="arn:aws:sns:ap-south-1:123456789012:test-topic",
        )

        assert result is True
        mock_boto_clients["cloudwatch"].put_metric_alarm.assert_called_once()

    def test_create_alarm_with_dimensions(self, alerting_service, mock_boto_clients):
        """Test alarm creation with dimensions"""
        dimensions = [
            {"Name": "Endpoint", "Value": "/api/users"},
            {"Name": "Method", "Value": "GET"},
        ]

        result = alerting_service.create_alarm(
            alarm_name="test-alarm",
            alarm_description="Test alarm",
            metric_name="APIRequests",
            comparison_operator="GreaterThanThreshold",
            threshold=1000.0,
            evaluation_periods=1,
            period=300,
            statistic="Sum",
            sns_topic_arn="arn:aws:sns:ap-south-1:123456789012:test-topic",
            dimensions=dimensions,
        )

        assert result is True
        call_args = mock_boto_clients["cloudwatch"].put_metric_alarm.call_args
        assert call_args[1]["Dimensions"] == dimensions

    def test_create_alarm_failure(self, alerting_service, mock_boto_clients):
        """Test alarm creation failure"""
        error_response = {"Error": {"Code": "LimitExceeded"}}
        mock_boto_clients["cloudwatch"].put_metric_alarm.side_effect = ClientError(
            error_response, "PutMetricAlarm"
        )

        result = alerting_service.create_alarm(
            alarm_name="test-alarm",
            alarm_description="Test alarm",
            metric_name="TestMetric",
            comparison_operator="GreaterThanThreshold",
            threshold=100.0,
            evaluation_periods=2,
            period=300,
            statistic="Average",
            sns_topic_arn="arn:aws:sns:ap-south-1:123456789012:test-topic",
        )

        assert result is False


class TestAPIErrorAlerts:
    """Test API error alerting"""

    def test_create_api_error_rate_alarm(self, alerting_service, mock_boto_clients):
        """Test API error rate alarm creation"""
        topic_arn = "arn:aws:sns:ap-south-1:123456789012:test-topic"

        result = alerting_service.create_api_error_rate_alarm(
            sns_topic_arn=topic_arn, threshold_percent=5.0
        )

        assert result is True
        mock_boto_clients["cloudwatch"].put_metric_alarm.assert_called_once()

        # Verify metric math expression
        call_args = mock_boto_clients["cloudwatch"].put_metric_alarm.call_args
        metrics = call_args[1]["Metrics"]

        # Should have 3 metrics: errors, requests, error_rate
        assert len(metrics) == 3
        assert metrics[2]["Expression"] == "(errors / requests) * 100"

    def test_create_api_error_count_alarm(self, alerting_service, mock_boto_clients):
        """Test API error count alarm creation"""
        topic_arn = "arn:aws:sns:ap-south-1:123456789012:test-topic"

        result = alerting_service.create_api_error_count_alarm(
            sns_topic_arn=topic_arn, threshold=10
        )

        assert result is True
        mock_boto_clients["cloudwatch"].put_metric_alarm.assert_called_once()


class TestPerformanceAlerts:
    """Test performance alerting"""

    def test_create_api_response_time_alarm(self, alerting_service, mock_boto_clients):
        """Test API response time alarm creation"""
        topic_arn = "arn:aws:sns:ap-south-1:123456789012:test-topic"

        result = alerting_service.create_api_response_time_alarm(
            sns_topic_arn=topic_arn, threshold_ms=3000.0
        )

        assert result is True

        # Verify p95 statistic is used
        call_args = mock_boto_clients["cloudwatch"].put_metric_alarm.call_args
        assert call_args[1]["Statistic"] == "p95"
        assert call_args[1]["Threshold"] == 3000.0

    def test_create_bedrock_response_time_alarm(self, alerting_service, mock_boto_clients):
        """Test Bedrock response time alarm creation"""
        topic_arn = "arn:aws:sns:ap-south-1:123456789012:test-topic"

        result = alerting_service.create_bedrock_response_time_alarm(
            sns_topic_arn=topic_arn, threshold_ms=10000.0
        )

        assert result is True

        # Verify configuration
        call_args = mock_boto_clients["cloudwatch"].put_metric_alarm.call_args
        assert call_args[1]["MetricName"] == "BedrockResponseTime"
        assert call_args[1]["Threshold"] == 10000.0


class TestCostMonitoringAlerts:
    """Test cost monitoring alerting"""

    def test_create_bedrock_daily_cost_alarm(self, alerting_service, mock_boto_clients):
        """Test Bedrock daily cost alarm creation"""
        topic_arn = "arn:aws:sns:ap-south-1:123456789012:test-topic"

        result = alerting_service.create_bedrock_cost_alarm(
            sns_topic_arn=topic_arn, daily_threshold_usd=100.0
        )

        assert result is True

        # Verify 24-hour period
        call_args = mock_boto_clients["cloudwatch"].put_metric_alarm.call_args
        assert call_args[1]["Period"] == 86400  # 24 hours
        assert call_args[1]["Threshold"] == 100.0

    def test_create_bedrock_hourly_cost_alarm(self, alerting_service, mock_boto_clients):
        """Test Bedrock hourly cost alarm creation"""
        topic_arn = "arn:aws:sns:ap-south-1:123456789012:test-topic"

        result = alerting_service.create_bedrock_hourly_cost_alarm(
            sns_topic_arn=topic_arn, hourly_threshold_usd=10.0
        )

        assert result is True

        # Verify 1-hour period
        call_args = mock_boto_clients["cloudwatch"].put_metric_alarm.call_args
        assert call_args[1]["Period"] == 3600  # 1 hour
        assert call_args[1]["Threshold"] == 10.0


class TestDatabaseAlerts:
    """Test database alerting"""

    def test_create_database_query_time_alarm(self, alerting_service, mock_boto_clients):
        """Test database query time alarm creation"""
        topic_arn = "arn:aws:sns:ap-south-1:123456789012:test-topic"

        result = alerting_service.create_database_query_time_alarm(
            sns_topic_arn=topic_arn, threshold_ms=500.0
        )

        assert result is True

        # Verify configuration
        call_args = mock_boto_clients["cloudwatch"].put_metric_alarm.call_args
        assert call_args[1]["MetricName"] == "DatabaseQueryTime"
        assert call_args[1]["Statistic"] == "p95"


class TestCompositeAlarmSetup:
    """Test composite alarm setup"""

    def test_setup_all_alarms(self, alerting_service, mock_boto_clients):
        """Test setting up all alarms"""
        critical_topic = "arn:aws:sns:ap-south-1:123456789012:critical"
        warning_topic = "arn:aws:sns:ap-south-1:123456789012:warning"

        results = alerting_service.setup_all_alarms(
            critical_topic_arn=critical_topic, warning_topic_arn=warning_topic
        )

        # Should create 8 alarms
        assert len(results) == 8

        # Verify all alarms were attempted
        expected_alarms = [
            "api_error_rate",
            "api_error_count",
            "service_health",
            "api_response_time",
            "bedrock_response_time",
            "database_query_time",
            "bedrock_daily_cost",
            "bedrock_hourly_cost",
        ]

        for alarm_name in expected_alarms:
            assert alarm_name in results


class TestAlarmManagement:
    """Test alarm management operations"""

    def test_list_alarms(self, alerting_service, mock_boto_clients):
        """Test listing alarms"""
        mock_boto_clients["cloudwatch"].describe_alarms.return_value = {
            "MetricAlarms": [
                {"AlarmName": "alarm1", "StateValue": "OK"},
                {"AlarmName": "alarm2", "StateValue": "ALARM"},
            ]
        }

        alarms = alerting_service.list_alarms()

        assert len(alarms) == 2
        assert alarms[0]["AlarmName"] == "alarm1"
        assert alarms[1]["StateValue"] == "ALARM"

    def test_delete_alarm(self, alerting_service, mock_boto_clients):
        """Test deleting an alarm"""
        result = alerting_service.delete_alarm("test-alarm")

        assert result is True
        mock_boto_clients["cloudwatch"].delete_alarms.assert_called_once_with(
            AlarmNames=["test-alarm"]
        )

    def test_get_alarm_state(self, alerting_service, mock_boto_clients):
        """Test getting alarm state"""
        mock_boto_clients["cloudwatch"].describe_alarms.return_value = {
            "MetricAlarms": [{"AlarmName": "test-alarm", "StateValue": "OK"}]
        }

        state = alerting_service.get_alarm_state("test-alarm")

        assert state == "OK"

    def test_get_alarm_state_not_found(self, alerting_service, mock_boto_clients):
        """Test getting state for non-existent alarm"""
        mock_boto_clients["cloudwatch"].describe_alarms.return_value = {"MetricAlarms": []}

        state = alerting_service.get_alarm_state("non-existent")

        assert state is None


class TestDisabledAlerting:
    """Test behavior when alerting is disabled"""

    def test_disabled_alerting_operations(self):
        """Test that operations return safely when disabled"""
        service = AlertingService(enabled=False)

        # All operations should return False/None without errors
        assert service.create_sns_topic("test", "Test") is None
        assert service.subscribe_email("arn", "test@example.com") is False
        assert (
            service.create_alarm(
                "test", "desc", "metric", "GreaterThanThreshold", 100, 1, 300, "Average", "arn"
            )
            is False
        )
        assert service.list_alarms() == []
        assert service.delete_alarm("test") is False
        assert service.get_alarm_state("test") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
