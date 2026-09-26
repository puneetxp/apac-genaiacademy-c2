#!/usr/bin/env python3
"""
Integration Test for Marketplace Listings

Tests the complete marketplace browsing flow including:
- Filtering by various criteria
- Sorting by different fields
- Pagination through multiple pages
- Combined filter, sort, and pagination scenarios
- Verification that no HTTP 500 errors occur

This test validates that the marketplace listings endpoint works correctly
after the SQLAlchemy query API was replaced with custom ORM methods.
"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

# Configuration
API_BASE_URL = "http://localhost:8000"
MARKETPLACE_ENDPOINT = f"{API_BASE_URL}/api/v1/marketplace/listings"


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}\n")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")


def make_request(
    params: Optional[Dict[str, Any]] = None, expected_status: int = 200
) -> Dict[str, Any]:
    """
    Make a request to the marketplace listings endpoint

    Args:
        params: Query parameters
        expected_status: Expected HTTP status code

    Returns:
        Response JSON data

    Raises:
        AssertionError: If response status doesn't match expected
    """
    try:
        response = requests.get(MARKETPLACE_ENDPOINT, params=params, timeout=10)

        # Check status code
        if response.status_code != expected_status:
            print_error(f"Expected status {expected_status}, got {response.status_code}")
            print_error(f"Response: {response.text}")
            raise AssertionError(
                f"Status code mismatch: {response.status_code} != {expected_status}"
            )

        # Parse JSON
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        raise


def test_basic_listing_retrieval():
    """Test 1: Basic listing retrieval without filters"""
    print_test_header("Basic Listing Retrieval")

    data = make_request()

    # Verify response structure
    assert "success" in data, "Response missing 'success' field"
    assert data["success"] is True, "Response success is not True"
    assert "listings" in data, "Response missing 'listings' field"
    assert "pagination" in data, "Response missing 'pagination' field"

    print_success(f"Retrieved {len(data['listings'])} listings")
    print_success(f"Total items: {data['pagination']['total_items']}")
    print_success(f"Total pages: {data['pagination']['total_pages']}")

    # Verify pagination structure
    pagination = data["pagination"]
    assert "page" in pagination, "Pagination missing 'page' field"
    assert "page_size" in pagination, "Pagination missing 'page_size' field"
    assert "total_items" in pagination, "Pagination missing 'total_items' field"
    assert "total_pages" in pagination, "Pagination missing 'total_pages' field"
    assert "has_next" in pagination, "Pagination missing 'has_next' field"
    assert "has_prev" in pagination, "Pagination missing 'has_prev' field"

    print_success("Response structure is valid")

    return data


def test_crop_type_filter():
    """Test 2: Filter by crop type"""
    print_test_header("Crop Type Filter")

    # Test with common crop types
    crop_types = ["rice", "wheat", "cotton"]

    for crop_type in crop_types:
        print_info(f"Testing filter: crop_type={crop_type}")

        data = make_request(params={"crop_type": crop_type})

        assert data["success"] is True, "Response success is not True"
        print_success(f"Found {len(data['listings'])} listings for {crop_type}")

        # Verify filter was applied
        if "filters_applied" in data:
            assert data["filters_applied"].get("crop_type") == crop_type
            print_success(f"Filter correctly applied: {crop_type}")


def test_location_filters():
    """Test 3: Filter by state and district"""
    print_test_header("Location Filters")

    # Test state filter
    print_info("Testing state filter: Punjab")
    data = make_request(params={"state": "Punjab"})
    assert data["success"] is True
    print_success(f"Found {len(data['listings'])} listings in Punjab")

    # Test district filter
    print_info("Testing district filter: Ludhiana")
    data = make_request(params={"state": "Punjab", "district": "Ludhiana"})
    assert data["success"] is True
    print_success(f"Found {len(data['listings'])} listings in Ludhiana, Punjab")


def test_quantity_filters():
    """Test 4: Filter by quantity range"""
    print_test_header("Quantity Range Filters")

    # Test minimum quantity
    print_info("Testing min_quantity filter: 100")
    data = make_request(params={"min_quantity": 100})
    assert data["success"] is True
    print_success(f"Found {len(data['listings'])} listings with quantity >= 100")

    # Test maximum quantity
    print_info("Testing max_quantity filter: 500")
    data = make_request(params={"max_quantity": 500})
    assert data["success"] is True
    print_success(f"Found {len(data['listings'])} listings with quantity <= 500")

    # Test quantity range
    print_info("Testing quantity range: 100-500")
    data = make_request(params={"min_quantity": 100, "max_quantity": 500})
    assert data["success"] is True
    print_success(f"Found {len(data['listings'])} listings with quantity 100-500")


def test_quality_grade_filter():
    """Test 5: Filter by quality grade"""
    print_test_header("Quality Grade Filter")

    grades = ["A", "B", "C"]

    for grade in grades:
        print_info(f"Testing quality_grade filter: {grade}")
        data = make_request(params={"quality_grade": grade})
        assert data["success"] is True
        print_success(f"Found {len(data['listings'])} listings with grade {grade}")


def test_sorting():
    """Test 6: Sort by different fields"""
    print_test_header("Sorting")

    sort_fields = [
        ("harvest_date", "asc"),
        ("harvest_date", "desc"),
        ("quantity", "asc"),
        ("quantity", "desc"),
        ("quality_grade", "asc"),
        ("quality_grade", "desc"),
        ("price", "asc"),
        ("price", "desc"),
    ]

    for sort_by, sort_order in sort_fields:
        print_info(f"Testing sort: {sort_by} {sort_order}")

        data = make_request(params={"sort_by": sort_by, "sort_order": sort_order, "page_size": 10})

        assert data["success"] is True
        print_success(f"Sorted by {sort_by} {sort_order}: {len(data['listings'])} listings")

        # Verify sort metadata
        if "sort" in data:
            assert data["sort"]["by"] == sort_by
            assert data["sort"]["order"] == sort_order
            print_success(f"Sort metadata correct: {sort_by} {sort_order}")


def test_pagination():
    """Test 7: Pagination through multiple pages"""
    print_test_header("Pagination")

    # Get first page
    print_info("Fetching page 1")
    page1 = make_request(params={"page": 1, "page_size": 5})
    assert page1["success"] is True
    assert page1["pagination"]["page"] == 1
    print_success(f"Page 1: {len(page1['listings'])} listings")

    # Get second page if available
    if page1["pagination"]["has_next"]:
        print_info("Fetching page 2")
        page2 = make_request(params={"page": 2, "page_size": 5})
        assert page2["success"] is True
        assert page2["pagination"]["page"] == 2
        print_success(f"Page 2: {len(page2['listings'])} listings")

        # Verify listings are different
        page1_ids = {listing["id"] for listing in page1["listings"]}
        page2_ids = {listing["id"] for listing in page2["listings"]}
        assert page1_ids != page2_ids, "Page 1 and Page 2 have same listings"
        print_success("Page 1 and Page 2 have different listings")
    else:
        print_info("Only one page available, skipping page 2 test")

    # Test different page sizes
    for page_size in [10, 20, 50]:
        print_info(f"Testing page_size: {page_size}")
        data = make_request(params={"page_size": page_size})
        assert data["success"] is True
        assert len(data["listings"]) <= page_size
        print_success(f"Page size {page_size}: {len(data['listings'])} listings")


def test_combined_filters():
    """Test 8: Combined filter, sort, and pagination"""
    print_test_header("Combined Filters, Sort, and Pagination")

    # Complex query: Filter by crop type and state, sort by harvest date, paginate
    print_info("Testing combined scenario")

    params = {
        "crop_type": "rice",
        "state": "Punjab",
        "min_quantity": 50,
        "sort_by": "harvest_date",
        "sort_order": "asc",
        "page": 1,
        "page_size": 10,
    }

    data = make_request(params=params)
    assert data["success"] is True

    print_success(f"Combined query returned {len(data['listings'])} listings")
    print_success(f"Filters: crop_type=rice, state=Punjab, min_quantity=50")
    print_success(f"Sort: harvest_date asc")
    print_success(f"Pagination: page 1, size 10")

    # Verify all parameters were applied
    if "filters_applied" in data:
        print_success(f"Filters applied: {data['filters_applied']}")

    if "sort" in data:
        print_success(f"Sort applied: {data['sort']}")


def test_edge_cases():
    """Test 9: Edge cases and boundary conditions"""
    print_test_header("Edge Cases")

    # Test empty results
    print_info("Testing filter that returns no results")
    data = make_request(params={"crop_type": "nonexistent_crop_xyz"})
    assert data["success"] is True
    assert len(data["listings"]) == 0
    print_success("Empty result set handled correctly")

    # Test page beyond available pages
    print_info("Testing page number beyond available pages")
    data = make_request(params={"page": 9999, "page_size": 10})
    assert data["success"] is True
    assert len(data["listings"]) == 0
    print_success("Out of range page handled correctly")

    # Test maximum page size
    print_info("Testing maximum page size (100)")
    data = make_request(params={"page_size": 100})
    assert data["success"] is True
    assert len(data["listings"]) <= 100
    print_success(f"Maximum page size: {len(data['listings'])} listings")


def test_listing_detail_structure():
    """Test 10: Verify listing detail structure"""
    print_test_header("Listing Detail Structure")

    # Get a listing
    data = make_request(params={"page_size": 1})

    if len(data["listings"]) == 0:
        print_info("No listings available, skipping detail structure test")
        return

    listing = data["listings"][0]

    # Verify required fields
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
        "status",
    ]

    for field in required_fields:
        assert field in listing, f"Listing missing required field: {field}"
        print_success(f"Field present: {field}")

    # Verify nested structures
    assert "location" in listing and isinstance(listing["location"], dict)
    print_success("Location structure is valid")

    if "harvest_window" in listing:
        assert isinstance(listing["harvest_window"], dict)
        print_success("Harvest window structure is valid")

    if "market_intelligence" in listing:
        assert isinstance(listing["market_intelligence"], dict)
        print_success("Market intelligence structure is valid")


def test_no_500_errors():
    """Test 11: Verify no HTTP 500 errors occur"""
    print_test_header("HTTP 500 Error Prevention")

    # Test various parameter combinations that previously caused 500 errors
    test_cases = [
        {"sort_by": "harvest_date", "sort_order": "desc"},
        {"sort_by": "quantity", "sort_order": "asc"},
        {"sort_by": "quality_grade", "sort_order": "desc"},
        {"sort_by": "price", "sort_order": "asc"},
        {"crop_type": "rice", "sort_by": "harvest_date"},
        {"state": "Punjab", "sort_by": "quantity"},
        {"min_quantity": 100, "sort_by": "price"},
        {"page": 1, "page_size": 20, "sort_by": "harvest_date"},
    ]

    for i, params in enumerate(test_cases, 1):
        print_info(f"Test case {i}: {params}")

        try:
            data = make_request(params=params)
            assert data["success"] is True
            print_success(f"Test case {i} passed: No 500 error")
        except AssertionError as e:
            print_error(f"Test case {i} failed: {e}")
            raise


def run_all_tests():
    """Run all integration tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}MARKETPLACE LISTINGS INTEGRATION TEST SUITE{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")

    tests = [
        ("Basic Listing Retrieval", test_basic_listing_retrieval),
        ("Crop Type Filter", test_crop_type_filter),
        ("Location Filters", test_location_filters),
        ("Quantity Filters", test_quantity_filters),
        ("Quality Grade Filter", test_quality_grade_filter),
        ("Sorting", test_sorting),
        ("Pagination", test_pagination),
        ("Combined Filters", test_combined_filters),
        ("Edge Cases", test_edge_cases),
        ("Listing Detail Structure", test_listing_detail_structure),
        ("HTTP 500 Error Prevention", test_no_500_errors),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print_error(f"Test '{test_name}' failed: {e}")

    # Print summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")

    print(f"Total tests: {passed + failed}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")

    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)
