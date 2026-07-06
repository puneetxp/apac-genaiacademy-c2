# EC2 Deployment Guide - Rural Farming Platform

Complete guide to deploy the Rural Farming Platform on AWS EC2 using Terraform.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                            │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    VPC (10.0.0.0/16)                   │ │
│  │                                                         │ │
│  │  ┌──────────────────┐      ┌──────────────────┐       │ │
│  │  │  Public Subnet   │      │  Public Subnet   │       │ │
│  │  │   (AZ-1)         │      │   (AZ-2)         │       │ │
│  │  │                  │      │                  │       │ │
│  │  │  ┌────────────┐  │      │                  │       │ │
│  │  │  │ Frontend   │  │      │                  │       │ │
│  │  │  │ EC2        │  │      │                  │       │ │
│  │  │  │ (SolidJS)  │  │      │                  │       │ │
│  │  │  └────────────┘  │      │                  │       │ │
│  │  │                  │      │                  │       │ │
│  │  │  ┌────────────┐  │      │                  │       │ │
│  │  │  │ Backend    │  │      │                  │       │ │
│  │  │  │ EC2        │  │      │                  │       │ │
│  │  │  │ (FastAPI)  │  │      │                  │       │ │
│  │  │  └────────────┘  │      │                  │       │ │
│  │  └──────────────────┘      └──────────────────┘       │ │
│  │                                                         │ │
│  │  ┌──────────────────┐      ┌──────────────────┐       │ │
│  │  │  Private Subnet  │      │  Private Subnet  │       │ │
│  │  │   (AZ-1)         │      │   (AZ-2)         │       │ │
│  │  │                  │      │                  │       │ │
│  │  │  ┌────────────┐  │      │  ┌────────────┐  │       │ │
│  │  │  │ RDS        │  │      │  │ RDS        │  │       │ │
│  │  │  │ PostgreSQL │  │      │  │ Standby    │  │       │ │
│  │  │  │ (Primary)  │  │      │  │ (Multi-AZ) │  │       │ │
│  │  │  └────────────┘  │      │  └────────────┘  │       │ │
│  │  └──────────────────┘      └──────────────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Cognito   │  │     S3      │  │   Bedrock   │         │
│  │  User Pool  │  │   Bucket    │  │     AI      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### 1. Install Required Tools

```bash
# Install Terraform
brew install terraform  # macOS
# OR
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform --version

# Install AWS CLI
brew install awscli  # macOS
# OR
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Enter your credentials:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region name: ap-south-1
# Default output format: json

# Verify credentials
aws sts get-caller-identity
```

### 3. Generate SSH Key Pair

```bash
# Generate new SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/cropsense-deployer -C "cropsense-deployer"

# This creates:
# - Private key: ~/.ssh/cropsense-deployer
# - Public key: ~/.ssh/cropsense-deployer.pub

# Set proper permissions
chmod 600 ~/.ssh/cropsense-deployer
chmod 644 ~/.ssh/cropsense-deployer.pub

# Get public key content (you'll need this for terraform.tfvars)
cat ~/.ssh/cropsense-deployer.pub
```

## Deployment Steps

### Step 1: Prepare Configuration

```bash
# Navigate to terraform directory
cd rural-farming-platform/terraform

# Copy example tfvars
cp terraform.tfvars terraform.tfvars.backup

# Edit terraform.tfvars with your values
nano terraform.tfvars
```

Update `terraform.tfvars`:

```hcl
# AWS Configuration
aws_region   = "ap-south-1"
environment  = "production"  # or "development"
project_name = "rural-farming-platform"

# Database Configuration
db_name                  = "cropsense_prod"
db_username              = "admin"
db_password              = "CHANGE_THIS_STRONG_PASSWORD_123!"  # IMPORTANT: Change this!
db_engine_version        = "14.10"
db_instance_class        = "db.t3.medium"  # Upgrade for production
db_allocated_storage     = 50
db_max_allocated_storage = 200
db_backup_retention_days = 30  # Increase for production

# S3 Configuration
s3_bucket_name = "cropsense-prod-bucket-unique-name-12345"  # Must be globally unique!

# CORS Configuration
allowed_origins = [
  "https://your-domain.com",
  "https://www.your-domain.com"
]

# EC2 Configuration
backend_instance_type  = "t3.medium"   # 2 vCPU, 4 GB RAM
frontend_instance_type = "t3.small"    # 2 vCPU, 2 GB RAM
use_elastic_ips        = true          # Recommended for production

# SSH Configuration
ssh_public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC... cropsense-deployer"  # Paste your public key here

# Network Configuration (leave empty to create new VPC)
vpc_id             = ""
private_subnet_ids = []
public_subnet_ids  = []
app_cidr_blocks    = ["10.0.0.0/16"]
```

### Step 2: Initialize Terraform

```bash
# Initialize Terraform (downloads providers)
terraform init

# Validate configuration
terraform validate

# Format configuration files
terraform fmt
```

### Step 3: Plan Deployment

```bash
# Create execution plan
terraform plan -out=tfplan

# Review the plan carefully
# This shows what resources will be created
```

Expected resources to be created:
- VPC with public and private subnets
- Internet Gateway and NAT Gateways
- Security Groups
- RDS PostgreSQL instance
- S3 bucket with encryption
- Cognito User Pool
- 2 EC2 instances (backend + frontend)
- IAM roles and policies
- CloudWatch alarms
- SNS topics

### Step 4: Apply Configuration

```bash
# Apply the plan
terraform apply tfplan

# OR apply directly (will prompt for confirmation)
terraform apply

# Type 'yes' when prompted

# This will take 10-15 minutes to complete
```

### Step 5: Get Deployment Information

```bash
# View all outputs
terraform output

# Get specific outputs
terraform output backend_public_ip
terraform output frontend_public_ip
terraform output backend_url
terraform output frontend_url

# Get sensitive outputs
terraform output -raw env_file_config > deployment-config.txt
```

## Post-Deployment Steps

### 1. Verify EC2 Instances

```bash
# SSH into backend server
ssh -i ~/.ssh/cropsense-deployer ec2-user@<BACKEND_PUBLIC_IP>

# Check backend service status
sudo systemctl status cropsense-backend
sudo systemctl status nginx

# View logs
sudo journalctl -u cropsense-backend -f
sudo tail -f /var/log/nginx/error.log

# Exit
exit

# SSH into frontend server
ssh -i ~/.ssh/cropsense-deployer ec2-user@<FRONTEND_PUBLIC_IP>

# Check nginx status
sudo systemctl status nginx

# View logs
sudo tail -f /var/log/nginx/error.log

# Exit
exit
```

### 2. Deploy Application Code

The user-data scripts create placeholder directories. You need to deploy your actual code:

#### Backend Deployment

```bash
# SSH into backend server
ssh -i ~/.ssh/cropsense-deployer ec2-user@<BACKEND_PUBLIC_IP>

# Switch to application user
sudo su - cropsense

# Navigate to application directory
cd /opt/cropsense/backend/python

# Clone your repository (replace with your repo URL)
git clone https://github.com/your-org/rural-farming-platform.git temp
mv temp/python/* .
rm -rf temp

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Restart service
sudo systemctl restart cropsense-backend

# Check status
sudo systemctl status cropsense-backend
```

#### Frontend Deployment

```bash
# SSH into frontend server
ssh -i ~/.ssh/cropsense-deployer ec2-user@<FRONTEND_PUBLIC_IP>

# Switch to application user
sudo su - cropsense

# Navigate to application directory
cd /opt/cropsense/frontend/solidjs

# Clone your repository
git clone https://github.com/your-org/rural-farming-platform.git temp
mv temp/solidjs/* .
rm -rf temp

# Install dependencies
npm install

# Build production bundle
npm run build

# Restart nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### 3. Configure Domain Names (Optional)

If you have a domain:

```bash
# Update Route 53 or your DNS provider
# Point your domain to the Elastic IPs:
# - api.yourdomain.com → Backend Elastic IP
# - app.yourdomain.com → Frontend Elastic IP

# Update Nginx configuration on backend
sudo nano /etc/nginx/conf.d/cropsense-backend.conf
# Change: server_name api.yourdomain.com;

# Update Nginx configuration on frontend
sudo nano /etc/nginx/conf.d/cropsense-frontend.conf
# Change: server_name app.yourdomain.com;

# Restart Nginx on both servers
sudo systemctl restart nginx
```

### 4. Setup SSL/TLS Certificates

```bash
# Install Certbot on both servers
sudo dnf install -y certbot python3-certbot-nginx

# On backend server
sudo certbot --nginx -d api.yourdomain.com

# On frontend server
sudo certbot --nginx -d app.yourdomain.com

# Certificates will auto-renew
```

### 5. Configure Monitoring

```bash
# CloudWatch dashboards are automatically created
# Access them at: https://console.aws.amazon.com/cloudwatch/

# Set up SNS email notifications
aws sns subscribe \
    --topic-arn <ALERTS_TOPIC_ARN> \
    --protocol email \
    --notification-endpoint your-email@example.com

# Confirm subscription via email
```

## Testing the Deployment

### 1. Test Backend API

```bash
# Health check
curl http://<BACKEND_PUBLIC_IP>:8000/health

# API documentation
curl http://<BACKEND_PUBLIC_IP>:8000/docs

# Test endpoint
curl http://<BACKEND_PUBLIC_IP>:8000/health
```

### 2. Test Frontend

```bash
# Open in browser
open http://<FRONTEND_PUBLIC_IP>

# Or use curl
curl http://<FRONTEND_PUBLIC_IP>
```

### 3. Test Database Connection

```bash
# SSH into backend server
ssh -i ~/.ssh/cropsense-deployer ec2-user@<BACKEND_PUBLIC_IP>

# Test PostgreSQL connection
psql -h <RDS_ENDPOINT> -U <DB_USERNAME> -d <DB_NAME>

# Enter password when prompted
# If successful, you'll see: cropsense_prod=>

# Exit
\q
```

## Maintenance

### Updating Application Code

```bash
# Backend update
ssh -i ~/.ssh/cropsense-deployer ec2-user@<BACKEND_PUBLIC_IP>
sudo su - cropsense
cd /opt/cropsense/backend/python
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart cropsense-backend

# Frontend update
ssh -i ~/.ssh/cropsense-deployer ec2-user@<FRONTEND_PUBLIC_IP>
sudo su - cropsense
cd /opt/cropsense/frontend/solidjs
git pull origin main
npm install
npm run build
sudo systemctl restart nginx
```

### Viewing Logs

```bash
# Backend logs
ssh -i ~/.ssh/cropsense-deployer ec2-user@<BACKEND_PUBLIC_IP>
sudo journalctl -u cropsense-backend -f

# Frontend logs
ssh -i ~/.ssh/cropsense-deployer ec2-user@<FRONTEND_PUBLIC_IP>
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# CloudWatch Logs
aws logs tail /aws/rural-farming-platform/backend --follow
aws logs tail /aws/rural-farming-platform/frontend --follow
```

### Database Backups

```bash
# Manual backup
aws rds create-db-snapshot \
    --db-instance-identifier rural-farming-platform-db-production \
    --db-snapshot-identifier manual-backup-$(date +%Y%m%d-%H%M%S)

# List backups
aws rds describe-db-snapshots \
    --db-instance-identifier rural-farming-platform-db-production

# Restore from backup
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier rural-farming-platform-db-restored \
    --db-snapshot-identifier <SNAPSHOT_ID>
```

## Scaling

### Vertical Scaling (Upgrade Instance Size)

```bash
# Update terraform.tfvars
backend_instance_type  = "t3.large"   # 2 vCPU, 8 GB RAM
frontend_instance_type = "t3.medium"  # 2 vCPU, 4 GB RAM

# Apply changes
terraform apply

# Note: This will cause downtime during instance replacement
```

### Horizontal Scaling (Add Load Balancer)

For production with high traffic, consider adding:
- Application Load Balancer (ALB)
- Auto Scaling Groups
- Multiple EC2 instances
- ElastiCache for Redis

## Troubleshooting

### Backend Not Starting

```bash
# Check service status
sudo systemctl status cropsense-backend

# View detailed logs
sudo journalctl -u cropsense-backend -n 100 --no-pager

# Check if port is listening
sudo netstat -tlnp | grep 8000

# Test manually
cd /opt/cropsense/backend/python
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database Connection Issues

```bash
# Check security group rules
aws ec2 describe-security-groups \
    --group-ids <RDS_SECURITY_GROUP_ID>

# Test connection from backend server
telnet <RDS_ENDPOINT> 5432

# Check RDS status
aws rds describe-db-instances \
    --db-instance-identifier rural-farming-platform-db-production
```

### High CPU Usage

```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=<INSTANCE_ID> \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average

# SSH into instance and check processes
ssh -i ~/.ssh/cropsense-deployer ec2-user@<PUBLIC_IP>
top
htop
```

## Cleanup (Destroy Resources)

**WARNING**: This will delete all resources and data!

```bash
# Create final backup before destroying
aws rds create-db-snapshot \
    --db-instance-identifier rural-farming-platform-db-production \
    --db-snapshot-identifier final-backup-$(date +%Y%m%d-%H%M%S)

# Destroy all resources
terraform destroy

# Type 'yes' when prompted

# Verify all resources are deleted
aws ec2 describe-instances --filters "Name=tag:Application,Values=rural-farming-platform"
aws rds describe-db-instances
aws s3 ls | grep cropsense
```

## Cost Estimation

Approximate monthly costs (ap-south-1 region):

| Resource | Configuration | Monthly Cost (USD) |
|----------|--------------|-------------------|
| EC2 Backend | t3.medium | ~$30 |
| EC2 Frontend | t3.small | ~$15 |
| RDS PostgreSQL | db.t3.medium, 50GB | ~$50 |
| S3 Storage | 10GB + requests | ~$1 |
| Data Transfer | 100GB out | ~$9 |
| Elastic IPs | 2 IPs | ~$7 |
| CloudWatch | Logs + Alarms | ~$5 |
| **Total** | | **~$117/month** |

Production with Multi-AZ RDS: ~$180/month

## Security Best Practices

1. **Change default passwords** in terraform.tfvars
2. **Restrict SSH access** to your IP only
3. **Enable MFA** on AWS account
4. **Use AWS Secrets Manager** for sensitive values
5. **Enable CloudTrail** for audit logging
6. **Regular security updates**: `sudo dnf update -y`
7. **Monitor CloudWatch alarms**
8. **Enable AWS GuardDuty** for threat detection
9. **Use SSL/TLS certificates** (Let's Encrypt)
10. **Regular backups** and test restore procedures

## Support

For issues or questions:
- Check CloudWatch Logs
- Review Terraform state: `terraform show`
- AWS Support: https://console.aws.amazon.com/support/
- Project Documentation: See DOCUMENTATION_INDEX.md

## Next Steps

1. ✅ Deploy infrastructure with Terraform
2. ✅ Deploy application code
3. ✅ Configure domain and SSL
4. ✅ Set up monitoring and alerts
5. ⬜ Configure CI/CD pipeline
6. ⬜ Set up automated backups
7. ⬜ Performance testing
8. ⬜ Security audit
9. ⬜ Documentation updates
10. ⬜ User training

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Environment**: _____________
**Backend URL**: _____________
**Frontend URL**: _____________
