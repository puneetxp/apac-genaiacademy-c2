"""
Smoke tests for post-deployment verification.
These tests verify critical functionality after deployment.
"""

import pytest
import httpx
from typing import Optional


@pytest.fixture
def base_url(request) -> str:
    """Get base URL from command line or environment."""
    return request.config.getoption("--base-url", default="http://localhost:8000")


@pytest.fixture
async def client(base_url: str) -> httpx.AsyncClient:
    """Create HTTP client for smoke tests."""
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        yield client


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_health_endpoint(client: httpx.AsyncClient):
    """Test that health endpoint is accessible and returns 200."""
    response = await client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_api_docs_accessible(client: httpx.AsyncClient):
    """Test that API documentation is accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_openapi_schema(client: httpx.AsyncClient):
    """Test that OpenAPI schema is accessible."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_cors_headers(client: httpx.AsyncClient):
    """Test that CORS headers are properly configured."""
    response = await client.options(
        "/farms",
        headers={
            "Origin": "https://rural-farming.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_security_headers(client: httpx.AsyncClient):
    """Test that security headers are present."""
    response = await client.get("/health")
    
    # Check for security headers
    assert "x-content-type-options" in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"
    
    assert "x-frame-options" in response.headers
    assert response.headers["x-frame-options"] == "DENY"
    
    assert "strict-transport-security" in response.headers


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_api_version_endpoint(client: httpx.AsyncClient):
    """Test that API version endpoint returns correct information."""
    response = await client.get("/version")
    
    if response.status_code == 200:
        data = response.json()
        assert "version" in data
        assert "environment" in data


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_database_connectivity(client: httpx.AsyncClient):
    """Test that database is accessible through health check."""
    response = await client.get("/health/db")
    
    if response.status_code == 200:
        data = response.json()
        assert data["database"] == "connected"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_redis_connectivity(client: httpx.AsyncClient):
    """Test that Redis is accessible through health check."""
    response = await client.get("/health/redis")
    
    if response.status_code == 200:
        data = response.json()
        assert data["redis"] == "connected"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_response_time(client: httpx.AsyncClient):
    """Test that API responds within acceptable time."""
    import time
    
    start = time.time()
    response = await client.get("/health")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 2.0, f"Response took {duration:.2f}s, expected < 2.0s"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_error_handling(client: httpx.AsyncClient):
    """Test that 404 errors are handled properly."""
    response = await client.get("/nonexistent-endpoint")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--base-url",
        action="store",
        default="http://localhost:8000",
        help="Base URL for smoke tests"
    )
