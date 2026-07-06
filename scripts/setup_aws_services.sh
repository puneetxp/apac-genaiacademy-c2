#!/bin/bash

# AWS Services Setup Script
# Task 20.2: Configure AWS services for production
# Validates: Requirements AC1, AC2, AC3, AC4, AC6

set -e  # Exit on error

echo "=========================================="
echo "AWS Services Configuration Setup"
echo "Rural Farming Platform - Production"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${YELLOW}Warning: Terraform is not installed${NC}"
    echo "Terraform is recommended for infrastructure as code"
    echo "Install from: https://www.terraform.io/downloads"
fi

# Check AWS credentials
echo "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Please configure AWS credentials:"
    echo "  aws configure"
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-ap-south-1}

echo -e "${GREEN}✓ AWS credentials configured${NC}"
echo "  Account ID: $AWS_ACCOUNT_ID"
echo "  Region: $AWS_REGION"
echo ""

# Function to check if service is available
check_service() {
    local service=$1
    echo "Checking $service availability..."
    
    case $service in
        "cognito")
            if aws cognito-idp list-user-pools --max-results 1 --region $AWS_REGION &> /dev/null; then
                echo -e "${GREEN}✓ Amazon Cognito is available${NC}"
                return 0
            fi
            ;;
        "bedrock")
            if aws bedrock list-foundation-models --region $AWS_REGION &> /dev/null; then
                echo -e "${GREEN}✓ Amazon Bedrock is available${NC}"
                return 0
            fi
            ;;
        "sns")
            if aws sns list-topics --region $AWS_REGION &> /dev/null; then
                echo -e "${GREEN}✓ Amazon SNS is available${NC}"
                return 0
            fi
            ;;
        "elasticache")
            if aws elasticache describe-cache-clusters --region $AWS_REGION &> /dev/null; then
                echo -e "${GREEN}✓ Amazon ElastiCache is available${NC}"
                return 0
            fi
            ;;
    esac
    
    echo -e "${RED}✗ $service is not available${NC}"
    return 1
}

# Check all services
echo "Checking AWS service availability..."
check_service "cognito"
check_service "bedrock"
check_service "sns"
check_service "elasticache"
echo ""

# Setup options
echo "Setup Options:"
echo "1. Use Terraform (Recommended - Infrastructure as Code)"
echo "2. Use Python configuration script"
echo "3. Manual setup (AWS Console)"
echo "4. Exit"
echo ""
read -p "Select option (1-4): " option

case $option in
    1)
        echo ""
        echo "Setting up with Terraform..."
        
        if ! command -v terraform &> /dev/null; then
            echo -e "${RED}Error: Terraform is not installed${NC}"
            exit 1
        fi
        
        cd terraform/
        
        # Check if terraform.tfvars exists
        if [ ! -f "terraform.tfvars" ]; then
            echo -e "${YELLOW}Warning: terraform.tfvars not found${NC}"
            echo "Creating from example..."
            cp terraform.tfvars.example terraform.tfvars
            echo ""
            echo -e "${YELLOW}Please edit terraform.tfvars with your VPC and subnet IDs${NC}"
            echo "Then run: terraform init && terraform apply"
            exit 0
        fi
        
        # Initialize Terraform
        echo "Initializing Terraform..."
        terraform init
        
        # Plan
        echo ""
        echo "Generating Terraform plan..."
        terraform plan -out=tfplan
        
        # Ask for confirmation
        echo ""
        read -p "Apply Terraform configuration? (yes/no): " confirm
        
        if [ "$confirm" = "yes" ]; then
            terraform apply tfplan
            echo ""
            echo -e "${GREEN}✓ AWS services configured successfully${NC}"
            echo ""
            echo "Terraform outputs:"
            terraform output
        else
            echo "Terraform apply cancelled"
        fi
        ;;
        
    2)
        echo ""
        echo "Setting up with Python configuration script..."
        
        cd python/
        
        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment
        source venv/bin/activate
        
        # Install dependencies
        echo "Installing dependencies..."
        pip install boto3 python-dotenv
        
        # Run configuration script
        echo ""
        echo "Running AWS services configuration..."
        python aws_services_config.py
        
        echo ""
        echo -e "${GREEN}✓ Configuration script completed${NC}"
        ;;
        
    3)
        echo ""
        echo "Manual setup selected"
        echo ""
        echo "Please follow the AWS Services Configuration Guide:"
        echo "  File: AWS_SERVICES_CONFIGURATION.md"
        echo ""
        echo "Services to configure:"
        echo "  1. Amazon Cognito User Pool"
        echo "  2. Amazon Bedrock (request model access)"
        echo "  3. Amazon SNS Topics (4 topics)"
        echo "  4. Redis ElastiCache Cluster"
        echo ""
        echo "After configuration, update .env.production with service details"
        ;;
        
    4)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Update .env.production with service configuration"
echo "2. Test services using provided test scripts"
echo "3. Configure monitoring and alerts"
echo "4. Review security settings"
echo ""
echo "Documentation: AWS_SERVICES_CONFIGURATION.md"
echo ""
