#!/bin/bash

# Fix Cognito USER_PASSWORD_AUTH Flow
# This script enables the USER_PASSWORD_AUTH authentication flow for the Cognito User Pool Client

set -e

echo "🔧 Fixing Cognito Authentication Flow..."
echo ""

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../python/.env"

if [ -f "$ENV_FILE" ]; then
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
else
    echo "❌ Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI is not installed"
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ Error: AWS credentials not found in .env file"
    exit 1
fi

echo "📋 Current Configuration:"
echo "   User Pool ID: $COGNITO_USER_POOL_ID"
echo "   Client ID: $COGNITO_CLIENT_ID"
echo "   Region: $COGNITO_REGION"
echo ""

# Update the User Pool Client to enable USER_PASSWORD_AUTH
echo "🔄 Updating Cognito User Pool Client..."
aws cognito-idp update-user-pool-client \
  --user-pool-id "$COGNITO_USER_POOL_ID" \
  --client-id "$COGNITO_CLIENT_ID" \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH ALLOW_USER_SRP_AUTH \
  --region "$COGNITO_REGION" \
  > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Successfully enabled USER_PASSWORD_AUTH flow"
    echo ""
    echo "🎉 Authentication flow fixed!"
    echo ""
    echo "You can now sign in with username/password."
    echo ""
    echo "Test with:"
    echo "  curl -X POST 'http://localhost:8000/auth/signin' \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"username\": \"puneetxp\", \"password\": \"your-password\"}'"
else
    echo "❌ Failed to update Cognito User Pool Client"
    echo "Please check your AWS credentials and permissions"
    exit 1
fi
