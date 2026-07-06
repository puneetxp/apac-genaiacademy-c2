# Create New Cognito User Pool with Terraform

## Overview

This guide will help you create a brand new Cognito User Pool with the correct authentication flows enabled from the start.

## Prerequisites

- Terraform installed (v1.0+)
- AWS credentials configured
- Access to AWS Console

## Step 1: Review Configuration

The Terraform configuration in `cognito.tf` is already set up correctly with:
- ✅ `ALLOW_USER_PASSWORD_AUTH` enabled
- ✅ `ALLOW_REFRESH_TOKEN_AUTH` enabled
- ✅ `ALLOW_USER_SRP_AUTH` enabled
- ✅ Email and phone number verification
- ✅ MFA support (optional)
- ✅ Password policy

## Step 2: Initialize Terraform

```bash
cd rural-farming-platform/terraform

# Initialize Terraform (if not already done)
terraform init
```

## Step 3: Plan the Deployment

```bash
# See what will be created
terraform plan
```

This will show you:
- New Cognito User Pool
- New Cognito User Pool Client (with correct auth flows!)
- SNS topics for notifications
- ElastiCache Redis cluster
- CloudWatch alarms

## Step 4: Create the Resources

```bash
# Create all resources
terraform apply
```

Type `yes` when prompted.

This will:
1. Create a new Cognito User Pool: `rural-farming-platform-users-development`
2. Create a new App Client with USER_PASSWORD_AUTH enabled
3. Output the new User Pool ID and Client ID
4. Create SNS topics for notifications
5. Set up Redis cache

## Step 5: Update .env File

After Terraform completes, it will output the new credentials. Update your `.env` file:

```bash
# Run the update script
./update_env.sh
```

Or manually update `python/.env`:

```env
COGNITO_USER_POOL_ID=<new-user-pool-id>
COGNITO_CLIENT_ID=<new-client-id>
COGNITO_CLIENT_SECRET=<new-client-secret>
```

## Step 6: Verify Configuration

Check that the auth flows are enabled:

```bash
cd ..
python3 scripts/check_cognito_config.py
```

You should see:
```
✅ ENABLED  ALLOW_USER_PASSWORD_AUTH
✅ ENABLED  ALLOW_REFRESH_TOKEN_AUTH
✅ ENABLED  ALLOW_USER_SRP_AUTH
```

## Step 7: Test Authentication

Restart your FastAPI server and test:

```bash
# Sign up a new user
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!@#",
    "phone_number": "+919876543210",
    "full_name": "Test User"
  }'

# Confirm the user (check email for code)
curl -X POST "http://localhost:8000/auth/confirm-signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "confirmation_code": "123456"
  }'

# Sign in
curl -X POST "http://localhost:8000/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!@#"
  }'
```

## What Gets Created

### Cognito User Pool
- Name: `rural-farming-platform-users-development`
- Region: `ap-south-1`
- Features:
  - Email and phone verification
  - MFA optional
  - Password policy (8+ chars, uppercase, lowercase, numbers, symbols)
  - Account recovery via email/phone

### Cognito App Client
- Name: `rural-farming-platform-client-development`
- Auth Flows: USER_PASSWORD_AUTH, REFRESH_TOKEN_AUTH, USER_SRP_AUTH
- Token Validity:
  - Access Token: 60 minutes
  - ID Token: 60 minutes
  - Refresh Token: 30 days
- Client Secret: Generated automatically

### SNS Topics
- Buyer interests notifications
- Strategy reminders
- Weather alerts
- Harvest reminders
- System alerts

### ElastiCache Redis
- Node Type: cache.t3.micro
- Engine: Redis 7.0
- Purpose: API response caching

## Troubleshooting

### Error: "Backend configuration changed"

If you get a backend error, remove the S3 backend configuration:

```bash
# Edit terraform/main.tf and comment out the backend block:
# backend "s3" {
#   bucket = "rural-farming-platform-terraform-state"
#   ...
# }
```

Then run:
```bash
terraform init -reconfigure
```

### Error: "VPC not found"

The configuration will create a new VPC automatically. If you want to use an existing VPC:

1. Edit `terraform.tfvars`
2. Set `vpc_id` and `private_subnet_ids`

### Error: "Insufficient permissions"

Make sure your AWS credentials have permissions to create:
- Cognito User Pools
- SNS Topics
- ElastiCache clusters
- IAM roles

## Cost Estimate

Development environment costs (monthly):
- Cognito: Free tier (50,000 MAUs)
- ElastiCache t3.micro: ~$12/month
- SNS: ~$0.50/month (first 1M requests free)
- CloudWatch: ~$1/month

**Total: ~$13-15/month**

## Clean Up (Optional)

To delete all resources:

```bash
terraform destroy
```

Type `yes` when prompted. This will delete:
- Cognito User Pool (and all users!)
- App Client
- SNS Topics
- ElastiCache cluster
- CloudWatch alarms

---

**Next Steps:**
1. Run `terraform apply`
2. Update `.env` with new credentials
3. Test authentication
4. Start developing!
