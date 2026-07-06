#!/bin/bash
# Quick Deploy Script - Deploy from GitHub to EC2 in one command
# Usage: ./quick-deploy.sh

set -e

# Configuration - UPDATE THESE VALUES
BACKEND_IP="${BACKEND_IP:-}"
FRONTEND_IP="${FRONTEND_IP:-}"
GITHUB_REPO="${GITHUB_REPO:-https://github.com/YOUR_USERNAME/cropsense-ai.git}"
SSH_KEY="${SSH_KEY:-~/.ssh/cropsense-deployer}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Quick Deploy to EC2${NC}"
echo ""

# Get IPs if not set
if [ -z "$BACKEND_IP" ]; then
    read -p "Enter Backend EC2 IP: " BACKEND_IP
fi

if [ -z "$FRONTEND_IP" ]; then
    read -p "Enter Frontend EC2 IP: " FRONTEND_IP
fi

if [ "$GITHUB_REPO" = "https://github.com/YOUR_USERNAME/cropsense-ai.git" ]; then
    read -p "Enter GitHub repo URL: " GITHUB_REPO
fi

echo ""
echo -e "${YELLOW}Deploying from: $GITHUB_REPO${NC}"
echo -e "${YELLOW}Backend: $BACKEND_IP${NC}"
echo -e "${YELLOW}Frontend: $FRONTEND_IP${NC}"
echo ""

# Deploy Backend
echo -e "${GREEN}📦 Deploying Backend...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@"$BACKEND_IP" "bash -s" << EOF
sudo su - cropsense -c "
cd /opt/cropsense/backend && \
[ -d cropsense-ai ] && cd cropsense-ai && git pull || git clone $GITHUB_REPO cropsense-ai && cd cropsense-ai && \
cd python && \
source venv/bin/activate && \
pip install -q -r requirements.txt && \
[ -f alembic.ini ] && alembic upgrade head || echo 'No migrations' && \
echo '✅ Backend code updated'
"
sudo systemctl restart cropsense-backend
echo "✅ Backend service restarted"
EOF

# Deploy Frontend
echo -e "${GREEN}📦 Deploying Frontend...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@"$FRONTEND_IP" "bash -s" << EOF
sudo su - cropsense -c "
cd /opt/cropsense/frontend && \
[ -d cropsense-ai ] && cd cropsense-ai && git pull || git clone $GITHUB_REPO cropsense-ai && cd cropsense-ai && \
cd solidjs && \
npm install && \
npm run build && \
sudo cp -r dist/* /opt/cropsense/frontend/solidjs/dist/ && \
echo '✅ Frontend built and deployed'
"
sudo systemctl restart nginx
echo "✅ Nginx restarted"
EOF

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "Backend: http://$BACKEND_IP:8000"
echo "Frontend: http://$FRONTEND_IP"
echo ""
