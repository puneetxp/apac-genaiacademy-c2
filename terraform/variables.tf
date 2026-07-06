# Terraform Variables for Rural Farming Platform
# Complete variable definitions with descriptions and defaults

# ==================== CORE VARIABLES ====================

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "development"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "rural-farming-platform"
}

# ==================== DATABASE VARIABLES ====================

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "14.10"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage in GB"
  type        = number
  default     = 20
  
  validation {
    condition     = var.db_allocated_storage >= 20 && var.db_allocated_storage <= 65536
    error_message = "Allocated storage must be between 20 and 65536 GB."
  }
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage in GB (for autoscaling)"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "cropsense_dev"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "puneetsharma"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
  
  validation {
    condition     = length(var.db_password) >= 8
    error_message = "Database password must be at least 8 characters long."
  }
}

variable "db_backup_retention_days" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
  
  validation {
    condition     = var.db_backup_retention_days >= 0 && var.db_backup_retention_days <= 35
    error_message = "Backup retention must be between 0 and 35 days."
  }
}

# ==================== S3 VARIABLES ====================

variable "s3_bucket_name" {
  description = "S3 bucket name for file uploads (must be globally unique)"
  type        = string
  default     = "cropsense-dev-bucket"
}

variable "allowed_origins" {
  description = "Allowed CORS origins for S3 bucket"
  type        = list(string)
  default     = ["http://localhost:3000", "http://localhost:5173"]
}

# ==================== CACHE VARIABLES ====================

variable "cache_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

# ==================== NETWORK VARIABLES ====================

variable "vpc_id" {
  description = "Existing VPC ID (leave empty to create new VPC)"
  type        = string
  default     = ""
}

variable "private_subnet_ids" {
  description = "Existing private subnet IDs (leave empty to create new subnets)"
  type        = list(string)
  default     = []
}

variable "app_cidr_blocks" {
  description = "CIDR blocks allowed to access application resources"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

# ==================== MONITORING VARIABLES ====================

variable "enable_enhanced_monitoring" {
  description = "Enable enhanced monitoring for RDS"
  type        = bool
  default     = false
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
  default     = ""
}

# ==================== EC2 VARIABLES ====================

variable "backend_instance_type" {
  description = "EC2 instance type for backend server"
  type        = string
  default     = "t3.medium"
}

variable "frontend_instance_type" {
  description = "EC2 instance type for frontend server"
  type        = string
  default     = "t3.small"
}

variable "ssh_public_key" {
  description = "SSH public key for EC2 access"
  type        = string
  sensitive   = true
}

variable "use_elastic_ips" {
  description = "Whether to use Elastic IPs for EC2 instances"
  type        = bool
  default     = false
}

variable "public_subnet_ids" {
  description = "Existing public subnet IDs (leave empty to create new subnets)"
  type        = list(string)
  default     = []
}

# ==================== TAGS ====================

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
