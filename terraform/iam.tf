# IAM Configuration for CropSense AI Platform
# Grants necessary permissions for managing Cognito and other AWS services

# Data source to get the current IAM user
data "aws_caller_identity" "current" {}

# IAM Policy for Cognito Management
resource "aws_iam_policy" "cognito_management" {
  name        = "${var.project_name}-cognito-management-policy"
  description = "Policy for managing Cognito User Pools and Clients"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CognitoUserPoolManagement"
        Effect = "Allow"
        Action = [
          "cognito-idp:UpdateUserPool",
          "cognito-idp:UpdateUserPoolClient",
          "cognito-idp:DescribeUserPool",
          "cognito-idp:DescribeUserPoolClient",
          "cognito-idp:ListUserPools",
          "cognito-idp:ListUserPoolClients",
          "cognito-idp:CreateUserPoolClient",
          "cognito-idp:DeleteUserPoolClient"
        ]
        Resource = [
          "arn:aws:cognito-idp:${var.aws_region}:${data.aws_caller_identity.current.account_id}:userpool/*"
        ]
      },
      {
        Sid    = "CognitoUserManagement"
        Effect = "Allow"
        Action = [
          "cognito-idp:AdminCreateUser",
          "cognito-idp:AdminDeleteUser",
          "cognito-idp:AdminGetUser",
          "cognito-idp:AdminUpdateUserAttributes",
          "cognito-idp:AdminSetUserPassword",
          "cognito-idp:AdminResetUserPassword",
          "cognito-idp:ListUsers"
        ]
        Resource = [
          "arn:aws:cognito-idp:${var.aws_region}:${data.aws_caller_identity.current.account_id}:userpool/*"
        ]
      }
    ]
  })
  
  tags = {
    Name        = "${var.project_name}-cognito-management"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# IAM Policy for Bedrock Access
resource "aws_iam_policy" "bedrock_access" {
  name        = "${var.project_name}-bedrock-access-policy"
  description = "Policy for accessing Amazon Bedrock AI services"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockInvokeModel"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = "*"
      }
    ]
  })
  
  tags = {
    Name        = "${var.project_name}-bedrock-access"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# IAM Policy for S3 Access
resource "aws_iam_policy" "s3_access" {
  name        = "${var.project_name}-s3-access-policy"
  description = "Policy for accessing S3 buckets"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3BucketAccess"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketVersioning"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}"
        ]
      },
      {
        Sid    = "S3ObjectAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetObjectVersion"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      }
    ]
  })
  
  tags = {
    Name        = "${var.project_name}-s3-access"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# IAM Policy for SNS Publishing
resource "aws_iam_policy" "sns_publish" {
  name        = "${var.project_name}-sns-publish-policy"
  description = "Policy for publishing to SNS topics"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "SNSPublish"
        Effect = "Allow"
        Action = [
          "sns:Publish",
          "sns:Subscribe",
          "sns:Unsubscribe",
          "sns:ListTopics",
          "sns:GetTopicAttributes"
        ]
        Resource = [
          aws_sns_topic.buyer_interests.arn,
          aws_sns_topic.strategy_reminders.arn,
          aws_sns_topic.weather_alerts.arn,
          aws_sns_topic.harvest_reminders.arn,
          aws_sns_topic.alerts.arn
        ]
      }
    ]
  })
  
  tags = {
    Name        = "${var.project_name}-sns-publish"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# IAM User for Application (if needed)
resource "aws_iam_user" "app_user" {
  count = var.create_app_user ? 1 : 0
  name  = "${var.project_name}-app-user-${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-app-user"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Attach policies to app user
resource "aws_iam_user_policy_attachment" "app_user_cognito" {
  count      = var.create_app_user ? 1 : 0
  user       = aws_iam_user.app_user[0].name
  policy_arn = aws_iam_policy.cognito_management.arn
}

resource "aws_iam_user_policy_attachment" "app_user_bedrock" {
  count      = var.create_app_user ? 1 : 0
  user       = aws_iam_user.app_user[0].name
  policy_arn = aws_iam_policy.bedrock_access.arn
}

resource "aws_iam_user_policy_attachment" "app_user_s3" {
  count      = var.create_app_user ? 1 : 0
  user       = aws_iam_user.app_user[0].name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_user_policy_attachment" "app_user_sns" {
  count      = var.create_app_user ? 1 : 0
  user       = aws_iam_user.app_user[0].name
  policy_arn = aws_iam_policy.sns_publish.arn
}

# Access keys for app user (if created)
resource "aws_iam_access_key" "app_user" {
  count = var.create_app_user ? 1 : 0
  user  = aws_iam_user.app_user[0].name
}

# Attach policies to existing IAM user (puneetxp)
resource "aws_iam_user_policy_attachment" "existing_user_cognito" {
  count      = var.attach_to_existing_user ? 1 : 0
  user       = var.existing_iam_username
  policy_arn = aws_iam_policy.cognito_management.arn
}

resource "aws_iam_user_policy_attachment" "existing_user_bedrock" {
  count      = var.attach_to_existing_user ? 1 : 0
  user       = var.existing_iam_username
  policy_arn = aws_iam_policy.bedrock_access.arn
}

resource "aws_iam_user_policy_attachment" "existing_user_s3" {
  count      = var.attach_to_existing_user ? 1 : 0
  user       = var.existing_iam_username
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_user_policy_attachment" "existing_user_sns" {
  count      = var.attach_to_existing_user ? 1 : 0
  user       = var.existing_iam_username
  policy_arn = aws_iam_policy.sns_publish.arn
}

# Variables for IAM configuration
variable "create_app_user" {
  description = "Whether to create a new IAM user for the application"
  type        = bool
  default     = false
}

variable "attach_to_existing_user" {
  description = "Whether to attach policies to an existing IAM user"
  type        = bool
  default     = true
}

variable "existing_iam_username" {
  description = "Existing IAM username to attach policies to"
  type        = string
  default     = "puneetxp"
}

# Outputs
output "cognito_management_policy_arn" {
  description = "ARN of the Cognito management policy"
  value       = aws_iam_policy.cognito_management.arn
}

output "bedrock_access_policy_arn" {
  description = "ARN of the Bedrock access policy"
  value       = aws_iam_policy.bedrock_access.arn
}

output "s3_access_policy_arn" {
  description = "ARN of the S3 access policy"
  value       = aws_iam_policy.s3_access.arn
}

output "sns_publish_policy_arn" {
  description = "ARN of the SNS publish policy"
  value       = aws_iam_policy.sns_publish.arn
}

output "app_user_access_key_id" {
  description = "Access key ID for app user (if created)"
  value       = var.create_app_user ? aws_iam_access_key.app_user[0].id : null
}

output "app_user_secret_access_key" {
  description = "Secret access key for app user (if created)"
  value       = var.create_app_user ? aws_iam_access_key.app_user[0].secret : null
  sensitive   = true
}
