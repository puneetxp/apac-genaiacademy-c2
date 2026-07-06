#!/bin/bash

# Apply Cognito username custom attribute update
# WARNING: This will modify the existing Cognito User Pool

echo "=========================================="
echo "Cognito User Pool - Add Username Attribute"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will modify your existing Cognito User Pool"
echo "   - Adds custom:username attribute"
echo "   - Existing users will NOT have this attribute set"
echo "   - New users will have this attribute"
echo ""
read -p "Do you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Step 1: Initialize Terraform"
echo "----------------------------------------"
terraform init

echo ""
echo "Step 2: Plan changes"
echo "----------------------------------------"
terraform plan

echo ""
read -p "Do you want to apply these changes? (yes/no): " APPLY

if [ "$APPLY" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Step 3: Apply changes"
echo "----------------------------------------"
terraform apply -auto-approve

echo ""
echo "=========================================="
echo "✓ Cognito User Pool updated successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Existing users (like puneetxp) will NOT have the username attribute"
echo "2. You need to manually update existing users using AWS CLI or Console"
echo "3. New users will automatically get the username attribute"
echo ""
echo "To update existing user 'puneetxp':"
echo "  aws cognito-idp admin-update-user-attributes \\"
echo "    --user-pool-id \$(terraform output -raw cognito_user_pool_id) \\"
echo "    --username puneetsharma9@hotmail.com \\"
echo "    --user-attributes Name=custom:username,Value=puneetxp"
echo ""
