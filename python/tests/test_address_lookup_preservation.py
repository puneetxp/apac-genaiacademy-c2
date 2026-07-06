"""
Preservation Property Tests for Address Lookup Functionality

**Validates: Requirements 3.8, 3.9, 3.10**

These tests validate that pincode lookup, caching, and address validation
functionality continues to work correctly. They capture baseline behavior
on unfixed code and should PASS to confirm no regressions.

Property 2: Preservation - Address Lookup Functionality

For any pincode lookup, caching, or address validation operation, the
implementation SHALL produce the same results as before, preserving all
address lookup functionality.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta
import json

from app.services.pincode_lookup_service import PincodeLookupService


# ============================================================================
# Test Data Strategies
# ============================================================================

@st.composite
def valid_pincode_strategy(draw):
    """Generate valid 6-digit Indian pincodes"""
    # Indian pincodes are 6 digits, first digit 1-9, rest 0-9
    first_digit = draw(st.integers(min_value=1, max_value=9))
    remaining_digits = draw(st.integers(min_value=0, max_value=99999))
    pincode = f"{first_digit}{remaining_digits:05d}"
    return pincode


@st.composite
def pincode_api_response_strategy(draw):
    """Generate realistic pincode API responses"""
    pincode = draw(valid_pincode_strategy())
    state = draw(st.sampled_from([
        "Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "West Bengal",
        "Gujarat", "Rajasthan", "Punjab", "Haryana", "Uttar Pradesh"
    ]))
    # Use ASCII-only characters for reliable case conversion
    district = draw(st.text(
        min_size=5, max_size=30, 
        alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
    ))
    
    # Generate 1-5 villages with ASCII-only characters
    num_villages = draw(st.integers(min_value=1, max_value=5))
    villages = [
        draw(st.text(
            min_size=5, max_size=30,
            alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
        ))
        for _ in range(num_villages)
    ]
    
    # API returns list of location objects
    return [
        {
            "pincode": pincode,
            "state": state,
            "district": district,
            "vpo": village
        }
        for village in villages
    ]


@st.composite
def address_data_strategy(draw):
    """Generate address data for validation testing"""
    api_response = draw(pincode_api_response_strategy())
    first_entry = api_response[0]
    
    return {
        "pincode": first_entry["pincode"],
        "state": first_entry["state"],
        "district": first_entry["district"],
        "village": first_entry["vpo"],
        "api_response": api_response
    }


class TestAddressLookupPreservation:
    """
    Preservation property tests for address lookup functionality.
    
    Property 2: Preservation - Address Lookup Functionality
    
    These tests validate that non-buggy pincode lookup operations continue
    to work correctly, preserving all existing functionality.
    """
    
    @pytest.fixture
    def service_no_cache(self):
        """Create service instance without Redis caching"""
        return PincodeLookupService(redis_client=None)
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        redis = MagicMock()
        redis.get = AsyncMock(return_value=None)
        redis.setex = AsyncMock()
        return redis
    
    @pytest.fixture
    def service_with_cache(self, mock_redis):
        """Create service instance with Redis caching"""
        return PincodeLookupService(redis_client=mock_redis)
    
    # ========================================================================
    # Requirement 3.8: Valid Pincode Lookups Return State, District, Village
    # ========================================================================
    
    @given(api_response=pincode_api_response_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_valid_pincode_returns_state_district_villages(
        self, api_response, service_no_cache
    ):
        """
        Property: Valid pincode lookups return state, district, and villages
        
        **Validates: Requirement 3.8**
        
        For any valid pincode lookup that returns data from the API,
        the service SHALL return a dictionary containing:
        - pincode: the queried pincode
        - state: the state name
        - district: the district name
        - villages: list of village/VPO names
        """
        pincode = api_response[0]["pincode"]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await service_no_cache.lookup_pincode(pincode)
            
            # Verify result structure
            assert result is not None, "Result should not be None for valid pincode"
            assert "pincode" in result, "Result should contain pincode"
            assert "state" in result, "Result should contain state"
            assert "district" in result, "Result should contain district"
            assert "villages" in result, "Result should contain villages list"
            
            # Verify data types
            assert isinstance(result["pincode"], str), "Pincode should be string"
            assert isinstance(result["state"], str), "State should be string"
            assert isinstance(result["district"], str), "District should be string"
            assert isinstance(result["villages"], list), "Villages should be list"
            
            # Verify data matches API response
            assert result["pincode"] == api_response[0]["pincode"]
            assert result["state"] == api_response[0]["state"]
            assert result["district"] == api_response[0]["district"]
            
            # Verify all villages are included
            expected_villages = set(entry["vpo"] for entry in api_response)
            actual_villages = set(result["villages"])
            assert actual_villages == expected_villages, (
                "All villages from API should be in result"
            )
    
    @given(api_response=pincode_api_response_strategy())
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_multiple_villages_are_all_returned(
        self, api_response, service_no_cache
    ):
        """
        Property: All villages from API response are included in result
        
        **Validates: Requirement 3.8**
        
        When the API returns multiple villages for a pincode, the service
        SHALL include all unique villages in the villages list.
        """
        assume(len(api_response) > 1)  # Only test with multiple villages
        
        pincode = api_response[0]["pincode"]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await service_no_cache.lookup_pincode(pincode)
            
            # Verify all villages are present
            expected_villages = set(entry["vpo"] for entry in api_response)
            actual_villages = set(result["villages"])
            
            assert len(actual_villages) == len(expected_villages), (
                f"Expected {len(expected_villages)} villages, got {len(actual_villages)}"
            )
            assert actual_villages == expected_villages, (
                "All villages should be included in result"
            )
    
    # ========================================================================
    # Requirement 3.9: Pincode Data Caching Behavior
    # ========================================================================
    
    @given(api_response=pincode_api_response_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_cached_data_is_used_for_subsequent_requests(
        self, api_response, mock_redis
    ):
        """
        Property: Cached pincode data is used for subsequent requests
        
        **Validates: Requirement 3.9**
        
        When pincode data is cached in Redis, subsequent requests for the
        same pincode SHALL use the cached data instead of making API calls.
        """
        service = PincodeLookupService(redis_client=mock_redis)
        pincode = api_response[0]["pincode"]
        
        # Prepare cached data
        cached_result = {
            "pincode": pincode,
            "state": api_response[0]["state"],
            "district": api_response[0]["district"],
            "villages": [entry["vpo"] for entry in api_response]
        }
        
        # Mock Redis to return cached data
        mock_redis.get = AsyncMock(return_value=json.dumps(cached_result))
        
        with patch('httpx.AsyncClient') as mock_client:
            # This should NOT be called since we have cached data
            mock_client.return_value.__aenter__.return_value.get = AsyncMock()
            
            result = await service.lookup_pincode(pincode)
            
            # Verify cached data was returned
            assert result == cached_result, "Should return cached data"
            
            # Verify Redis get was called
            cache_key = f"pincode:{pincode}"
            mock_redis.get.assert_called_once_with(cache_key)
            
            # Verify API was NOT called (cache hit)
            mock_client.return_value.__aenter__.return_value.get.assert_not_called()
    
    @given(api_response=pincode_api_response_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_successful_lookups_are_cached(
        self, api_response, mock_redis
    ):
        """
        Property: Successful API lookups are cached in Redis
        
        **Validates: Requirement 3.9**
        
        When a pincode lookup succeeds via API call, the result SHALL be
        cached in Redis with the configured TTL (30 days).
        """
        # Create fresh mock for each test run
        fresh_redis = MagicMock()
        fresh_redis.get = AsyncMock(return_value=None)
        fresh_redis.setex = AsyncMock()
        
        service = PincodeLookupService(redis_client=fresh_redis)
        pincode = api_response[0]["pincode"]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await service.lookup_pincode(pincode)
            
            # Verify result was returned
            assert result is not None, "Result should be returned"
            
            # Verify data was cached
            cache_key = f"pincode:{pincode}"
            fresh_redis.setex.assert_called_once()
            
            # Verify cache key and TTL
            call_args = fresh_redis.setex.call_args
            assert call_args[0][0] == cache_key, "Cache key should be correct"
            
            # TTL should be 30 days in seconds
            expected_ttl = int(timedelta(days=30).total_seconds())
            actual_ttl = call_args[0][1]
            assert actual_ttl == expected_ttl, (
                f"Cache TTL should be {expected_ttl} seconds (30 days)"
            )
            
            # Verify cached data matches result
            cached_data = json.loads(call_args[0][2])
            assert cached_data == result, "Cached data should match result"
    
    @given(
        api_response=pincode_api_response_strategy(),
        num_requests=st.integers(min_value=2, max_value=5)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_cache_reduces_api_calls(
        self, api_response, num_requests, mock_redis
    ):
        """
        Property: Caching reduces API calls for repeated requests
        
        **Validates: Requirement 3.9**
        
        When the same pincode is looked up multiple times, only the first
        request SHALL make an API call; subsequent requests SHALL use cache.
        """
        service = PincodeLookupService(redis_client=mock_redis)
        pincode = api_response[0]["pincode"]
        
        # First request: no cache
        # Subsequent requests: return cached data
        call_count = 0
        
        async def mock_redis_get(key):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return None  # First call: cache miss
            else:
                # Subsequent calls: cache hit
                return json.dumps({
                    "pincode": pincode,
                    "state": api_response[0]["state"],
                    "district": api_response[0]["district"],
                    "villages": [entry["vpo"] for entry in api_response]
                })
        
        mock_redis.get = mock_redis_get
        
        api_call_count = 0
        
        async def mock_api_get(url):
            nonlocal api_call_count
            api_call_count += 1
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            return mock_response
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = mock_api_get
            
            # Make multiple requests
            for _ in range(num_requests):
                result = await service.lookup_pincode(pincode)
                assert result is not None, "Each request should return data"
            
            # Verify only one API call was made
            assert api_call_count == 1, (
                f"Expected 1 API call, got {api_call_count} for {num_requests} requests"
            )
    
    # ========================================================================
    # Requirement 3.10: Address Validation Against Pincode Data
    # ========================================================================
    
    @given(address_data=address_data_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_valid_address_passes_validation(
        self, address_data, service_no_cache
    ):
        """
        Property: Valid addresses pass validation against pincode data
        
        **Validates: Requirement 3.10**
        
        When address validation is performed with correct state, district,
        and village matching the pincode data, validation SHALL return True.
        """
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = address_data["api_response"]
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            is_valid = await service_no_cache.validate_address(
                pincode=address_data["pincode"],
                state=address_data["state"],
                district=address_data["district"],
                village=address_data["village"]
            )
            
            assert is_valid is True, (
                "Valid address should pass validation"
            )
    
    @given(address_data=address_data_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_validation_is_case_insensitive(
        self, address_data, service_no_cache
    ):
        """
        Property: Address validation is case-insensitive
        
        **Validates: Requirement 3.10**
        
        Address validation SHALL perform case-insensitive comparison for
        state, district, and village names.
        """
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = address_data["api_response"]
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            # Test with different case variations
            is_valid_upper = await service_no_cache.validate_address(
                pincode=address_data["pincode"],
                state=address_data["state"].upper(),
                district=address_data["district"].upper(),
                village=address_data["village"].upper()
            )
            
            is_valid_lower = await service_no_cache.validate_address(
                pincode=address_data["pincode"],
                state=address_data["state"].lower(),
                district=address_data["district"].lower(),
                village=address_data["village"].lower()
            )
            
            assert is_valid_upper is True, (
                "Uppercase address should pass validation"
            )
            assert is_valid_lower is True, (
                "Lowercase address should pass validation"
            )
    
    @given(
        address_data=address_data_strategy(),
        wrong_state=st.text(min_size=5, max_size=20)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_wrong_state_fails_validation(
        self, address_data, wrong_state, service_no_cache
    ):
        """
        Property: Incorrect state fails address validation
        
        **Validates: Requirement 3.10**
        
        When the provided state does not match the pincode data, validation
        SHALL return False.
        """
        assume(wrong_state.lower() != address_data["state"].lower())
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = address_data["api_response"]
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            is_valid = await service_no_cache.validate_address(
                pincode=address_data["pincode"],
                state=wrong_state,
                district=address_data["district"],
                village=address_data["village"]
            )
            
            assert is_valid is False, (
                "Wrong state should fail validation"
            )
    
    @given(
        address_data=address_data_strategy(),
        wrong_district=st.text(min_size=5, max_size=20)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_wrong_district_fails_validation(
        self, address_data, wrong_district, service_no_cache
    ):
        """
        Property: Incorrect district fails address validation
        
        **Validates: Requirement 3.10**
        
        When the provided district does not match the pincode data, validation
        SHALL return False.
        """
        assume(wrong_district.lower() != address_data["district"].lower())
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = address_data["api_response"]
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            is_valid = await service_no_cache.validate_address(
                pincode=address_data["pincode"],
                state=address_data["state"],
                district=wrong_district,
                village=address_data["village"]
            )
            
            assert is_valid is False, (
                "Wrong district should fail validation"
            )
    
    @given(
        address_data=address_data_strategy(),
        wrong_village=st.text(min_size=5, max_size=20)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_wrong_village_fails_validation(
        self, address_data, wrong_village, service_no_cache
    ):
        """
        Property: Incorrect village fails address validation
        
        **Validates: Requirement 3.10**
        
        When the provided village is not in the pincode's village list,
        validation SHALL return False.
        """
        # Ensure wrong_village is not in the villages list
        villages = [entry["vpo"].lower() for entry in address_data["api_response"]]
        assume(wrong_village.lower() not in villages)
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = address_data["api_response"]
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            is_valid = await service_no_cache.validate_address(
                pincode=address_data["pincode"],
                state=address_data["state"],
                district=address_data["district"],
                village=wrong_village
            )
            
            assert is_valid is False, (
                "Wrong village should fail validation"
            )
    
    @given(address_data=address_data_strategy())
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.asyncio
    async def test_validation_uses_lookup_internally(
        self, address_data, service_no_cache
    ):
        """
        Property: Address validation uses pincode lookup internally
        
        **Validates: Requirement 3.10**
        
        The validate_address method SHALL use lookup_pincode internally
        to fetch pincode data for validation.
        """
        api_call_count = 0
        
        async def mock_api_get(url):
            nonlocal api_call_count
            api_call_count += 1
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = address_data["api_response"]
            return mock_response
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = mock_api_get
            
            await service_no_cache.validate_address(
                pincode=address_data["pincode"],
                state=address_data["state"],
                district=address_data["district"],
                village=address_data["village"]
            )
            
            # Verify API was called (lookup happened)
            assert api_call_count == 1, (
                "validate_address should call lookup_pincode internally"
            )
