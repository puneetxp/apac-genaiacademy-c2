"""
Bug Condition Exploration Test for Farm Registration CSRF Issue

This test demonstrates the bug where POST requests to /api/v1/farms fail
because CSRFProtectionMiddleware expects X-CSRF-Token header but none is provided.

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

The test encodes the expected behavior - it will validate the fix when it passes.
"""

from datetime import datetime

import pytest
import requests

# Test configuration
BASE_URL = "http://localhost:8000"
FARMS_ENDPOINT = f"{BASE_URL}/api/v1/farms"
AUTH_ENDPOINT = f"{BASE_URL}/api/v1/auth/signin"


def get_auth_token():
    """Get JWT token for test user"""
    # Use existing test user credentials
    response = requests.post(
        AUTH_ENDPOINT,
        json={"username": "puneetxp", "password": "testpass123"},  # Adjust if different
    )

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        pytest.skip(f"Could not authenticate test user: {response.status_code}")


def test_farm_registration_without_csrf_token_fails_on_unfixed_code():
    """
    Property 1: Fault Condition - Farm Registration Fails Without CSRF Token

    This test demonstrates the bug condition:
    - POST request to /api/v1/farms
    - Valid JWT token in Authorization header
    - NO X-CSRF-Token header
    - CSRFProtectionMiddleware is enabled

    EXPECTED OUTCOME ON UNFIXED CODE: Test FAILS
    - Request may return 403 Forbidden
    - Request may fail with connection error
    - Request never reaches the endpoint handler

    EXPECTED OUTCOME ON FIXED CODE: Test PASSES
    - Request returns 201 Created
    - Farm is created in database
    - Response includes farm details

    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    # Get authentication token
    token = get_auth_token()

    # Prepare farm data
    farm_data = {
        "name": "Test Farm - Bug Exploration",
        "state": "Haryana",
        "district": "Gurugram",
        "village": "Wazirabad",
        "pincode": "122001",
        "address_line1": "Plot 45, Sector 12",
        "address_line2": "",
        "total_area_acres": 5.5,
        "latitude": 28.4595,
        "longitude": 77.0266,
    }

    # Make POST request WITHOUT X-CSRF-Token header
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        # NOTE: NO X-CSRF-Token header
    }

    print("\n=== Bug Condition Exploration Test ===")
    print(f"Endpoint: {FARMS_ENDPOINT}")
    print(f"Method: POST")
    print(f"Headers: {headers}")
    print(f"Data: {farm_data}")

    try:
        response = requests.post(FARMS_ENDPOINT, json=farm_data, headers=headers, timeout=10)

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:500]}")

        # Expected behavior (after fix): 201 Created
        assert response.status_code == 201, (
            f"Expected 201 Created, got {response.status_code}. "
            f"ON UNFIXED CODE: This failure is EXPECTED and confirms the bug exists. "
            f"ON FIXED CODE: This should pass."
        )

        # Verify response contains farm data
        response_data = response.json()
        assert "id" in response_data, "Response should include farm ID"
        assert response_data["name"] == farm_data["name"]
        assert response_data["total_area_acres"] == farm_data["total_area_acres"]

        print("\n✅ TEST PASSED: Farm registration succeeded without CSRF token")
        print("This means the bug is FIXED!")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST FAILED: {type(e).__name__}: {e}")
        print("This is the bug! Request failed before reaching backend.")
        pytest.fail(
            f"Request failed with {type(e).__name__}: {e}. "
            f"ON UNFIXED CODE: This failure is EXPECTED and confirms the bug exists. "
            f"ON FIXED CODE: This should not happen."
        )


def test_cors_preflight_for_farms_endpoint():
    """
    Test CORS preflight (OPTIONS request) to isolate CORS vs CSRF issues

    This helps determine if the issue is:
    - CORS configuration problem (preflight fails)
    - CSRF middleware problem (preflight succeeds but POST fails)
    """
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization",
    }

    print("\n=== CORS Preflight Test ===")
    print(f"Endpoint: {FARMS_ENDPOINT}")
    print(f"Method: OPTIONS")
    print(f"Headers: {headers}")

    try:
        response = requests.options(FARMS_ENDPOINT, headers=headers, timeout=10)

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        # Check CORS headers
        assert (
            "Access-Control-Allow-Origin" in response.headers
        ), "Missing Access-Control-Allow-Origin header"
        assert (
            "Access-Control-Allow-Methods" in response.headers
        ), "Missing Access-Control-Allow-Methods header"

        print("\n✅ CORS Preflight PASSED")
        print("CORS is configured correctly. Issue is likely CSRF middleware.")

    except (requests.exceptions.RequestException, AssertionError) as e:
        print(f"\n❌ CORS Preflight FAILED: {e}")
        print("Issue may be CORS configuration, not just CSRF middleware.")
        pytest.fail(f"CORS preflight failed: {e}")


if __name__ == "__main__":
    print("Running bug condition exploration tests...")
    print("=" * 60)

    # Run tests
    pytest.main([__file__, "-v", "-s"])
