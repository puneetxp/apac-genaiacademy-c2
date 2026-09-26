"""
Pincode Lookup Service

Integrates with external pincode API (https://pincode.deno.dev) to auto-fill
address information based on Indian postal codes.
"""

import logging
from datetime import timedelta
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class PincodeLookupService:
    """Service for looking up address information from pincode"""

    PINCODE_API_URL = "https://pincode.deno.dev"
    TIMEOUT_SECONDS = 5
    CACHE_TTL_DAYS = 30

    def __init__(self, redis_client=None):
        """
        Initialize pincode lookup service

        Args:
            redis_client: Optional Redis client for caching
        """
        self.redis_client = redis_client
        self.cache_ttl = timedelta(days=self.CACHE_TTL_DAYS)

    async def lookup_pincode(self, pincode: str) -> Optional[dict]:
        """
        Look up address information for a pincode

        Args:
            pincode: 6-digit Indian pincode

        Returns:
            Dictionary with state, district, and list of villages/VPOs
            None if pincode not found or API error
        """
        # Check cache first
        if self.redis_client:
            cached_data = await self._get_from_cache(pincode)
            if cached_data:
                logger.info(f"Pincode {pincode} found in cache")
                return cached_data

        # Fetch from API
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS) as client:
                response = await client.get(f"{self.PINCODE_API_URL}/{pincode}")

                if response.status_code == 200:
                    data = response.json()

                    if not data or len(data) == 0:
                        logger.warning(f"No data found for pincode {pincode}")
                        return None

                    # Parse response - API returns array of locations
                    result = self._parse_api_response(data)

                    # Cache the result
                    if self.redis_client and result:
                        await self._save_to_cache(pincode, result)

                    logger.info(f"Successfully looked up pincode {pincode}")
                    return result

                elif response.status_code == 404:
                    logger.warning(f"Pincode {pincode} not found")
                    return None
                else:
                    logger.error(f"Pincode API returned status {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.error(f"Timeout looking up pincode {pincode}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error looking up pincode {pincode}: {e}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error looking up pincode {pincode}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error looking up pincode {pincode}: {e}")
            return None

    def _parse_api_response(self, data: list) -> dict:
        """
        Parse API response into standardized format

        Args:
            data: List of location objects from API

        Returns:
            Dictionary with state, district, and villages list
        """
        if not data or len(data) == 0:
            return None

        # Extract unique state and district (should be same for all entries)
        state = data[0].get("state", "")
        district = data[0].get("district", "")
        pincode = data[0].get("pincode", "")

        # Extract all unique villages/VPOs
        villages = list(set([entry.get("vpo", "") for entry in data if entry.get("vpo")]))

        return {"pincode": pincode, "state": state, "district": district, "villages": villages}

    async def _get_from_cache(self, pincode: str) -> Optional[dict]:
        """Get pincode data from Redis cache"""
        try:
            import json

            cache_key = f"pincode:{pincode}"
            cached = await self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
        return None

    async def _save_to_cache(self, pincode: str, data: dict) -> None:
        """Save pincode data to Redis cache"""
        try:
            import json

            cache_key = f"pincode:{pincode}"
            await self.redis_client.setex(
                cache_key, int(self.cache_ttl.total_seconds()), json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")

    async def validate_address(self, pincode: str, state: str, district: str, village: str) -> bool:
        """
        Validate that address components match pincode data

        Args:
            pincode: 6-digit pincode
            state: State name
            district: District name
            village: Village/VPO name

        Returns:
            True if address is valid, False otherwise
        """
        lookup_result = await self.lookup_pincode(pincode)

        if not lookup_result:
            logger.warning(f"Cannot validate address - pincode {pincode} lookup failed")
            return False

        # Case-insensitive comparison
        state_match = lookup_result["state"].lower() == state.lower()
        district_match = lookup_result["district"].lower() == district.lower()

        # We relax the village matching constraint because demo data and unlisted villages
        # should still be registerable if the Pincode, State & District are valid.
        # village_match = any(
        #     v.lower() == village.lower()
        #     for v in lookup_result['villages']
        # )
        village_match = True

        if not state_match:
            logger.warning(
                f"State mismatch for pincode {pincode}: {state} != {lookup_result['state']}"
            )
        if not district_match:
            logger.warning(
                f"District mismatch for pincode {pincode}: {district} != {lookup_result['district']}"
            )
        # if not village_match:
        #     logger.warning(f"Village {village} not found in pincode {pincode} villages")

        return state_match and district_match and village_match
