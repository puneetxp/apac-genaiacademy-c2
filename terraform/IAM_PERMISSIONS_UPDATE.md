# IAM Permissions Update via Terraform

## Overview

This guide shows how to use Terraform to grant your IAM user (`puneetxp`) the necessary permissions to manage Cognito User Pools and other AWS services.

## What Will Be Created

Terraform will create these IAM policies and attach them to your user:

1. **Cognito Management Policy** - Allows updating User Pools and Clients
2. **Bedrock Access Policy** - Allows invoking Bedrock AI models
3. **S3 Access Policy** - Allows reading/writing to S3 buckets
4. **SNS Publish Policy** - Allows publishing notifications

## Prerequisites

- Terraform installed (v1.0+)
- AWS credentials with IAM permissions to create policies and attach them to users
- Access to AWS account with admin privileges (to grant IAM permissions)

## Steps

### 1. Review the Configuration

The new `iam.tf` file has been created with:
- IAM policies for Cognito, Bedrock, S3, and SNS
- Configuration to attach policies to your existing user (`puneetxp`)
- Variables to control behavior

### 2. Initialize Terraform (if not already done)

```bash
cd terraform
terraform init
```

### 3. Review the Changes

```bash
terraform plan
```

This will show you what Terraform will create:
- 4 new IAM policies
- 4 policy attachments to user `puneetxp`

### 4. Apply the Changes

```bash
terraform apply
```

Type `yes` when prompted to confirm.

### 5. Verify the Permissions

After applying, test that you can now update Cognito:

```bash
aws cognito-idp update-user-pool-client \
  --user-pool-id ap-south-1_tkyDqxDIq \
  --client-id 59vo1fega8kmfekojgsp6vdug3 \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH ALLOW_USER_SRP_AUTH \
  --region ap-south-1
```

This should now succeed without the `AccessDeniedException` error.

## Configuration Variables

The `iam.tf` file uses these variables (with defaults):

```hcl
attach_to_existing_user = true        # Attach policies to existing user
existing_iam_username   = "puneetxp"  # Your IAM username
create_app_user         = false       # Don't create a new user
```

To change these, edit `terraform.tfvars` or pass them via command line:

```bash
terraform apply -var="existing_iam_username=your-username"
```

## Alternative: Manual IAM Policy Attachment

If you don't want to use Terraform, you can manually attach the policies via AWS Console:

1. Go to IAM → Users → puneetxp
2. Click "Add permissions" → "Attach policies directly"
3. Create and attach a custom policy with this JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cognito-idp:UpdateUserPool",
        "cognito-idp:UpdateUserPoolClient",
        "cognito-idp:DescribeUserPool",
        "cognito-idp:DescribeUserPoolClient"
      ],
      "Resource": "arn:aws:cognito-idp:ap-south-1:339713064684:userpool/*"
    }
  ]
}
```

## After Granting Permissions

Once you have the permissions, you can:

1. **Update Cognito via CLI:**
   ```bash
   ./scripts/fix_cognito_auth_flow.sh
   ```

2. **Update Cognito via Terraform:**
   ```bash
   cd terraform
   terraform apply
   ```
   This will update the User Pool Client with `ALLOW_USER_PASSWORD_AUTH` enabled.

3. **Test Sign-In:**
   ```bash
   curl -X POST "http://localhost:8000/auth/signin" \
     -H "Content-Type: application/json" \
     -d '{"username": "puneetxp", "password": "your-password"}'
   ```

## Troubleshooting

### Error: "User already has policy attached"

If the policy is already attached, Terraform will detect this and skip it. This is safe.

### Error: "Access Denied when creating IAM policy"

Your current AWS credentials don't have permission to create IAM policies. You need to:
1. Use AWS Console with admin access to create the policies manually
2. Or use different AWS credentials with IAM admin permissions

### Error: "Cannot find user puneetxp"

Update the `existing_iam_username` variable to match your actual IAM username:

```bash
terraform apply -var="existing_iam_username=your-actual-username"
```

## Security Notes

- These policies follow the principle of least privilege
- Cognito permissions are scoped to your account's user pools
- S3 permissions are scoped to your specific bucket
- SNS permissions are scoped to your specific topics
- Bedrock permissions are account-wide (required by AWS)

## Next Steps

After granting permissions:

1. ✅ Update Cognito User Pool Client to enable USER_PASSWORD_AUTH
2. ✅ Test authentication flow
3. ✅ Verify all AWS services are accessible
4. ✅ Continue with application development

---

**Created:** February 28, 2026
**Status:** Ready to apply
**Priority:** High - Unblocks Cognito configuration
