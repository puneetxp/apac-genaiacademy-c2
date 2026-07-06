#!/bin/bash

# Create New Cognito User Pool with Terraform
# This script will create a new Cognito User Pool with correct auth flows

set -e

echo "🚀 Creating New Cognito User Pool..."
echo ""

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Error: Terraform is not installed"
    echo "Install from: https://www.terraform.io/downloads"
    exit 1
fi

# Check if AWS credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️  AWS credentials not found in environment"
    echo "Loading from ../python/.env..."
    
    if [ -f "../python/.env" ]; then
        export $(cat ../python/.env | grep AWS_ACCESS_KEY_ID | xargs)
        export $(cat ../python/.env | grep AWS_SECRET_ACCESS_KEY | xargs)
        export $(cat ../python/.env | grep AWS_REGION | xargs)
    else
        echo "❌ Error: .env file not found"
        exit 1
    fi
fi

echo "📋 Configuration:"
echo "   AWS Region: ${AWS_REGION:-ap-south-1}"
echo "   Project: cropsense-ai"
echo "   Environment: development"
echo ""

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init -reconfigure

if [ $? -ne 0 ]; then
    echo "❌ Terraform initialization failed"
    exit 1
fi

echo ""
echo "📝 Planning deployment..."
terraform plan -out=tfplan

if [ $? -ne 0 ]; then
    echo "❌ Terraform plan failed"
    exit 1
fi

echo ""
echo "🎯 Ready to create resources!"
echo ""
echo "This will create:"
echo "  - Cognito User Pool with USER_PASSWORD_AUTH enabled"
echo "  - Cognito App Client with correct auth flows"
echo "  - SNS topics for notifications"
echo "  - ElastiCache Redis cluster"
echo "  - CloudWatch alarms"
echo ""
read -p "Do you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled"
    rm -f tfplan
    exit 0
fi

echo ""
echo "🚀 Creating resources..."
terraform apply tfplan

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Resources created successfully!"
    echo ""
    echo "📋 Getting outputs..."
    terraform output
    
    echo ""
    echo "🔄 Updating .env file..."
    if [ -f "./update_env.sh" ]; then
        chmod +x ./update_env.sh
        ./update_env.sh
    else
        echo "⚠️  update_env.sh not found. Please manually update python/.env with:"
        echo ""
        terraform output -json | jq -r '
            "COGNITO_USER_POOL_ID=" + .cognito_user_pool_id.value,
            "COGNITO_CLIENT_ID=" + .cognito_client_id.value,
            "COGNITO_CLIENT_SECRET=" + .cognito_client_secret.value
        '
    fi
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Restart your FastAPI server"
    echo "2. Test authentication with: python3 ../scripts/check_cognito_config.py"
    echo "3. Try signing up a new user"
    echo ""
else
    echo "❌ Deployment failed"
    rm -f tfplan
    exit 1
fi

rm -f tfplan
