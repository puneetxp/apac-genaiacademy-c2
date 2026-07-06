#!/bin/bash
# Frontend EC2 Instance Setup Script
# Installs and configures SolidJS frontend

set -e

# Update system
echo "Updating system packages..."
dnf update -y

# Install required packages
echo "Installing required packages..."
dnf install -y \
    git \
    nginx

# Install Node.js 20.x
echo "Installing Node.js..."
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
dnf install -y nodejs

# Create application user
echo "Creating application user..."
useradd -m -s /bin/bash cropsense || true

# Create application directory
echo "Setting up application directory..."
mkdir -p /opt/cropsense/frontend
chown -R cropsense:cropsense /opt/cropsense

# Clone repository (replace with your actual repo)
echo "Cloning application repository..."
cd /opt/cropsense
# TODO: Replace with actual git clone command
# git clone https://github.com/your-org/cropsense-ai.git .

# For now, we'll create a placeholder
mkdir -p /opt/cropsense/frontend/solidjs
cd /opt/cropsense/frontend/solidjs

# Create .env file for frontend
echo "Creating environment configuration..."
cat > .env << EOF
VITE_API_URL=${backend_url}/api/v1
VITE_ENVIRONMENT=${environment}
EOF

chown cropsense:cropsense .env

# Install dependencies and build
echo "Installing dependencies..."
# TODO: Copy package.json from your repo
# npm install

# Build production bundle
echo "Building production bundle..."
# npm run build

# Configure Nginx for SPA
echo "Configuring Nginx..."
cat > /etc/nginx/conf.d/cropsense-frontend.conf << 'EOF'
server {
    listen 80;
    server_name _;
    
    root /opt/cropsense/frontend/solidjs/dist;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # SPA routing - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Create placeholder index.html if build doesn't exist
mkdir -p /opt/cropsense/frontend/solidjs/dist
cat > /opt/cropsense/frontend/solidjs/dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CropSense AI - Rural Farming Platform</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
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
            <p>✅ Frontend server is running</p>
            <p>📦 Waiting for application deployment...</p>
        </div>
    </div>
</body>
</html>
EOF

chown -R cropsense:cropsense /opt/cropsense/frontend

# Enable and start Nginx
echo "Starting Nginx..."
systemctl enable nginx
systemctl start nginx

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
            "log_group_name": "/aws/cropsense-ai/frontend",
            "log_stream_name": "nginx-access"
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "/aws/cropsense-ai/frontend",
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

echo "Frontend setup complete!"
echo "Frontend should be available at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
