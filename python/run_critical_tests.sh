#!/bin/bash

# Critical Tests Runner
# Runs essential tests to verify system functionality

set -e

echo "🧪 Running Critical System Tests"
echo "================================="
echo ""

# Change to python directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Warning: No virtual environment found"
fi
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0
TOTAL=0

run_test() {
    local test_name=$1
    local test_file=$2
    
    TOTAL=$((TOTAL + 1))
    echo -e "${YELLOW}[$TOTAL] Running: $test_name${NC}"
    
    # Run test and capture exit code
    if python3 -m pytest "$test_file" -v --tb=short; then
        echo -e "${GREEN}✓ PASSED: $test_name${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAILED: $test_name${NC}"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# 1. Health Checks
run_test "Health Checks" "tests/smoke/test_health_checks.py"

# 2. Authentication & User Management
run_test "User Registration & Auth" "tests/test_user_registration_auth.py"

# 3. Farm Management
run_test "Farm Address" "tests/test_farm_address.py"
run_test "Farm Profile Management" "tests/test_farm_profile_management.py"

# 4. Address & Pincode Services
run_test "Pincode Lookup Service" "tests/test_pincode_lookup_service.py"
run_test "Address Service" "tests/test_address_service.py"
run_test "Address API" "tests/test_address_api.py"

# 5. Crop Management
run_test "Crop Recommendations" "tests/test_crop_recommendations.py"
run_test "Crop Milestones" "tests/test_crop_milestones.py"

# 6. Marketplace
run_test "Marketplace Integration" "tests/test_marketplace_integration.py"
run_test "Marketplace Search" "tests/test_marketplace_search.py"

# 7. Weather & Recommendations
run_test "Weather Integration" "tests/test_weather_integration.py"
run_test "Weather Recommendations" "tests/test_weather_recommendations.py"

# 8. AI & Bedrock Integration
run_test "Bedrock API Integration" "tests/test_bedrock_api_integration.py"
run_test "AI Quota Integration" "tests/test_bedrock_quota_integration.py"

# 9. Livestock Management
run_test "Livestock Registration" "tests/test_livestock_registration.py"
run_test "Livestock Health Management" "tests/test_livestock_health_management.py"

# 10. Data Validation & Security
run_test "Data Validation Security" "tests/test_data_validation_security.py"
run_test "Security Headers" "tests/test_security_headers.py"

# Summary
echo ""
echo "================================="
echo "📊 Test Summary"
echo "================================="
echo -e "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Check output above.${NC}"
    exit 1
fi
