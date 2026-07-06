#!/bin/bash

# Test password reset with verification code
# Usage: ./test_reset_with_code.sh <verification_code> <new_password>

if [ $# -lt 2 ]; then
    echo "Usage: $0 <verification_code> <new_password>"
    echo ""
    echo "Example:"
    echo "  $0 123456 'NewPass123!'"
    echo ""
    exit 1
fi

VERIFICATION_CODE=$1
NEW_PASSWORD=$2
USERNAME="puneetsharma9@hotmail.com"
BASE_URL="http://localhost:8000"

echo "Testing Password Reset with Code"
echo "================================="
echo "Username: $USERNAME"
echo "Code: $VERIFICATION_CODE"
echo ""

# Reset password
echo "Resetting password..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"confirmation_code\":\"$VERIFICATION_CODE\",\"new_password\":\"$NEW_PASSWORD\"}")

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if successful
if echo "$RESPONSE" | grep -q "success.*true"; then
    echo "✓ Password reset successful!"
    echo ""
    echo "Testing sign in with new password..."
    
    SIGNIN=$(curl -s -X POST "$BASE_URL/api/v1/auth/signin" \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"$USERNAME\",\"password\":\"$NEW_PASSWORD\"}")
    
    if echo "$SIGNIN" | grep -q "access_token"; then
        echo "✓ Sign in successful!"
        echo ""
        echo "New credentials:"
        echo "  Email: $USERNAME"
        echo "  Password: $NEW_PASSWORD"
    else
        echo "✗ Sign in failed"
        echo "$SIGNIN" | python3 -m json.tool 2>/dev/null || echo "$SIGNIN"
    fi
else
    echo "✗ Password reset failed"
    echo ""
    echo "Possible issues:"
    echo "  - Invalid or expired code"
    echo "  - Password requirements not met (min 8 chars, uppercase, lowercase, number, special char)"
fi

echo ""
echo "================================="
