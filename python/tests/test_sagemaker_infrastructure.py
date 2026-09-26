"""
Unit Tests for SageMaker Infrastructure

Tests for SageMaker endpoint configuration, deployment, auto-scaling,
multi-model endpoints, A/B testing, and model versioning.

Compatible with Python 3.14.3 and pytest
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from botocore.exceptions import ClientError

from app.services.sagemaker_service import SageMakerService


@pytest.fixture
def sagemaker_service():
    """Create SageMaker service instance with mocked clients"""
    with patch("app.services.sagemaker_service.boto3.client") as mock_boto3:
        # Mock SageMaker client
        mock_sagemaker = Mock()
        mock_runtime = Mock()

        def client_factory(service_name, **kwargs):
            if service_name == "sagemaker":
                return mock_sagemaker
            elif service_name == "sagemaker-runtime":
                return mock_runtime
            elif service_name == "application-autoscaling":
                return Mock()
            elif service_name == "cloudwatch":
                return Mock()
            return Mock()

        mock_boto3.side_effect = client_factory

        service = SageMakerService()
        service.client = mock_sagemaker
        service.runtime_client = mock_runtime

        yield service


# ==================== Endpoint Configuration Tests ====================


@pytest.mark.asyncio
async def test_create_standard_endpoint_config(sagemaker_service):
    """Test creating standard endpoint configuration with instances"""
    # Arrange
    sagemaker_service.client.create_endpoint_config.return_value = {
        "EndpointConfigArn": "arn:aws:sagemaker:region:account:endpoint-config/test-config"
    }

    # Act
    result = await sagemaker_service.create_endpoint_config(
        config_name="test-config",
        model_name="test-model",
        instance_type="ml.m5.large",
        initial_instance_count=2,
        serverless=False,
    )

    # Assert
    assert result["config_name"] == "test-config"
    assert result["serverless"] is False
    assert result["status"] == "created"
    assert "config_arn" in result

    # Verify API call
    sagemaker_service.client.create_endpoint_config.assert_called_once()
    call_args = sagemaker_service.client.create_endpoint_config.call_args[1]
    assert call_args["EndpointConfigName"] == "test-config"
    assert len(call_args["ProductionVariants"]) == 1
    assert call_args["ProductionVariants"][0]["InstanceType"] == "ml.m5.large"
    assert call_args["ProductionVariants"][0]["InitialInstanceCount"] == 2


@pytest.mark.asyncio
async def test_create_serverless_endpoint_config(sagemaker_service):
    """Test creating serverless endpoint configuration"""
    # Arrange
    sagemaker_service.client.create_endpoint_config.return_value = {
        "EndpointConfigArn": "arn:aws:sagemaker:region:account:endpoint-config/serverless-config"
    }

    # Act
    result = await sagemaker_service.create_endpoint_config(
        config_name="serverless-config",
        model_name="test-model",
        serverless=True,
        serverless_memory_mb=4096,
        serverless_max_concurrency=20,
    )

    # Assert
    assert result["config_name"] == "serverless-config"
    assert result["serverless"] is True
    assert result["status"] == "created"

    # Verify serverless configuration
    call_args = sagemaker_service.client.create_endpoint_config.call_args[1]
    variant = call_args["ProductionVariants"][0]
    assert "ServerlessConfig" in variant
    assert variant["ServerlessConfig"]["MemorySizeInMB"] == 4096
    assert variant["ServerlessConfig"]["MaxConcurrency"] == 20
    assert "InstanceType" not in variant


@pytest.mark.asyncio
async def test_create_multi_model_endpoint_config(sagemaker_service):
    """Test creating multi-model endpoint configuration"""
    # Arrange
    sagemaker_service.client.create_endpoint_config.return_value = {
        "EndpointConfigArn": "arn:aws:sagemaker:region:account:endpoint-config/multi-model-config"
    }

    # Act
    result = await sagemaker_service.create_multi_model_endpoint_config(
        config_name="multi-model-config",
        model_name="multi-model-container",
        instance_type="ml.m5.xlarge",
        initial_instance_count=2,
    )

    # Assert
    assert result["config_name"] == "multi-model-config"
    assert result["multi_model"] is True
    assert result["status"] == "created"

    # Verify tags include multi-model type
    call_args = sagemaker_service.client.create_endpoint_config.call_args[1]
    tags = call_args["Tags"]
    assert any(tag["Key"] == "Type" and tag["Value"] == "MultiModel" for tag in tags)


@pytest.mark.asyncio
async def test_create_endpoint_config_error_handling(sagemaker_service):
    """Test error handling when endpoint config creation fails"""
    # Arrange
    sagemaker_service.client.create_endpoint_config.side_effect = ClientError(
        {"Error": {"Code": "ValidationException", "Message": "Invalid configuration"}},
        "CreateEndpointConfig",
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await sagemaker_service.create_endpoint_config(
            config_name="invalid-config", model_name="test-model"
        )

    assert "Failed to create endpoint config" in str(exc_info.value)


# ==================== Endpoint Management Tests ====================


@pytest.mark.asyncio
async def test_create_endpoint(sagemaker_service):
    """Test creating SageMaker endpoint"""
    # Arrange
    sagemaker_service.client.create_endpoint.return_value = {
        "EndpointArn": "arn:aws:sagemaker:region:account:endpoint/test-endpoint"
    }

    # Act
    result = await sagemaker_service.create_endpoint(
        endpoint_name="test-endpoint", config_name="test-config"
    )

    # Assert
    assert result["endpoint_name"] == "test-endpoint"
    assert result["status"] == "creating"
    assert "endpoint_arn" in result

    sagemaker_service.client.create_endpoint.assert_called_once()


@pytest.mark.asyncio
async def test_wait_for_endpoint_success(sagemaker_service):
    """Test waiting for endpoint to be in service"""
    # Arrange
    sagemaker_service.client.describe_endpoint.return_value = {
        "EndpointStatus": "InService",
        "EndpointArn": "arn:aws:sagemaker:region:account:endpoint/test-endpoint",
    }

    # Act
    result = await sagemaker_service.wait_for_endpoint(
        endpoint_name="test-endpoint", timeout_seconds=60
    )

    # Assert
    assert result["endpoint_name"] == "test-endpoint"
    assert result["status"] == "in_service"
    assert "endpoint_arn" in result


@pytest.mark.asyncio
async def test_wait_for_endpoint_failure(sagemaker_service):
    """Test handling endpoint creation failure"""
    # Arrange
    sagemaker_service.client.describe_endpoint.return_value = {
        "EndpointStatus": "Failed",
        "FailureReason": "Insufficient capacity",
    }

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await sagemaker_service.wait_for_endpoint(endpoint_name="test-endpoint", timeout_seconds=60)

    assert "Endpoint creation failed" in str(exc_info.value)
    assert "Insufficient capacity" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_endpoint(sagemaker_service):
    """Test updating endpoint with new configuration"""
    # Arrange
    sagemaker_service.client.update_endpoint.return_value = {
        "EndpointArn": "arn:aws:sagemaker:region:account:endpoint/test-endpoint"
    }

    # Act
    result = await sagemaker_service.update_endpoint(
        endpoint_name="test-endpoint", new_config_name="new-config"
    )

    # Assert
    assert result["endpoint_name"] == "test-endpoint"
    assert result["status"] == "updating"

    sagemaker_service.client.update_endpoint.assert_called_once_with(
        EndpointName="test-endpoint", EndpointConfigName="new-config"
    )


@pytest.mark.asyncio
async def test_delete_endpoint(sagemaker_service):
    """Test deleting endpoint"""
    # Arrange
    sagemaker_service.client.delete_endpoint.return_value = {}

    # Act
    result = await sagemaker_service.delete_endpoint(endpoint_name="test-endpoint")

    # Assert
    assert result["endpoint_name"] == "test-endpoint"
    assert result["status"] == "deleting"

    sagemaker_service.client.delete_endpoint.assert_called_once_with(EndpointName="test-endpoint")


# ==================== Auto-Scaling Tests ====================


@pytest.mark.asyncio
async def test_configure_autoscaling(sagemaker_service):
    """Test configuring auto-scaling for endpoint"""
    # Arrange
    with patch("app.services.sagemaker_service.boto3.client") as mock_boto3:
        mock_autoscaling = Mock()
        mock_boto3.return_value = mock_autoscaling

        # Act
        result = await sagemaker_service.configure_autoscaling(
            endpoint_name="test-endpoint",
            variant_name="AllTraffic",
            min_capacity=2,
            max_capacity=10,
            target_invocations_per_instance=1500,
        )

        # Assert
        assert result["endpoint_name"] == "test-endpoint"
        assert result["min_capacity"] == 2
        assert result["max_capacity"] == 10
        assert result["target_invocations"] == 1500
        assert result["status"] == "configured"

        # Verify scalable target registration
        mock_autoscaling.register_scalable_target.assert_called_once()

        # Verify scaling policy creation
        mock_autoscaling.put_scaling_policy.assert_called_once()
        policy_args = mock_autoscaling.put_scaling_policy.call_args[1]
        assert policy_args["PolicyType"] == "TargetTrackingScaling"
        assert policy_args["TargetTrackingScalingPolicyConfiguration"]["TargetValue"] == 1500.0


# ==================== A/B Testing Tests ====================


@pytest.mark.asyncio
async def test_create_ab_test_endpoint_config(sagemaker_service):
    """Test creating A/B test endpoint configuration"""
    # Arrange
    sagemaker_service.client.create_endpoint_config.return_value = {
        "EndpointConfigArn": "arn:aws:sagemaker:region:account:endpoint-config/ab-test-config"
    }

    # Act
    result = await sagemaker_service.create_ab_test_endpoint_config(
        config_name="ab-test-config",
        model_a_name="baseline-model",
        model_b_name="challenger-model",
        traffic_split_percentage=30,
        instance_type="ml.m5.large",
        initial_instance_count=1,
    )

    # Assert
    assert result["config_name"] == "ab-test-config"
    assert result["model_a"] == "baseline-model"
    assert result["model_b"] == "challenger-model"
    assert result["traffic_split"]["model_a_percentage"] == 70
    assert result["traffic_split"]["model_b_percentage"] == 30

    # Verify production variants
    call_args = sagemaker_service.client.create_endpoint_config.call_args[1]
    variants = call_args["ProductionVariants"]
    assert len(variants) == 2
    assert variants[0]["VariantName"] == "ModelA"
    assert variants[1]["VariantName"] == "ModelB"
    assert variants[0]["InitialVariantWeight"] == 0.7
    assert variants[1]["InitialVariantWeight"] == 0.3


@pytest.mark.asyncio
async def test_update_traffic_split(sagemaker_service):
    """Test updating traffic split between models"""
    # Arrange
    sagemaker_service.client.update_endpoint_weights_and_capacities.return_value = {
        "EndpointArn": "arn:aws:sagemaker:region:account:endpoint/ab-test-endpoint"
    }

    # Act
    result = await sagemaker_service.update_traffic_split(
        endpoint_name="ab-test-endpoint", model_a_weight=0.5, model_b_weight=0.5
    )

    # Assert
    assert result["endpoint_name"] == "ab-test-endpoint"
    assert result["traffic_split"]["model_a_percentage"] == 50
    assert result["traffic_split"]["model_b_percentage"] == 50

    # Verify API call
    call_args = sagemaker_service.client.update_endpoint_weights_and_capacities.call_args[1]
    capacities = call_args["DesiredWeightsAndCapacities"]
    assert len(capacities) == 2
    assert capacities[0]["DesiredWeight"] == 0.5
    assert capacities[1]["DesiredWeight"] == 0.5


@pytest.mark.asyncio
async def test_update_traffic_split_normalization(sagemaker_service):
    """Test traffic split weight normalization"""
    # Arrange
    sagemaker_service.client.update_endpoint_weights_and_capacities.return_value = {
        "EndpointArn": "arn:aws:sagemaker:region:account:endpoint/ab-test-endpoint"
    }

    # Act - weights don't sum to 1.0
    result = await sagemaker_service.update_traffic_split(
        endpoint_name="ab-test-endpoint", model_a_weight=3.0, model_b_weight=1.0
    )

    # Assert - weights are normalized
    assert result["traffic_split"]["model_a_percentage"] == 75
    assert result["traffic_split"]["model_b_percentage"] == 25


# ==================== Model Versioning Tests ====================


@pytest.mark.asyncio
async def test_create_model_version(sagemaker_service):
    """Test creating versioned model"""
    # Arrange
    sagemaker_service.client.create_model.return_value = {
        "ModelArn": "arn:aws:sagemaker:region:account:model/crop-yield-v1"
    }

    # Act
    result = await sagemaker_service.create_model_version(
        model_name="crop-yield",
        model_data_url="s3://bucket/models/crop-yield-v1/model.tar.gz",
        image_uri="123456789.dkr.ecr.region.amazonaws.com/inference:latest",
        execution_role_arn="arn:aws:iam::123456789:role/SageMakerRole",
        version="v1",
    )

    # Assert
    assert result["model_name"] == "crop-yield-v1"
    assert result["base_name"] == "crop-yield"
    assert result["version"] == "v1"
    assert result["status"] == "created"

    # Verify model creation
    call_args = sagemaker_service.client.create_model.call_args[1]
    assert call_args["ModelName"] == "crop-yield-v1"
    assert call_args["PrimaryContainer"]["Environment"]["MODEL_VERSION"] == "v1"


@pytest.mark.asyncio
async def test_list_model_versions(sagemaker_service):
    """Test listing model versions"""
    # Arrange
    sagemaker_service.client.list_models.return_value = {
        "Models": [
            {
                "ModelName": "crop-yield-v2",
                "ModelArn": "arn:aws:sagemaker:region:account:model/crop-yield-v2",
                "CreationTime": datetime(2024, 1, 15, 12, 0, 0),
            },
            {
                "ModelName": "crop-yield-v1",
                "ModelArn": "arn:aws:sagemaker:region:account:model/crop-yield-v1",
                "CreationTime": datetime(2024, 1, 10, 12, 0, 0),
            },
        ]
    }

    # Act
    result = await sagemaker_service.list_model_versions(base_model_name="crop-yield")

    # Assert
    assert len(result) == 2
    # Should be sorted by creation time (newest first)
    assert result[0]["version"] == "v2"
    assert result[1]["version"] == "v1"
    assert result[0]["model_name"] == "crop-yield-v2"


# ==================== Inference Tests ====================


@pytest.mark.asyncio
async def test_invoke_endpoint(sagemaker_service):
    """Test invoking endpoint for inference"""
    # Arrange
    mock_response = Mock()
    mock_response.read.return_value = b'{"predictions": [0.85, 0.92]}'

    sagemaker_service.runtime_client.invoke_endpoint.return_value = {
        "Body": mock_response,
        "InvokedProductionVariant": "AllTraffic",
    }

    # Act
    result = await sagemaker_service.invoke_endpoint(
        endpoint_name="test-endpoint",
        payload={"features": [1, 2, 3, 4, 5]},
        content_type="application/json",
    )

    # Assert
    assert result["status"] == "success"
    assert result["predictions"] == {"predictions": [0.85, 0.92]}
    assert result["invoked_variant"] == "AllTraffic"

    # Verify API call
    sagemaker_service.runtime_client.invoke_endpoint.assert_called_once()


@pytest.mark.asyncio
async def test_invoke_endpoint_with_target_variant(sagemaker_service):
    """Test invoking specific variant in A/B test"""
    # Arrange
    mock_response = Mock()
    mock_response.read.return_value = b'{"predictions": [0.88]}'

    sagemaker_service.runtime_client.invoke_endpoint.return_value = {
        "Body": mock_response,
        "InvokedProductionVariant": "ModelB",
    }

    # Act
    result = await sagemaker_service.invoke_endpoint(
        endpoint_name="ab-test-endpoint", payload={"features": [1, 2, 3]}, target_variant="ModelB"
    )

    # Assert
    assert result["invoked_variant"] == "ModelB"

    # Verify target variant was specified
    call_args = sagemaker_service.runtime_client.invoke_endpoint.call_args[1]
    assert call_args["TargetVariant"] == "ModelB"


@pytest.mark.asyncio
async def test_invoke_multi_model_endpoint(sagemaker_service):
    """Test invoking specific model on multi-model endpoint"""
    # Arrange
    mock_response = Mock()
    mock_response.read.return_value = b'{"predictions": [0.91]}'

    sagemaker_service.runtime_client.invoke_endpoint.return_value = {"Body": mock_response}

    # Act
    result = await sagemaker_service.invoke_multi_model_endpoint(
        endpoint_name="multi-model-endpoint",
        model_name="wheat-yield-model",
        payload={"features": [1, 2, 3, 4, 5]},
    )

    # Assert
    assert result["status"] == "success"
    assert result["model_name"] == "wheat-yield-model"
    assert result["predictions"] == {"predictions": [0.91]}

    # Verify TargetModel was specified
    call_args = sagemaker_service.runtime_client.invoke_endpoint.call_args[1]
    assert call_args["TargetModel"] == "wheat-yield-model"


# ==================== Monitoring Tests ====================


@pytest.mark.asyncio
async def test_get_endpoint_metrics(sagemaker_service):
    """Test retrieving CloudWatch metrics for endpoint"""
    # Arrange
    with patch("app.services.sagemaker_service.boto3.client") as mock_boto3:
        mock_cloudwatch = Mock()
        mock_boto3.return_value = mock_cloudwatch

        mock_cloudwatch.get_metric_statistics.return_value = {
            "Datapoints": [
                {
                    "Timestamp": datetime(2024, 1, 15, 12, 0, 0),
                    "Average": 250.5,
                    "Sum": 1000.0,
                    "Maximum": 500.0,
                    "Minimum": 100.0,
                },
                {
                    "Timestamp": datetime(2024, 1, 15, 12, 5, 0),
                    "Average": 275.3,
                    "Sum": 1100.0,
                    "Maximum": 550.0,
                    "Minimum": 120.0,
                },
            ]
        }

        # Act
        result = await sagemaker_service.get_endpoint_metrics(
            endpoint_name="test-endpoint",
            metric_name="ModelLatency",
            start_time=datetime(2024, 1, 15, 12, 0, 0),
            end_time=datetime(2024, 1, 15, 13, 0, 0),
            period_seconds=300,
        )

        # Assert
        assert result["endpoint_name"] == "test-endpoint"
        assert result["metric_name"] == "ModelLatency"
        assert len(result["datapoints"]) == 2
        assert result["datapoints"][0]["average"] == 250.5
        assert result["datapoints"][1]["average"] == 275.3


# ==================== Integration Tests ====================


@pytest.mark.asyncio
async def test_complete_endpoint_deployment_workflow(sagemaker_service):
    """Test complete workflow: config -> endpoint -> autoscaling"""
    # Arrange
    sagemaker_service.client.create_endpoint_config.return_value = {
        "EndpointConfigArn": "arn:aws:sagemaker:region:account:endpoint-config/test-config"
    }
    sagemaker_service.client.create_endpoint.return_value = {
        "EndpointArn": "arn:aws:sagemaker:region:account:endpoint/test-endpoint"
    }
    sagemaker_service.client.describe_endpoint.return_value = {
        "EndpointStatus": "InService",
        "EndpointArn": "arn:aws:sagemaker:region:account:endpoint/test-endpoint",
    }

    with patch("app.services.sagemaker_service.boto3.client") as mock_boto3:
        mock_autoscaling = Mock()
        mock_boto3.return_value = mock_autoscaling

        # Act - Create config
        config_result = await sagemaker_service.create_endpoint_config(
            config_name="test-config",
            model_name="test-model",
            instance_type="ml.m5.large",
            initial_instance_count=1,
        )

        # Act - Create endpoint
        endpoint_result = await sagemaker_service.create_endpoint(
            endpoint_name="test-endpoint", config_name="test-config"
        )

        # Act - Wait for endpoint
        wait_result = await sagemaker_service.wait_for_endpoint(
            endpoint_name="test-endpoint", timeout_seconds=60
        )

        # Act - Configure autoscaling
        autoscaling_result = await sagemaker_service.configure_autoscaling(
            endpoint_name="test-endpoint", min_capacity=1, max_capacity=5
        )

        # Assert
        assert config_result["status"] == "created"
        assert endpoint_result["status"] == "creating"
        assert wait_result["status"] == "in_service"
        assert autoscaling_result["status"] == "configured"


@pytest.mark.asyncio
async def test_ab_test_deployment_workflow(sagemaker_service):
    """Test A/B testing workflow: config -> endpoint -> traffic adjustment"""
    # Arrange
    sagemaker_service.client.create_endpoint_config.return_value = {
        "EndpointConfigArn": "arn:aws:sagemaker:region:account:endpoint-config/ab-config"
    }
    sagemaker_service.client.create_endpoint.return_value = {
        "EndpointArn": "arn:aws:sagemaker:region:account:endpoint/ab-endpoint"
    }
    sagemaker_service.client.update_endpoint_weights_and_capacities.return_value = {
        "EndpointArn": "arn:aws:sagemaker:region:account:endpoint/ab-endpoint"
    }

    # Act - Create A/B test config (10% traffic to model B)
    config_result = await sagemaker_service.create_ab_test_endpoint_config(
        config_name="ab-config",
        model_a_name="baseline",
        model_b_name="challenger",
        traffic_split_percentage=10,
    )

    # Act - Create endpoint
    endpoint_result = await sagemaker_service.create_endpoint(
        endpoint_name="ab-endpoint", config_name="ab-config"
    )

    # Act - Increase traffic to model B (50%)
    traffic_result = await sagemaker_service.update_traffic_split(
        endpoint_name="ab-endpoint", model_a_weight=0.5, model_b_weight=0.5
    )

    # Assert
    assert config_result["traffic_split"]["model_b_percentage"] == 10
    assert endpoint_result["status"] == "creating"
    assert traffic_result["traffic_split"]["model_b_percentage"] == 50
