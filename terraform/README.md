# Terraform Infrastructure for Rural Farming Platform

Complete AWS infrastructure as code for CropSense AI platform.

## 📋 Overview

This Terraform configuration provisions all AWS resources needed for the Rural Farming Platform:

- **VPC & Networking** - Complete network infrastructure with public/private subnets
- **RDS PostgreSQL** - Database with pgvector extension for ML features
- **ElastiCache Redis** - Caching layer for API performance
- **S3 Bucket** - File storage for uploads (images, documents)
- **Cognito** - User authentication and authorization
- **SNS Topics** - Notification system for alerts and reminders
- **CloudWatch** - Monitoring, logging, and alarms
- **IAM Roles** - Secure access policies

## 🚀 Quick Start

### Prerequisites

1. **Install Terraform** (>= 1.0)
   ```bash
   brew install terraform  # macOS
   # or download from https://www.terraform.io/downloads
   ```

2. **Configure AWS Credentials**
   ```bash
   aws configure
   # Enter your AWS Access Key ID and Secret Access Key
   ```

3. **Update terraform.tfvars**
   ```bash
   cd terraform
   cp terraform.tfvars terraform.tfvars.backup
   # Edit terraform.tfvars with your values
   ```

### Deployment Steps

```bash
# 1. Navigate to terraform directory
cd rural-farming-platform/terraform

# 2. Initialize Terraform
terraform init

# 3. Review the execution plan
terraform plan

# 4. Apply the configuration
terraform apply

# 5. Save outputs to .env file
terraform output -json > outputs.json
```

## 📁 File Structure

```
terraform/
├── main.tf           # Provider config, Cognito, SNS, ElastiCache, CloudWatch
├── rds.tf            # PostgreSQL database configuration
├── s3.tf             # S3 bucket and IAM policies
├── vpc.tf            # VPC, subnets, NAT gateways, routing
├── variables.tf      # Variable definitions
├── terraform.tfvars  # Variable values (from .env)
└── README.md         # This file
```

## 🔧 Configuration

### terraform.tfvars

The `terraform.tfvars` file is pre-populated from `python/.env`:

```hcl
# Core Configuration
aws_region   = "ap-south-1"
environment  = "development"
project_name = "rural-farming-platform"

# Database (from .env)
db_name     = "cropsense_dev"
db_username = "puneetsharma"
db_password = "password"  # CHANGE IN PRODUCTION!

# S3 (from .env)
s3_bucket_name = "cropsense-dev-bucket"

# CORS (from .env)
allowed_origins = [
  "http://localhost:3000",
  "http://localhost:5173"
]
```

### Important Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aws_region` | AWS region | `ap-south-1` | Yes |
| `environment` | Environment name | `development` | Yes |
| `db_password` | Database password | - | Yes |
| `s3_bucket_name` | S3 bucket name (globally unique) | - | Yes |
| `vpc_id` | Existing VPC ID (empty = create new) | `""` | No |
| `private_subnet_ids` | Existing subnet IDs | `[]` | No |

## 📊 Resources Created

### Networking
- **VPC** - 10.0.0.0/16 CIDR block
- **Public Subnets** - 2 subnets across AZs
- **Private Subnets** - 2 subnets across AZs
- **Internet Gateway** - Public internet access
- **NAT Gateways** - 2 NAT gateways for private subnet internet access
- **Route Tables** - Public and private routing
- **VPC Flow Logs** - Network traffic logging

### Database
- **RDS PostgreSQL 14** - Primary database
- **DB Subnet Group** - Multi-AZ subnet group
- **DB Parameter Group** - Custom parameters with pgvector
- **DB Security Group** - Network access control
- **Automated Backups** - 7-day retention
- **Performance Insights** - Query performance monitoring

### Caching
- **ElastiCache Redis 7.0** - API caching layer
- **Cache Subnet Group** - Multi-AZ subnet group
- **Cache Security Group** - Network access control
- **Automated Backups** - 7-day snapshots

### Storage
- **S3 Bucket** - File uploads storage
- **Bucket Versioning** - File version control
- **Bucket Encryption** - AES-256 encryption
- **Lifecycle Rules** - Automatic archival to Glacier
- **CORS Configuration** - Cross-origin access
- **Bucket Policy** - IAM-based access control

### Authentication
- **Cognito User Pool** - User management
- **Cognito Client** - Application client
- **MFA Support** - Optional multi-factor auth
- **Password Policy** - Strong password requirements
- **Custom Attributes** - farm_id attribute

### Notifications
- **SNS Topics** - 5 notification topics:
  - Buyer Interests
  - Strategy Reminders
  - Weather Alerts
  - Harvest Reminders
  - System Alerts

### Monitoring
- **CloudWatch Alarms** - 7 alarms:
  - Bedrock API costs
  - RDS CPU utilization
  - RDS storage space
  - RDS connections
  - ElastiCache CPU
  - ElastiCache memory
  - S3 bucket size

### IAM
- **App Role** - EC2 instance role
- **Instance Profile** - EC2 instance profile
- **S3 Access Policy** - S3 read/write permissions
- **Bedrock Access Policy** - AI model access
- **SNS Access Policy** - Notification permissions
- **CloudWatch Policy** - Logging and metrics

## 📤 Outputs

After `terraform apply`, you'll get these outputs:

```bash
# View all outputs
terraform output

# View specific output
terraform output rds_endpoint
terraform output redis_url
terraform output s3_bucket_name
```

### Key Outputs

| Output | Description | Usage |
|--------|-------------|-------|
| `rds_endpoint` | PostgreSQL endpoint | Update `POSTGRES_SERVER` in .env |
| `redis_url` | Redis connection URL | Update `REDIS_HOST` in .env |
| `s3_bucket_name` | S3 bucket name | Update `S3_BUCKET_NAME` in .env |
| `cognito_user_pool_id` | Cognito pool ID | Update `COGNITO_USER_POOL_ID` in .env |
| `cognito_client_id` | Cognito client ID | Update `COGNITO_CLIENT_ID` in .env |

## 🔄 Update .env File

After deployment, update your `python/.env` file:

```bash
# Extract outputs
terraform output -json > outputs.json

# Update .env manually or use script:
export POSTGRES_SERVER=$(terraform output -raw rds_address)
export REDIS_HOST=$(terraform output -raw elasticache_endpoint)
export S3_BUCKET_NAME=$(terraform output -raw s3_bucket_name)
export COGNITO_USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
export COGNITO_CLIENT_ID=$(terraform output -raw cognito_client_id)
```

## 🔒 Security Best Practices

### For Production:

1. **Change Default Password**
   ```hcl
   db_password = "STRONG_PASSWORD_HERE"  # Use AWS Secrets Manager
   ```

2. **Enable Multi-AZ**
   ```hcl
   environment = "production"  # Automatically enables multi-AZ
   ```

3. **Use Larger Instances**
   ```hcl
   db_instance_class = "db.t3.medium"
   cache_node_type   = "cache.t3.medium"
   ```

4. **Enable Deletion Protection**
   - Automatically enabled for production environment

5. **Use AWS Secrets Manager**
   ```bash
   # Store sensitive values in Secrets Manager
   aws secretsmanager create-secret \
     --name rural-farming-platform/db-password \
     --secret-string "YOUR_PASSWORD"
   ```

6. **Enable CloudTrail**
   - Track all API calls for audit

7. **Configure Backup Retention**
   ```hcl
   db_backup_retention_days = 30  # Production: 30 days
   ```

## 💰 Cost Estimation

### Development Environment (~$50-70/month)

- RDS db.t3.micro: ~$15/month
- ElastiCache cache.t3.micro: ~$12/month
- NAT Gateways (2): ~$32/month
- S3 Storage: ~$1/month (10GB)
- Data Transfer: ~$5/month
- CloudWatch: ~$5/month

### Production Environment (~$200-300/month)

- RDS db.t3.medium (Multi-AZ): ~$120/month
- ElastiCache cache.t3.medium: ~$50/month
- NAT Gateways (2): ~$32/month
- S3 Storage: ~$10/month (100GB)
- Data Transfer: ~$20/month
- CloudWatch: ~$10/month
- Bedrock API: Variable (pay per use)

## 🧹 Cleanup

To destroy all resources:

```bash
# Review what will be destroyed
terraform plan -destroy

# Destroy all resources
terraform destroy

# Confirm with 'yes' when prompted
```

**WARNING**: This will permanently delete:
- All data in RDS database
- All files in S3 bucket
- All Redis cache data
- All CloudWatch logs

## 🐛 Troubleshooting

### Issue: S3 Bucket Name Already Exists

```bash
# Error: BucketAlreadyExists
# Solution: Change bucket name in terraform.tfvars
s3_bucket_name = "cropsense-dev-bucket-YOUR_UNIQUE_ID"
```

### Issue: VPC Limit Reached

```bash
# Error: VpcLimitExceeded
# Solution: Use existing VPC
vpc_id = "vpc-xxxxx"
private_subnet_ids = ["subnet-xxxxx", "subnet-yyyyy"]
```

### Issue: RDS Snapshot Exists

```bash
# Error: DBSnapshotAlreadyExists
# Solution: Delete old snapshot or change identifier
aws rds delete-db-snapshot --db-snapshot-identifier <snapshot-id>
```

## 📚 Additional Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [AWS VPC Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Terraform plan output carefully
3. Check AWS CloudWatch logs
4. Verify AWS credentials and permissions

---

**Last Updated**: 2026-02-28
**Terraform Version**: >= 1.0
**AWS Provider Version**: ~> 5.0
