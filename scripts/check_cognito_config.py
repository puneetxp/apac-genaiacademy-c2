#!/usr/bin/env python3
"""
Check Cognito User Pool Client Configuration
Shows which authentication flows are currently enabled
"""

import boto3
import os
import sys
from pathlib import Path

# Load environment variables from .env file
env_file = Path(__file__).parent.parent / "python" / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Get configuration from environment
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
REGION = os.getenv('COGNITO_REGION', 'ap-south-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

def check_cognito_config():
    """Check Cognito User Pool Client configuration"""
    
    print("🔍 Checking Cognito Configuration...")
    print(f"   User Pool ID: {USER_POOL_ID}")
    print(f"   Client ID: {CLIENT_ID}")
    print(f"   Region: {REGION}")
    print()
    
    try:
        # Create Cognito client
        cognito = boto3.client(
            'cognito-idp',
            region_name=REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Get User Pool Client details
        response = cognito.describe_user_pool_client(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID
        )
        
        client = response['UserPoolClient']
        auth_flows = client.get('ExplicitAuthFlows', [])
        
        print("📋 Current Authentication Flows:")
        print()
        
        # Check each required auth flow
        required_flows = {
            'ALLOW_USER_PASSWORD_AUTH': 'Username/Password Authentication',
            'ALLOW_REFRESH_TOKEN_AUTH': 'Refresh Token Authentication',
            'ALLOW_USER_SRP_AUTH': 'Secure Remote Password (SRP) Authentication'
        }
        
        all_enabled = True
        for flow, description in required_flows.items():
            enabled = flow in auth_flows
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            print(f"   {status}  {flow}")
            print(f"              {description}")
            print()
            
            if not enabled:
                all_enabled = False
        
        print()
        print("=" * 70)
        print()
        
        if all_enabled:
            print("✅ SUCCESS! All required authentication flows are enabled.")
            print()
            print("Your sign-in should work now. Test with:")
            print()
            print('   curl -X POST "http://localhost:8000/auth/signin" \\')
            print('     -H "Content-Type: application/json" \\')
            print('     -d \'{"username": "puneetxp", "password": "your-password"}\'')
            print()
            return 0
        else:
            print("❌ PROBLEM: USER_PASSWORD_AUTH is not enabled!")
            print()
            print("To fix this:")
            print()
            print("1. Go to AWS Console → Cognito → User Pools")
            print(f"2. Click on user pool: {USER_POOL_ID}")
            print("3. Go to 'App integration' tab")
            print(f"4. Click on app client: {CLIENT_ID}")
            print("5. Click 'Edit' in Authentication flows section")
            print("6. Check the box: ✅ ALLOW_USER_PASSWORD_AUTH")
            print("7. Also check: ✅ ALLOW_REFRESH_TOKEN_AUTH")
            print("8. Also check: ✅ ALLOW_USER_SRP_AUTH")
            print("9. Click 'Save changes'")
            print()
            print("Or see: FIX_COGNITO_NOW.md for detailed instructions")
            print()
            return 1
            
    except Exception as e:
        print(f"❌ Error checking Cognito configuration: {e}")
        print()
        print("This might be because:")
        print("1. AWS credentials don't have cognito-idp:DescribeUserPoolClient permission")
        print("2. User Pool ID or Client ID is incorrect")
        print("3. Network connectivity issues")
        print()
        print("You can still fix this manually via AWS Console.")
        print("See: FIX_COGNITO_NOW.md for instructions")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(check_cognito_config())
