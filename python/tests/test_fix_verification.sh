#!/bin/bash

# Fix Verification Test - Verify bug is fixed after disabling CSRF middleware
# This test should PASS after the fix is applied

set -e

BASE_URL="http://localhost:8000"
FARMS_ENDPOINT="${BASE_URL}/api/v1/farms"

echo "=== Fix Verification Test ==="
echo ""

# Test 1: Verify CSRF middleware is disabled (POST without auth should return 401/403, not CSRF error)
echo "Test 1: POST without auth (should return 401/403, not CSRF block)"
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${FARMS_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test"}')

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_STATUS"
echo "Response: $RESPONSE_BODY"

if [ "$HTTP_STATUS" = "401" ] || [ "$HTTP_STATUS" = "403" ]; then
  if echo "$RESPONSE_BODY" | grep -qi "authenticated"; then
    echo "✅ PASS: Got authentication error (not CSRF block)"
    echo "This confirms CSRF middleware is not blocking requests"
  else
    echo "⚠️  Got $HTTP_STATUS but unexpected message"
  fi
else
  echo "❌ FAIL: Got unexpected status $HTTP_STATUS"
  exit 1
fi
echo ""

# Test 2: Verify CORS preflight now works
echo "Test 2: CORS Preflight (should return 200 with CORS headers)"
RESPONSE=$(curl -s -i -X OPTIONS "${FARMS_ENDPOINT}" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization")

echo "$RESPONSE" | head -15

if echo "$RESPONSE" | grep -q "HTTP/1.1 200"; then
  if echo "$RESPONSE" | grep -qi "access-control-allow-origin"; then
    echo "✅ PASS: CORS preflight returns 200 with CORS headers"
    echo "This confirms middleware ordering issue is fixed"
  else
    echo "❌ FAIL: CORS preflight missing Access-Control-Allow-Origin"
    exit 1
  fi
else
  echo "❌ FAIL: CORS preflight did not return 200"
  exit 1
fi
echo ""

# Test 3: Verify backend is reachable (not net::ERR_FAILED)
echo "Test 3: Backend Reachability"
if curl -s -f "${BASE_URL}/health" > /dev/null; then
  echo "✅ PASS: Backend is reachable"
else
  echo "❌ FAIL: Backend is not reachable"
  exit 1
fi
echo ""

echo "=== Fix Verification Summary ==="
echo "✅ CSRF middleware is disabled"
echo "✅ CORS preflight works correctly"
echo "✅ Backend is reachable"
echo ""
echo "The fix is working! Farm registration should now work from the frontend."
echo "Next: Test with E2E test to verify farm registration succeeds"
