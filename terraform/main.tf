# AWS Services Configuration for Rural Farming Platform
# Task 20.2: Configure AWS services for production
# Validates: Requirements AC1, AC2, AC3, AC4, AC6

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
  
  # Backend configuration commented out for initial setup
  # Uncomment and configure S3 bucket for production state management
  # backend "s3" {
  #   bucket = "rural-farming-platform-terraform-state"
  #   key    = "production/terraform.tfstate"
  #   region = "ap-south-1"
  #   encrypt = true
  # }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Application = "rural-farming-platform"
      ManagedBy   = "terraform"
    }
  }
}

# Variables are defined in variables.tf
# Resources are defined in separate files:
# - cognito.tf: Cognito User Pool and App Client
# - vpc.tf: VPC, Subnets, Security Groups
# - rds.tf: PostgreSQL Database
# - s3.tf: S3 Buckets for file storage
# - iam.tf: IAM Policies and Roles
# - outputs.tf: Output values

# Note: All resources have been moved to their respective files
# to avoid duplication and improve maintainability
