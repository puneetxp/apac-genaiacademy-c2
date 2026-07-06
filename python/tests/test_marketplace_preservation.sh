#!/bin/bash

# Marketplace Preservation Property Tests Runner
# Tests marketplace functionality that should NOT be affected by the bug

set -e

echo "=========================================="
echo "MARKETPLACE PRESERVATION PROPERTY TESTS"
echo "=========================================="
echo ""
echo "Testing marketplace endpoints that are NOT affected by the bug:"
echo "  - POST /api/v1/marketplace/listings (requirement 3.11)"
echo "  - GET /api/v1/marketplace/listings/{id} (requirement 3.12)"
echo "  - POST /api/v1/marketplace/buyer-interest (requirement 3.13)"
echo "  - Other ORM queries in different services (requirement 3.14)"
echo ""
echo "Expected outcome: Tests PASS (confirms baseline behavior to preserve)"
echo ""
echo "=========================================="
echo ""

# Change to python directory
cd "$(dirname "$0")/.."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend is not running on http://localhost:8000"
    echo "Please start the backend first:"
    echo "  cd cropsense-ai/python"
    echo "  ./start_backend.sh"
    exit 1
fi

echo "✓ Backend is running"
echo ""

# Set environment variables
export API_BASE_URL="http://localhost:8000"
export TEST_USER_EMAIL="${TEST_USER_EMAIL:-test@example.com}"
export TEST_USER_PASSWORD="${TEST_USER_PASSWORD:-testpass123}"

# Install hypothesis if not already installed
if ! python3 -c "import hypothesis" 2>/dev/null; then
    echo "Installing hypothesis..."
    pip install hypothesis
    echo ""
fi

# Run the preservation tests
echo "Running preservation property tests..."
echo ""

python3 tests/test_marketplace_preservation.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ ALL PRESERVATION TESTS PASSED"
    echo "=========================================="
    echo ""
    echo "Baseline behavior confirmed:"
    echo "  ✓ Marketplace listing creation works (requirement 3.11)"
    echo "  ✓ Marketplace listing detail retrieval works (requirement 3.12)"
    echo "  ✓ Buyer interest registration works (requirement 3.13)"
    echo "  ✓ Other ORM queries continue to work (requirement 3.14)"
    echo ""
    echo "These operations must continue to work after implementing the fix."
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ PRESERVATION TESTS FAILED"
    echo "=========================================="
    echo ""
    echo "Some baseline functionality is not working correctly."
    echo "This needs to be investigated before implementing the fix."
    echo ""
fi

exit $exit_code
