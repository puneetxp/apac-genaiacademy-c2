# Minimal Cognito Configuration - Just to get authentication working
# This creates only the Cognito User Pool and App Client

# Cognito User Pool
resource "aws_cognito_user_pool" "minimal" {
  name = "${var.project_name}-users-${var.environment}-minimal"
  
  # Username configuration
  username_attributes      = ["email", "phone_number"]
  auto_verified_attributes = ["email"]
  
  # Password policy
  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = true
    temporary_password_validity_days = 7
  }
  
  # MFA configuration
  mfa_configuration = "OPTIONAL"
  
  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
  
  # User attributes
  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true
    
    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }
  
  schema {
    name                = "phone_number"
    attribute_data_type = "String"
    required            = false
    mutable             = true
  }
  
  schema {
    name                = "name"
    attribute_data_type = "String"
    required            = true
    mutable             = true
    
    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }
  
  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }
  
  # Verification message templates
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "CropSense AI - Verify your email"
    email_message        = "Your verification code is {####}"
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-user-pool-minimal"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Cognito User Pool Client with USER_PASSWORD_AUTH enabled
resource "aws_cognito_user_pool_client" "minimal" {
  name         = "${var.project_name}-${var.environment}-web-client-minimal"
  user_pool_id = aws_cognito_user_pool.minimal.id
  
  # Generate client secret
  generate_secret = true
  
  # Auth flows - THIS IS THE CRITICAL PART!
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",      # ← This enables username/password auth
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
  
  # Token validity
  refresh_token_validity = 30
  access_token_validity  = 1
  id_token_validity      = 1
  
  token_validity_units {
    refresh_token = "days"
    access_token  = "hours"
    id_token      = "hours"
  }
  
  # Prevent user existence errors
  prevent_user_existence_errors = "ENABLED"
}

# Outputs
output "minimal_cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.minimal.id
}

output "minimal_cognito_client_id" {
  description = "Cognito User Pool Client ID"
  value       = aws_cognito_user_pool_client.minimal.id
}

output "minimal_cognito_client_secret" {
  description = "Cognito User Pool Client Secret"
  value       = aws_cognito_user_pool_client.minimal.client_secret
  sensitive   = true
}

output "minimal_cognito_region" {
  description = "AWS Region for Cognito"
  value       = var.aws_region
}

output "minimal_env_config" {
  description = "Configuration for .env file"
  value = <<-EOT
    # Update these values in python/.env:
    COGNITO_USER_POOL_ID=${aws_cognito_user_pool.minimal.id}
    COGNITO_CLIENT_ID=${aws_cognito_user_pool_client.minimal.id}
    COGNITO_CLIENT_SECRET=${aws_cognito_user_pool_client.minimal.client_secret}
    COGNITO_REGION=${var.aws_region}
  EOT
  sensitive = true
}
