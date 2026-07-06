#!/bin/bash

# Preservation Property Tests - Run BEFORE implementing fix
# These tests verify that existing functionality works correctly on UNFIXED code
# After the fix, these same tests should still pass (no regressions)

set -e

BASE_URL="http://localhost:8000"
PASS_COUNT=0
FAIL_COUNT=0

echo "=== Preservation Property Tests (BEFORE Fix) ==="
echo "Testing existing functionality on UNFIXED code"
echo ""

# Test Case 1: Pincode Lookup (GET request, no auth required)
echo "Test 1: Pincode Lookup - GET /api/v1/address/pincode/122001"
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BASE_URL}/api/v1/address/pincode/122001")
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
  if echo "$RESPONSE_BODY" | grep -q "Haryana"; then
    echo "✅ PASS: Pincode lookup returns 200 with address data"
    ((PASS_COUNT++))
  else
    echo "❌ FAIL: Pincode lookup returns 200 but missing expected data"
    echo "Response: $RESPONSE_BODY"
    ((FAIL_COUNT++))
  fi
else
  echo "❌ FAIL: Pincode lookup returns $HTTP_STATUS (expected 200)"
  echo "Response: $RESPONSE_BODY"
  ((FAIL_COUNT++))
fi
echo ""

# Test Case 2: Health Check (GET request, no auth required)
echo "Test 2: Health Check - GET /health"
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BASE_URL}/health")
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
  if echo "$RESPONSE_BODY" | grep -q "healthy"; then
    echo "✅ PASS: Health check returns 200 with healthy status"
    ((PASS_COUNT++))
  else
    echo "❌ FAIL: Health check returns 200 but missing healthy status"
    echo "Response: $RESPONSE_BODY"
    ((FAIL_COUNT++))
  fi
else
  echo "❌ FAIL: Health check returns $HTTP_STATUS (expected 200)"
  echo "Response: $RESPONSE_BODY"
  ((FAIL_COUNT++))
fi
echo ""

# Test Case 3: CORS Preflight (OPTIONS request)
echo "Test 3: CORS Preflight - OPTIONS /api/v1/farms"
RESPONSE=$(curl -s -i -X OPTIONS "${BASE_URL}/api/v1/farms" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization")

if echo "$RESPONSE" | grep -q "HTTP/1.1 200"; then
  if echo "$RESPONSE" | grep -qi "access-control-allow-origin"; then
    if echo "$RESPONSE" | grep -qi "access-control-allow-methods"; then
      echo "✅ PASS: CORS preflight returns 200 with correct CORS headers"
      ((PASS_COUNT++))
    else
      echo "❌ FAIL: CORS preflight missing Access-Control-Allow-Methods header"
      ((FAIL_COUNT++))
    fi
  else
    echo "❌ FAIL: CORS preflight missing Access-Control-Allow-Origin header"
    ((FAIL_COUNT++))
  fi
else
  echo "❌ FAIL: CORS preflight did not return 200"
  echo "Response: $(echo "$RESPONSE" | head -5)"
  ((FAIL_COUNT++))
fi
echo ""

# Test Case 4: Security Headers (check any GET request)
echo "Test 4: Security Headers - Verify security headers in responses"
RESPONSE=$(curl -s -i "${BASE_URL}/health")

SECURITY_HEADERS_FOUND=0
if echo "$RESPONSE" | grep -qi "X-Content-Type-Options"; then
  ((SECURITY_HEADERS_FOUND++))
fi
if echo "$RESPONSE" | grep -qi "X-Frame-Options"; then
  ((SECURITY_HEADERS_FOUND++))
fi

if [ $SECURITY_HEADERS_FOUND -ge 1 ]; then
  echo "✅ PASS: Security headers present in responses ($SECURITY_HEADERS_FOUND found)"
  ((PASS_COUNT++))
else
  echo "❌ FAIL: No security headers found in responses"
  ((FAIL_COUNT++))
fi
echo ""

# Test Case 5: OpenAPI Docs (GET request, no auth required)
echo "Test 5: OpenAPI Docs - GET /docs"
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BASE_URL}/docs")
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "200" ]; then
  echo "✅ PASS: OpenAPI docs accessible at /docs"
  ((PASS_COUNT++))
else
  echo "❌ FAIL: OpenAPI docs returns $HTTP_STATUS (expected 200)"
  ((FAIL_COUNT++))
fi
echo ""

# Summary
echo "=== Test Summary ==="
echo "Passed: $PASS_COUNT"
echo "Failed: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
  echo "✅ ALL PRESERVATION TESTS PASSED"
  echo "Existing functionality works correctly on UNFIXED code"
  echo "After fix, these tests should still pass (no regressions)"
  exit 0
else
  echo "❌ SOME PRESERVATION TESTS FAILED"
  echo "This indicates existing functionality has issues"
  echo "Fix should not make these worse"
  exit 1
fi
