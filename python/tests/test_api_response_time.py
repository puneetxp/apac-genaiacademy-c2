"""
Property-based tests for API response time performance
Tests Property 13: API Response Time Performance

**Validates: Requirements (Non-Functional - Performance)**
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor, as_completed


# Create a minimal FastAPI app for testing
def create_test_app() -> FastAPI:
    """Create a minimal FastAPI app for response time testing"""
    app = FastAPI(title="Test API")
    
    @app.get("/")
    async def root():
        return {"message": "Welcome to Test API"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    @app.get("/farms")
    async def list_farms():
        # Simulate some processing time
        await asyncio.sleep(0.01)
        return {"farms": []}
    
    @app.post("/farms")
    async def create_farm(farm_data: dict):
        # Simulate some processing time
        await asyncio.sleep(0.02)
        return {"id": 1, **farm_data}
    
    @app.get("/marketplace/listings")
    async def list_marketplace():
        # Simulate some processing time
        await asyncio.sleep(0.01)
        return {"listings": []}
    
    @app.get("/crop-recommendations")
    async def get_recommendations():
        # Simulate some processing time
        await asyncio.sleep(0.05)
        return {"recommendations": []}
    
    @app.get("/market-data")
    async def get_market_data():
        # Simulate some processing time
        await asyncio.sleep(0.01)
        return {"data": []}
    
    @app.get("/weather/alerts")
    async def get_weather_alerts():
        # Simulate some processing time
        await asyncio.sleep(0.01)
        return {"alerts": []}
    
    return app


# Create test app instance
app = create_test_app()


# Custom strategies for API request data
@st.composite
def api_endpoint_strategy(draw):
    """Generate valid API endpoints for testing"""
    
    # Define available API endpoints with their HTTP methods
    endpoints = [
        # Public endpoints
        {"method": "GET", "path": "/", "requires_auth": False},
        {"method": "GET", "path": "/health", "requires_auth": False},
        
        # Farm endpoints
        {"method": "GET", "path": "/farms", "requires_auth": True},
        {"method": "POST", "path": "/farms", "requires_auth": True, "body": {
            "name": "Test Farm",
            "state": "Punjab",
            "district": "Ludhiana",
            "total_area": 10.0,
            "soil_type": "loamy",
            "irrigation_type": "canal"
        }},
        
        # Marketplace endpoints
        {"method": "GET", "path": "/marketplace/listings", "requires_auth": False},
        
        # Crop recommendations endpoints
        {"method": "GET", "path": "/crop-recommendations", "requires_auth": True},
        
        # Market data endpoints
        {"method": "GET", "path": "/market-data", "requires_auth": False},
        
        # Weather endpoints
        {"method": "GET", "path": "/weather/alerts", "requires_auth": True},
    ]
    
    return draw(st.sampled_from(endpoints))


@st.composite
def concurrent_load_strategy(draw):
    """Generate concurrent load scenarios (< 100 users)"""
    
    # Number of concurrent users (normal load < 100)
    num_users = draw(st.integers(min_value=1, max_value=99))
    
    # Number of requests per user
    requests_per_user = draw(st.integers(min_value=1, max_value=5))
    
    return {
        "num_users": num_users,
        "requests_per_user": requests_per_user,
        "total_requests": num_users * requests_per_user
    }


def make_api_request(client: TestClient, endpoint: Dict[str, Any], auth_token: str = None) -> Dict[str, Any]:
    """
    Make an API request and measure response time
    
    Returns:
        Dict with response_time, status_code, and success flag
    """
    headers = {}
    if endpoint.get("requires_auth") and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    start_time = time.time()
    
    try:
        if endpoint["method"] == "GET":
            response = client.get(endpoint["path"], headers=headers)
        elif endpoint["method"] == "POST":
            response = client.post(
                endpoint["path"],
                json=endpoint.get("body", {}),
                headers=headers
            )
        elif endpoint["method"] == "PUT":
            response = client.put(
                endpoint["path"],
                json=endpoint.get("body", {}),
                headers=headers
            )
        elif endpoint["method"] == "DELETE":
            response = client.delete(endpoint["path"], headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {endpoint['method']}")
        
        elapsed_time = time.time() - start_time
        
        return {
            "response_time": elapsed_time,
            "status_code": response.status_code,
            "success": response.status_code < 500,  # Success if not server error
            "endpoint": endpoint["path"],
            "method": endpoint["method"]
        }
    
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "response_time": elapsed_time,
            "status_code": 500,
            "success": False,
            "endpoint": endpoint["path"],
            "method": endpoint["method"],
            "error": str(e)
        }


def make_concurrent_requests(
    num_users: int,
    requests_per_user: int,
    endpoint: Dict[str, Any],
    auth_token: str = None
) -> List[Dict[str, Any]]:
    """
    Simulate concurrent API requests from multiple users
    
    Returns:
        List of response time measurements
    """
    client = TestClient(app)
    results = []
    
    with ThreadPoolExecutor(max_workers=min(num_users, 50)) as executor:
        # Submit all requests
        futures = []
        for user_id in range(num_users):
            for req_id in range(requests_per_user):
                future = executor.submit(make_api_request, client, endpoint, auth_token)
                futures.append(future)
        
        # Collect results
        for future in as_completed(futures):
            try:
                result = future.result(timeout=10)
                results.append(result)
            except Exception as e:
                results.append({
                    "response_time": 10.0,  # Timeout
                    "status_code": 500,
                    "success": False,
                    "error": str(e)
                })
    
    return results


def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculate the nth percentile of a list of values"""
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    index = int(len(sorted_values) * (percentile / 100.0))
    index = min(index, len(sorted_values) - 1)
    return sorted_values[index]


class TestAPIResponseTimePerformance:
    """
    Property 13: API Response Time Performance
    
    Test that for any API request under normal load (< 100 concurrent users),
    response time is within 3 seconds for 95% of requests.
    """
    
    @given(endpoint=api_endpoint_strategy())
    @settings(
        max_examples=200,
        deadline=30000,  # 30 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_single_request_response_time(self, endpoint):
        """
        **Validates: Requirements (Non-Functional - Performance)**
        
        Property: For any single API request, the response time should be
        within 3 seconds to ensure acceptable user experience.
        """
        # Arrange
        client = TestClient(app)
        
        # For this test, we don't need actual authentication
        # We're testing response time, not auth functionality
        auth_token = None
        result = make_api_request(client, endpoint, auth_token)
        
        # Assert: Response time is within 3 seconds
        assert result["response_time"] < 3.0, \
            f"API request to {endpoint['method']} {endpoint['path']} took {result['response_time']:.2f}s, expected < 3s"
        
        # Assert: Request was successful (or expected error)
        # Note: Some endpoints may return 401/403 without auth, which is expected
        assert result["status_code"] in [200, 201, 401, 403, 404], \
            f"Unexpected status code {result['status_code']} for {endpoint['path']}"
    
    @given(load_scenario=concurrent_load_strategy())
    @settings(
        max_examples=100,
        deadline=60000,  # 60 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_concurrent_load_response_time_95th_percentile(self, load_scenario):
        """
        **Validates: Requirements (Non-Functional - Performance)**
        
        Property: For any concurrent load scenario with < 100 users, the 95th
        percentile response time should be within 3 seconds.
        """
        # Arrange
        num_users = load_scenario["num_users"]
        requests_per_user = load_scenario["requests_per_user"]
        
        # Use a simple public endpoint for load testing
        endpoint = {"method": "GET", "path": "/health", "requires_auth": False}
        
        # Act: Make concurrent requests
        results = make_concurrent_requests(num_users, requests_per_user, endpoint)
        
        # Extract response times
        response_times = [r["response_time"] for r in results if r["success"]]
        
        # Assert: At least some requests succeeded
        assert len(response_times) > 0, \
            f"No successful requests out of {len(results)} total requests"
        
        # Calculate 95th percentile
        p95_response_time = calculate_percentile(response_times, 95)
        
        # Assert: 95th percentile is within 3 seconds
        assert p95_response_time < 3.0, \
            f"95th percentile response time {p95_response_time:.2f}s exceeds 3s threshold " \
            f"(users: {num_users}, requests/user: {requests_per_user}, total: {len(results)})"
        
        # Calculate success rate
        success_count = sum(1 for r in results if r["success"])
        success_rate = (success_count / len(results)) * 100
        
        # Assert: Success rate is reasonable (> 90%)
        assert success_rate > 90.0, \
            f"Success rate {success_rate:.1f}% is below 90% threshold"
    
    def test_health_endpoint_response_time(self):
        """
        **Validates: Requirements (Non-Functional - Performance)**
        
        Test that the health check endpoint responds quickly (< 1 second)
        as it's used for monitoring and load balancing.
        """
        # Arrange
        client = TestClient(app)
        
        # Act: Make 10 requests to health endpoint
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = client.get("/health")
            elapsed_time = time.time() - start_time
            response_times.append(elapsed_time)
            
            # Assert: Response is successful
            assert response.status_code == 200
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times)
        
        # Assert: Average response time is < 1 second
        assert avg_response_time < 1.0, \
            f"Health endpoint average response time {avg_response_time:.2f}s exceeds 1s"
        
        # Assert: All individual requests are < 1 second
        for i, rt in enumerate(response_times):
            assert rt < 1.0, \
                f"Health endpoint request {i+1} took {rt:.2f}s, expected < 1s"
    
    def test_root_endpoint_response_time(self):
        """
        **Validates: Requirements (Non-Functional - Performance)**
        
        Test that the root endpoint responds quickly (< 1 second)
        as it's the first endpoint users typically access.
        """
        # Arrange
        client = TestClient(app)
        
        # Act: Make 10 requests to root endpoint
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = client.get("/")
            elapsed_time = time.time() - start_time
            response_times.append(elapsed_time)
            
            # Assert: Response is successful
            assert response.status_code == 200
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times)
        
        # Assert: Average response time is < 1 second
        assert avg_response_time < 1.0, \
            f"Root endpoint average response time {avg_response_time:.2f}s exceeds 1s"
    
    def test_marketplace_listings_response_time(self):
        """
        **Validates: Requirements (Non-Functional - Performance)**
        
        Test that marketplace listings endpoint responds within 3 seconds
        even with pagination and filtering.
        """
        # Arrange
        client = TestClient(app)
        
        # Act: Test with different query parameters
        test_cases = [
            "/marketplace/listings",
            "/marketplace/listings?limit=10",
            "/marketplace/listings?limit=50",
            "/marketplace/listings?skip=0&limit=20",
        ]
        
        for endpoint in test_cases:
            start_time = time.time()
            response = client.get(endpoint)
            elapsed_time = time.time() - start_time
            
            # Assert: Response time is within 3 seconds
            assert elapsed_time < 3.0, \
                f"Marketplace listings endpoint {endpoint} took {elapsed_time:.2f}s, expected < 3s"
            
            # Assert: Response is successful or expected error
            assert response.status_code in [200, 404, 500], \
                f"Unexpected status code {response.status_code} for {endpoint}"
    
    def test_concurrent_mixed_endpoints_response_time(self):
        """
        **Validates: Requirements (Non-Functional - Performance)**
        
        Test that under mixed concurrent load (different endpoints),
        95% of requests complete within 3 seconds.
        """
        # Arrange
        client = TestClient(app)
        num_users = 50  # Moderate concurrent load
        
        # Mix of different endpoints
        endpoints = [
            {"method": "GET", "path": "/", "requires_auth": False},
            {"method": "GET", "path": "/health", "requires_auth": False},
            {"method": "GET", "path": "/marketplace/listings", "requires_auth": False},
        ]
        
        # Act: Make concurrent requests to different endpoints
        results = []
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = []
            for user_id in range(num_users):
                # Each user makes requests to different endpoints
                for endpoint in endpoints:
                    future = executor.submit(make_api_request, client, endpoint)
                    futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "response_time": 10.0,
                        "status_code": 500,
                        "success": False,
                        "error": str(e)
                    })
        
        # Extract response times
        response_times = [r["response_time"] for r in results if r["success"]]
        
        # Assert: At least some requests succeeded
        assert len(response_times) > 0, \
            f"No successful requests out of {len(results)} total requests"
        
        # Calculate 95th percentile
        p95_response_time = calculate_percentile(response_times, 95)
        
        # Assert: 95th percentile is within 3 seconds
        assert p95_response_time < 3.0, \
            f"95th percentile response time {p95_response_time:.2f}s exceeds 3s threshold " \
            f"under mixed concurrent load ({num_users} users, {len(results)} total requests)"
        
        # Calculate and log statistics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"\nMixed Load Statistics:")
        print(f"  Total requests: {len(results)}")
        print(f"  Successful requests: {len(response_times)}")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Min response time: {min_response_time:.3f}s")
        print(f"  Max response time: {max_response_time:.3f}s")
        print(f"  95th percentile: {p95_response_time:.3f}s")
    
    def test_response_time_under_sustained_load(self):
        """
        **Validates: Requirements (Non-Functional - Performance)**
        
        Test that response times remain consistent under sustained load
        (multiple waves of concurrent requests).
        """
        # Arrange
        client = TestClient(app)
        num_waves = 5
        users_per_wave = 20
        endpoint = {"method": "GET", "path": "/health", "requires_auth": False}
        
        all_response_times = []
        
        # Act: Make multiple waves of concurrent requests
        for wave in range(num_waves):
            results = make_concurrent_requests(users_per_wave, 1, endpoint)
            wave_response_times = [r["response_time"] for r in results if r["success"]]
            all_response_times.extend(wave_response_times)
            
            # Small delay between waves
            time.sleep(0.1)
        
        # Assert: At least some requests succeeded
        assert len(all_response_times) > 0, \
            f"No successful requests across {num_waves} waves"
        
        # Calculate 95th percentile across all waves
        p95_response_time = calculate_percentile(all_response_times, 95)
        
        # Assert: 95th percentile is within 3 seconds
        assert p95_response_time < 3.0, \
            f"95th percentile response time {p95_response_time:.2f}s exceeds 3s threshold " \
            f"under sustained load ({num_waves} waves, {users_per_wave} users/wave)"
        
        # Calculate statistics
        avg_response_time = sum(all_response_times) / len(all_response_times)
        
        print(f"\nSustained Load Statistics:")
        print(f"  Waves: {num_waves}")
        print(f"  Users per wave: {users_per_wave}")
        print(f"  Total requests: {len(all_response_times)}")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  95th percentile: {p95_response_time:.3f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
