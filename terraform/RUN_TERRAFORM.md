# Run Terraform to Create Cognito User Pool

## Quick Start (3 commands)

```bash
cd rural-farming-platform/terraform

# 1. Set AWS credentials
source set_aws_credentials.sh

# 2. Run the automated script
./create_cognito.sh
```

That's it! The script will create everything and update your `.env` file.

## Manual Method (if script fails)

### Step 1: Set AWS Credentials

```bash
cd terraform

# Option A: Source the credentials script
source set_aws_credentials.sh

# Option B: Export manually
export AWS_REGION=ap-south-1
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
```

### Step 2: Initialize Terraform

```bash
terraform init -reconfigure
```

### Step 3: Plan the Deployment

```bash
terraform plan
```

Review what will be created. You should see:
- Cognito User Pool
- Cognito App Client
- SNS Topics (4 topics)
- IAM Roles
- Random string for domain

### Step 4: Apply the Configuration

```bash
terraform apply
```

Type `yes` when prompted.

### Step 5: Get the Outputs

```bash
terraform output
```

Copy these values:
- `cognito_user_pool_id`
- `cognito_client_id`
- `cognito_client_secret` (use: `terraform output -raw cognito_client_secret`)

### Step 6: Update .env File

Edit `../python/.env` and update:

```env
COGNITO_USER_POOL_ID=<value-from-output>
COGNITO_CLIENT_ID=<value-from-output>
COGNITO_CLIENT_SECRET=<value-from-output>
```

### Step 7: Verify

```bash
cd ..
python3 scripts/check_cognito_config.py
```

## Alternative: AWS CLI Configuration

If you prefer to configure AWS CLI permanently:

```bash
# Configure AWS CLI
aws configure

# Enter when prompted:
AWS Access Key ID: YOUR_AWS_ACCESS_KEY_ID
AWS Secret Access Key: BK+66zP5R9jOejId1n0XNA52dtB5uldc/rH+8XdT
Default region name: ap-south-1
Default output format: json
```

Then Terraform will automatically use these credentials.

## Troubleshooting

### Error: "No valid credential sources found"

Make sure you've exported the AWS credentials:
```bash
source set_aws_credentials.sh
```

Or check if they're set:
```bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

### Error: "Duplicate resource"

The main.tf file has been cleaned up. If you still see this:
```bash
rm -rf .terraform
terraform init -reconfigure
```

### Error: "Backend configuration changed"

The S3 backend is commented out. This should not happen. If it does:
```bash
terraform init -reconfigure
```

### Error: "Access Denied"

Your AWS credentials might not have sufficient permissions. You need:
- `cognito-idp:CreateUserPool`
- `cognito-idp:CreateUserPoolClient`
- `sns:CreateTopic`
- `iam:CreateRole`

## What Gets Created

1. **Cognito User Pool**: `rural-farming-platform-users-development`
   - With USER_PASSWORD_AUTH enabled ✅
   - Email & phone verification
   - MFA optional
   - Strong password policy

2. **Cognito App Client**: `rural-farming-platform-client-development`
   - Auth flows: USER_PASSWORD_AUTH, REFRESH_TOKEN_AUTH, USER_SRP_AUTH
   - Token validity: 60 min (access/id), 30 days (refresh)
   - Client secret generated

3. **SNS Topics** (4 topics):
   - Buyer interests notifications
   - Strategy reminders
   - Weather alerts
   - Harvest reminders

4. **IAM Role**: For Cognito SMS (MFA)

5. **Cognito Domain**: For hosted UI (if needed later)

## Cost Estimate

- Cognito: Free (up to 50,000 MAUs)
- SNS: ~$0.50/month (first 1M requests free)
- Total: ~$0.50/month for development

## After Creation

1. ✅ Restart your FastAPI server
2. ✅ Test sign-up: `POST /auth/signup`
3. ✅ Test sign-in: `POST /auth/signin`
4. ✅ Authentication should work!

## Clean Up (Delete Everything)

To delete all resources:

```bash
terraform destroy
```

⚠️ This will delete the User Pool and all users!

---

**Time Required:** 5-10 minutes
**Difficulty:** Easy
**Result:** Working Cognito with correct auth flows
