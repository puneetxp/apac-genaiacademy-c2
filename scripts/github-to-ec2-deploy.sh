#!/bin/bash
# GitHub to EC2 Deployment Script
# Deploys Rural Farming Platform from GitHub to EC2 instances

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
GITHUB_REPO="${GITHUB_REPO:-https://github.com/YOUR_USERNAME/cropsense-ai.git}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
SSH_KEY="${SSH_KEY:-~/.ssh/cropsense-deployer}"
BACKEND_IP="${BACKEND_IP}"
FRONTEND_IP="${FRONTEND_IP}"

# Functions
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    if [ ! -f "$SSH_KEY" ]; then
        print_error "SSH key not found at $SSH_KEY"
        exit 1
    fi
    print_success "SSH key found"
    
    if [ -z "$BACKEND_IP" ]; then
        print_error "BACKEND_IP not set"
        echo "Usage: BACKEND_IP=x.x.x.x FRONTEND_IP=y.y.y.y GITHUB_REPO=your-repo $0"
        exit 1
    fi
    
    if [ -z "$FRONTEND_IP" ]; then
        print_error "FRONTEND_IP not set"
        exit 1
    fi
    
    print_success "Backend IP: $BACKEND_IP"
    print_success "Frontend IP: $FRONTEND_IP"
    print_success "GitHub Repo: $GITHUB_REPO"
}

# Deploy backend
deploy_backend() {
    print_header "Deploying Backend from GitHub"
    
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@"$BACKEND_IP" bash -s << ENDSSH
set -e

echo "📦 Updating system..."
sudo dnf update -y

echo "🔧 Installing dependencies..."
sudo dnf install -y git python3.11 python3.11-pip python3.11-devel postgresql15 gcc

echo "👤 Deploying as cropsense user..."
sudo -u cropsense bash << 'ENDSU'
set -e

cd /opt/cropsense/backend

# Clone or update repository
if [ -d "repo" ]; then
    echo "📥 Updating existing repository..."
    cd repo
    git fetch origin
    git reset --hard origin/$GITHUB_BRANCH
    git pull origin $GITHUB_BRANCH
else
    echo "📥 Cloning repository..."
    git clone -b $GITHUB_BRANCH $GITHUB_REPO repo
    cd repo
fi

cd python

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3.11 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
if [ -f "alembic.ini" ]; then
    echo "🗄️ Running migrations..."
    alembic upgrade head
fi

echo "✅ Backend code deployed"
ENDSU

# Restart service
echo "🔄 Restarting backend service..."
sudo systemctl restart cropsense-backend
sleep 3
sudo systemctl status cropsense-backend --no-pager

echo "✅ Backend deployment complete"
ENDSSH
    
    print_success "Backend deployed"
}

# Deploy frontend
deploy_frontend() {
    print_header "Deploying Frontend from GitHub"
    
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@"$FRONTEND_IP" bash -s << ENDSSH
set -e

echo "📦 Updating system..."
sudo dnf update -y

echo "🔧 Installing dependencies..."
sudo dnf install -y git

# Install Node.js if needed
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
    sudo dnf install -y nodejs
fi

echo "👤 Deploying as cropsense user..."
sudo -u cropsense bash << 'ENDSU'
set -e

cd /opt/cropsense/frontend

# Clone or update repository
if [ -d "repo" ]; then
    echo "📥 Updating existing repository..."
    cd repo
    git fetch origin
    git reset --hard origin/$GITHUB_BRANCH
    git pull origin $GITHUB_BRANCH
else
    echo "📥 Cloning repository..."
    git clone -b $GITHUB_BRANCH $GITHUB_REPO repo
    cd repo
fi

cd solidjs

# Install and build
echo "📦 Installing dependencies..."
npm install

echo "🏗️ Building production bundle..."
npm run build

# Copy to web root
echo "📋 Deploying build..."
sudo rm -rf /opt/cropsense/frontend/dist
sudo cp -r dist /opt/cropsense/frontend/

echo "✅ Frontend code deployed"
ENDSU

# Restart nginx
echo "🔄 Restarting nginx..."
sudo systemctl restart nginx
sudo systemctl status nginx --no-pager

echo "✅ Frontend deployment complete"
ENDSSH
    
    print_success "Frontend deployed"
}

# Test deployment
test_deployment() {
    print_header "Testing Deployment"
    
    sleep 5
    
    if curl -f -s "http://$BACKEND_IP:8000/health" > /dev/null; then
        print_success "Backend health check passed"
    else
        print_warning "Backend health check failed"
    fi
    
    if curl -f -s "http://$FRONTEND_IP" > /dev/null; then
        print_success "Frontend health check passed"
    else
        print_warning "Frontend health check failed"
    fi
}

# Main
main() {
    print_header "GitHub to EC2 Deployment"
    
    check_prerequisites
    
    echo ""
    echo "Deploy options:"
    echo "1) Backend only"
    echo "2) Frontend only"
    echo "3) Both (default)"
    read -p "Choice [1-3]: " choice
    
    case $choice in
        1) deploy_backend ;;
        2) deploy_frontend ;;
        *) deploy_backend && deploy_frontend ;;
    esac
    
    test_deployment
    
    print_header "Deployment Complete"
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "Backend: http://$BACKEND_IP:8000"
    echo "Frontend: http://$FRONTEND_IP"
    echo ""
    print_success "All done! 🚀"
}

main
