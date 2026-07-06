# EC2 Configuration for Rural Farming Platform
# Application servers for backend and frontend

# ==================== DATA SOURCES ====================

# Latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ==================== SECURITY GROUPS ====================

# Security Group for Backend EC2
resource "aws_security_group" "backend" {
  name        = "${var.project_name}-backend-sg-${var.environment}"
  description = "Security group for backend API server"
  vpc_id      = local.vpc_id
  
  # SSH access (restrict to your IP in production)
  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTP access
  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTPS access
  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # FastAPI default port
  ingress {
    description = "FastAPI from anywhere"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.project_name}-backend-sg"
  }
}

# Security Group for Frontend EC2
resource "aws_security_group" "frontend" {
  name        = "${var.project_name}-frontend-sg-${var.environment}"
  description = "Security group for frontend web server"
  vpc_id      = local.vpc_id
  
  # SSH access
  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTP access
  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTPS access
  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Vite dev server port (for development)
  ingress {
    description = "Vite dev server"
    from_port   = 5173
    to_port     = 5173
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.project_name}-frontend-sg"
  }
}

# ==================== KEY PAIR ====================

# SSH Key Pair (you need to create this manually or provide existing key)
resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-deployer-${var.environment}"
  public_key = var.ssh_public_key
  
  tags = {
    Name = "${var.project_name}-deployer-key"
  }
}

# ==================== EC2 INSTANCES ====================

# Backend EC2 Instance
resource "aws_instance" "backend" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.backend_instance_type
  
  subnet_id                   = var.vpc_id == "" ? aws_subnet.public[0].id : var.public_subnet_ids[0]
  vpc_security_group_ids      = [aws_security_group.backend.id]
  associate_public_ip_address = true
  
  key_name             = aws_key_pair.deployer.key_name
  iam_instance_profile = aws_iam_instance_profile.app_profile.name
  
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 30
    delete_on_termination = true
    encrypted             = true
  }
  
  user_data = templatefile("${path.module}/user-data/backend-setup.sh", {
    db_host     = aws_db_instance.main.address
    db_port     = aws_db_instance.main.port
    db_name     = var.db_name
    db_username = var.db_username
    db_password = var.db_password
    aws_region  = var.aws_region
    s3_bucket   = aws_s3_bucket.uploads.id
    environment = var.environment
    cognito_user_pool_id     = aws_cognito_user_pool.main.id
    cognito_app_client_id    = aws_cognito_user_pool_client.main.id
    cognito_app_client_secret = aws_cognito_user_pool_client.main.client_secret
  })
  
  tags = {
    Name        = "${var.project_name}-backend-${var.environment}"
    Environment = var.environment
    Role        = "backend"
  }
  
  depends_on = [
    aws_db_instance.main,
    aws_s3_bucket.uploads
  ]
}

# Frontend EC2 Instance
resource "aws_instance" "frontend" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.frontend_instance_type
  
  subnet_id                   = var.vpc_id == "" ? aws_subnet.public[0].id : var.public_subnet_ids[0]
  vpc_security_group_ids      = [aws_security_group.frontend.id]
  associate_public_ip_address = true
  
  key_name             = aws_key_pair.deployer.key_name
  iam_instance_profile = aws_iam_instance_profile.app_profile.name
  
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true
  }
  
  user_data = templatefile("${path.module}/user-data/frontend-setup.sh", {
    backend_url = "http://${aws_instance.backend.public_ip}:8000"
    environment = var.environment
  })
  
  tags = {
    Name        = "${var.project_name}-frontend-${var.environment}"
    Environment = var.environment
    Role        = "frontend"
  }
  
  depends_on = [aws_instance.backend]
}

# ==================== ELASTIC IPS ====================

# Elastic IP for Backend (optional but recommended for production)
resource "aws_eip" "backend" {
  count = var.use_elastic_ips ? 1 : 0
  
  instance = aws_instance.backend.id
  domain   = "vpc"
  
  tags = {
    Name = "${var.project_name}-backend-eip"
  }
}

# Elastic IP for Frontend (optional but recommended for production)
resource "aws_eip" "frontend" {
  count = var.use_elastic_ips ? 1 : 0
  
  instance = aws_instance.frontend.id
  domain   = "vpc"
  
  tags = {
    Name = "${var.project_name}-frontend-eip"
  }
}

# ==================== CLOUDWATCH MONITORING ====================

# CloudWatch Log Group for Backend
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/aws/${var.project_name}/backend"
  retention_in_days = 7
  
  tags = {
    Name = "${var.project_name}-backend-logs"
  }
}

# CloudWatch Log Group for Frontend
resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/aws/${var.project_name}/frontend"
  retention_in_days = 7
  
  tags = {
    Name = "${var.project_name}-frontend-logs"
  }
}

# CloudWatch Alarm for Backend CPU
resource "aws_cloudwatch_metric_alarm" "backend_cpu" {
  alarm_name          = "${var.project_name}-backend-cpu-alert"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80.0
  alarm_description   = "Alert when backend CPU exceeds 80%"
  treat_missing_data  = "notBreaching"
  
  dimensions = {
    InstanceId = aws_instance.backend.id
  }
  
  alarm_actions = [aws_sns_topic.alerts.arn]
}

# CloudWatch Alarm for Frontend CPU
resource "aws_cloudwatch_metric_alarm" "frontend_cpu" {
  alarm_name          = "${var.project_name}-frontend-cpu-alert"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80.0
  alarm_description   = "Alert when frontend CPU exceeds 80%"
  treat_missing_data  = "notBreaching"
  
  dimensions = {
    InstanceId = aws_instance.frontend.id
  }
  
  alarm_actions = [aws_sns_topic.alerts.arn]
}

# CloudWatch Alarm for Backend Status Check
resource "aws_cloudwatch_metric_alarm" "backend_status" {
  alarm_name          = "${var.project_name}-backend-status-alert"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "Alert when backend instance fails status check"
  treat_missing_data  = "notBreaching"
  
  dimensions = {
    InstanceId = aws_instance.backend.id
  }
  
  alarm_actions = [aws_sns_topic.alerts.arn]
}

# CloudWatch Alarm for Frontend Status Check
resource "aws_cloudwatch_metric_alarm" "frontend_status" {
  alarm_name          = "${var.project_name}-frontend-status-alert"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "Alert when frontend instance fails status check"
  treat_missing_data  = "notBreaching"
  
  dimensions = {
    InstanceId = aws_instance.frontend.id
  }
  
  alarm_actions = [aws_sns_topic.alerts.arn]
}
