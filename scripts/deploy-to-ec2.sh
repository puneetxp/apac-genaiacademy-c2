#!/bin/bash
# Deploy Rural Farming Platform to EC2 from GitHub
# This script deploys both backend and frontend to EC2 instances

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="https://github.com/YOUR_USERNAME/cropsense-ai.git"
GITHUB_BRANCH="main"
SSH_KEY="~/.ssh/cropsense-deployer"

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
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check SSH key
    if [ ! -f "$SSH_KEY" ]; then
        print_error "SSH key not found at $SSH_KEY"
        exit 1
    fi
    print_success "SSH key found"
    
    # Check if backend IP is provided
    if [ -z "$BACKEND_IP" ]; then
        print_error "BACKEND_IP environment variable not set"
        echo "Usage: BACKEND_IP=x.x.x.x FRONTEND_IP=y.y.y.y $0"
        exit 1
    fi
    print_success "Backend IP: $BACKEND_IP"
    
    # Check if frontend IP is provided
    if [ -z "$FRONTEND_IP" ]; then
        print_error "FRONTEND_IP environment variable not set"
        echo "Usage: BACKEND_IP=x.x.x.x FRONTEND_IP=y.y.y.y $0"
        exit 1
    fi
    print_success "Frontend IP: $FRONTEND_IP"
    
    # Test SSH connection to backend
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no ec2-user@"$BACKEND_IP" "echo 'SSH OK'" &>/dev/null; then
        print_error "Cannot connect to backend server via SSH"
        exit 1
    fi
    print_success "Backend SSH connection OK"
    
    # Test SSH connection to frontend
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no ec2-user@"$FRONTEND_IP" "echo 'SSH OK'" &>/dev/null; then
        print_error "Cannot connect to frontend server via SSH"
        exit 1
    fi
    print_success "Frontend SSH connection OK"
}

# Deploy backend
deploy_backend() {
    print_header "Deploying Backend (FastAPI)"
    
    print_info "Connecting to backend server..."
    
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@"$BACKEND_IP" << 'ENDSSH'
set -e

echo "📦 Updating system packages..."
sudo dnf update -y

echo "🔧 Installing dependencies..."
sudo dnf install -y git python3.11 python3.11-pip python3.11-devel postgresql15 gcc

echo "👤 Switching to application user..."
sudo su - cropsense << 'ENDSU'
set -e

cd /opt/cropsense/backend

echo "📥 Cloning/updating repository..."
if [ -d "cropsense-ai" ]; then
    cd cropsense-ai
    git fetch origin
    git reset --hard origin/main
    git pull origin main
else
    git clone GITHUB_REPO cropsense-ai
    cd cropsense-ai
fi

cd python

echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi

source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ Running database migrations..."
if [ -f "alembic.ini" ]; then
    alembic upgrade head
else
    echo "⚠️  No alembic.ini found, skipping migrations"
fi

echo "✅ Backend code updated"
ENDSU

echo "🔄 Restarting backend service..."
sudo systemctl restart cropsense-backend

echo "🔍 Checking service status..."
sleep 3
sudo systemctl status cropsense-backend --no-pager

echo "✅ Backend deployment complete"
ENDSSH
    
    print_success "Backend deployed successfully"
}

# Deploy frontend
deploy_frontend() {
    print_header "Deploying Frontend (SolidJS)"
    
    print_info "Connecting to frontend server..."
    
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@"$FRONTEND_IP" << ENDSSH
set -e

echo "📦 Updating system packages..."
sudo dnf update -y

echo "🔧 Installing dependencies..."
sudo dnf install -y git

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
    sudo dnf install -y nodejs
fi

echo "👤 Switching to application user..."
sudo su - cropsense << 'ENDSU'
set -e

cd /opt/cropsense/frontend

echo "📥 Cloning/updating repository..."
if [ -d "cropsense-ai" ]; then
    cd cropsense-ai
    git fetch origin
    git reset --hard origin/main
    git pull origin main
else
    git clone $GITHUB_REPO cropsense-ai
    cd cropsense-ai
fi

cd solidjs

echo "📦 Installing Node.js dependencies..."
npm install

echo "🏗️  Building production bundle..."
npm run build

echo "📋 Copying build to web root..."
sudo rm -rf /opt/cropsense/frontend/solidjs/dist
sudo cp -r dist /opt/cropsense/frontend/solidjs/

echo "✅ Frontend code updated"
ENDSU

echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

echo "🔍 Checking Nginx status..."
sudo systemctl status nginx --no-pager

echo "✅ Frontend deployment complete"
ENDSSH
    
    print_success "Frontend deployed successfully"
}

# Test deployment
test_deployment() {
    print_header "Testing Deployment"
    
    # Test backend
    print_info "Testing backend API..."
    if curl -f -s "http://$BACKEND_IP:8000/health" > /dev/null; then
        print_success "Backend health check passed"
    else
        print_warning "Backend health check failed (service may still be starting)"
    fi
    
    # Test frontend
    print_info "Testing frontend..."
    if curl -f -s "http://$FRONTEND_IP" > /dev/null; then
        print_success "Frontend health check passed"
    else
        print_warning "Frontend health check failed"
    fi
}

# Show deployment info
show_info() {
    print_header "Deployment Complete"
    
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "Backend API:"
    echo "  URL: http://$BACKEND_IP:8000"
    echo "  Docs: http://$BACKEND_IP:8000/docs"
    echo "  Health: http://$BACKEND_IP:8000/health"
    echo ""
    echo "Frontend App:"
    echo "  URL: http://$FRONTEND_IP"
    echo ""
    echo "SSH Access:"
    echo "  Backend: ssh -i $SSH_KEY ec2-user@$BACKEND_IP"
    echo "  Frontend: ssh -i $SSH_KEY ec2-user@$FRONTEND_IP"
    echo ""
    echo "View Logs:"
    echo "  Backend: ssh -i $SSH_KEY ec2-user@$BACKEND_IP 'sudo journalctl -u cropsense-backend -f'"
    echo "  Frontend: ssh -i $SSH_KEY ec2-user@$FRONTEND_IP 'sudo tail -f /var/log/nginx/error.log'"
    echo ""
}

# Main execution
main() {
    print_header "Rural Farming Platform - EC2 Deployment"
    
    # Get GitHub repo from user if not set
    if [ "$GITHUB_REPO" = "https://github.com/YOUR_USERNAME/cropsense-ai.git" ]; then
        read -p "Enter your GitHub repository URL: " GITHUB_REPO
    fi
    
    check_prerequisites
    
    # Ask what to deploy
    echo ""
    echo "What would you like to deploy?"
    echo "1) Backend only"
    echo "2) Frontend only"
    echo "3) Both (default)"
    read -p "Enter choice [1-3]: " choice
    
    case $choice in
        1)
            deploy_backend
            ;;
        2)
            deploy_frontend
            ;;
        *)
            deploy_backend
            deploy_frontend
            ;;
    esac
    
    test_deployment
    show_info
    
    print_success "All done! 🚀"
}

# Run main function
main
