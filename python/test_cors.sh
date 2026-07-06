#!/bin/bash

# Test CORS Configuration
# This script tests if CORS is properly configured on the backend

echo "Testing CORS Configuration..."
echo "=============================="
echo ""

# Test OPTIONS preflight request
echo "1. Testing OPTIONS preflight request..."
curl -X OPTIONS http://localhost:8000/auth/signup \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v 2>&1 | grep -i "access-control"

echo ""
echo "2. Testing POST request with CORS headers..."
curl -X POST http://localhost:8000/auth/signup \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "password": "Test@1234",
    "email": "test123@example.com",
    "phone_number": "+919876543210",
    "full_name": "Test User",
    "user_type": "farmer"
  }' \
  -v 2>&1 | grep -i "access-control"

echo ""
echo "=============================="
echo "CORS Test Complete"
echo ""
echo "Expected headers:"
echo "  - access-control-allow-origin: http://localhost:3000"
echo "  - access-control-allow-credentials: true"
echo "  - access-control-allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS"
echo "  - access-control-allow-headers: Content-Type, Authorization, X-CSRF-Token, X-Requested-With"
