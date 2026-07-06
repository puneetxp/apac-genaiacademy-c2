#!/bin/bash

# Bug Condition Exploration Test for Farm Registration CSRF Issue
# This test demonstrates the bug where POST requests to /api/v1/farms fail
# because CSRFProtectionMiddleware expects X-CSRF-Token header but none is provided.
#
# CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
# EXPECTED OUTCOME ON FIXED CODE: Test PASSES (201 Created response)

set -e

BASE_URL="http://localhost:8000"
FARMS_ENDPOINT="${BASE_URL}/api/v1/farms"
AUTH_ENDPOINT="${BASE_URL}/api/v1/auth/signin"

echo "=== Bug Condition Exploration Test ==="
echo ""

# Step 1: Get authentication token
echo "Step 1: Authenticating test user..."
AUTH_RESPONSE=$(curl -s -X POST "${AUTH_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{"username":"puneetxp","password":"Pa$w0rd!"}')

TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get authentication token"
  echo "Response: $AUTH_RESPONSE"
  exit 1
fi

echo "✅ Authentication successful"
echo "Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Test CORS preflight (OPTIONS request)
echo "Step 2: Testing CORS preflight..."
CORS_RESPONSE=$(curl -s -i -X OPTIONS "${FARMS_ENDPOINT}" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization")

echo "$CORS_RESPONSE" | head -20
echo ""

if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
  echo "✅ CORS preflight passed"
else
  echo "❌ CORS preflight failed - missing CORS headers"
fi
echo ""

# Step 3: Test POST request WITHOUT X-CSRF-Token header
echo "Step 3: Testing POST to /api/v1/farms WITHOUT X-CSRF-Token..."
echo "This is the bug condition - request should fail on unfixed code"
echo ""

FARM_DATA='{
  "name": "Test Farm - Bug Exploration",
  "state": "Haryana",
  "district": "Gurugram",
  "village": "Wazirabad",
  "pincode": "122001",
  "address_line1": "Plot 45, Sector 12",
  "address_line2": "",
  "total_area_acres": 5.5,
  "latitude": 28.4595,
  "longitude": 77.0266
}'

FARM_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${FARMS_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d "$FARM_DATA")

HTTP_STATUS=$(echo "$FARM_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE_BODY=$(echo "$FARM_RESPONSE" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_STATUS"
echo "Response Body:"
echo "$RESPONSE_BODY" | head -20
echo ""

# Check result
if [ "$HTTP_STATUS" = "201" ]; then
  echo "✅ TEST PASSED: Farm registration succeeded without CSRF token"
  echo "This means the bug is FIXED!"
  exit 0
elif [ "$HTTP_STATUS" = "403" ]; then
  echo "❌ TEST FAILED: Got 403 Forbidden"
  echo "ON UNFIXED CODE: This failure is EXPECTED and confirms the bug exists"
  echo "ON FIXED CODE: This should return 201 Created"
  exit 1
else
  echo "❌ TEST FAILED: Got unexpected status $HTTP_STATUS"
  echo "ON UNFIXED CODE: This failure is EXPECTED and confirms the bug exists"
  echo "ON FIXED CODE: This should return 201 Created"
  exit 1
fi
