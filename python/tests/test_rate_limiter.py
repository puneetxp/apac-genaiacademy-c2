"""Tests for rate limiting middleware."""
import pytest
import asyncio
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import time

from app.core.rate_limiter import RateLimiter, init_rate_limiter


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    mock_client.pipeline = Mock()
    
    # Mock pipeline
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = Mock(return_value=mock_pipeline)
    mock_pipeline.zcard = Mock(return_value=mock_pipeline)
    mock_pipeline.zadd = Mock(return_value=mock_pipeline)
    mock_pipeline.expire = Mock(return_value=mock_pipeline)
    mock_pipeline.execute = AsyncMock(return_value=[None, 0, None, None])  # request_count = 0
    
    mock_client.pipeline.return_value = mock_pipeline
    mock_client.close = AsyncMock()
    
    return mock_client


@pytest.fixture
def rate_limiter(mock_redis):
    """Create rate limiter instance with mocked Redis."""
    limiter = RateLimiter(
        redis_url="redis://localhost:6379/0",
        default_limit=10,
        window_seconds=60,
        enabled=True
    )
    limiter.redis_client = mock_redis
    return limiter


@pytest.mark.asyncio
async def test_rate_limiter_init(mock_redis):
    """Test rate limiter initialization."""
    with patch('redis.asyncio.from_url', return_value=mock_redis):
        limiter = RateLimiter(
            redis_url="redis://localhost:6379/0",
            default_limit=100,
            window_seconds=60,
            enabled=True
        )
        await limiter.init()
        
        assert limiter.redis_client is not None
        assert limiter.enabled is True
        mock_redis.ping.assert_called_once()


@pytest.mark.asyncio
async def test_rate_limiter_disabled():
    """Test rate limiter when disabled."""
    limiter = RateLimiter(
        redis_url="redis://localhost:6379/0",
        default_limit=100,
        window_seconds=60,
        enabled=False
    )
    
    mock_request = Mock(spec=Request)
    mock_request.url.path = "/test"
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {}
    mock_request.state = Mock()
    
    is_allowed, rate_info = await limiter.check_rate_limit(mock_request)
    
    assert is_allowed is True
    assert rate_info == {}


@pytest.mark.asyncio
async def test_get_identifier_with_user_id(rate_limiter):
    """Test identifier generation with authenticated user."""
    mock_request = Mock(spec=Request)
    mock_request.state = Mock()
    mock_request.state.user_id = "user123"
    
    identifier = rate_limiter._get_identifier(mock_request)
    
    assert identifier == "user:user123"


@pytest.mark.asyncio
async def test_get_identifier_with_ip(rate_limiter):
    """Test identifier generation with IP address."""
    mock_request = Mock(spec=Request)
    mock_request.state = Mock()
    mock_request.state.user_id = None
    mock_request.client = Mock()
    mock_request.client.host = "192.168.1.1"
    mock_request.headers = {}
    
    identifier = rate_limiter._get_identifier(mock_request)
    
    assert identifier == "ip:192.168.1.1"


@pytest.mark.asyncio
async def test_get_identifier_with_forwarded_ip(rate_limiter):
    """Test identifier generation with X-Forwarded-For header."""
    mock_request = Mock(spec=Request)
    mock_request.state = Mock()
    mock_request.state.user_id = None
    mock_request.headers = {"X-Forwarded-For": "203.0.113.1, 198.51.100.1"}
    
    identifier = rate_limiter._get_identifier(mock_request)
    
    assert identifier == "ip:203.0.113.1"


@pytest.mark.asyncio
async def test_check_rate_limit_allowed(rate_limiter, mock_redis):
    """Test rate limit check when request is allowed."""
    mock_request = Mock(spec=Request)
    mock_request.url.path = "/test"
    mock_request.state = Mock()
    mock_request.state.user_id = "user123"
    
    # Mock pipeline to return low request count
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = Mock(return_value=mock_pipeline)
    mock_pipeline.zcard = Mock(return_value=mock_pipeline)
    mock_pipeline.zadd = Mock(return_value=mock_pipeline)
    mock_pipeline.expire = Mock(return_value=mock_pipeline)
    mock_pipeline.execute = AsyncMock(return_value=[None, 5, None, None])  # 5 requests
    
    mock_redis.pipeline.return_value = mock_pipeline
    
    is_allowed, rate_info = await rate_limiter.check_rate_limit(mock_request, limit=10)
    
    assert is_allowed is True
    assert rate_info["limit"] == 10
    assert rate_info["remaining"] == 4  # 10 - 5 - 1
    assert "reset" in rate_info
    assert rate_info["window"] == 60


@pytest.mark.asyncio
async def test_check_rate_limit_exceeded(rate_limiter, mock_redis):
    """Test rate limit check when limit is exceeded."""
    mock_request = Mock(spec=Request)
    mock_request.url.path = "/test"
    mock_request.state = Mock()
    mock_request.state.user_id = "user123"
    
    # Mock pipeline to return high request count
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = Mock(return_value=mock_pipeline)
    mock_pipeline.zcard = Mock(return_value=mock_pipeline)
    mock_pipeline.zadd = Mock(return_value=mock_pipeline)
    mock_pipeline.expire = Mock(return_value=mock_pipeline)
    mock_pipeline.execute = AsyncMock(return_value=[None, 15, None, None])  # 15 requests
    
    mock_redis.pipeline.return_value = mock_pipeline
    
    is_allowed, rate_info = await rate_limiter.check_rate_limit(mock_request, limit=10)
    
    assert is_allowed is False
    assert rate_info["limit"] == 10
    assert rate_info["remaining"] == 0


@pytest.mark.asyncio
async def test_rate_limit_key_generation(rate_limiter):
    """Test rate limit key generation."""
    key = rate_limiter._get_rate_limit_key("user:123", "/test")
    
    assert key == "rate_limit:user:123:/test"


@pytest.mark.asyncio
async def test_middleware_skips_health_endpoints(rate_limiter):
    """Test that middleware skips health check endpoints."""
    app = FastAPI()
    
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    middleware = rate_limiter.get_middleware(limit=10, window=60, public_limit=5)
    
    # Create mock request for health endpoint
    mock_request = Mock(spec=Request)
    mock_request.url.path = "/health"
    
    # Mock call_next
    async def mock_call_next(request):
        return Mock(headers={})
    
    response = await middleware(mock_request, mock_call_next)
    
    # Should not check rate limit for health endpoint
    assert response is not None


@pytest.mark.asyncio
async def test_rate_limiter_close(rate_limiter, mock_redis):
    """Test rate limiter connection close."""
    await rate_limiter.close()
    
    mock_redis.close.assert_called_once()


def test_init_rate_limiter():
    """Test global rate limiter initialization."""
    limiter = init_rate_limiter(
        redis_url="redis://localhost:6379/0",
        default_limit=100,
        window_seconds=60,
        enabled=True
    )
    
    assert limiter is not None
    assert limiter.default_limit == 100
    assert limiter.window_seconds == 60
    assert limiter.enabled is True


@pytest.mark.asyncio
async def test_rate_limit_error_handling(rate_limiter, mock_redis):
    """Test rate limiter error handling (fail open)."""
    mock_request = Mock(spec=Request)
    mock_request.url.path = "/test"
    mock_request.state = Mock()
    mock_request.state.user_id = "user123"
    
    # Mock pipeline to raise exception
    mock_redis.pipeline.side_effect = Exception("Redis connection error")
    
    is_allowed, rate_info = await rate_limiter.check_rate_limit(mock_request)
    
    # Should allow request on error (fail open)
    assert is_allowed is True
    assert rate_info == {}
