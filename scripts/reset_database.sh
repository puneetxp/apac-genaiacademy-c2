#!/bin/bash

# Database Reset Script for Rural Farming Platform
# This script drops and recreates the database, then runs all migrations

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Rural Farming Platform - Database Reset ===${NC}\n"

# Load environment variables
if [ -f "python/.env" ]; then
    export $(cat python/.env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: python/.env file not found${NC}"
    exit 1
fi

# Database connection details
DB_HOST="${POSTGRES_SERVER:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-cropsense_dev}"

echo -e "${YELLOW}Database Configuration:${NC}"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  User: $DB_USER"
echo "  Database: $DB_NAME"
echo ""

# Confirm action
read -p "This will DELETE all data in the database. Are you sure? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Operation cancelled${NC}"
    exit 0
fi

echo -e "\n${YELLOW}Step 1: Dropping existing database...${NC}"
PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || {
    echo -e "${RED}Warning: Could not drop database (it may not exist)${NC}"
}

echo -e "${GREEN}✓ Database dropped${NC}\n"

echo -e "${YELLOW}Step 2: Creating fresh database...${NC}"
PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" || {
    echo -e "${RED}Error: Failed to create database${NC}"
    exit 1
}

echo -e "${GREEN}✓ Database created${NC}\n"

echo -e "${YELLOW}Step 3: Installing pgvector extension...${NC}"
PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;" || {
    echo -e "${YELLOW}Warning: Could not install pgvector extension (may not be available)${NC}"
}

echo -e "${GREEN}✓ Extensions installed${NC}\n"

echo -e "${YELLOW}Step 4: Running Alembic migrations...${NC}"
cd python
alembic upgrade head || {
    echo -e "${RED}Error: Migration failed${NC}"
    exit 1
}
cd ..

echo -e "${GREEN}✓ Migrations completed${NC}\n"

echo -e "${GREEN}=== Database reset completed successfully! ===${NC}"
echo -e "\nYou can now start the application with:"
echo -e "  ${YELLOW}cd python && uvicorn app.main:app --reload${NC}\n"
