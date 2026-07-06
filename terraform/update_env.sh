#!/bin/bash

# Script to update .env file with Terraform outputs
# Usage: ./update_env.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR"
ENV_FILE="$SCRIPT_DIR/../python/.env"

echo "🔧 Updating .env file with Terraform outputs..."

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Check if terraform is initialized
if [ ! -d "$TERRAFORM_DIR/.terraform" ]; then
    echo "❌ Error: Terraform not initialized. Run 'terraform init' first."
    exit 1
fi

# Backup .env file
BACKUP_FILE="$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
cp "$ENV_FILE" "$BACKUP_FILE"
echo "📦 Backup created: $BACKUP_FILE"

# Get Terraform outputs
cd "$TERRAFORM_DIR"

echo "📥 Fetching Terraform outputs..."

COGNITO_USER_POOL_ID=$(terraform output -raw cognito_user_pool_id 2>/dev/null || echo "")
COGNITO_CLIENT_ID=$(terraform output -raw cognito_client_id 2>/dev/null || echo "")
COGNITO_CLIENT_SECRET=$(terraform output -raw cognito_client_secret 2>/dev/null || echo "")
COGNITO_REGION=$(terraform output -raw cognito_region 2>/dev/null || echo "ap-south-1")

# Check if outputs are available
if [ -z "$COGNITO_USER_POOL_ID" ] || [ -z "$COGNITO_CLIENT_ID" ] || [ -z "$COGNITO_CLIENT_SECRET" ]; then
    echo "❌ Error: Could not fetch Terraform outputs. Make sure 'terraform apply' has been run."
    echo "   Run: cd terraform && terraform apply"
    exit 1
fi

# Update .env file
echo "✏️  Updating Cognito configuration..."

# Use sed to update values (macOS compatible)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|^COGNITO_USER_POOL_ID=.*|COGNITO_USER_POOL_ID=$COGNITO_USER_POOL_ID|" "$ENV_FILE"
    sed -i '' "s|^COGNITO_CLIENT_ID=.*|COGNITO_CLIENT_ID=$COGNITO_CLIENT_ID|" "$ENV_FILE"
    sed -i '' "s|^COGNITO_CLIENT_SECRET=.*|COGNITO_CLIENT_SECRET=$COGNITO_CLIENT_SECRET|" "$ENV_FILE"
    sed -i '' "s|^COGNITO_REGION=.*|COGNITO_REGION=$COGNITO_REGION|" "$ENV_FILE"
else
    # Linux
    sed -i "s|^COGNITO_USER_POOL_ID=.*|COGNITO_USER_POOL_ID=$COGNITO_USER_POOL_ID|" "$ENV_FILE"
    sed -i "s|^COGNITO_CLIENT_ID=.*|COGNITO_CLIENT_ID=$COGNITO_CLIENT_ID|" "$ENV_FILE"
    sed -i "s|^COGNITO_CLIENT_SECRET=.*|COGNITO_CLIENT_SECRET=$COGNITO_CLIENT_SECRET|" "$ENV_FILE"
    sed -i "s|^COGNITO_REGION=.*|COGNITO_REGION=$COGNITO_REGION|" "$ENV_FILE"
fi

echo ""
echo "✅ .env file updated successfully!"
echo ""
echo "📋 New Cognito Configuration:"
echo "   COGNITO_USER_POOL_ID=$COGNITO_USER_POOL_ID"
echo "   COGNITO_CLIENT_ID=$COGNITO_CLIENT_ID"
echo "   COGNITO_CLIENT_SECRET=***${COGNITO_CLIENT_SECRET: -8}"
echo "   COGNITO_REGION=$COGNITO_REGION"
echo ""
echo "🔄 Restart your backend server to apply changes:"
echo "   cd ../python"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "💾 Backup saved to: $BACKUP_FILE"
