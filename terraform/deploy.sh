#!/bin/bash
# Quick Deployment Script for Rural Farming Platform
# This script automates the Terraform deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${NC}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        echo "Visit: https://www.terraform.io/downloads"
        exit 1
    fi
    print_success "Terraform found: $(terraform version | head -n1)"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        echo "Visit: https://aws.amazon.com/cli/"
        exit 1
    fi
    print_success "AWS CLI found: $(aws --version)"
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    print_success "AWS credentials configured"
    
    # Check SSH key
    if [ ! -f ~/.ssh/cropsense-deployer.pub ]; then
        print_warning "SSH key not found at ~/.ssh/cropsense-deployer.pub"
        read -p "Generate new SSH key? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ssh-keygen -t rsa -b 4096 -f ~/.ssh/cropsense-deployer -C "cropsense-deployer" -N ""
            print_success "SSH key generated"
        else
            print_error "SSH key required for deployment"
            exit 1
        fi
    fi
    print_success "SSH key found"
}

# Initialize Terraform
init_terraform() {
    print_info "Initializing Terraform..."
    terraform init
    print_success "Terraform initialized"
}

# Validate configuration
validate_config() {
    print_info "Validating Terraform configuration..."
    
    if [ ! -f terraform.tfvars ]; then
        print_error "terraform.tfvars not found!"
        print_info "Creating terraform.tfvars from template..."
        
        # Get SSH public key
        SSH_KEY=$(cat ~/.ssh/cropsense-deployer.pub)
        
        # Create terraform.tfvars
        cat > terraform.tfvars << EOF
# AWS Configuration
aws_region   = "ap-south-1"
environment  = "development"
project_name = "cropsense-ai"

# Database Configuration
db_name                  = "cropsense_dev"
db_username              = "admin"
db_password              = "CHANGE_THIS_PASSWORD_$(openssl rand -hex 8)"
db_engine_version        = "14.10"
db_instance_class        = "db.t3.micro"
db_allocated_storage     = 20
db_max_allocated_storage = 100
db_backup_retention_days = 7

# S3 Configuration
s3_bucket_name = "cropsense-dev-bucket-$(date +%s)"

# CORS Configuration
allowed_origins = [
  "http://localhost:3000",
  "http://localhost:5173"
]

# EC2 Configuration
backend_instance_type  = "t3.medium"
frontend_instance_type = "t3.small"
use_elastic_ips        = false

# SSH Configuration
ssh_public_key = "$SSH_KEY"

# Network Configuration
vpc_id             = ""
private_subnet_ids = []
public_subnet_ids  = []
app_cidr_blocks    = ["10.0.0.0/16"]
EOF
        
        print_success "terraform.tfvars created"
        print_warning "Please review and update terraform.tfvars before continuing"
        print_info "Especially change the db_password and s3_bucket_name"
        read -p "Press Enter to continue after reviewing terraform.tfvars..."
    fi
    
    terraform validate
    print_success "Configuration validated"
}

# Plan deployment
plan_deployment() {
    print_info "Creating deployment plan..."
    terraform plan -out=tfplan
    print_success "Deployment plan created"
    
    print_warning "Review the plan above carefully"
    read -p "Continue with deployment? (yes/no) " -r
    if [[ ! $REPLY =~ ^yes$ ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
}

# Apply deployment
apply_deployment() {
    print_info "Applying deployment..."
    print_warning "This will take 10-15 minutes..."
    
    terraform apply tfplan
    
    print_success "Deployment complete!"
}

# Show outputs
show_outputs() {
    print_info "Deployment Information:"
    echo ""
    
    BACKEND_IP=$(terraform output -raw backend_public_ip 2>/dev/null || echo "N/A")
    FRONTEND_IP=$(terraform output -raw frontend_public_ip 2>/dev/null || echo "N/A")
    BACKEND_URL=$(terraform output -raw backend_url 2>/dev/null || echo "N/A")
    FRONTEND_URL=$(terraform output -raw frontend_url 2>/dev/null || echo "N/A")
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Backend Server:"
    echo "  Public IP:  $BACKEND_IP"
    echo "  API URL:    $BACKEND_URL"
    echo "  SSH:        ssh -i ~/.ssh/cropsense-deployer ec2-user@$BACKEND_IP"
    echo ""
    echo "Frontend Server:"
    echo "  Public IP:  $FRONTEND_IP"
    echo "  App URL:    $FRONTEND_URL"
    echo "  SSH:        ssh -i ~/.ssh/cropsense-deployer ec2-user@$FRONTEND_IP"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Save outputs to file
    terraform output > deployment-outputs.txt
    print_success "Outputs saved to deployment-outputs.txt"
    
    # Save sensitive config
    terraform output -raw env_file_config > deployment-config.txt 2>/dev/null || true
    if [ -f deployment-config.txt ]; then
        print_success "Configuration saved to deployment-config.txt"
        chmod 600 deployment-config.txt
    fi
}

# Post-deployment instructions
post_deployment() {
    echo ""
    print_info "Next Steps:"
    echo ""
    echo "1. Wait 2-3 minutes for EC2 instances to complete initialization"
    echo ""
    echo "2. Test backend health:"
    echo "   curl http://$BACKEND_IP:8000/health"
    echo ""
    echo "3. Test frontend:"
    echo "   open http://$FRONTEND_IP"
    echo ""
    echo "4. Deploy your application code:"
    echo "   See EC2_DEPLOYMENT_GUIDE.md for detailed instructions"
    echo ""
    echo "5. Configure monitoring:"
    echo "   aws sns subscribe --topic-arn <TOPIC_ARN> --protocol email --notification-endpoint your-email@example.com"
    echo ""
    print_warning "Remember to:"
    echo "  - Change default passwords"
    echo "  - Configure domain names"
    echo "  - Set up SSL certificates"
    echo "  - Deploy application code"
    echo ""
}

# Main execution
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Rural Farming Platform - AWS Deployment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    check_prerequisites
    echo ""
    
    init_terraform
    echo ""
    
    validate_config
    echo ""
    
    plan_deployment
    echo ""
    
    apply_deployment
    echo ""
    
    show_outputs
    echo ""
    
    post_deployment
    
    print_success "Deployment script completed!"
}

# Run main function
main
