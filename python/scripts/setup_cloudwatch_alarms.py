"""
CloudWatch Alarms Setup Script
Task 20.4: Configure alerting

Sets up comprehensive CloudWatch alarms with SNS notifications for:
- API errors and failures (> 5% error rate)
- Performance degradation (response time > 3 seconds)
- Cost monitoring (Bedrock, RDS, EC2)
- Uptime monitoring

Validates: Requirements (Non-Functional - Reliability)
"""

import boto3
import sys
import os
import logging
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.alerting import AlertingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlarmSetupManager:
    """
    Manages complete alarm setup process
    """
    
    def __init__(self, region: str = "ap-south-1"):
        """
        Initialize alarm setup manager
        
        Args:
            region: AWS region
        """
        self.region = region
        self.alerting = AlertingService(region=region)
        self.namespace = "RuralFarmingPlatform"
    
    def setup_sns_topics(
        self,
        critical_emails: List[str],
        warning_emails: List[str],
        sms_numbers: List[str] = None
    ) -> Dict[str, str]:
        """
        Set up SNS topics and subscriptions
        
        Args:
            critical_emails: Email addresses for critical alerts
            warning_emails: Email addresses for warning alerts
            sms_numbers: Phone numbers for SMS alerts (optional)
            
        Returns:
            Dictionary with topic ARNs
        """
        logger.info("=" * 60)
        logger.info("Setting up SNS topics...")
        logger.info("=" * 60)
        
        topics = {}
        
        # Create critical alerts topic
        logger.info("Creating critical alerts topic...")
        critical_topic_arn = self.alerting.create_sns_topic(
            topic_name=f"{self.namespace}-Critical-Alerts",
            display_name="Rural Farming Platform - Critical Alerts"
        )
        
        if critical_topic_arn:
            topics['critical'] = critical_topic_arn
            logger.info(f"✓ Critical topic created: {critical_topic_arn}")
            
            # Subscribe emails
            for email in critical_emails:
                if self.alerting.subscribe_email(critical_topic_arn, email):
                    logger.info(f"  ✓ Subscribed email: {email}")
                else:
                    logger.error(f"  ✗ Failed to subscribe: {email}")
            
            # Subscribe SMS numbers
            if sms_numbers:
                for phone in sms_numbers:
                    if self.alerting.subscribe_sms(critical_topic_arn, phone):
                        logger.info(f"  ✓ Subscribed SMS: {phone}")
                    else:
                        logger.error(f"  ✗ Failed to subscribe SMS: {phone}")
        else:
            logger.error("✗ Failed to create critical topic")
        
        # Create warning alerts topic
        logger.info("\nCreating warning alerts topic...")
        warning_topic_arn = self.alerting.create_sns_topic(
            topic_name=f"{self.namespace}-Warning-Alerts",
            display_name="Rural Farming Platform - Warning Alerts"
        )
        
        if warning_topic_arn:
            topics['warning'] = warning_topic_arn
            logger.info(f"✓ Warning topic created: {warning_topic_arn}")
            
            # Subscribe emails
            for email in warning_emails:
                if self.alerting.subscribe_email(warning_topic_arn, email):
                    logger.info(f"  ✓ Subscribed email: {email}")
                else:
                    logger.error(f"  ✗ Failed to subscribe: {email}")
        else:
            logger.error("✗ Failed to create warning topic")
        
        logger.info("")
        logger.info("⚠️  IMPORTANT: Check your email and confirm SNS subscriptions!")
        logger.info("")
        
        return topics
    
    def setup_all_alarms(
        self,
        critical_topic_arn: str,
        warning_topic_arn: str
    ) -> Dict[str, bool]:
        """
        Set up all CloudWatch alarms
        
        Args:
            critical_topic_arn: SNS topic ARN for critical alerts
            warning_topic_arn: SNS topic ARN for warning alerts
            
        Returns:
            Dictionary with alarm setup results
        """
        logger.info("=" * 60)
        logger.info("Setting up CloudWatch alarms...")
        logger.info("=" * 60)
        
        results = self.alerting.setup_all_alarms(
            critical_topic_arn=critical_topic_arn,
            warning_topic_arn=warning_topic_arn
        )
        
        # Print results
        logger.info("")
        logger.info("Alarm Setup Results:")
        logger.info("-" * 60)
        
        for alarm_name, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"{alarm_name:30s} {status}")
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        logger.info("-" * 60)
        logger.info(f"Total: {success_count}/{total_count} alarms created successfully")
        logger.info("")
        
        return results
    
    def verify_setup(self) -> Dict[str, Any]:
        """
        Verify alarm setup
        
        Returns:
            Verification results
        """
        logger.info("=" * 60)
        logger.info("Verifying alarm setup...")
        logger.info("=" * 60)
        
        alarms = self.alerting.list_alarms()
        
        logger.info(f"\nFound {len(alarms)} alarms:")
        logger.info("-" * 60)
        
        for alarm in alarms:
            name = alarm['AlarmName']
            state = alarm['StateValue']
            description = alarm.get('AlarmDescription', 'N/A')
            
            state_icon = {
                'OK': '✓',
                'ALARM': '⚠️',
                'INSUFFICIENT_DATA': '?'
            }.get(state, '?')
            
            logger.info(f"{state_icon} {name}")
            logger.info(f"  State: {state}")
            logger.info(f"  Description: {description}")
            logger.info("")
        
        return {
            'total_alarms': len(alarms),
            'alarms': alarms
        }
    
    def print_summary(
        self,
        topics: Dict[str, str],
        alarm_results: Dict[str, bool]
    ):
        """
        Print setup summary
        
        Args:
            topics: SNS topic ARNs
            alarm_results: Alarm setup results
        """
        logger.info("=" * 60)
        logger.info("SETUP COMPLETE")
        logger.info("=" * 60)
        
        logger.info("\n📧 SNS Topics:")
        logger.info("-" * 60)
        for topic_type, arn in topics.items():
            logger.info(f"{topic_type.upper():15s} {arn}")
        
        logger.info("\n🔔 Alarms Created:")
        logger.info("-" * 60)
        success_count = sum(1 for success in alarm_results.values() if success)
        total_count = len(alarm_results)
        logger.info(f"Total: {success_count}/{total_count} alarms")
        
        logger.info("\n📊 View in AWS Console:")
        logger.info("-" * 60)
        logger.info(f"Alarms:  https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#alarmsV2:")
        logger.info(f"SNS:     https://{self.region}.console.aws.amazon.com/sns/v3/home?region={self.region}#/topics")
        
        logger.info("\n⚠️  NEXT STEPS:")
        logger.info("-" * 60)
        logger.info("1. Check your email and confirm SNS subscriptions")
        logger.info("2. Test alarms by triggering conditions (optional)")
        logger.info("3. Adjust thresholds based on actual traffic patterns")
        logger.info("4. Set up additional alarms for RDS and EC2 if needed")
        
        logger.info("\n" + "=" * 60)


def main():
    """
    Main function to set up CloudWatch alarms
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Set up CloudWatch alarms with SNS notifications'
    )
    parser.add_argument(
        '--region',
        default='ap-south-1',
        help='AWS region (default: ap-south-1)'
    )
    parser.add_argument(
        '--critical-emails',
        nargs='+',
        required=True,
        help='Email addresses for critical alerts'
    )
    parser.add_argument(
        '--warning-emails',
        nargs='+',
        help='Email addresses for warning alerts (defaults to critical emails)'
    )
    parser.add_argument(
        '--sms-numbers',
        nargs='+',
        help='Phone numbers for SMS alerts (E.164 format: +919876543210)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify existing alarms, do not create new ones'
    )
    
    args = parser.parse_args()
    
    # Use critical emails for warnings if not specified
    warning_emails = args.warning_emails or args.critical_emails
    
    # Initialize manager
    manager = AlarmSetupManager(region=args.region)
    
    if args.verify_only:
        # Only verify existing setup
        manager.verify_setup()
        return
    
    # Set up SNS topics
    topics = manager.setup_sns_topics(
        critical_emails=args.critical_emails,
        warning_emails=warning_emails,
        sms_numbers=args.sms_numbers
    )
    
    if not topics.get('critical') or not topics.get('warning'):
        logger.error("Failed to create SNS topics. Aborting.")
        sys.exit(1)
    
    # Set up alarms
    alarm_results = manager.setup_all_alarms(
        critical_topic_arn=topics['critical'],
        warning_topic_arn=topics['warning']
    )
    
    # Verify setup
    manager.verify_setup()
    
    # Print summary
    manager.print_summary(topics, alarm_results)


if __name__ == "__main__":
    main()
