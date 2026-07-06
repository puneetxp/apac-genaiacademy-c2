# Quick Start: Deploy Cognito with Terraform

## TL;DR - Fast Track

```bash
# 1. Navigate to terraform directory
cd rural-farming-platform/terraform

# 2. Initialize Terraform (first time only)
terraform init -backend=false

# 3. Apply configuration
terraform apply -auto-approve

# 4. Update .env file automatically
./update_env.sh

# 5. Done! Your .env is updated with new Cognito credentials
```

## What This Does

1. Creates a new AWS Cognito User Pool with:
   - Email and phone verification
   - Strong password policy
   - Optional MFA
   - Custom user attributes

2. Creates a Cognito App Client with:
   - Client secret for secure authentication
   - 30-day refresh tokens
   - 1-hour access tokens

3. Sets up supporting infrastructure:
   - IAM roles for SMS verification
   - SNS topics for notifications
   - ElastiCache Redis for caching
   - CloudWatch alarms for monitoring

4. Updates your `.env` file with the new credentials

## Step-by-Step

### 1. Initialize Terraform

```bash
cd rural-farming-platform/terraform
terraform init -backend=false
```

This downloads the required providers (AWS, Random).

### 2. Review What Will Be Created

```bash
terraform plan
```

Look for:
- `aws_cognito_user_pool.main` - User pool
- `aws_cognito_user_pool_client.main` - App client
- `aws_iam_role.cognito_sns_role` - IAM role
- SNS topics, ElastiCache, CloudWatch alarms

### 3. Deploy

```bash
terraform apply
```

Type `yes` when prompted. This takes ~2-3 minutes.

### 4. Update .env File

```bash
./update_env.sh
```

This automatically:
- Backs up your current `.env`
- Fetches Terraform outputs
- Updates Cognito credentials
- Shows you the new values

### 5. Restart Backend

If using `--reload`, the server will auto-restart. Otherwise:

```bash
cd ../python
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Verify It Works

Test signup:

```bash
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

Expected: `{"user_sub": "...", "user_confirmed": false, ...}`

## Manual .env Update (If Script Fails)

```bash
# Get values
cd rural-farming-platform/terraform
terraform output cognito_user_pool_id
terraform output cognito_client_id
terraform output -raw cognito_client_secret

# Edit python/.env and update:
# COGNITO_USER_POOL_ID=<value>
# COGNITO_CLIENT_ID=<value>
# COGNITO_CLIENT_SECRET=<value>
# COGNITO_REGION=ap-south-1
```

## Troubleshooting

### "Backend configuration required"

Use local state instead:
```bash
terraform init -backend=false
```

### "VPC not found"

The ElastiCache needs a VPC. Either:

1. Skip ElastiCache for now:
```bash
terraform apply -target=aws_cognito_user_pool.main -target=aws_cognito_user_pool_client.main
```

2. Or create VPC first (see `vpc.tf`)

### "Insufficient permissions"

Your AWS credentials need:
- `cognito-idp:*`
- `iam:CreateRole`
- `sns:CreateTopic`

Check: `aws sts get-caller-identity`

## What Gets Updated in .env

Before:
```env
COGNITO_USER_POOL_ID=ap-south-1_tkyDqxDIq
COGNITO_CLIENT_ID=59vo1fega8kmfekojgsp6vdug3
COGNITO_CLIENT_SECRET=180hskl8fkjlc8hqnufauband2pmpl6b3bhrgd1h96rdl3h717ot
COGNITO_REGION=ap-south-1
```

After:
```env
COGNITO_USER_POOL_ID=ap-south-1_ABC123XYZ  # New pool ID
COGNITO_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j  # New client ID
COGNITO_CLIENT_SECRET=<new-secret>  # New client secret
COGNITO_REGION=ap-south-1  # Same region
```

## Cleanup

To remove all resources:

```bash
terraform destroy
```

⚠️ This deletes the User Pool and all users!

## Cost

- Cognito: Free for first 50,000 users
- ElastiCache: ~$12/month (t3.micro)
- SNS: ~$0.50 per 1M messages
- Total: ~$15-20/month for development

## Next Steps

1. Test authentication flow
2. Configure SNS email subscriptions
3. Set up custom email templates
4. Enable advanced security features
5. Configure Cognito hosted UI (optional)

## Need Help?

See detailed guide: `COGNITO_DEPLOYMENT.md`
