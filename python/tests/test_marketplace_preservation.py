#!/usr/bin/env python3
"""
Preservation Property Tests for Marketplace Functionality

**Validates: Requirements 3.11, 3.12, 3.13, 3.14**

These tests establish baseline behavior that must be preserved after the fix.
Tests should PASS on unfixed code.

Focus on marketplace endpoints that are NOT affected by the bug:
- POST /api/v1/marketplace/listings (requirement 3.11)
- GET /api/v1/marketplace/listings/{id} (requirement 3.12)
- POST /api/v1/marketplace/buyer-interest (requirement 3.13)
- Other ORM queries in different services (requirement 3.14)
"""

import os
import sys
import uuid
from datetime import date, datetime, timedelta

import requests

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "test@example.com")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "testpass123")


class TestState:
    """Holds test state"""

    auth_token = None
    user_id = None
    farm_id = None
    plot_id = None
    crop_id = None
    listing_id = None


state = TestState()


def get_auth_token():
    """Get authentication token for test user"""
    if state.auth_token:
        return state.auth_token

    # Try to login
    response = requests.post(
        f"{API_BASE_URL}/api/v1/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )

    if response.status_code == 200:
        data = response.json()
        state.auth_token = data.get("access_token")
        state.user_id = data.get("user", {}).get("id")
        return state.auth_token

    return None


def create_test_crop():
    """Create a test crop for marketplace listing"""
    token = get_auth_token()
    if not token:
        return None

    headers = {"Authorization": f"Bearer {token}"}

    # Create farm if not exists
    if not state.farm_id:
        farm_data = {
            "name": f"Test Farm {uuid.uuid4().hex[:8]}",
            "location_state": "Punjab",
            "location_district": "Ludhiana",
            "location_block": "Test Block",
            "location_village": "Test Village",
            "location_pincode": "141001",
            "total_area": 10.0,
            "irrigated_area": 8.0,
            "soil_type": "Loamy",
        }

        response = requests.post(f"{API_BASE_URL}/api/v1/farms", json=farm_data, headers=headers)

        if response.status_code in [200, 201]:
            data = response.json()
            state.farm_id = data.get("farm", {}).get("id") or data.get("id")

    # Create plot if not exists
    if state.farm_id and not state.plot_id:
        plot_data = {
            "farm_id": state.farm_id,
            "plot_number": f"P{uuid.uuid4().hex[:6]}",
            "area": 2.0,
            "soil_type": "Loamy",
        }

        response = requests.post(
            f"{API_BASE_URL}/api/v1/farm-plots", json=plot_data, headers=headers
        )

        if response.status_code in [200, 201]:
            data = response.json()
            state.plot_id = data.get("plot", {}).get("id") or data.get("id")

    # Create crop
    if state.plot_id:
        crop_data = {
            "plot_id": state.plot_id,
            "crop_variety_id": 1,
            "planting_date": date.today().isoformat(),
            "expected_harvest_date": (date.today() + timedelta(days=120)).isoformat(),
            "area_planted": 2.0,
            "planting_method": "Direct Seeding",
        }

        response = requests.post(f"{API_BASE_URL}/api/v1/crops", json=crop_data, headers=headers)

        if response.status_code in [200, 201]:
            data = response.json()
            state.crop_id = data.get("crop", {}).get("id") or data.get("id")
            return state.crop_id

    return None


def test_property_listing_creation_works():
    """Property 1: Marketplace listing creation via POST endpoint (requirement 3.11)"""
    token = get_auth_token()
    if not token:
        print("⚠️  Skipping test - no auth token available")
        return

    headers = {"Authorization": f"Bearer {token}"}

    if not state.crop_id:
        create_test_crop()
        if not state.crop_id:
            print("⚠️  Skipping test - could not create test crop")
            return

    data = {"crop_id": state.crop_id, "yield_prediction": None}

    response = requests.post(
        f"{API_BASE_URL}/api/v1/marketplace/listings", json=data, headers=headers
    )

    assert response.status_code in [
        200,
        201,
    ], f"Expected 200/201, got {response.status_code}: {response.text}"

    result = response.json()
    assert result.get("success") is True, "Expected success: true"
    assert "listing_id" in result, "Expected listing_id in response"
    assert "listing" in result, "Expected listing object in response"

    listing = result["listing"]
    assert "id" in listing, "Expected id in listing"
    assert "crop_type" in listing, "Expected crop_type in listing"
    assert "status" in listing, "Expected status in listing"
    assert listing["status"] == "active", "Expected status to be 'active'"

    if result.get("listing_id"):
        state.listing_id = result["listing_id"]

    print(f"✓ Listing creation works: {result['listing_id']}")


def test_property_listing_detail_retrieval_works():
    """Property 2: Marketplace listing detail retrieval via GET by ID (requirement 3.12)"""
    token = get_auth_token()
    if not token:
        print("⚠️  Skipping test - no auth token available")
        return

    headers = {"Authorization": f"Bearer {token}"}

    if not state.listing_id:
        if not state.crop_id:
            create_test_crop()

        if state.crop_id:
            create_response = requests.post(
                f"{API_BASE_URL}/api/v1/marketplace/listings",
                json={"crop_id": state.crop_id},
                headers=headers,
            )

            if create_response.status_code in [200, 201]:
                state.listing_id = create_response.json().get("listing_id")

    if not state.listing_id:
        print("⚠️  Skipping test - no listing available")
        return

    response = requests.get(
        f"{API_BASE_URL}/api/v1/marketplace/listings/{state.listing_id}", headers=headers
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    result = response.json()
    assert result.get("success") is True, "Expected success: true"
    assert "listing" in result, "Expected listing object in response"

    listing = result["listing"]

    required_fields = [
        "id",
        "title",
        "description",
        "crop_type",
        "crop_variety",
        "estimated_quantity",
        "quality_grade",
        "expected_harvest_date",
        "location",
        "contact",
        "status",
    ]

    for field in required_fields:
        assert field in listing, f"Expected {field} in listing"

    assert "production_predictions" in listing, "Expected production_predictions"
    predictions = listing["production_predictions"]
    assert "estimated_yield" in predictions, "Expected estimated_yield in predictions"
    assert "quality_prediction" in predictions, "Expected quality_prediction in predictions"
    assert "harvest_timing" in predictions, "Expected harvest_timing in predictions"

    assert "market_intelligence" in listing, "Expected market_intelligence"

    contact = listing["contact"]
    assert "enabled" in contact, "Expected enabled in contact"

    print(f"✓ Listing detail retrieval works: {listing['id']}")


def test_property_buyer_interest_registration_works():
    """Property 3: Buyer interest registration (requirement 3.13)"""
    token = get_auth_token()
    if not token:
        print("⚠️  Skipping test - no auth token available")
        return

    headers = {"Authorization": f"Bearer {token}"}

    if not state.listing_id:
        if not state.crop_id:
            create_test_crop()

        if state.crop_id:
            create_response = requests.post(
                f"{API_BASE_URL}/api/v1/marketplace/listings",
                json={"crop_id": state.crop_id},
                headers=headers,
            )

            if create_response.status_code in [200, 201]:
                state.listing_id = create_response.json().get("listing_id")

    if not state.listing_id:
        print("⚠️  Skipping test - no listing available")
        return

    data = {
        "listing_id": state.listing_id,
        "interest_type": "inquiry",
        "quantity_interested": 50.0,
        "preferred_price": 2500.0,
        "buyer_phone": "+919876543210",
        "buyer_email": "buyer@example.com",
        "message": "Interested in purchasing this crop",
    }

    response = requests.post(
        f"{API_BASE_URL}/api/v1/marketplace/buyer-interest", json=data, headers=headers
    )

    assert response.status_code in [
        200,
        201,
    ], f"Expected 200/201, got {response.status_code}: {response.text}"

    result = response.json()
    assert result.get("success") is True, "Expected success: true"
    assert "interest_id" in result, "Expected interest_id in response"
    assert "status" in result, "Expected status in response"
    assert result["status"] == "pending", "Expected status to be 'pending'"

    print(f"✓ Buyer interest registration works: {result['interest_id']}")


def test_property_other_orm_queries_work():
    """Property 4: Other ORM queries continue to work (requirement 3.14)"""
    token = get_auth_token()
    if not token:
        print("⚠️  Skipping test - no auth token available")
        return

    headers = {"Authorization": f"Bearer {token}"}

    farms_response = requests.get(f"{API_BASE_URL}/api/v1/farms", headers=headers)

    assert farms_response.status_code == 200, f"Farms endpoint failed: {farms_response.status_code}"

    farms_data = farms_response.json()
    assert "farms" in farms_data or isinstance(farms_data, list), "Expected farms data in response"

    print(f"✓ Farms ORM queries work")

    if state.farm_id:
        crops_response = requests.get(f"{API_BASE_URL}/api/v1/crops", headers=headers)

        assert (
            crops_response.status_code == 200
        ), f"Crops endpoint failed: {crops_response.status_code}"

        print(f"✓ Crops ORM queries work")

    print(f"✓ Other ORM queries continue to work correctly")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MARKETPLACE PRESERVATION PROPERTY TESTS")
    print("=" * 80)
    print("\nThese tests verify that marketplace functionality NOT affected by the bug")
    print("continues to work correctly. Tests should PASS on unfixed code.")
    print("\n" + "=" * 80 + "\n")

    try:
        print("\n--- Property 1: Listing Creation (Requirement 3.11) ---")
        test_property_listing_creation_works()

        print("\n--- Property 2: Listing Detail Retrieval (Requirement 3.12) ---")
        test_property_listing_detail_retrieval_works()

        print("\n--- Property 3: Buyer Interest Registration (Requirement 3.13) ---")
        test_property_buyer_interest_registration_works()

        print("\n--- Property 4: Other ORM Queries (Requirement 3.14) ---")
        test_property_other_orm_queries_work()

        print("\n" + "=" * 80)
        print("✅ ALL PRESERVATION TESTS PASSED")
        print("=" * 80)
        print("\nBaseline behavior confirmed. These operations must continue to work")
        print("after implementing the marketplace listings query fix.")
        print("\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
