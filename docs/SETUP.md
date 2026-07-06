# Setup Guide - Rural Farming Platform

Complete setup instructions for local development and production deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Database Setup](#database-setup)
4. [AWS Services Configuration](#aws-services-configuration)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Python 3.14.3** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
- **Redis 5+** - [Download](https://redis.io/download)
- **PHP 8.0+** - [Download](https://www.php.net/downloads) (for code generation)
- **Git** - [Download](https://git-scm.com/downloads)

### AWS Account

You'll need an AWS account with access to:
- Amazon Cognito
- Amazon Bedrock
- Amazon SNS
- Amazon RDS (for production)
- Amazon ElastiCache (for production)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rural-farming-platform
```

### 2. Backend Setup (Python/FastAPI)

#### Create Virtual Environment

```bash
cd python
python3.14 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Application
APP_NAME="CropSense AI"
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-min-32-chars-change-this

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=cropsense_dev
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# AWS Configuration
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Amazon Cognito
COGNITO_USER_POOL_ID=your_pool_id
COGNITO_CLIENT_ID=your_client_id
COGNITO_CLIENT_SECRET=your_client_secret
COGNITO_REGION=ap-south-1

# Amazon SNS
SNS_ENABLED=true
SNS_TOPIC_ARN_BOOKING_NOTIFICATIONS=your_topic_arn
SNS_TOPIC_ARN_BUYER_INTEREST=your_topic_arn
SNS_TOPIC_ARN_STRATEGY_REMINDERS=your_topic_arn
SNS_TOPIC_ARN_WEATHER_ALERTS=your_topic_arn
SNS_TOPIC_ARN_HARVEST_REMINDERS=your_topic_arn

# S3
S3_BUCKET_NAME=your-bucket-name
S3_REGION=ap-south-1
```

### 3. Frontend Setup (SolidJS)

```bash
cd solidjs
npm install
```

Configure frontend environment:

```bash
cp .env.example .env
```

Edit `solidjs/.env`:

```bash
VITE_API_URL=http://localhost:8000
VITE_AWS_REGION=ap-south-1
VITE_COGNITO_USER_POOL_ID=your_pool_id
VITE_COGNITO_CLIENT_ID=your_client_id
```

## Database Setup

### 1. Install PostgreSQL

#### macOS (using Homebrew)

```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql-14 postgresql-contrib
sudo systemctl start postgresql
```

#### Windows

Download and install from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE cropsense_dev;

# Create user (optional)
CREATE USER cropsense_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cropsense_dev TO cropsense_admin;

# Exit
\q
```

### 3. Install pgvector Extension (Optional)

```bash
# macOS
brew install pgvector

# Ubuntu/Debian
sudo apt install postgresql-14-pgvector

# Then in psql:
psql -U postgres -d cropsense_dev
CREATE EXTENSION vector;
\q
```

### 4. Run Migrations

```bash
cd python
alembic upgrade head
```

### 5. Reset Database (if needed)

To completely reset the database:

```bash
cd rural-farming-platform
./scripts/reset_database.sh
```

## AWS Services Configuration

### 1. Amazon Cognito Setup

#### Create User Pool

```bash
aws cognito-idp create-user-pool \
  --pool-name cropsense-users \
  --auto-verified-attributes email phone_number \
  --mfa-configuration OPTIONAL \
  --policies '{
    "PasswordPolicy": {
      "MinimumLength": 8,
      "RequireUppercase": true,
      "RequireLowercase": true,
      "RequireNumbers": true,
      "RequireSymbols": true
    }
  }'
```

#### Create User Pool Client

```bash
aws cognito-idp create-user-pool-client \
  --user-pool-id <your-pool-id> \
  --client-name cropsense-client \
  --generate-secret \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH ALLOW_USER_SRP_AUTH
```

### 2. Amazon SNS Setup

#### Create Topics

```bash
# Booking notifications
aws sns create-topic --name cropsense-booking-notifications

# Buyer interests
aws sns create-topic --name cropsense-buyer-interests

# Strategy reminders
aws sns create-topic --name cropsense-strategy-reminders

# Weather alerts
aws sns create-topic --name cropsense-weather-alerts

# Harvest reminders
aws sns create-topic --name cropsense-harvest-reminders
```

#### Subscribe to Topics

```bash
# Email subscription
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-south-1:ACCOUNT_ID:cropsense-booking-notifications \
  --protocol email \
  --notification-endpoint your-email@example.com

# SMS subscription
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-south-1:ACCOUNT_ID:cropsense-booking-notifications \
  --protocol sms \
  --notification-endpoint +919876543210
```

### 3. Amazon Bedrock Setup

Enable Bedrock models in your AWS account:

1. Go to AWS Console → Bedrock
2. Navigate to "Model access"
3. Request access to:
   - Claude 3 Sonnet
   - Claude 3 Haiku
   - Titan Text models

### 4. S3 Bucket Setup

```bash
# Create bucket
aws s3 mb s3://cropsense-dev-bucket --region ap-south-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket cropsense-dev-bucket \
  --versioning-configuration Status=Enabled

# Configure CORS
aws s3api put-bucket-cors \
  --bucket cropsense-dev-bucket \
  --cors-configuration file://s3-cors.json
```

`s3-cors.json`:
```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["http://localhost:5173", "http://localhost:3000"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

## Running the Application

### 1. Start Redis

```bash
# macOS
brew services start redis

# Ubuntu/Debian
sudo systemctl start redis

# Windows
redis-server
```

### 2. Start Backend (FastAPI)

```bash
cd py