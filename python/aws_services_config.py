"""
AWS Services Configuration for Production Deployment
Task 20.2: Configure AWS services for production

This module provides configuration and setup utilities for:
- Amazon Cognito User Pool (authentication)
- Amazon Bedrock (AI/ML inference)
- Amazon SNS (notifications)
- Redis ElastiCache (caching layer)

Validates: Requirements AC1, AC2, AC3, AC4, AC6
"""

import boto3
from botocore.exceptions import ClientError
import logging
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)


class AWSServicesConfigurator:
    """
    AWS Services Configuration Manager
    Handles setup and configuration of AWS services for production
    """
    
    def __init__(
        self,
        region: str = "ap-south-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize AWS services configurator
        
        Args:
            region: AWS region (default: ap-south-1 for India)
            aws_access_key_id: AWS access key ID (optional, uses IAM role if not provided)
            aws_secret_access_key: AWS secret access key (optional)
        """
        self.region = region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        
        # Initialize AWS clients
        self._init_clients()
    
    def _init_clients(self):
        """Initialize AWS service clients"""
        client_config = {
            'region_name': self.region
        }
        
        if self.aws_access_key_id and self.aws_secret_access_key:
            client_config['aws_access_key_id'] = self.aws_access_key_id
            client_config['aws_secret_access_key'] = self.aws_secret_access_key
        
        try:
            self.cognito_client = boto3.client('cognito-idp', **client_config)
            self.bedrock_client = boto3.client('bedrock', **client_config)
            self.bedrock_runtime_client = boto3.client('bedrock-runtime', **client_config)
            self.sns_client = boto3.client('sns', **client_config)
            self.elasticache_client = boto3.client('elasticache', **client_config)
            self.cloudwatch_client = boto3.client('cloudwatch', **client_config)
            logger.info("AWS clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
            raise
    
    # ==================== COGNITO CONFIGURATION ====================
    
    def configure_cognito_user_pool(
        self,
        pool_name: str = "cropsense-ai-users",
        auto_verified_attributes: List[str] = None,
        mfa_configuration: str = "OPTIONAL",
        password_policy: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Configure Amazon Cognito User Pool for production
        
        Security Settings:
        - Password policy: Min 8 chars, requires uppercase, lowercase, numbers, symbols
        - MFA: Optional SMS-based MFA
        - Auto-verified attributes: email and phone_number
        - Account recovery: Email and phone
        - User attributes: email, phone_number, name, custom:farm_id
        
        Args:
            pool_name: User pool name
            auto_verified_attributes: Attributes to auto-verify (default: email, phone_number)
            mfa_configuration: MFA configuration (OFF, OPTIONAL, ON)
            password_policy: Custom password policy (optional)
            
        Returns:
            Dict with user pool configuration details
            
        Validates: AC1 - Cognito authentication with MFA support
        """
        if auto_verified_attributes is None:
            auto_verified_attributes = ['email', 'phone_number']
        
        if password_policy is None:
            password_policy = {
                'MinimumLength': 8,
                'RequireUppercase': True,
                'RequireLowercase': True,
                'RequireNumbers': True,
                'RequireSymbols': True,
                'TemporaryPasswordValidityDays': 7
            }
        
        try:
            # Create user pool
            response = self.cognito_client.create_user_pool(
                PoolName=pool_name,
                Policies={
                    'PasswordPolicy': password_policy
                },
                AutoVerifiedAttributes=auto_verified_attributes,
                MfaConfiguration=mfa_configuration,
                SmsConfiguration={
                    'SnsCallerArn': f'arn:aws:iam::ACCOUNT_ID:role/CognitoSNSRole',
                    'ExternalId': 'cropsense-ai'
                },
                AccountRecoverySetting={
                    'RecoveryMechanisms': [
                        {'Priority': 1, 'Name': 'verified_email'},
                        {'Priority': 2, 'Name': 'verified_phone_number'}
                    ]
                },
                Schema=[
                    {
                        'Name': 'email',
                        'AttributeDataType': 'String',
                        'Required': True,
                        'Mutable': True
                    },
                    {
                        'Name': 'phone_number',
                        'AttributeDataType': 'String',
                        'Required': True,
                        'Mutable': True
                    },
                    {
                        'Name': 'name',
                        'AttributeDataType': 'String',
                        'Required': True,
                        'Mutable': True
                    },
                    {
                        'Name': 'farm_id',
                        'AttributeDataType': 'String',
                        'DeveloperOnlyAttribute': False,
                        'Mutable': True
                    }
                ],
                UserAttributeUpdateSettings={
                    'AttributesRequireVerificationBeforeUpdate': ['email', 'phone_number']
                },
                EmailConfiguration={
                    'EmailSendingAccount': 'COGNITO_DEFAULT'
                },
                SmsAuthenticationMessage='Your CropSense AI verification code is {####}',
                SmsVerificationMessage='Your CropSense AI verification code is {####}',
                UserPoolTags={
                    'Environment': 'production',
                    'Application': 'cropsense-ai',
                    'ManagedBy': 'terraform'
                }
            )
            
            user_pool_id = response['UserPool']['Id']
            logger.info(f"Cognito User Pool created: {user_pool_id}")
            
            # Create user pool client
            client_response = self.cognito_client.create_user_pool_client(
                UserPoolId=user_pool_id,
                ClientName=f'{pool_name}-client',
                GenerateSecret=True,
                RefreshTokenValidity=30,  # 30 days
                AccessTokenValidity=60,  # 60 minutes
                IdTokenValidity=60,  # 60 minutes
                TokenValidityUnits={
                    'AccessToken': 'minutes',
                    'IdToken': 'minutes',
                    'RefreshToken': 'days'
                },
                ExplicitAuthFlows=[
                    'ALLOW_USER_PASSWORD_AUTH',
                    'ALLOW_REFRESH_TOKEN_AUTH',
                    'ALLOW_USER_SRP_AUTH'
                ],
                PreventUserExistenceErrors='ENABLED',
                EnableTokenRevocation=True,
                EnablePropagateAdditionalUserContextData=False
            )
            
            client_id = client_response['UserPoolClient']['ClientId']
            client_secret = client_response['UserPoolClient']['ClientSecret']
            
            logger.info(f"Cognito User Pool Client created: {client_id}")
            
            return {
                'user_pool_id': user_pool_id,
                'client_id': client_id,
                'client_secret': client_secret,
                'region': self.region,
                'mfa_configuration': mfa_configuration,
                'auto_verified_attributes': auto_verified_attributes
            }
            
        except ClientError as e:
            logger.error(f"Failed to configure Cognito User Pool: {e}")
            raise
    
    def get_cognito_user_pool_info(self, user_pool_id: str) -> Dict[str, Any]:
        """
        Get Cognito User Pool configuration details
        
        Args:
            user_pool_id: User pool ID
            
        Returns:
            User pool configuration details
        """
        try:
            response = self.cognito_client.describe_user_pool(
                UserPoolId=user_pool_id
            )
            return response['UserPool']
        except ClientError as e:
            logger.error(f"Failed to get Cognito User Pool info: {e}")
            raise
    
    # ==================== BEDROCK CONFIGURATION ====================
    
    def configure_bedrock_access(
        self,
        model_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Configure Amazon Bedrock access and quotas
        
        Models:
        - anthropic.claude-v2 (primary for annual strategies)
        - anthropic.claude-instant-v1 (faster responses)
        
        Quotas:
        - Monitor usage and costs via CloudWatch
        - Set up billing alerts for cost control
        - Implement caching to reduce API calls (6-hour TTL)
        
        Args:
            model_ids: List of Bedrock model IDs to enable
            
        Returns:
            Dict with Bedrock configuration details
            
        Validates: AC2, AC3 - Bedrock API integration for crop intelligence
        """
        if model_ids is None:
            model_ids = [
                'anthropic.claude-v2',
                'anthropic.claude-instant-v1'
            ]
        
        try:
            # List available foundation models
            response = self.bedrock_client.list_foundation_models()
            available_models = response.get('modelSummaries', [])
            
            # Filter for requested models
            enabled_models = []
            for model in available_models:
                if model['modelId'] in model_ids:
                    enabled_models.append({
                        'model_id': model['modelId'],
                        'model_name': model['modelName'],
                        'provider_name': model['providerName'],
                        'input_modalities': model.get('inputModalities', []),
                        'output_modalities': model.get('outputModalities', [])
                    })
            
            logger.info(f"Bedrock models available: {len(enabled_models)}")
            
            # Set up CloudWatch metrics for Bedrock usage monitoring
            self._setup_bedrock_monitoring()
            
            return {
                'region': self.region,
                'enabled_models': enabled_models,
                'caching_enabled': True,
                'cache_ttl_hours': 6,
                'monitoring_enabled': True,
                'cost_tracking': 'CloudWatch Metrics'
            }
            
        except ClientError as e:
            logger.error(f"Failed to configure Bedrock access: {e}")
            raise
    
    def _setup_bedrock_monitoring(self):
        """Set up CloudWatch monitoring for Bedrock API usage"""
        try:
            # Create CloudWatch alarm for Bedrock API costs
            self.cloudwatch_client.put_metric_alarm(
                AlarmName='bedrock-api-cost-alert',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='EstimatedCharges',
                Namespace='AWS/Bedrock',
                Period=86400,  # 24 hours
                Statistic='Sum',
                Threshold=100.0,  # Alert if daily cost > $100
                ActionsEnabled=True,
                AlarmDescription='Alert when Bedrock API costs exceed threshold',
                Dimensions=[
                    {
                        'Name': 'ServiceName',
                        'Value': 'AmazonBedrock'
                    }
                ]
            )
            logger.info("Bedrock cost monitoring alarm created")
        except ClientError as e:
            logger.warning(f"Failed to create Bedrock monitoring alarm: {e}")
    
    def get_bedrock_usage_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get Bedrock API usage metrics from CloudWatch
        
        Args:
            days: Number of days to retrieve metrics for
            
        Returns:
            Usage metrics including API calls, costs, and latency
        """
        try:
            from datetime import datetime, timedelta
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get API invocation count
            invocations_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Bedrock',
                MetricName='Invocations',
                Dimensions=[],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # Daily
                Statistics=['Sum']
            )
            
            # Get estimated charges
            cost_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Bedrock',
                MetricName='EstimatedCharges',
                Dimensions=[
                    {
                        'Name': 'ServiceName',
                        'Value': 'AmazonBedrock'
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=['Sum']
            )
            
            return {
                'period_days': days,
                'invocations': invocations_response.get('Datapoints', []),
                'estimated_costs': cost_response.get('Datapoints', []),
                'monitoring_enabled': True
            }
            
        except ClientError as e:
            logger.error(f"Failed to get Bedrock usage metrics: {e}")
            return {}
    
    # ==================== SNS CONFIGURATION ====================
    
    def configure_sns_topics(
        self,
        topic_names: Dict[str, str] = None
    ) -> Dict[str, str]:
        """
        Configure Amazon SNS topics for notifications
        
        Topics:
        - buyer-interests: Notify farmers when buyers express interest
        - strategy-reminders: Monthly implementation reminders
        - weather-alerts: Extreme weather condition alerts
        - harvest-reminders: Harvest timing notifications
        
        Args:
            topic_names: Custom topic names (optional)
            
        Returns:
            Dict mapping topic types to ARNs
            
        Validates: AC4, AC6 - SNS notifications for buyer interests and reminders
        """
        if topic_names is None:
            topic_names = {
                'buyer_interests': 'rural-farming-buyer-interests',
                'strategy_reminders': 'rural-farming-strategy-reminders',
                'weather_alerts': 'rural-farming-weather-alerts',
                'harvest_reminders': 'rural-farming-harvest-reminders'
            }
        
        topic_arns = {}
        
        try:
            for topic_type, topic_name in topic_names.items():
                # Create SNS topic
                response = self.sns_client.create_topic(
                    Name=topic_name,
                    Tags=[
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Application', 'Value': 'cropsense-ai'},
                        {'Key': 'NotificationType', 'Value': topic_type}
                    ]
                )
                
                topic_arn = response['TopicArn']
                topic_arns[topic_type] = topic_arn
                
                # Set topic attributes
                self.sns_client.set_topic_attributes(
                    TopicArn=topic_arn,
                    AttributeName='DisplayName',
                    AttributeValue=f'CropSense AI - {topic_type.replace("_", " ").title()}'
                )
                
                logger.info(f"SNS topic created: {topic_name} ({topic_arn})")
            
            return topic_arns
            
        except ClientError as e:
            logger.error(f"Failed to configure SNS topics: {e}")
            raise
    
    def subscribe_to_sns_topic(
        self,
        topic_arn: str,
        protocol: str,
        endpoint: str
    ) -> str:
        """
        Subscribe to SNS topic
        
        Args:
            topic_arn: SNS topic ARN
            protocol: Protocol (sms, email, https, lambda)
            endpoint: Endpoint (phone number, email, URL, Lambda ARN)
            
        Returns:
            Subscription ARN
        """
        try:
            response = self.sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol=protocol,
                Endpoint=endpoint
            )
            
            subscription_arn = response['SubscriptionArn']
            logger.info(f"Subscribed to SNS topic: {topic_arn} ({protocol}: {endpoint})")
            return subscription_arn
            
        except ClientError as e:
            logger.error(f"Failed to subscribe to SNS topic: {e}")
            raise
    
    # ==================== ELASTICACHE CONFIGURATION ====================
    
    def configure_elasticache_redis(
        self,
        cluster_id: str = "rural-farming-cache",
        node_type: str = "cache.t3.micro",
        num_cache_nodes: int = 1,
        engine_version: str = "7.0"
    ) -> Dict[str, Any]:
        """
        Configure Redis ElastiCache for caching layer
        
        Cache Strategy:
        - Bedrock API responses: 6-hour TTL
        - Market intelligence data: 24-hour TTL
        - Farm profiles: 1-hour TTL
        - Crop recommendations: 1-hour TTL
        
        Args:
            cluster_id: ElastiCache cluster ID
            node_type: Cache node type (default: cache.t3.micro for dev/test)
            num_cache_nodes: Number of cache nodes
            engine_version: Redis engine version
            
        Returns:
            Dict with ElastiCache configuration details
            
        Validates: AC2, AC3 - Redis caching for API responses
        """
        try:
            # Create ElastiCache Redis cluster
            response = self.elasticache_client.create_cache_cluster(
                CacheClusterId=cluster_id,
                CacheNodeType=node_type,
                Engine='redis',
                EngineVersion=engine_version,
                NumCacheNodes=num_cache_nodes,
                PreferredMaintenanceWindow='sun:05:00-sun:06:00',
                Port=6379,
                CacheParameterGroupName='default.redis7',
                CacheSubnetGroupName='default',
                SecurityGroupIds=[],  # Configure security groups separately
                Tags=[
                    {'Key': 'Environment', 'Value': 'production'},
                    {'Key': 'Application', 'Value': 'cropsense-ai'},
                    {'Key': 'Purpose', 'Value': 'api-caching'}
                ],
                SnapshotRetentionLimit=7,  # 7-day backup retention
                SnapshotWindow='03:00-04:00',
                AutoMinorVersionUpgrade=True
            )
            
            cluster_info = response['CacheCluster']
            logger.info(f"ElastiCache Redis cluster created: {cluster_id}")
            
            return {
                'cluster_id': cluster_id,
                'node_type': node_type,
                'engine': 'redis',
                'engine_version': engine_version,
                'num_nodes': num_cache_nodes,
                'port': 6379,
                'status': cluster_info['CacheClusterStatus'],
                'cache_strategies': {
                    'bedrock_api': '6-hour TTL',
                    'market_data': '24-hour TTL',
                    'farm_profiles': '1-hour TTL',
                    'crop_recommendations': '1-hour TTL'
                }
            }
            
        except ClientError as e:
            logger.error(f"Failed to configure ElastiCache Redis: {e}")
            raise
    
    def get_elasticache_endpoint(self, cluster_id: str) -> Dict[str, Any]:
        """
        Get ElastiCache cluster endpoint
        
        Args:
            cluster_id: ElastiCache cluster ID
            
        Returns:
            Dict with endpoint details
        """
        try:
            response = self.elasticache_client.describe_cache_clusters(
                CacheClusterId=cluster_id,
                ShowCacheNodeInfo=True
            )
            
            cluster = response['CacheClusters'][0]
            endpoint = cluster['CacheNodes'][0]['Endpoint']
            
            return {
                'cluster_id': cluster_id,
                'endpoint': endpoint['Address'],
                'port': endpoint['Port'],
                'status': cluster['CacheClusterStatus'],
                'redis_url': f"redis://{endpoint['Address']}:{endpoint['Port']}/0"
            }
            
        except ClientError as e:
            logger.error(f"Failed to get ElastiCache endpoint: {e}")
            raise
    
    # ==================== CONFIGURATION SUMMARY ====================
    
    def generate_configuration_summary(
        self,
        user_pool_id: Optional[str] = None,
        topic_arns: Optional[Dict[str, str]] = None,
        elasticache_cluster_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AWS services configuration summary
        
        Args:
            user_pool_id: Cognito User Pool ID
            topic_arns: SNS topic ARNs
            elasticache_cluster_id: ElastiCache cluster ID
            
        Returns:
            Complete configuration summary
        """
        summary = {
            'region': self.region,
            'services': {}
        }
        
        # Cognito configuration
        if user_pool_id:
            try:
                cognito_info = self.get_cognito_user_pool_info(user_pool_id)
                summary['services']['cognito'] = {
                    'user_pool_id': user_pool_id,
                    'mfa_configuration': cognito_info.get('MfaConfiguration'),
                    'status': cognito_info.get('Status'),
                    'auto_verified_attributes': cognito_info.get('AutoVerifiedAttributes', [])
                }
            except Exception as e:
                logger.warning(f"Could not retrieve Cognito info: {e}")
        
        # Bedrock configuration
        try:
            bedrock_config = self.configure_bedrock_access()
            summary['services']['bedrock'] = bedrock_config
        except Exception as e:
            logger.warning(f"Could not retrieve Bedrock info: {e}")
        
        # SNS configuration
        if topic_arns:
            summary['services']['sns'] = {
                'topics': topic_arns,
                'notification_types': list(topic_arns.keys())
            }
        
        # ElastiCache configuration
        if elasticache_cluster_id:
            try:
                cache_endpoint = self.get_elasticache_endpoint(elasticache_cluster_id)
                summary['services']['elasticache'] = cache_endpoint
            except Exception as e:
                logger.warning(f"Could not retrieve ElastiCache info: {e}")
        
        return summary


def generate_env_file(config_summary: Dict[str, Any], output_path: str = ".env.production"):
    """
    Generate .env file with AWS service configuration
    
    Args:
        config_summary: Configuration summary from generate_configuration_summary()
        output_path: Output file path
    """
    env_lines = [
        "# AWS Services Configuration - Production",
        "# Generated by aws_services_config.py",
        "",
        f"# AWS Region",
        f"AWS_REGION={config_summary['region']}",
        "",
    ]
    
    # Cognito configuration
    if 'cognito' in config_summary['services']:
        cognito = config_summary['services']['cognito']
        env_lines.extend([
            "# Amazon Cognito Configuration",
            f"COGNITO_USER_POOL_ID={cognito['user_pool_id']}",
            "COGNITO_CLIENT_ID=<from_aws_console>",
            "COGNITO_CLIENT_SECRET=<from_aws_console>",
            f"COGNITO_REGION={config_summary['region']}",
            ""
        ])
    
    # SNS configuration
    if 'sns' in config_summary['services']:
        sns = config_summary['services']['sns']
        env_lines.extend([
            "# Amazon SNS Configuration",
            "SNS_ENABLED=true",
        ])
        for topic_type, topic_arn in sns['topics'].items():
            env_var_name = f"SNS_TOPIC_ARN_{topic_type.upper()}"
            env_lines.append(f"{env_var_name}={topic_arn}")
        env_lines.append("")
    
    # ElastiCache configuration
    if 'elasticache' in config_summary['services']:
        cache = config_summary['services']['elasticache']
        env_lines.extend([
            "# Redis ElastiCache Configuration",
            f"REDIS_HOST={cache['endpoint']}",
            f"REDIS_PORT={cache['port']}",
            "REDIS_DB=0",
            "CACHE_ENABLED=true",
            ""
        ])
    
    # Bedrock configuration
    if 'bedrock' in config_summary['services']:
        env_lines.extend([
            "# Amazon Bedrock Configuration",
            "# Bedrock access configured via IAM role",
            "# Models: anthropic.claude-v2, anthropic.claude-instant-v1",
            ""
        ])
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(env_lines))
    
    logger.info(f"Environment configuration written to {output_path}")


if __name__ == "__main__":
    """
    Example usage for AWS services configuration
    """
    import os
    
    # Initialize configurator
    configurator = AWSServicesConfigurator(
        region=os.getenv('AWS_REGION', 'ap-south-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    print("AWS Services Configuration Tool")
    print("=" * 50)
    print("\nThis tool helps configure AWS services for production deployment.")
    print("\nServices to configure:")
    print("1. Amazon Cognito User Pool (authentication)")
    print("2. Amazon Bedrock (AI/ML inference)")
    print("3. Amazon SNS (notifications)")
    print("4. Redis ElastiCache (caching)")
    print("\nNote: Ensure you have appropriate AWS permissions before running.")
