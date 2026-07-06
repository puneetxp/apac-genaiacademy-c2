# Cognito Deployment with Terraform

This guide will help you deploy or update AWS Cognito configuration using Terraform and automatically update your `.env` file.

## Prerequisites

1. AWS CLI configured with credentials
2. Terraform installed (>= 1.0)
3. Appropriate AWS permissions for Cognito, IAM, and SNS

## Step 1: Initialize Terraform

```bash
cd rural-farming-platform/terraform

# Initialize Terraform (first time only)
terraform init

# Or if you want to skip the S3 backend (for local state)
terraform init -backend=false
```

## Step 2: Review the Plan

```bash
# See what will be created/updated
terraform plan
```

This will show:
- Cognito User Pool configuration
- Cognito User Pool Client with secret
- IAM roles for SNS
- SNS topics for notifications
- ElastiCache Redis cluster
- CloudWatch alarms

## Step 3: Apply the Configuration

```bash
# Apply the changes
terraform apply

# Review the changes and type 'yes' to confirm
```

## Step 4: Get the Cognito Credentials

After successful deployment, get the outputs:

```bash
# Get all outputs
terraform output

# Get specific values
terraform output cognito_user_pool_id
terraform output cognito_client_id
terraform output -raw cognito_client_secret

# Get formatted .env configuration
terraform output -raw env_file_config
```

## Step 5: Update .env File

### Option A: Automatic Update (Recommended)

```bash
# Navigate to python directory
cd ../python

# Backup current .env
cp .env .env.backup

# Get Cognito values from Terraform
COGNITO_USER_POOL_ID=$(cd ../terraform && terraform output -raw cognito_user_pool_id)
COGNITO_CLIENT_ID=$(cd ../terraform && terraform output -raw cognito_client_id)
COGNITO_CLIENT_SECRET=$(cd ../terraform && terraform output -raw cognito_client_secret)
COGNITO_REGION=$(cd ../terraform && terraform output -raw cognito_region)

# Update .env file
sed -i.bak "s/^COGNITO_USER_POOL_ID=.*/COGNITO_USER_POOL_ID=$COGNITO_USER_POOL_ID/" .env
sed -i.bak "s/^COGNITO_CLIENT_ID=.*/COGNITO_CLIENT_ID=$COGNITO_CLIENT_ID/" .env
sed -i.bak "s/^COGNITO_CLIENT_SECRET=.*/COGNITO_CLIENT_SECRET=$COGNITO_CLIENT_SECRET/" .env
sed -i.bak "s/^COGNITO_REGION=.*/COGNITO_REGION=$COGNITO_REGION/" .env

echo "✅ .env file updated successfully!"
```

### Option B: Manual Update

1. Get the values:
```bash
cd rural-farming-platform/terraform
terraform output cognito_user_pool_id
terraform output cognito_client_id
terraform output -raw cognito_client_secret
```

2. Edit `python/.env` and update:
```env
COGNITO_USER_POOL_ID=<value from terraform output>
COGNITO_CLIENT_ID=<value from terraform output>
COGNITO_CLIENT_SECRET=<value from terraform output>
COGNITO_REGION=ap-south-1
```

## Step 6: Restart the Backend

```bash
cd ../python

# If using uvicorn with --reload, it will auto-reload
# Otherwise, restart manually:
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 7: Verify the Configuration

Test the authentication endpoints:

```bash
# Test signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@1234",
    "email": "test@example.com",
    "phone_number": "+919876543210",
    "full_name": "Test User",
    "user_type": "farmer"
  }'
```

Expected response:
```json
{
  "user_sub": "...",
  "user_confirmed": false,
  "message": "User created successfully. Please check your email/phone for verification code."
}
```

## Terraform Resources Created

### Cognito User Pool
- Name: `rural-farming-platform-users-{environment}`
- Auto-verified: email, phone_number
- MFA: Optional
- Password policy: 8+ chars, uppercase, lowercase, number, symbol
- Custom attributes: farm_id

### Cognito User Pool Client
- Name: `rural-farming-platform-client-{environment}`
- Client secret: Generated
- Token validity: 
  - Access token: 60 minutes
  - ID token: 60 minutes
  - Refresh token: 30 days
- Auth flows: USER_PASSWORD_AUTH, REFRESH_TOKEN_AUTH, USER_SRP_AUTH

### IAM Role
- Role: `rural-farming-platform-cognito-sns-role`
- Policy: SNS publish permissions for SMS verification

### SNS Topics
- Buyer interests notifications
- Strategy reminders
- Weather alerts
- Harvest reminders
- System alerts

### ElastiCache Redis
- Engine: Redis 7.0
- Node type: cache.t3.micro (configurable)
- Backup retention: 7 days
- Maintenance window: Sunday 05:00-06:00

### CloudWatch Alarms
- Bedrock API cost monitoring
- ElastiCache CPU utilization
- ElastiCache memory usage

## Troubleshooting

### Error: Backend configuration required

If you see this error, either:

1. Create the S3 bucket for state:
```bash
aws s3 mb s3://rural-farming-platform-terraform-state --region ap-south-1
aws s3api put-bucket-versioning \
  --bucket rural-farming-platform-terraform-state \
  --versioning-configuration Status=Enabled
```

2. Or use local state:
```bash
# Comment out the backend block in main.tf
terraform init -reconfigure
```

### Error: VPC or Subnets not found

The configuration expects VPC and subnets. Either:

1. Use existing VPC (update `terraform.tfvars`):
```hcl
vpc_id = "vpc-xxxxx"
private_subnet_ids = ["subnet-xxxxx", "subnet-yyyyy"]
```

2. Or create VPC first:
```bash
terraform apply -target=aws_vpc.main -target=aws_subnet.private
```

### Error: Insufficient permissions

Ensure your AWS credentials have these permissions:
- cognito-idp:*
- iam:CreateRole, iam:AttachRolePolicy
- sns:CreateTopic
- elasticache:CreateCacheCluster
- cloudwatch:PutMetricAlarm

## Cleanup

To destroy all resources:

```bash
cd rural-farming-platform/terraform
terraform destroy

# Review and type 'yes' to confirm
```

⚠️ **Warning**: This will delete the Cognito User Pool and all users!

## Next Steps

1. Configure SNS email subscriptions for alerts
2. Set up CloudWatch dashboards
3. Configure Cognito hosted UI (optional)
4. Set up custom email templates
5. Enable advanced security features (CAPTCHA, risk-based authentication)

## Security Best Practices

1. Never commit `.env` files to git
2. Use different credentials for each environment
3. Enable MFA for admin users
4. Rotate client secrets regularly
5. Monitor CloudWatch logs for suspicious activity
6. Use AWS Secrets Manager for production secrets
7. Enable CloudTrail for audit logging

## Cost Optimization

- Cognito: First 50,000 MAUs free, then $0.0055/MAU
- ElastiCache: ~$12/month for t3.micro
- SNS: $0.50 per 1M requests
- CloudWatch: First 10 metrics free

Total estimated cost for development: ~$15-20/month
