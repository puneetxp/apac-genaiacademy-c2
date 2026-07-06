#!/bin/bash

# Create Test User for E2E Tests
# This script creates the testfarmer user needed for E2E testing

set -e

echo "============================================================"
echo "Creating Test User for E2E Tests"
echo "============================================================"
echo ""

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend not running - starting it now..."
    cd cropsense-ai/python
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
    echo "   Waiting for backend to start..."
    sleep 5
    cd ../..
fi

echo ""
echo "Creating test user via Python script..."
echo ""

cd cropsense-ai/python
python3 create_test_user.py

echo ""
echo "============================================================"
echo "Testing Login"
echo "============================================================"
echo ""

# Test login via API
echo "Testing login via API..."
RESPONSE=$(curl -s -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username": "testfarmer", "password": "TestPass123!"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✅ Login successful!"
    echo ""
    echo "Test user is ready for E2E tests."
    echo ""
    echo "Run E2E tests with:"
    echo "  cd cropsense-ai/e2e"
    echo "  npm test"
else
    echo "❌ Login failed"
    echo "Response: $RESPONSE"
    exit 1
fi

echo ""
