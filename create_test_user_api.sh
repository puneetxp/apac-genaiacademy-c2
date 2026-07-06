#!/bin/bash

# Create Test User via API
# Simple script that uses the signup API endpoint to create test user

set -e

echo "============================================================"
echo "Creating Test User via API"
echo "============================================================"
echo ""

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running on port 8000"
    echo ""
    echo "Please start the backend first:"
    echo "  cd cropsense-ai/python"
    echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    exit 1
fi

echo ""
echo "Creating test user 'testfarmer'..."
echo ""

# Create test user via signup API
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testfarmer",
    "password": "TestPass123!",
    "email": "test.farmer@example.com",
    "phone_number": "+919876543210",
    "full_name": "Test Farmer",
    "user_type": "farmer"
  }')

# Extract HTTP status code and response body
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

echo "HTTP Status: $HTTP_CODE"
echo "Response: $RESPONSE_BODY"
echo ""

# Check if user was created or already exists
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "✅ Test user created successfully"
elif echo "$RESPONSE_BODY" | grep -q "already exists\|already registered"; then
    echo "✅ Test user already exists (this is fine)"
elif [ "$HTTP_CODE" = "400" ] && echo "$RESPONSE_BODY" | grep -q "already"; then
    echo "✅ Test user already exists (this is fine)"
else
    echo "⚠️  User creation returned status $HTTP_CODE"
    echo "   This might mean the user already exists or there was an error"
    echo "   Continuing to test login..."
fi

echo ""
echo "============================================================"
echo "Testing Login"
echo "============================================================"
echo ""

# Test login
echo "Testing login with testfarmer..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username": "testfarmer", "password": "TestPass123!"}')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✅ Login successful!"
    echo ""
    echo "============================================================"
    echo "✅ Setup Complete!"
    echo "============================================================"
    echo ""
    echo "Test User Credentials:"
    echo "  Username: testfarmer"
    echo "  Password: TestPass123!"
    echo "  Email: test.farmer@example.com"
    echo ""
    echo "You can now run E2E tests:"
    echo "  cd cropsense-ai/e2e"
    echo "  npm test"
    echo ""
else
    echo "❌ Login failed"
    echo "Response: $LOGIN_RESPONSE"
    echo ""
    echo "This might mean:"
    echo "  1. User was not created successfully"
    echo "  2. Password is incorrect"
    echo "  3. Backend authentication is not working"
    echo ""
    exit 1
fi
