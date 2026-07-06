#!/bin/bash

# Script to update .env file with new Cognito credentials from Terraform

echo "🔄 Extracting Cognito credentials from Terraform..."

# Get values from Terraform
USER_POOL_ID=$(terraform output -raw cognito_user_pool_id 2>/dev/null)
CLIENT_ID=$(terraform output -raw cognito_client_id 2>/dev/null)
CLIENT_SECRET=$(terraform output -raw cognito_client_secret 2>/dev/null)
REGION=$(terraform output -raw cognito_region 2>/dev/null)

if [ -z "$USER_POOL_ID" ] || [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    echo "❌ Error: Could not get Terraform outputs"
    echo "Make sure Terraform apply completed successfully"
    exit 1
fi

echo "✅ Got credentials from Terraform"
echo ""
echo "📝 Updating ../python/.env file..."

# Backup existing .env
cp ../python/.env ../python/.env.backup.$(date +%Y%m%d_%H%M%S)

# Update .env file
sed -i.tmp "s|^COGNITO_USER_POOL_ID=.*|COGNITO_USER_POOL_ID=$USER_POOL_ID|" ../python/.env
sed -i.tmp "s|^COGNITO_CLIENT_ID=.*|COGNITO_CLIENT_ID=$CLIENT_ID|" ../python/.env
sed -i.tmp "s|^COGNITO_CLIENT_SECRET=.*|COGNITO_CLIENT_SECRET=$CLIENT_SECRET|" ../python/.env
sed -i.tmp "s|^COGNITO_REGION=.*|COGNITO_REGION=$REGION|" ../python/.env

# Remove temp file
rm -f ../python/.env.tmp

echo "✅ Updated .env file with new Cognito credentials"
echo ""
echo "📋 New values:"
echo "  COGNITO_USER_POOL_ID=$USER_POOL_ID"
echo "  COGNITO_CLIENT_ID=$CLIENT_ID"
echo "  COGNITO_CLIENT_SECRET=$CLIENT_SECRET"
echo "  COGNITO_REGION=$REGION"
echo ""
echo "🔄 Please restart your FastAPI server for changes to take effect"
echo ""
echo "💾 Backup saved to: ../python/.env.backup.$(date +%Y%m%d_%H%M%S)"
