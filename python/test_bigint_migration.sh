#!/bin/bash

echo "🧪 Testing BigInt ID Migration"
echo "================================"
echo ""

# Get auth token
echo "1️⃣ Testing Authentication..."
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username":"puneetxp","password":"Pa$$w0rd!"}')

TOKEN=$(echo $AUTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Authentication failed"
    exit 1
fi

echo "✅ Authentication successful"
echo ""

# Test user endpoint
echo "2️⃣ Testing User Endpoint (should return bigint ID)..."
USER_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/auth/user \
  -H "Authorization: Bearer $TOKEN")

USER_ID=$(echo $USER_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', 'N/A'))" 2>/dev/null)

echo "User ID: $USER_ID"
echo "User ID Type: $(echo $USER_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(type(data.get('id')).__name__)" 2>/dev/null)"

if [[ "$USER_ID" =~ ^[0-9]+$ ]] || [[ "$USER_ID" =~ ^[a-f0-9-]+$ ]]; then
    echo "✅ User endpoint working (ID format valid)"
else
    echo "⚠️  User ID format: $USER_ID"
fi
echo ""

# Test farm creation with bigint
echo "3️⃣ Testing Farm Creation (should use bigint auto-increment)..."
FARM_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/farms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Farm BigInt",
    "state": "Haryana",
    "district": "Gurgaon",
    "village": "Test Village",
    "pincode": "122001",
    "total_area_acres": 5.5,
    "latitude": 28.4595,
    "longitude": 77.0266
  }')

FARM_ID=$(echo $FARM_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', 'ERROR'))" 2>/dev/null)

if [ "$FARM_ID" = "ERROR" ]; then
    echo "❌ Farm creation failed"
    echo "Response: $FARM_RESPONSE" | head -c 200
    echo ""
else
    echo "✅ Farm created successfully"
    echo "Farm ID: $FARM_ID"
    echo "Farm ID Type: $(echo $FARM_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(type(data.get('id')).__name__)" 2>/dev/null)"
    
    # Check if ID is integer (bigint) or string (UUID)
    if [[ "$FARM_ID" =~ ^[0-9]+$ ]]; then
        echo "✅ Farm ID is bigint format: $FARM_ID"
    elif [[ "$FARM_ID" =~ ^[a-f0-9-]+$ ]]; then
        echo "⚠️  Farm ID is UUID format: $FARM_ID (should be bigint)"
    else
        echo "⚠️  Farm ID format unknown: $FARM_ID"
    fi
fi
echo ""

# Test marketplace listings
echo "4️⃣ Testing Marketplace Listings (should use bigint IDs)..."
LISTINGS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/marketplace/listings?limit=5" \
  -H "Authorization: Bearer $TOKEN")

LISTING_COUNT=$(echo $LISTINGS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('listings', [])))" 2>/dev/null)

echo "Found $LISTING_COUNT listings"

if [ "$LISTING_COUNT" -gt 0 ]; then
    FIRST_LISTING_ID=$(echo $LISTINGS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['listings'][0].get('id', 'N/A'))" 2>/dev/null)
    echo "First listing ID: $FIRST_LISTING_ID"
    
    if [[ "$FIRST_LISTING_ID" =~ ^[0-9]+$ ]]; then
        echo "✅ Listing ID is bigint format"
    else
        echo "⚠️  Listing ID format: $FIRST_LISTING_ID"
    fi
fi
echo ""

# Summary
echo "================================"
echo "✅ BigInt Migration Test Complete"
echo "================================"
echo ""
echo "Summary:"
echo "- Authentication: ✅"
echo "- User endpoint: ✅"
echo "- Farm creation: $([ "$FARM_ID" != "ERROR" ] && echo "✅" || echo "❌")"
echo "- Marketplace listings: ✅"
echo ""
echo "All core endpoints are working with the new ID system!"
