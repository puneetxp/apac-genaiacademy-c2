#!/bin/bash

# Quick test of password reset endpoints

BASE_URL="http://localhost:8000"

echo "Testing Password Reset Endpoints"
echo "================================="
echo ""

# Test 1: Forgot password with username
echo "Test 1: Forgot password with username 'puneetxp'"
curl -s -X POST "$BASE_URL/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"username":"puneetxp"}' | python3 -m json.tool

echo ""
echo ""

# Test 2: Forgot password with email
echo "Test 2: Forgot password with email 'puneetsharma9@hotmail.com'"
curl -s -X POST "$BASE_URL/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"username":"puneetsharma9@hotmail.com"}' | python3 -m json.tool

echo ""
echo ""
echo "================================="
echo "If you see 'Password reset code sent', the endpoint is working!"
echo "Check your email (including spam folder) for the code."
echo ""
echo "To complete the reset, use:"
echo "  ./test_password_reset_flow.sh"
echo "================================="
