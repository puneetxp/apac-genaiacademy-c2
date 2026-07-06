#!/bin/bash
# EC2 Server Setup Script
# Run this on a fresh EC2 instance to set it up for the application
# Usage: curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/main/scripts/setup-ec2-server.sh | bash

set -e

# Detect server type
if [ "$1" = "backend" ] || [ "$1" = "frontend" ]; then
    SERVER_TYPE="$1"
else
    echo "Usage: $0 [backend|frontend]"
    echo "Or set SERVER_TYPE environment variable"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🚀 Setting up EC2 server as: $SERVER_TYPE${NC}"
echo ""

# Update system
echo -e "${BLUE}📦 Updating system...${NC}"
sudo dnf update -y

# Install common packages
echo -e "${BLUE}📦 Installing common packages...${NC}"
sudo dnf install -y git wget curl vim htop

# Setup based on server type
if [ "$SERVER_TYPE" = "backend" ]; then
    echo -e "${BLUE}🐍 Setting up Backend Server...${NC}"
    
    # Install Python 3.11
    sudo dnf install -y python3.11 python3.11-pip python3.11-devel
    
    # Install PostgreSQL client
    sudo dnf install -y postgresql15 postgresql15-devel
    
    # Install build tools
    sudo dnf install -y gcc gcc-c++ make
    
    # Install Nginx
    sudo dnf install -y nginx
    
    # Create application user
    sudo useradd -m -s /bin/bash cropsense || true
    
    # Create application directory
    sudo mkdir -p /opt/cropsense/backend/python
    sudo chown -R cropsense:cropsense /opt/cropsense
    
    # Setup Python virtual environment
    sudo su - cropsense -c "
        cd /opt/cropsense/backend/python
        python3.11 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
    "
    
    # Create systemd service
    sudo tee /etc/systemd/system/cropsense-backend.service > /dev/null << 'EOF'
[Unit]
Description=CropSense FastAPI Backend
After=network.target

[Service]
Type=simple
User=cropsense
Group=cropsense
WorkingDirectory=/opt/cropsense/backend/python/cropsense-ai/python
Environment="PATH=/opt/cropsense/backend/python/venv/bin"
ExecStart=/opt/cropsense/backend/python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Configure Nginx
    sudo tee /etc/nginx/conf.d/cropsense-backend.conf > /dev/null << 'EOF'
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}
EOF
    
    # Enable services
    sudo systemctl daemon-reload
    sudo systemctl enable nginx
    sudo systemctl start nginx
    
    echo -e "${GREEN}✅ Backend server setup complete${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Deploy your code: ./deploy-to-ec2.sh"
    echo "2. Configure .env file in /opt/cropsense/backend/python/cropsense-ai/python/"
    echo "3. Start service: sudo systemctl start cropsense-backend"
    
elif [ "$SERVER_TYPE" = "frontend" ]; then
    echo -e "${BLUE}⚛️  Setting up Frontend Server...${NC}"
    
    # Install Node.js 20.x
    curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
    sudo dnf install -y nodejs
    
    # Install Nginx
    sudo dnf install -y nginx
    
    # Create application user
    sudo useradd -m -s /bin/bash cropsense || true
    
    # Create application directory
    sudo mkdir -p /opt/cropsense/frontend/solidjs/dist
    sudo chown -R cropsense:cropsense /opt/cropsense
    
    # Configure Nginx for SPA
    sudo tee /etc/nginx/conf.d/cropsense-frontend.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    root /opt/cropsense/frontend/solidjs/dist;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}
EOF
    
    # Create placeholder index.html
    sudo tee /opt/cropsense/frontend/solidjs/dist/index.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CropSense AI - Rural Farming Platform</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 3rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 3rem; margin-bottom: 1rem; }
        p { font-size: 1.2rem; opacity: 0.9; }
        .status {
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌾 CropSense AI</h1>
        <p>Rural Farming Platform</p>
        <div class="status">
            <p>✅ Server is ready</p>
            <p>📦 Deploy your application to get started</p>
        </div>
    </div>
</body>
</html>
EOF
    
    sudo chown -R cropsense:cropsense /opt/cropsense/frontend
    
    # Enable and start Nginx
    sudo systemctl enable nginx
    sudo systemctl start nginx
    
    echo -e "${GREEN}✅ Frontend server setup complete${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Deploy your code: ./deploy-to-ec2.sh"
    echo "2. Configure .env file in /opt/cropsense/frontend/solidjs/"
fi

# Install CloudWatch Agent
echo -e "${BLUE}📊 Installing CloudWatch Agent...${NC}"
wget -q https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm
rm -f ./amazon-cloudwatch-agent.rpm

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Server IP: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "Test: curl http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/health"
echo ""
