"""
CloudWatch Dashboard Setup Script
Task 20.3: Set up application monitoring

Creates custom CloudWatch dashboards for:
- API Performance (requests, errors, response times)
- Business Metrics (user registrations, strategy generations, marketplace listings)
- Bedrock Usage (API calls, costs, token usage)
- Infrastructure (database, Redis, system resources)

Validates: Requirements (Non-Functional - Reliability)
"""

import boto3
from botocore.exceptions import ClientError
import json
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudWatchDashboardManager:
    """
    Manages CloudWatch dashboard creation and updates
    """
    
    def __init__(self, region: str = "ap-south-1"):
        """
        Initialize dashboard manager
        
        Args:
            region: AWS region
        """
        self.region = region
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.namespace = "RuralFarmingPlatform"
    
    def create_api_performance_dashboard(self) -> bool:
        """
        Create API Performance dashboard
        
        Widgets:
        - API request count by endpoint
        - API error rate
        - API response time (p50, p95, p99)
        - Status code distribution
        
        Returns:
            True if successful
        """
        dashboard_name = "RuralFarming-API-Performance"
        
        dashboard_body = {
            "widgets": [
                # API Requests by Endpoint
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "APIRequests", {"stat": "Sum"}]
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "API Requests (Total)",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 0,
                    "y": 0
                },
                # API Error Rate
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "APIErrors", {"stat": "Sum", "label": "Errors"}],
                            [self.namespace, "APIRequests", {"stat": "Sum", "label": "Total Requests"}]
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "API Error Rate",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 12,
                    "y": 0
                },
                # API Response Time (Percentiles)
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "APIResponseTime", {"stat": "p50", "label": "p50"}],
                            ["...", {"stat": "p95", "label": "p95"}],
                            ["...", {"stat": "p99", "label": "p99"}],
                            ["...", {"stat": "Average", "label": "Average"}]
                        ],
                        "period": 300,
                        "region": self.region,
                        "title": "API Response Time (ms)",
                        "yAxis": {"left": {"label": "Milliseconds"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 0,
                    "y": 6
                },
                # Status Code Distribution
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "APIRequests", "StatusCode", "200", {"stat": "Sum", "label": "200 OK"}],
                            ["...", "201", {"stat": "Sum", "label": "201 Created"}],
                            ["...", "400", {"stat": "Sum", "label": "400 Bad Request"}],
                            ["...", "401", {"stat": "Sum", "label": "401 Unauthorized"}],
                            ["...", "404", {"stat": "Sum", "label": "404 Not Found"}],
                            ["...", "500", {"stat": "Sum", "label": "500 Server Error"}]
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Status Code Distribution",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": True
                    },
                    "width": 12,
                    "height": 6,
                    "x": 12,
                    "y": 6
                }
            ]
        }
        
        return self._create_dashboard(dashboard_name, dashboard_body)
    
    def create_business_metrics_dashboard(self) -> bool:
        """
        Create Business Metrics dashboard
        
        Widgets:
        - User registrations
        - Strategy generations by state
        - Marketplace listings by crop type
        - Buyer interests
        
        Returns:
            True if successful
        """
        dashboard_name = "RuralFarming-Business-Metrics"
        
        dashboard_body = {
            "widgets": [
                # User Registrations
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "UserRegistrations", {"stat": "Sum"}]
                        ],
                        "period": 3600,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "User Registrations (Hourly)",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 0,
                    "y": 0
                },
                # Strategy Generations
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "StrategyGenerations", {"stat": "Sum"}]
                        ],
                        "period": 3600,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Annual Strategy Generations (Hourly)",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 12,
                    "y": 0
                },
                # Marketplace Listings
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "MarketplaceListings", "Action", "created", {"stat": "Sum", "label": "Created"}],
                            ["...", "updated", {"stat": "Sum", "label": "Updated"}],
                            ["...", "sold", {"stat": "Sum", "label": "Sold"}]
                        ],
                        "period": 3600,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Marketplace Listings Activity (Hourly)",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": True
                    },
                    "width": 12,
                    "height": 6,
                    "x": 0,
                    "y": 6
                },
                # Buyer Interests
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "BuyerInterests", {"stat": "Sum"}]
                        ],
                        "period": 3600,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Buyer Interests (Hourly)",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 12,
                    "y": 6
                }
            ]
        }
        
        return self._create_dashboard(dashboard_name, dashboard_body)
    
    def create_bedrock_usage_dashboard(self) -> bool:
        """
        Create Bedrock Usage dashboard
        
        Widgets:
        - Bedrock API requests
        - Bedrock response time
        - Token usage (input/output)
        - Estimated costs
        
        Returns:
            True if successful
        """
        dashboard_name = "RuralFarming-Bedrock-Usage"
        
        dashboard_body = {
            "widgets": [
                # Bedrock API Requests
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "BedrockRequests", {"stat": "Sum"}]
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Bedrock API Requests",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 0,
                    "y": 0
                },
                # Bedrock Response Time
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "BedrockResponseTime", {"stat": "Average", "label": "Average"}],
                            ["...", {"stat": "p95", "label": "p95"}],
                            ["...", {"stat": "p99", "label": "p99"}]
                        ],
                        "period": 300,
                        "region": self.region,
                        "title": "Bedrock Response Time (ms)",
                        "yAxis": {"left": {"label": "Milliseconds"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 12,
                    "y": 0
                },
                # Token Usage
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "BedrockInputTokens", {"stat": "Sum", "label": "Input Tokens"}],
                            [self.namespace, "BedrockOutputTokens", {"stat": "Sum", "label": "Output Tokens"}]
                        ],
                        "period": 3600,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Bedrock Token Usage (Hourly)",
                        "yAxis": {"left": {"label": "Tokens"}},
                        "view": "timeSeries",
                        "stacked": True
                    },
                    "width": 12,
                    "height": 6,
                    "x": 0,
                    "y": 6
                },
                # Estimated Costs
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "BedrockCost", {"stat": "Sum"}]
                        ],
                        "period": 3600,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Bedrock Estimated Costs (USD, Hourly)",
                        "yAxis": {"left": {"label": "USD"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 12,
                    "y": 6
                }
            ]
        }
        
        return self._create_dashboard(dashboard_name, dashboard_body)
    
    def create_infrastructure_dashboard(self) -> bool:
        """
        Create Infrastructure dashboard
        
        Widgets:
        - Database query performance
        - Cache hit/miss rate
        - Function invocations and duration
        
        Returns:
            True if successful
        """
        dashboard_name = "RuralFarming-Infrastructure"
        
        dashboard_body = {
            "widgets": [
                # Database Queries
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "DatabaseQueries", {"stat": "Sum"}]
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Database Queries",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 0,
                    "y": 0
                },
                # Database Query Time
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "DatabaseQueryTime", {"stat": "Average", "label": "Average"}],
                            ["...", {"stat": "p95", "label": "p95"}]
                        ],
                        "period": 300,
                        "region": self.region,
                        "title": "Database Query Time (ms)",
                        "yAxis": {"left": {"label": "Milliseconds"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 12,
                    "y": 0
                },
                # Cache Operations
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "CacheOperations", "Operation", "hit", {"stat": "Sum", "label": "Cache Hits"}],
                            ["...", "miss", {"stat": "Sum", "label": "Cache Misses"}],
                            ["...", "set", {"stat": "Sum", "label": "Cache Sets"}]
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Cache Operations",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": True
                    },
                    "width": 12,
                    "height": 6,
                    "x": 0,
                    "y": 6
                },
                # Function Invocations
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            [self.namespace, "FunctionInvocations", {"stat": "Sum"}]
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": self.region,
                        "title": "Function Invocations",
                        "yAxis": {"left": {"label": "Count"}},
                        "view": "timeSeries",
                        "stacked": False
                    },
                    "width": 12,
                    "height": 6,
                    "x": 12,
                    "y": 6
                }
            ]
        }
        
        return self._create_dashboard(dashboard_name, dashboard_body)
    
    def _create_dashboard(self, dashboard_name: str, dashboard_body: Dict[str, Any]) -> bool:
        """
        Create or update CloudWatch dashboard
        
        Args:
            dashboard_name: Dashboard name
            dashboard_body: Dashboard configuration
            
        Returns:
            True if successful
        """
        try:
            self.cloudwatch.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            logger.info(f"Dashboard created/updated: {dashboard_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to create dashboard {dashboard_name}: {e}")
            return False
    
    def create_all_dashboards(self) -> Dict[str, bool]:
        """
        Create all dashboards
        
        Returns:
            Dictionary with dashboard names and creation status
        """
        results = {
            "api_performance": self.create_api_performance_dashboard(),
            "business_metrics": self.create_business_metrics_dashboard(),
            "bedrock_usage": self.create_bedrock_usage_dashboard(),
            "infrastructure": self.create_infrastructure_dashboard()
        }
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        logger.info(f"Dashboard creation complete: {success_count}/{total_count} successful")
        
        return results


def main():
    """
    Main function to create all CloudWatch dashboards
    """
    import os
    
    # Get AWS region from environment or use default
    region = os.getenv('AWS_REGION', 'ap-south-1')
    
    logger.info("=" * 60)
    logger.info("CloudWatch Dashboard Setup")
    logger.info("=" * 60)
    logger.info(f"Region: {region}")
    logger.info(f"Namespace: RuralFarmingPlatform")
    logger.info("")
    
    # Create dashboard manager
    manager = CloudWatchDashboardManager(region=region)
    
    # Create all dashboards
    logger.info("Creating CloudWatch dashboards...")
    results = manager.create_all_dashboards()
    
    # Print results
    logger.info("")
    logger.info("Dashboard Creation Results:")
    logger.info("-" * 60)
    for dashboard, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        logger.info(f"{dashboard:30s} {status}")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("Dashboard setup complete!")
    logger.info("View dashboards in AWS Console:")
    logger.info(f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
