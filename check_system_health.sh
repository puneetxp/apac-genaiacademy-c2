#!/bin/bash

# System Health Check
# Verifies all components are working before running tests

echo "=========================================="
echo "System Health Check"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

HEALTH_OK=true

# Check 1: Backend Server
echo "1. Checking Backend Server (port 8000)..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ Backend is running${NC}"
else
    echo -e "${RED}   ✗ Backend is NOT running${NC}"
    echo "   Start with: cd python && uvicorn app.main:app --reload"
    HEALTH_OK=false
fi

# Check 2: Frontend Server
echo ""
echo "2. Checking Frontend Server (port 3000)..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ Frontend is running${NC}"
else
    echo -e "${RED}   ✗ Frontend is NOT running${NC}"
    echo "   Start with: cd solidjs && npm run dev"
    HEALTH_OK=false
fi

# Check 3: PostgreSQL Database
echo ""
echo "3. Checking PostgreSQL Database..."
if psql -U puneetsharma -d cropsense_dev -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ Database is accessible${NC}"
    
    # Check table count
    TABLE_COUNT=$(psql -U puneetsharma -d cropsense_dev -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null | tr -d ' ')
    echo "   Tables: $TABLE_COUNT"
else
    echo -e "${RED}   ✗ Database is NOT accessible${NC}"
    echo "   Check PostgreSQL is running: brew services list | grep postgresql"
    HEALTH_OK=false
fi

# Check 4: Test User Exists
echo ""
echo "4. Checking Test User..."
USER_EXISTS=$(psql -U puneetsharma -d cropsense_dev -t -c "SELECT COUNT(*) FROM users WHERE username = 'puneetxp'" 2>/dev/null | tr -d ' ')
if [ "$USER_EXISTS" = "1" ]; then
    echo -e "${GREEN}   ✓ Test user 'puneetxp' exists${NC}"
else
    echo -e "${YELLOW}   ⚠ Test user 'puneetxp' not found${NC}"
    echo "   User will be created during tests"
fi

# Check 5: Backend API Endpoints
echo ""
echo "5. Checking Backend API Endpoints..."

# Auth endpoint
if curl -s http://localhost:8000/api/v1/auth/signin -X POST -H "Content-Type: application/json" -d '{}' | grep -q "detail"; then
    echo -e "${GREEN}   ✓ Auth API responding${NC}"
else
    echo -e "${RED}   ✗ Auth API not responding${NC}"
    HEALTH_OK=false
fi

# Farms endpoint (requires auth, so 401 is expected)
if curl -s http://localhost:8000/api/v1/farms/my-farms | grep -q "detail"; then
    echo -e "${GREEN}   ✓ Farms API responding${NC}"
else
    echo -e "${RED}   ✗ Farms API not responding${NC}"
    HEALTH_OK=false
fi

# Check 6: Frontend Pages
echo ""
echo "6. Checking Frontend Pages..."

# Home page
if curl -s http://localhost:3000 | grep -q "CropSense"; then
    echo -e "${GREEN}   ✓ Home page loads${NC}"
else
    echo -e "${RED}   ✗ Home page not loading${NC}"
    HEALTH_OK=false
fi

# Check 7: E2E Test Dependencies
echo ""
echo "7. Checking E2E Test Dependencies..."

if command -v npx > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ npx is installed${NC}"
else
    echo -e "${RED}   ✗ npx is NOT installed${NC}"
    HEALTH_OK=false
fi

if [ -d "cropsense-ai/e2e/node_modules/@playwright" ]; then
    echo -e "${GREEN}   ✓ Playwright is installed${NC}"
else
    echo -e "${YELLOW}   ⚠ Playwright might not be installed${NC}"
    echo "   Install with: cd e2e && npm install"
fi

# Summary
echo ""
echo "=========================================="
if [ "$HEALTH_OK" = true ]; then
    echo -e "${GREEN}✓ System Health: GOOD${NC}"
    echo "=========================================="
    echo ""
    echo "Ready to run tests!"
    echo "  cd cropsense-ai/e2e"
    echo "  ./run_comprehensive_tests.sh"
    exit 0
else
    echo -e "${RED}✗ System Health: ISSUES FOUND${NC}"
    echo "=========================================="
    echo ""
    echo "Please fix the issues above before running tests."
    exit 1
fi
