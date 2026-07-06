"""
Verification Test for Pincode API Endpoint Configuration

**Validates: Requirements 1.7, 2.8**

This test verifies that the pincode lookup service is correctly configured
to use the external API endpoint "https://pincode.deno.dev".

NOTE: This test is expected to PASS on unfixed code since investigation
shows the configuration is already correct.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
import httpx

from app.services.pincode_lookup_service import PincodeLookupService


class TestPincodeAPIEndpointVerification:
    """
    Verification tests for pincode API endpoint configuration
    
    Property 1: Fault Condition - Pincode API Configuration
    
    For any pincode lookup request, the service SHALL use the correct
    API endpoint "https://pincode.deno.dev/{pincode}" as configured.
    """
    
    @pytest.fixture
    def service(self):
        """Create service instance without Redis"""
        return PincodeLookupService(redis_client=None)
    
    def test_pincode_api_url_constant_is_correct(self, service):
        """
        Test that PINCODE_API_URL constant is set to correct endpoint
        
        **Validates: Requirements 1.7, 2.8**
        
        Verifies that the service class constant PINCODE_API_URL is set to
        "https://pincode.deno.dev" as specified in the requirements.
        """
        expected_url = "https://pincode.deno.dev"
        actual_url = PincodeLookupService.PINCODE_API_URL
        
        assert actual_url == expected_url, (
            f"PINCODE_API_URL should be '{expected_url}' but got '{actual_url}'"
        )
    
    @pytest.mark.asyncio
    async def test_actual_api_calls_use_correct_endpoint(self, service):
        """
        Test that actual API calls use the correct endpoint format
        
        **Validates: Requirements 1.7, 2.8**
        
        Verifies that when lookup_pincode() is called, it makes HTTP requests
        to the correct endpoint: https://pincode.deno.dev/{pincode}
        """
        test_pincode = "110001"
        expected_url = f"https://pincode.deno.dev/{test_pincode}"
        
        with patch('httpx.AsyncClient') as mock_client:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {
                    "pincode": test_pincode,
                    "state": "Delhi",
                    "district": "Central Delhi",
                    "vpo": "Connaught Place"
                }
            ]
            
            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get
            
            # Make the API call
            result = await service.lookup_pincode(test_pincode)
            
            # Verify the correct endpoint was called
            mock_get.assert_called_once_with(expected_url)
            
            # Verify result is not None (successful lookup)
            assert result is not None, "API call should return data"
    
    @pytest.mark.asyncio
    async def test_multiple_pincodes_use_correct_endpoint_format(self, service):
        """
        Test that multiple different pincodes all use correct endpoint format
        
        **Validates: Requirements 1.7, 2.8**
        
        Verifies that the endpoint format is consistently correct across
        different pincode values.
        """
        test_pincodes = ["110001", "400001", "560001", "700001"]
        
        for pincode in test_pincodes:
            expected_url = f"https://pincode.deno.dev/{pincode}"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = [
                    {
                        "pincode": pincode,
                        "state": "Test State",
                        "district": "Test District",
                        "vpo": "Test Village"
                    }
                ]
                
                mock_get = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value.get = mock_get
                
                # Make the API call
                await service.lookup_pincode(pincode)
                
                # Verify the correct endpoint was called
                mock_get.assert_called_once_with(expected_url)
    
    @pytest.mark.asyncio
    async def test_response_parsing_works_correctly(self, service):
        """
        Test that responses from the API are parsed correctly
        
        **Validates: Requirements 1.7, 2.8**
        
        Verifies that the service correctly parses responses from the
        pincode API endpoint.
        """
        test_pincode = "110001"
        api_response = [
            {
                "pincode": "110001",
                "state": "Delhi",
                "district": "Central Delhi",
                "vpo": "Connaught Place"
            },
            {
                "pincode": "110001",
                "state": "Delhi",
                "district": "Central Delhi",
                "vpo": "Parliament Street"
            }
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await service.lookup_pincode(test_pincode)
            
            # Verify response is parsed correctly
            assert result is not None, "Result should not be None"
            assert result['pincode'] == "110001", "Pincode should be parsed correctly"
            assert result['state'] == "Delhi", "State should be parsed correctly"
            assert result['district'] == "Central Delhi", "District should be parsed correctly"
            assert len(result['villages']) == 2, "Villages should be parsed correctly"
            assert "Connaught Place" in result['villages'], "Village 1 should be in list"
            assert "Parliament Street" in result['villages'], "Village 2 should be in list"
    
    @pytest.mark.asyncio
    async def test_endpoint_configuration_with_timeout(self, service):
        """
        Test that timeout configuration doesn't affect endpoint URL
        
        **Validates: Requirements 1.7, 2.8**
        
        Verifies that the timeout setting (5 seconds) is applied correctly
        while still using the correct endpoint.
        """
        test_pincode = "110001"
        expected_url = f"https://pincode.deno.dev/{test_pincode}"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"pincode": test_pincode, "state": "Test", "district": "Test", "vpo": "Test"}
            ]
            
            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get
            
            await service.lookup_pincode(test_pincode)
            
            # Verify AsyncClient was created with correct timeout
            mock_client.assert_called_once_with(timeout=5)
            
            # Verify correct endpoint was called
            mock_get.assert_called_once_with(expected_url)
    
    def test_service_constants_are_correct(self, service):
        """
        Test that all service constants are correctly configured
        
        **Validates: Requirements 1.7, 2.8**
        
        Verifies that the service has all required constants set correctly:
        - PINCODE_API_URL: "https://pincode.deno.dev"
        - TIMEOUT_SECONDS: 5
        - CACHE_TTL_DAYS: 30
        """
        assert PincodeLookupService.PINCODE_API_URL == "https://pincode.deno.dev", (
            "PINCODE_API_URL should be 'https://pincode.deno.dev'"
        )
        assert PincodeLookupService.TIMEOUT_SECONDS == 5, (
            "TIMEOUT_SECONDS should be 5"
        )
        assert PincodeLookupService.CACHE_TTL_DAYS == 30, (
            "CACHE_TTL_DAYS should be 30"
        )
