#!/bin/bash
# Backend EC2 Instance Setup Script
# Installs and configures Python FastAPI backend

set -e

# Update system
echo "Updating system packages..."
dnf update -y

# Install required packages
echo "Installing required packages..."
dnf install -y \
    git \
    python3.11 \
    python3.11-pip \
    python3.11-devel \
    postgresql15 \
    postgresql15-devel \
    gcc \
    nginx \
    supervisor

# Install Node.js (for any build tools)
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
dnf install -y nodejs

# Create application user
echo "Creating application user..."
useradd -m -s /bin/bash cropsense || true

# Create application directory
echo "Setting up application directory..."
mkdir -p /opt/cropsense/backend
chown -R cropsense:cropsense /opt/cropsense

# Clone repository (replace with your actual repo)
echo "Cloning application repository..."
cd /opt/cropsense
# TODO: Replace with actual git clone command
# git clone https://github.com/your-org/cropsense-ai.git .

# For now, we'll create a placeholder
mkdir -p /opt/cropsense/backend/python
cd /opt/cropsense/backend/python

# Create virtual environment
echo "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
# TODO: Copy requirements.txt from your repo
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
boto3==1.29.7
redis==5.0.1
httpx==0.25.2
python-dotenv==1.0.0
pgvector==0.2.3
EOF

pip install -r requirements.txt

# Create .env file
echo "Creating environment configuration..."
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://${db_username}:${db_password}@${db_host}:${db_port}/${db_name}
DB_HOST=${db_host}
DB_PORT=${db_port}
DB_NAME=${db_name}
DB_USER=${db_username}
DB_PASSWORD=${db_password}

# AWS Configuration
AWS_REGION=${aws_region}
AWS_S3_BUCKET=${s3_bucket}

# Cognito Configuration
COGNITO_USER_POOL_ID=${cognito_user_pool_id}
COGNITO_APP_CLIENT_ID=${cognito_app_client_id}
COGNITO_APP_CLIENT_SECRET=${cognito_app_client_secret}

# Application Configuration
ENVIRONMENT=${environment}
DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_ORIGINS=*

# Redis Configuration (if using ElastiCache)
# REDIS_URL=redis://your-elasticache-endpoint:6379

# API Configuration
API_V1_PREFIX=/api/v1
EOF

chown cropsense:cropsense .env
chmod 600 .env

# Create systemd service for FastAPI
echo "Creating systemd service..."
cat > /etc/systemd/system/cropsense-backend.service << 'EOF'
[Unit]
Description=CropSense FastAPI Backend
After=network.target

[Service]
Type=simple
User=cropsense
Group=cropsense
WorkingDirectory=/opt/cropsense/backend/python
Environment="PATH=/opt/cropsense/backend/python/venv/bin"
ExecStart=/opt/cropsense/backend/python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx as reverse proxy
echo "Configuring Nginx..."
cat > /etc/nginx/conf.d/cropsense-backend.conf << 'EOF'
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
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable and start services
echo "Starting services..."
systemctl daemon-reload
systemctl enable nginx
systemctl enable cropsense-backend
systemctl start nginx
systemctl start cropsense-backend

# Setup CloudWatch Logs Agent
echo "Setting up CloudWatch Logs..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm

cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json << EOF
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "/aws/cropsense-ai/backend",
            "log_stream_name": "nginx-access"
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "/aws/cropsense-ai/backend",
            "log_stream_name": "nginx-error"
          }
        ]
      }
    }
  }
}
EOF

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json

echo "Backend setup complete!"
echo "Backend API should be available at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
