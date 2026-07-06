#!/bin/bash

# Quick start script for the backend server
# Handles activation and server startup

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Rural Farming Platform Backend${NC}"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
    echo ""
    echo "Please run the setup script first:"
    echo "  ./setup_python314.sh"
    echo ""
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

# Check if FastAPI is installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠ FastAPI not found${NC}"
    echo ""
    echo "Please run the setup script first:"
    echo "  ./setup_python314.sh"
    echo ""
    exit 1
fi

# Check database connection
echo -e "${BLUE}Checking database connection...${NC}"
if psql -U puneetsharma -d cropsense_dev -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Database connection OK"
else
    echo -e "${YELLOW}⚠ Database connection failed${NC}"
    echo "  Make sure PostgreSQL is running"
    echo ""
fi

# Start server
echo ""
echo -e "${GREEN}✓${NC} Starting backend server..."
echo ""
echo "  URL: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
