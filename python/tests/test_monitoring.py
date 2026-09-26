"""
Tests for CloudWatch Monitoring
Task 20.3: Set up application monitoring

Tests:
- CloudWatch monitor initialization
- Metric publishing
- Health check endpoints
- Monitoring middleware

Validates: Requirements (Non-Functional - Reliability)
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.core.monitoring import CloudWatchMonitor, get_monitor, init_monitor


class TestCloudWatchMonitor:
    """Test CloudWatch monitoring service"""

    def test_monitor_initialization(self):
        """Test monitor can be initialized"""
        monitor = CloudWatchMonitor(namespace="TestNamespace", region="us-east-1", enabled=True)

        assert monitor.namespace == "TestNamespace"
        assert monitor.region == "us-east-1"
        assert monitor.enabled == True

    def test_monitor_disabled(self):
        """Test monitor can be disabled"""
        monitor = CloudWatchMonitor(enabled=False)

        assert monitor.enabled == False

        # Metrics should not be published when disabled
        result = monitor.put_metric("TestMetric", 1.0)
        assert result == False

    @patch("boto3.client")
    def test_put_metric(self, mock_boto_client):
        """Test single metric publishing"""
        mock_cloudwatch = Mock()
        mock_boto_client.return_value = mock_cloudwatch

        monitor = CloudWatchMonitor(enabled=True)
        monitor.cloudwatch = mock_cloudwatch

        result = monitor.put_metric(
            metric_name="TestMetric", value=1.0, unit="Count", dimensions={"Type": "Test"}
        )

        assert result == True
        assert mock_cloudwatch.put_metric_data.called

    @patch("boto3.client")
    def test_put_metrics_batch(self, mock_boto_client):
        """Test batch metric publishing"""
        mock_cloudwatch = Mock()
        mock_boto_client.return_value = mock_cloudwatch

        monitor = CloudWatchMonitor(enabled=True)
        monitor.cloudwatch = mock_cloudwatch

        metrics = [
            {"metric_name": "Metric1", "value": 1.0, "unit": "Count"},
            {"metric_name": "Metric2", "value": 2.0, "unit": "Count"},
        ]

        result = monitor.put_metrics_batch(metrics)

        assert result == True
        assert mock_cloudwatch.put_metric_data.called

    @patch("boto3.client")
    def test_track_api_request(self, mock_boto_client):
        """Test API request tracking"""
        mock_cloudwatch = Mock()
        mock_boto_client.return_value = mock_cloudwatch

        monitor = CloudWatchMonitor(enabled=True)
        monitor.cloudwatch = mock_cloudwatch

        monitor.track_api_request(
            endpoint="/users", method="GET", status_code=200, response_time_ms=150.5
        )

        assert mock_cloudwatch.put_metric_data.called

    @patch("boto3.client")
    def test_track_bedrock_request(self, mock_boto_client):
        """Test Bedrock request tracking"""
        mock_cloudwatch = Mock()
        mock_boto_client.return_value = mock_cloudwatch

        monitor = CloudWatchMonitor(enabled=True)
        monitor.cloudwatch = mock_cloudwatch

        monitor.track_bedrock_request(
            model_id="anthropic.claude-v2",
            request_type="annual_strategy",
            response_time_ms=8500,
            input_tokens=2000,
            output_tokens=3000,
            estimated_cost_usd=0.11,
            success=True,
        )

        assert mock_cloudwatch.put_metric_data.called

    @patch("boto3.client")
    def test_track_business_metrics(self, mock_boto_client):
        """Test business metrics tracking"""
        mock_cloudwatch = Mock()
        mock_boto_client.return_value = mock_cloudwatch

        monitor = CloudWatchMonitor(enabled=True)
        monitor.cloudwatch = mock_cloudwatch

        # Test user registration
        monitor.track_user_registration(user_type="farmer")
        assert mock_cloudwatch.put_metric_data.called

        # Test strategy generation
        monitor.track_strategy_generation(state="Maharashtra", district="Pune", success=True)
        assert mock_cloudwatch.put_metric_data.called

        # Test marketplace listing
        monitor.track_marketplace_listing(crop_type="Rice", state="Maharashtra", action="created")
        assert mock_cloudwatch.put_metric_data.called

        # Test buyer interest
        monitor.track_buyer_interest(crop_type="Rice", state="Maharashtra")
        assert mock_cloudwatch.put_metric_data.called


class TestHealthCheckEndpoints:
    """Test health check endpoints"""

    def test_health_endpoints_exist(self):
        """Test that health check endpoints are defined"""
        from app.api.v1 import health

        # Check that router exists
        assert health.router is not None

        # Check that routes are defined
        routes = [route.path for route in health.router.routes]
        assert "/health" in routes
        assert "/ready" in routes
        assert "/health/detailed" in routes


class TestMonitoringSingleton:
    """Test monitoring singleton pattern"""

    def test_init_monitor(self):
        """Test monitor initialization"""
        monitor = init_monitor(
            namespace="TestNamespace",
            region="us-east-1",
            enabled=False,  # Disable to avoid AWS calls
        )

        assert monitor is not None
        assert monitor.namespace == "TestNamespace"

    def test_get_monitor(self):
        """Test getting monitor instance"""
        # Initialize first
        init_monitor(enabled=False)

        # Get instance
        monitor = get_monitor()

        assert monitor is not None


class TestMonitoringMiddleware:
    """Test monitoring middleware"""

    def test_middleware_class_exists(self):
        """Test middleware class is defined"""
        from app.core.monitoring_middleware import MonitoringMiddleware

        assert MonitoringMiddleware is not None


@pytest.mark.asyncio
class TestHealthCheckUtilities:
    """Test health check utility functions"""

    @patch("boto3.client")
    async def test_check_database_health(self, mock_boto_client):
        """Test database health check"""
        monitor = CloudWatchMonitor(enabled=False)

        health = await monitor.check_database_health()

        assert "status" in health
        assert "timestamp" in health

    @patch("boto3.client")
    async def test_check_redis_health(self, mock_boto_client):
        """Test Redis health check"""
        monitor = CloudWatchMonitor(enabled=False)

        health = await monitor.check_redis_health()

        assert "status" in health
        assert "timestamp" in health

    @patch("boto3.client")
    async def test_check_bedrock_health(self, mock_boto_client):
        """Test Bedrock health check"""
        mock_bedrock = Mock()
        mock_bedrock.list_foundation_models.return_value = {
            "modelSummaries": [{"modelId": "model1"}, {"modelId": "model2"}]
        }
        mock_boto_client.return_value = mock_bedrock

        monitor = CloudWatchMonitor(enabled=True)

        health = await monitor.check_bedrock_health()

        assert health["status"] == "healthy"
        assert health["available_models"] == 2

    @patch("boto3.client")
    async def test_comprehensive_health(self, mock_boto_client):
        """Test comprehensive health check"""
        monitor = CloudWatchMonitor(enabled=False)

        health = await monitor.get_comprehensive_health()

        assert "status" in health
        assert "timestamp" in health
        assert "services" in health
        assert "database" in health["services"]
        assert "redis" in health["services"]
        assert "bedrock" in health["services"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
