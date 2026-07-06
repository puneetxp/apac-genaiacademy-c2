#!/usr/bin/env python3
"""
Check AWS Cognito and SES status for email delivery issues
"""

import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')

def check_ses_status():
    """Check if SES is in sandbox mode"""
    print("\n=== Checking AWS SES Status ===")
    try:
        ses_client = boto3.client(
            'ses',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Get account sending status
        response = ses_client.get_account_sending_enabled()
        print(f"✓ SES Sending Enabled: {response.get('Enabled', False)}")
        
        # Check if in sandbox
        try:
            quota = ses_client.get_send_quota()
            print(f"✓ SES Send Quota:")
            print(f"  - Max 24 Hour Send: {quota['Max24HourSend']}")
            print(f"  - Max Send Rate: {quota['MaxSendRate']}")
            print(f"  - Sent Last 24 Hours: {quota['SentLast24Hours']}")
            
            # If Max24HourSend is 200, account is in sandbox
            if quota['Max24HourSend'] == 200:
                print("\n⚠️  WARNING: SES is in SANDBOX MODE")
                print("   You can only send emails to verified addresses.")
                print("   To fix: Request production access in AWS SES Console")
            else:
                print("\n✓ SES is in PRODUCTION MODE")
        except Exception as e:
            print(f"✗ Could not check SES quota: {e}")
        
        # List verified email addresses
        try:
            identities = ses_client.list_identities(IdentityType='EmailAddress')
            print(f"\n✓ Verified Email Addresses in SES:")
            if identities['Identities']:
                for email in identities['Identities']:
                    print(f"  - {email}")
            else:
                print("  - None (you need to verify emails in sandbox mode)")
        except Exception as e:
            print(f"✗ Could not list identities: {e}")
            
    except Exception as e:
        print(f"✗ SES check failed: {e}")


def check_cognito_user_status(username):
    """Check Cognito user status"""
    print(f"\n=== Checking Cognito User: {username} ===")
    try:
        cognito_client = boto3.client(
            'cognito-idp',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Get user details
        response = cognito_client.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username
        )
        
        print(f"✓ User Status: {response['UserStatus']}")
        print(f"✓ User Enabled: {response['Enabled']}")
        
        print(f"\n✓ User Attributes:")
        for attr in response['UserAttributes']:
            name = attr['Name']
            value = attr['Value']
            print(f"  - {name}: {value}")
        
        # Check email verification
        email_verified = False
        for attr in response['UserAttributes']:
            if attr['Name'] == 'email_verified':
                email_verified = attr['Value'] == 'true'
                break
        
        if not email_verified:
            print("\n⚠️  WARNING: Email is NOT verified in Cognito")
            print("   This might prevent password reset emails from being sent")
        else:
            print("\n✓ Email is verified in Cognito")
            
    except Exception as e:
        print(f"✗ Cognito user check failed: {e}")


def check_cognito_pool_config():
    """Check Cognito User Pool email configuration"""
    print(f"\n=== Checking Cognito User Pool Configuration ===")
    try:
        cognito_client = boto3.client(
            'cognito-idp',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        response = cognito_client.describe_user_pool(
            UserPoolId=COGNITO_USER_POOL_ID
        )
        
        pool = response['UserPool']
        
        # Check email configuration
        email_config = pool.get('EmailConfiguration', {})
        print(f"✓ Email Configuration:")
        print(f"  - Source ARN: {email_config.get('SourceArn', 'Default Cognito Email')}")
        print(f"  - Reply To: {email_config.get('ReplyToEmailAddress', 'N/A')}")
        print(f"  - From: {email_config.get('From', 'N/A')}")
        print(f"  - Email Sending Account: {email_config.get('EmailSendingAccount', 'COGNITO_DEFAULT')}")
        
        if email_config.get('EmailSendingAccount') == 'COGNITO_DEFAULT':
            print("\n⚠️  Using Cognito Default Email (limited to 50 emails/day)")
            print("   Consider configuring SES for production use")
        
    except Exception as e:
        print(f"✗ Cognito pool config check failed: {e}")


def admin_reset_password(username):
    """Admin reset password (bypass email)"""
    print(f"\n=== Admin Password Reset for {username} ===")
    try:
        cognito_client = boto3.client(
            'cognito-idp',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Set temporary password
        temp_password = "TempPass123!"
        
        response = cognito_client.admin_set_user_password(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
            Password=temp_password,
            Permanent=False  # User must change on first login
        )
        
        print(f"✓ Temporary password set successfully")
        print(f"✓ Temporary Password: {temp_password}")
        print(f"✓ User must change password on next login")
        
        return temp_password
        
    except Exception as e:
        print(f"✗ Admin password reset failed: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("AWS Cognito & SES Status Check")
    print("=" * 60)
    
    # Check SES status
    check_ses_status()
    
    # Check Cognito pool configuration
    check_cognito_pool_config()
    
    # Check specific user
    username = input("\nEnter username to check (or press Enter to skip): ").strip()
    if username:
        check_cognito_user_status(username)
        
        # Offer admin reset
        reset = input("\nDo you want to admin-reset password for this user? (yes/no): ").strip().lower()
        if reset == 'yes':
            temp_pass = admin_reset_password(username)
            if temp_pass:
                print(f"\n✓ User can now login with:")
                print(f"  Username: {username}")
                print(f"  Password: {temp_pass}")
                print(f"  (Must change password after login)")
    
    print("\n" + "=" * 60)
    print("Check complete!")
    print("=" * 60)
