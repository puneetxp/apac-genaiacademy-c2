#!/bin/bash

# Bug Condition Exploration Test for Marketplace Listings Query Error
# This test MUST FAIL on unfixed code to confirm the bug exists
# Bug: GET /api/v1/marketplace/listings fails with "Column expression expected, got <class 'MarketplaceListing'>" error
# Root cause: marketplace_service.py uses SQLAlchemy's query API with custom ORM model
# Error occurs at line 437 in get_listings() method

echo "=========================================="
echo "Marketplace Listings Bug Exploration Test"
echo "=========================================="
echo ""
echo "Testing GET /api/v1/marketplace/listings endpoint"
echo "Expected: HTTP 500 errors with column expression error"
echo ""

BASE_URL="http://localhost:8000"
API_ENDPOINT="${BASE_URL}/api/v1/marketplace/listings"

# Counter for failed tests (which is what we expect)
FAILED_COUNT=0
TOTAL_TESTS=0

# Function to test an endpoint
test_endpoint() {
    local description="$1"
    local url="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo "Test $TOTAL_TESTS: $description"
    echo "URL: $url"
    
    # Make the request and capture response
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    echo "HTTP Status: $http_code"
    
    # Check if we got a 500 error (expected for bug)
    if [ "$http_code" = "500" ]; then
        echo "✓ FAILED AS EXPECTED (Bug confirmed)"
        echo "Error response: $body"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    elif [ "$http_code" = "200" ]; then
        echo "✗ PASSED UNEXPECTEDLY (Bug may be fixed or not triggered)"
        echo "Response: $body"
    else
        echo "? UNEXPECTED STATUS CODE: $http_code"
        echo "Response: $body"
    fi
    
    echo ""
}

echo "=== Test 1: Basic Listings Query ==="
test_endpoint "Basic listings without parameters" "$API_ENDPOINT"

echo "=== Test 2: Sorting Scenarios ==="
test_endpoint "Sort by harvest_date ascending" "${API_ENDPOINT}?sort_by=harvest_date&sort_order=asc"
test_endpoint "Sort by harvest_date descending" "${API_ENDPOINT}?sort_by=harvest_date&sort_order=desc"
test_endpoint "Sort by quantity ascending" "${API_ENDPOINT}?sort_by=quantity&sort_order=asc"
test_endpoint "Sort by quantity descending" "${API_ENDPOINT}?sort_by=quantity&sort_order=desc"
test_endpoint "Sort by quality_grade" "${API_ENDPOINT}?sort_by=quality_grade&sort_order=desc"
test_endpoint "Sort by price" "${API_ENDPOINT}?sort_by=price&sort_order=desc"

echo "=== Test 3: Filtering Scenarios ==="
test_endpoint "Filter by crop_type" "${API_ENDPOINT}?crop_type=rice"
test_endpoint "Filter by state" "${API_ENDPOINT}?state=Punjab"
test_endpoint "Filter by crop_type and state" "${API_ENDPOINT}?crop_type=rice&state=Punjab"
test_endpoint "Filter by district" "${API_ENDPOINT}?district=Ludhiana"
test_endpoint "Filter by min_quantity" "${API_ENDPOINT}?min_quantity=100"
test_endpoint "Filter by max_quantity" "${API_ENDPOINT}?max_quantity=500"
test_endpoint "Filter by quality_grade" "${API_ENDPOINT}?quality_grade=A"

echo "=== Test 4: Pagination Scenarios ==="
test_endpoint "Pagination with limit" "${API_ENDPOINT}?limit=10"
test_endpoint "Pagination with limit and offset" "${API_ENDPOINT}?limit=10&offset=0"
test_endpoint "Pagination with limit and offset 20" "${API_ENDPOINT}?limit=5&offset=20"

echo "=== Test 5: Combined Scenarios ==="
test_endpoint "Sort + Filter" "${API_ENDPOINT}?crop_type=wheat&sort_by=harvest_date&sort_order=desc"
test_endpoint "Sort + Pagination" "${API_ENDPOINT}?sort_by=quantity&sort_order=desc&limit=10&offset=0"
test_endpoint "Filter + Pagination" "${API_ENDPOINT}?state=Punjab&limit=10&offset=0"
test_endpoint "Sort + Filter + Pagination" "${API_ENDPOINT}?crop_type=rice&state=Punjab&sort_by=harvest_date&sort_order=desc&limit=10&offset=0"

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Total tests: $TOTAL_TESTS"
echo "Failed as expected (bug confirmed): $FAILED_COUNT"
echo "Passed unexpectedly: $((TOTAL_TESTS - FAILED_COUNT))"
echo ""

if [ $FAILED_COUNT -gt 0 ]; then
    echo "✓ BUG CONFIRMED: Marketplace listings endpoint fails with column expression error"
    echo "  Root cause: SQLAlchemy query API incompatible with custom ORM model"
    echo "  Error location: marketplace_service.py line 437 in get_listings()"
    echo ""
    echo "Counterexamples found:"
    echo "  - Queries with sorting parameters fail"
    echo "  - Queries with filtering parameters fail"
    echo "  - Queries with pagination parameters fail"
    echo "  - All query variations return HTTP 500 errors"
    exit 0
else
    echo "✗ BUG NOT CONFIRMED: All tests passed unexpectedly"
    echo "  The bug may already be fixed or the test conditions are incorrect"
    exit 1
fi
