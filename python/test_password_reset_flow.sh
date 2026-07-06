#!/bin/bash

# Test Password Reset Flow
# Tests the complete forgot password and reset password flow

BASE_URL="http://localhost:8000"
USERNAME="puneetxp"

echo "=========================================="
echo "Password Reset Flow Test"
echo "=========================================="
echo ""

# Step 1: Request password reset code
echo "Step 1: Requesting password reset code for user: $USERNAME"
echo "----------------------------------------"

FORGOT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\"}")

echo "Response:"
echo "$FORGOT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$FORGOT_RESPONSE"
echo ""

# Check if successful
if echo "$FORGOT_RESPONSE" | grep -q "Password reset code sent"; then
    echo "✓ Password reset code requested successfully"
    echo ""
    echo "⚠️  Check your email for the verification code"
    echo "   Email might be in spam/junk folder"
    echo "   Look for emails from: no-reply@verificationemail.com"
    echo ""
else
    echo "✗ Failed to request password reset code"
    echo ""
    exit 1
fi

# Step 2: Prompt for verification code
echo "Step 2: Enter the verification code from your email"
echo "----------------------------------------"
read -p "Enter 6-digit verification code: " VERIFICATION_CODE

if [ -z "$VERIFICATION_CODE" ]; then
    echo "✗ No verification code provided"
    exit 1
fi

# Step 3: Prompt for new password
echo ""
echo "Step 3: Enter new password"
echo "----------------------------------------"
read -sp "Enter new password (min 8 chars, must include uppercase, lowercase, number, special char): " NEW_PASSWORD
echo ""

if [ -z "$NEW_PASSWORD" ]; then
    echo "✗ No password provided"
    exit 1
fi

# Step 4: Reset password
echo ""
echo "Step 4: Resetting password..."
echo "----------------------------------------"

RESET_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"confirmation_code\":\"$VERIFICATION_CODE\",\"new_password\":\"$NEW_PASSWORD\"}")

echo "Response:"
echo "$RESET_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESET_RESPONSE"
echo ""

# Check if successful
if echo "$RESET_RESPONSE" | grep -q "Password reset successfully"; then
    echo "✓ Password reset successfully!"
    echo ""
    
    # Step 5: Test sign in with new password
    echo "Step 5: Testing sign in with new password..."
    echo "----------------------------------------"
    
    SIGNIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/signin" \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"$USERNAME\",\"password\":\"$NEW_PASSWORD\"}")
    
    if echo "$SIGNIN_RESPONSE" | grep -q "access_token"; then
        echo "✓ Sign in successful with new password!"
        echo ""
        echo "=========================================="
        echo "Password Reset Flow: SUCCESS"
        echo "=========================================="
    else
        echo "✗ Sign in failed with new password"
        echo "Response:"
        echo "$SIGNIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SIGNIN_RESPONSE"
        echo ""
        echo "=========================================="
        echo "Password Reset Flow: PARTIAL SUCCESS"
        echo "Password was reset but sign in failed"
        echo "=========================================="
    fi
else
    echo "✗ Password reset failed"
    echo ""
    echo "Common issues:"
    echo "  - Invalid or expired verification code"
    echo "  - Password doesn't meet requirements (min 8 chars, uppercase, lowercase, number, special char)"
    echo "  - User not found in Cognito"
    echo ""
    echo "=========================================="
    echo "Password Reset Flow: FAILED"
    echo "=========================================="
    exit 1
fi
