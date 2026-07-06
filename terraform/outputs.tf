# Terraform Outputs

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

# RDS Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.main.db_name
}

output "rds_username" {
  description = "RDS master username"
  value       = aws_db_instance.main.username
  sensitive   = true
}

# S3 Outputs
output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.main.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.main.arn
}

# Cognito Outputs
output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_user_pool_arn" {
  description = "ARN of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.arn
}

output "cognito_client_id" {
  description = "ID of the Cognito User Pool Client"
  value       = aws_cognito_user_pool_client.web_client.id
}

output "cognito_client_secret" {
  description = "Secret of the Cognito User Pool Client"
  value       = aws_cognito_user_pool_client.web_client.client_secret
  sensitive   = true
}

output "cognito_domain" {
  description = "Cognito User Pool Domain"
  value       = aws_cognito_user_pool_domain.main.domain
}

output "cognito_region" {
  description = "AWS Region for Cognito"
  value       = var.aws_region
}

# Environment Configuration Output
output "env_file_config" {
  description = "Configuration values for .env file"
  value = <<-EOT
    # Amazon Cognito Configuration (from Terraform)
    COGNITO_USER_POOL_ID=${aws_cognito_user_pool.main.id}
    COGNITO_CLIENT_ID=${aws_cognito_user_pool_client.web_client.id}
    COGNITO_CLIENT_SECRET=${aws_cognito_user_pool_client.web_client.client_secret}
    COGNITO_REGION=${var.aws_region}
    
    # Database Configuration (from Terraform)
    DATABASE_URL=postgresql://${aws_db_instance.main.username}:${var.db_password}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}
    
    # S3 Configuration (from Terraform)
    AWS_S3_BUCKET=${aws_s3_bucket.main.id}
  EOT
  sensitive = true
}

# EC2 Outputs
output "backend_public_ip" {
  description = "Public IP address of backend EC2 instance"
  value       = aws_instance.backend.public_ip
}

output "backend_private_ip" {
  description = "Private IP address of backend EC2 instance"
  value       = aws_instance.backend.private_ip
}

output "frontend_public_ip" {
  description = "Public IP address of frontend EC2 instance"
  value       = aws_instance.frontend.public_ip
}

output "frontend_private_ip" {
  description = "Private IP address of frontend EC2 instance"
  value       = aws_instance.frontend.private_ip
}

output "backend_url" {
  description = "Backend API URL"
  value       = "http://${var.use_elastic_ips ? aws_eip.backend[0].public_ip : aws_instance.backend.public_ip}:8000"
}

output "frontend_url" {
  description = "Frontend application URL"
  value       = "http://${var.use_elastic_ips ? aws_eip.frontend[0].public_ip : aws_instance.frontend.public_ip}"
}

output "ssh_command_backend" {
  description = "SSH command to connect to backend server"
  value       = "ssh -i ~/.ssh/your-key.pem ec2-user@${aws_instance.backend.public_ip}"
}

output "ssh_command_frontend" {
  description = "SSH command to connect to frontend server"
  value       = "ssh -i ~/.ssh/your-key.pem ec2-user@${aws_instance.frontend.public_ip}"
}
