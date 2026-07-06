#!/bin/bash
set -e

# CI/CD Infrastructure Setup Script
# This script sets up AWS resources required for CI/CD pipeline

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
PROJECT_NAME="rural-farming"
ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
    echo -e "${RED}Error: Environment not specified${NC}"
    echo "Usage: $0 <staging|production>"
    exit 1
fi

if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo -e "${RED}Error: Environment must be 'staging' or 'production'${NC}"
    exit 1
fi

echo -e "${GREEN}Setting up CI/CD infrastructure for ${ENVIRONMENT}...${NC}"

# 1. Create ECR Repository
echo -e "${YELLOW}Creating ECR repository...${NC}"
aws ecr describe-repositories --repository-names ${PROJECT_NAME}-backend --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository \
    --repository-name ${PROJECT_NAME}-backend \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256

echo -e "${GREEN}✓ ECR repository created${NC}"

# 2. Create S3 Bucket for Frontend
BUCKET_NAME="${PROJECT_NAME}-frontend-${ENVIRONMENT}"
echo -e "${YELLOW}Creating S3 bucket: ${BUCKET_NAME}...${NC}"

aws s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null || \
aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $AWS_REGION \
    --create-bucket-configuration LocationConstraint=$AWS_REGION

# Configure bucket for static website hosting
aws s3 website s3://$BUCKET_NAME/ \
    --index-document index.html \
    --error-document index.html

# Set bucket policy for public read
cat > /tmp/bucket-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file:///tmp/bucket-policy.json

echo -e "${GREEN}✓ S3 bucket created and configured${NC}"

# 3. Create CloudFront Distribution
echo -e "${YELLOW}Creating CloudFront distribution...${NC}"

cat > /tmp/cloudfront-config.json <<EOF
{
    "CallerReference": "${PROJECT_NAME}-${ENVIRONMENT}-$(date +%s)",
    "Comment": "${PROJECT_NAME} ${ENVIRONMENT} frontend",
    "Enabled": true,
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-${BUCKET_NAME}",
                "DomainName": "${BUCKET_NAME}.s3.${AWS_REGION}.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-${BUCKET_NAME}",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"]
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "Compress": true
    },
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    }
}
EOF

DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config file:///tmp/cloudfront-config.json \
    --query 'Distribution.Id' \
    --output text 2>/dev/null || echo "")

if [ -n "$DISTRIBUTION_ID" ]; then
    echo -e "${GREEN}✓ CloudFront distribution created: ${DISTRIBUTION_ID}${NC}"
    echo "Save this distribution ID as CLOUDFRONT_DISTRIBUTION_ID_${ENVIRONMENT^^} in GitHub Secrets"
else
    echo -e "${YELLOW}⚠ CloudFront distribution may already exist${NC}"
fi

# 4. Create ECS Cluster
echo -e "${YELLOW}Creating ECS cluster...${NC}"
CLUSTER_NAME="${PROJECT_NAME}-cluster-${ENVIRONMENT}"

aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION 2>/dev/null | grep -q "ACTIVE" || \
aws ecs create-cluster \
    --cluster-name $CLUSTER_NAME \
    --region $AWS_REGION \
    --capacity-providers FARGATE FARGATE_SPOT \
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1

echo -e "${GREEN}✓ ECS cluster created${NC}"

# 5. Create CloudWatch Log Group
echo -e "${YELLOW}Creating CloudWatch log group...${NC}"
LOG_GROUP="/ecs/${PROJECT_NAME}-backend-${ENVIRONMENT}"

aws logs describe-log-groups --log-group-name-prefix $LOG_GROUP --region $AWS_REGION 2>/dev/null | grep -q "$LOG_GROUP" || \
aws logs create-log-group \
    --log-group-name $LOG_GROUP \
    --region $AWS_REGION

aws logs put-retention-policy \
    --log-group-name $LOG_GROUP \
    --retention-in-days 30 \
    --region $AWS_REGION

echo -e "${GREEN}✓ CloudWatch log group created${NC}"

# 6. Create IAM Roles
echo -e "${YELLOW}Creating IAM roles...${NC}"

# ECS Task Execution Role
cat > /tmp/ecs-task-execution-role.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam get-role --role-name ecsTaskExecutionRole 2>/dev/null || \
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file:///tmp/ecs-task-execution-role.json

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# ECS Task Role
cat > /tmp/ecs-task-role.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam get-role --role-name ecsTaskRole 2>/dev/null || \
aws iam create-role \
    --role-name ecsTaskRole \
    --assume-role-policy-document file:///tmp/ecs-task-role.json

# Attach policies for AWS services
aws iam attach-role-policy \
    --role-name ecsTaskRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam attach-role-policy \
    --role-name ecsTaskRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonCognitoPowerUser

aws iam attach-role-policy \
    --role-name ecsTaskRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess

echo -e "${GREEN}✓ IAM roles created${NC}"

# 7. Create Secrets in Secrets Manager
echo -e "${YELLOW}Creating secrets in Secrets Manager...${NC}"

# Database URL
aws secretsmanager describe-secret --secret-id ${ENVIRONMENT}/database-url --region $AWS_REGION 2>/dev/null || \
aws secretsmanager create-secret \
    --name ${ENVIRONMENT}/database-url \
    --description "Database URL for ${ENVIRONMENT}" \
    --secret-string "postgresql://user:password@host:5432/dbname" \
    --region $AWS_REGION

# Redis URL
aws secretsmanager describe-secret --secret-id ${ENVIRONMENT}/redis-url --region $AWS_REGION 2>/dev/null || \
aws secretsmanager create-secret \
    --name ${ENVIRONMENT}/redis-url \
    --description "Redis URL for ${ENVIRONMENT}" \
    --secret-string "redis://host:6379/0" \
    --region $AWS_REGION

# AWS Access Key
aws secretsmanager describe-secret --secret-id ${ENVIRONMENT}/aws-access-key --region $AWS_REGION 2>/dev/null || \
aws secretsmanager create-secret \
    --name ${ENVIRONMENT}/aws-access-key \
    --description "AWS Access Key for ${ENVIRONMENT}" \
    --secret-string "YOUR_ACCESS_KEY" \
    --region $AWS_REGION

# AWS Secret Key
aws secretsmanager describe-secret --secret-id ${ENVIRONMENT}/aws-secret-key --region $AWS_REGION 2>/dev/null || \
aws secretsmanager create-secret \
    --name ${ENVIRONMENT}/aws-secret-key \
    --description "AWS Secret Key for ${ENVIRONMENT}" \
    --secret-string "YOUR_SECRET_KEY" \
    --region $AWS_REGION

# Cognito User Pool ID
aws secretsmanager describe-secret --secret-id ${ENVIRONMENT}/cognito-pool-id --region $AWS_REGION 2>/dev/null || \
aws secretsmanager create-secret \
    --name ${ENVIRONMENT}/cognito-pool-id \
    --description "Cognito User Pool ID for ${ENVIRONMENT}" \
    --secret-string "YOUR_POOL_ID" \
    --region $AWS_REGION

# Cognito Client ID
aws secretsmanager describe-secret --secret-id ${ENVIRONMENT}/cognito-client-id --region $AWS_REGION 2>/dev/null || \
aws secretsmanager create-secret \
    --name ${ENVIRONMENT}/cognito-client-id \
    --description "Cognito Client ID for ${ENVIRONMENT}" \
    --secret-string "YOUR_CLIENT_ID" \
    --region $AWS_REGION

echo -e "${GREEN}✓ Secrets created (update with actual values)${NC}"

# 8. Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CI/CD Infrastructure Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Update secrets in AWS Secrets Manager with actual values"
echo "2. Add the following secrets to GitHub repository:"
echo "   - AWS_ACCESS_KEY_ID_${ENVIRONMENT^^}"
echo "   - AWS_SECRET_ACCESS_KEY_${ENVIRONMENT^^}"
echo "   - DATABASE_URL_${ENVIRONMENT^^}"
if [ -n "$DISTRIBUTION_ID" ]; then
    echo "   - CLOUDFRONT_DISTRIBUTION_ID_${ENVIRONMENT^^}: ${DISTRIBUTION_ID}"
fi
echo ""
echo "3. Update ECS task definitions in .aws/ with your AWS account ID"
echo "4. Create RDS database and ElastiCache Redis cluster"
echo "5. Update task definitions with actual resource ARNs"
echo ""
echo -e "${YELLOW}Resources created:${NC}"
echo "  - ECR Repository: ${PROJECT_NAME}-backend"
echo "  - S3 Bucket: ${BUCKET_NAME}"
if [ -n "$DISTRIBUTION_ID" ]; then
    echo "  - CloudFront Distribution: ${DISTRIBUTION_ID}"
fi
echo "  - ECS Cluster: ${CLUSTER_NAME}"
echo "  - CloudWatch Log Group: ${LOG_GROUP}"
echo "  - IAM Roles: ecsTaskExecutionRole, ecsTaskRole"
echo ""

# Cleanup temp files
rm -f /tmp/bucket-policy.json /tmp/cloudfront-config.json /tmp/ecs-task-*.json

echo -e "${GREEN}Done!${NC}"
