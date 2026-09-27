"""
Tests for Pincode Lookup Service

Tests the integration with India Post pincode API (https://api.postalpincode.in)
including caching, error handling, and validation.
"""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.pincode_lookup_service import PincodeLookupService


class TestPincodeLookupService:
    """Test suite for PincodeLookupService"""

    @pytest.fixture
    def service(self):
        """Create service instance without Redis"""
        return PincodeLookupService(redis_client=None)

    @pytest.fixture
    def service_with_redis(self):
        """Create service instance with mocked Redis"""
        redis_mock = AsyncMock()
        return PincodeLookupService(redis_client=redis_mock), redis_mock

    @pytest.fixture
    def sample_api_response(self):
        """Sample response from pincode API"""
        return [
            {
                "pincode": "110001",
                "state": "Delhi",
                "district": "Central Delhi",
                "vpo": "Connaught Place",
            },
            {
                "pincode": "110001",
                "state": "Delhi",
                "district": "Central Delhi",
                "vpo": "Parliament Street",
            },
        ]

    @pytest.mark.asyncio
    async def test_lookup_pincode_success(self, service, sample_api_response):
        """Test successful pincode lookup"""
        with patch("httpx.AsyncClient") as mock_client:
            # Mock the response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await service.lookup_pincode("110001")

            assert result is not None
            assert result["pincode"] == "110001"
            assert result["state"] == "Delhi"
            assert result["district"] == "Central Delhi"
            assert len(result["villages"]) == 2
            assert "Connaught Place" in result["villages"]
            assert "Parliament Street" in result["villages"]

    @pytest.mark.asyncio
    async def test_lookup_pincode_not_found(self, service):
        """Test pincode not found (404 response)"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await service.lookup_pincode("999999")

            assert result is None

    @pytest.mark.asyncio
    async def test_lookup_pincode_empty_data(self, service):
        """Test pincode with empty data array"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await service.lookup_pincode("000000")

            assert result is None

    @pytest.mark.asyncio
    async def test_lookup_pincode_timeout(self, service):
        """Test API timeout handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            result = await service.lookup_pincode("110001")

            assert result is None

    @pytest.mark.asyncio
    async def test_lookup_pincode_request_error(self, service):
        """Test API request error handling"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.RequestError("Connection failed")
            )

            result = await service.lookup_pincode("110001")

            assert result is None

    @pytest.mark.asyncio
    async def test_lookup_pincode_with_cache_hit(self, service_with_redis, sample_api_response):
        """Test cache hit scenario"""
        service, redis_mock = service_with_redis

        # Mock cache hit
        import json

        cached_data = {
            "pincode": "110001",
            "state": "Delhi",
            "district": "Central Delhi",
            "villages": ["Connaught Place", "Parliament Street"],
        }
        redis_mock.get.return_value = json.dumps(cached_data)

        result = await service.lookup_pincode("110001")

        assert result == cached_data
        redis_mock.get.assert_called_once_with("pincode:110001")

    @pytest.mark.asyncio
    async def test_lookup_pincode_cache_miss_then_save(
        self, service_with_redis, sample_api_response
    ):
        """Test cache miss followed by API call and cache save"""
        service, redis_mock = service_with_redis

        # Mock cache miss
        redis_mock.get.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await service.lookup_pincode("110001")

            assert result is not None
            assert result["pincode"] == "110001"

            # Verify cache save was called
            redis_mock.setex.assert_called_once()
            call_args = redis_mock.setex.call_args
            assert call_args[0][0] == "pincode:110001"
            assert call_args[0][1] == int(timedelta(days=30).total_seconds())

    @pytest.mark.asyncio
    async def test_validate_address_success(self, service, sample_api_response):
        """Test successful address validation"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            is_valid = await service.validate_address(
                pincode="110001", state="Delhi", district="Central Delhi", village="Connaught Place"
            )

            assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_address_state_mismatch(self, service, sample_api_response):
        """Test address validation with state mismatch"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            is_valid = await service.validate_address(
                pincode="110001",
                state="Maharashtra",  # Wrong state
                district="Central Delhi",
                village="Connaught Place",
            )

            assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_address_district_mismatch(self, service, sample_api_response):
        """Test address validation with district mismatch"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            is_valid = await service.validate_address(
                pincode="110001",
                state="Delhi",
                district="South Delhi",  # Wrong district
                village="Connaught Place",
            )

            assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_address_village_mismatch(self, service, sample_api_response):
        """Test address validation with village mismatch"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            is_valid = await service.validate_address(
                pincode="110001",
                state="Delhi",
                district="Central Delhi",
                village="Invalid Village",  # Wrong village
            )

            assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_address_case_insensitive(self, service, sample_api_response):
        """Test address validation is case-insensitive"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_api_response

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            is_valid = await service.validate_address(
                pincode="110001",
                state="DELHI",  # Uppercase
                district="central delhi",  # Lowercase
                village="CONNAUGHT PLACE",  # Uppercase
            )

            assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_address_lookup_failure(self, service):
        """Test address validation when pincode lookup fails"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            is_valid = await service.validate_address(
                pincode="999999", state="Delhi", district="Central Delhi", village="Connaught Place"
            )

            assert is_valid is False

    def test_parse_api_response(self, service, sample_api_response):
        """Test API response parsing"""
        result = service._parse_api_response(sample_api_response)

        assert result["pincode"] == "110001"
        assert result["state"] == "Delhi"
        assert result["district"] == "Central Delhi"
        assert len(result["villages"]) == 2
        assert "Connaught Place" in result["villages"]
        assert "Parliament Street" in result["villages"]

    def test_parse_api_response_empty(self, service):
        """Test parsing empty API response"""
        result = service._parse_api_response([])

        assert result is None

    def test_parse_api_response_none(self, service):
        """Test parsing None API response"""
        result = service._parse_api_response(None)

        assert result is None

    def test_parse_api_response_duplicate_villages(self, service):
        """Test parsing response with duplicate villages"""
        data = [
            {"pincode": "110001", "state": "Delhi", "district": "Central Delhi", "vpo": "Place A"},
            {"pincode": "110001", "state": "Delhi", "district": "Central Delhi", "vpo": "Place A"},
            {"pincode": "110001", "state": "Delhi", "district": "Central Delhi", "vpo": "Place B"},
        ]

        result = service._parse_api_response(data)

        # Should have unique villages only
        assert len(result["villages"]) == 2
        assert "Place A" in result["villages"]
        assert "Place B" in result["villages"]


def test_parse_india_post_response():
    """India Post shape (api.postalpincode.in) maps to state/district/villages"""
    service = PincodeLookupService(redis_client=None)
    data = [
        {
            "Message": "Number of pincode(s) found:2",
            "Status": "Success",
            "PostOffice": [
                {"Name": "Durgapuri", "District": "Ludhiana", "State": "Punjab", "Pincode": "141001"},
                {"Name": "Ludhiana", "District": "Ludhiana", "State": "Punjab", "Pincode": "141001"},
            ],
        }
    ]
    assert service._parse_api_response(data) == {
        "pincode": "141001",
        "state": "Punjab",
        "district": "Ludhiana",
        "villages": ["Durgapuri", "Ludhiana"],
    }


def test_parse_india_post_no_records():
    """India Post answers 200 with Status=Error for unknown pincodes"""
    service = PincodeLookupService(redis_client=None)
    data = [{"Message": "No records found", "Status": "Error", "PostOffice": None}]
    assert service._parse_api_response(data) is None
