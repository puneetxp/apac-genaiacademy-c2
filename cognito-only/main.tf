# Standalone Cognito Configuration
# Creates ONLY Cognito User Pool and App Client with USER_PASSWORD_AUTH enabled

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "cropsense"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "development"
}

# Cognito User Pool
resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-${var.environment}"
  
  username_attributes      = ["email", "phone_number"]
  auto_verified_attributes = ["email"]
  
  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = true
    temporary_password_validity_days = 7
  }
  
  mfa_configuration = "OFF"
  
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
  
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
  
  # Custom attribute for username (display name)
  schema {
    name                     = "username"
    attribute_data_type      = "String"
    mutable                  = true
    developer_only_attribute = false
    
    string_attribute_constraints {
      min_length = 3
      max_length = 50
    }
  }
  
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }
  
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "CropSense AI - Verify your email"
    email_message        = "Your verification code is {####}"
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Cognito App Client with USER_PASSWORD_AUTH enabled
resource "aws_cognito_user_pool_client" "main" {
  name         = "${var.project_name}-${var.environment}-client"
  user_pool_id = aws_cognito_user_pool.main.id
  
  generate_secret = true
  
  # THIS IS THE CRITICAL PART - enables username/password authentication
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
  
  refresh_token_validity = 30
  access_token_validity  = 1
  id_token_validity      = 1
  
  token_validity_units {
    refresh_token = "days"
    access_token  = "hours"
    id_token      = "hours"
  }
  
  prevent_user_existence_errors = "ENABLED"
}

# Outputs
output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  description = "Cognito Client ID"
  value       = aws_cognito_user_pool_client.main.id
}

output "cognito_client_secret" {
  description = "Cognito Client Secret"
  value       = aws_cognito_user_pool_client.main.client_secret
  sensitive   = true
}

output "cognito_region" {
  description = "AWS Region"
  value       = var.aws_region
}

output "env_config" {
  description = "Configuration for .env file"
  value = <<-EOT
    
    # Copy these values to python/.env:
    COGNITO_USER_POOL_ID=${aws_cognito_user_pool.main.id}
    COGNITO_CLIENT_ID=${aws_cognito_user_pool_client.main.id}
    COGNITO_CLIENT_SECRET=${aws_cognito_user_pool_client.main.client_secret}
    COGNITO_REGION=${var.aws_region}
  EOT
  sensitive = true
}
