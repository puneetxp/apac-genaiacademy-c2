#!/usr/bin/env python3
"""
Update existing Cognito user with username custom attribute
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

def update_user_username(email, username):
    """Update user's custom:username attribute"""
    print(f"\n=== Updating User: {email} ===")
    print(f"Setting custom:username = {username}")
    
    try:
        cognito_client = boto3.client(
            'cognito-idp',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Update user attributes
        response = cognito_client.admin_update_user_attributes(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=email,
            UserAttributes=[
                {
                    'Name': 'custom:username',
                    'Value': username
                }
            ]
        )
        
        print(f"✓ Successfully updated user {email}")
        print(f"  custom:username = {username}")
        
        # Verify the update
        print(f"\n=== Verifying Update ===")
        user_info = cognito_client.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=email
        )
        
        print(f"✓ User Attributes:")
        for attr in user_info['UserAttributes']:
            print(f"  - {attr['Name']}: {attr['Value']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to update user: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Update Cognito User - Add Username Attribute")
    print("=" * 60)
    
    # Update the existing user
    email = "puneetsharma9@hotmail.com"
    username = "puneetxp"
    
    success = update_user_username(email, username)
    
    if success:
        print("\n" + "=" * 60)
        print("✓ User updated successfully!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Sign in with username or email")
        print("2. The username will be visible in Cognito Console")
        print("3. New users will automatically get this attribute")
    else:
        print("\n" + "=" * 60)
        print("✗ Update failed!")
        print("=" * 60)
        print("\nPossible issues:")
        print("1. Custom attribute not yet added to User Pool (run Terraform apply first)")
        print("2. AWS credentials invalid")
        print("3. User not found")
