#!/bin/bash

# Simple CSRF Bug Test - Test without authentication to isolate CSRF issue
# This bypasses authentication to focus on CSRF middleware behavior

set -e

BASE_URL="http://localhost:8000"
FARMS_ENDPOINT="${BASE_URL}/api/v1/farms"

echo "=== Simple CSRF Bug Test ==="
echo ""
echo "Testing POST to /api/v1/farms WITHOUT X-CSRF-Token header"
echo "Expected on UNFIXED code: 401 Unauthorized (no auth) or 403 Forbidden (CSRF)"
echo "Expected on FIXED code: 401 Unauthorized (no auth, but CSRF not blocking)"
echo ""

# Test POST request WITHOUT authentication and WITHOUT X-CSRF-Token
FARM_DATA='{
  "name": "Test Farm",
  "state": "Haryana",
  "district": "Gurugram",
  "village": "Wazirabad",
  "pincode": "122001",
  "total_area_acres": 5.5
}'

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${FARMS_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d "$FARM_DATA")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_STATUS"
echo "Response:"
echo "$RESPONSE_BODY"
echo ""

# Analyze result
if [ "$HTTP_STATUS" = "401" ]; then
  echo "✅ Got 401 Unauthorized - CSRF middleware is NOT blocking (or is disabled)"
  echo "This suggests CSRF is not the issue, or it's already fixed"
  exit 0
elif [ "$HTTP_STATUS" = "403" ]; then
  echo "❌ Got 403 Forbidden - Likely CSRF middleware blocking"
  echo "This confirms the CSRF bug exists"
  exit 1
else
  echo "⚠️  Got unexpected status $HTTP_STATUS"
  echo "Need to investigate further"
  exit 1
fi
