"""
Example script to test rate limiting functionality.

This script demonstrates how to test the rate limiting implementation
by making multiple requests to the API.

Requirements:
- FastAPI server running on http://localhost:8000
- Redis server running on localhost:6379
"""

import asyncio
import httpx
import time
from typing import Dict, List


async def make_request(client: httpx.AsyncClient, url: str, headers: Dict = None) -> Dict:
    """Make a single request and return response details."""
    try:
        response = await client.get(url, headers=headers or {})
        return {
            "status": response.status_code,
            "limit": response.headers.get("X-RateLimit-Limit"),
            "remaining": response.headers.get("X-RateLimit-Remaining"),
            "reset": response.headers.get("X-RateLimit-Reset"),
            "body": response.json() if response.status_code != 429 else response.text
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def test_public_rate_limit(base_url: str, num_requests: int = 25):
    """
    Test public/unauthenticated rate limiting.
    
    Expected behavior:
    - First 20 requests should succeed (200 OK)
    - Requests 21+ should be rate limited (429 Too Many Requests)
    """
    print("\n" + "="*80)
    print("Testing Public Rate Limit (20 requests/minute)")
    print("="*80)
    
    async with httpx.AsyncClient() as client:
        results = []
        
        for i in range(1, num_requests + 1):
            result = await make_request(client, f"{base_url}/marketplace/listings")
            results.append(result)
            
            print(f"Request {i:2d}: Status={result['status']}, "
                  f"Remaining={result.get('remaining', 'N/A')}, "
                  f"Limit={result.get('limit', 'N/A')}")
            
            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.1)
        
        # Summary
        success_count = sum(1 for r in results if r["status"] == 200)
        rate_limited_count = sum(1 for r in results if r["status"] == 429)
        
        print(f"\nSummary:")
        print(f"  Successful requests: {success_count}")
        print(f"  Rate limited requests: {rate_limited_count}")
        print(f"  Expected rate limit at request: 21")


async def test_authenticated_rate_limit(base_url: str, token: str, num_requests: int = 105):
    """
    Test authenticated user rate limiting.
    
    Expected behavior:
    - First 100 requests should succeed (200 OK)
    - Requests 101+ should be rate limited (429 Too Many Requests)
    """
    print("\n" + "="*80)
    print("Testing Authenticated Rate Limit (100 requests/minute)")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        results = []
        
        for i in range(1, num_requests + 1):
            result = await make_request(client, f"{base_url}/farms", headers)
            results.append(result)
            
            # Print every 10th request to avoid spam
            if i % 10 == 0 or result["status"] == 429:
                print(f"Request {i:3d}: Status={result['status']}, "
                      f"Remaining={result.get('remaining', 'N/A')}, "
                      f"Limit={result.get('limit', 'N/A')}")
            
            # Small delay
            await asyncio.sleep(0.05)
        
        # Summary
        success_count = sum(1 for r in results if r["status"] == 200)
        rate_limited_count = sum(1 for r in results if r["status"] == 429)
        
        print(f"\nSummary:")
        print(f"  Successful requests: {success_count}")
        print(f"  Rate limited requests: {rate_limited_count}")
        print(f"  Expected rate limit at request: 101")


async def test_rate_limit_headers(base_url: str):
    """Test that rate limit headers are present in responses."""
    print("\n" + "="*80)
    print("Testing Rate Limit Headers")
    print("="*80)
    
    async with httpx.AsyncClient() as client:
        result = await make_request(client, f"{base_url}/marketplace/listings")
        
        print(f"Status Code: {result['status']}")
        print(f"X-RateLimit-Limit: {result.get('limit', 'Missing')}")
        print(f"X-RateLimit-Remaining: {result.get('remaining', 'Missing')}")
        print(f"X-RateLimit-Reset: {result.get('reset', 'Missing')}")
        
        if result.get('limit') and result.get('remaining') and result.get('reset'):
            print("\n✅ All rate limit headers present")
        else:
            print("\n❌ Some rate limit headers missing")


async def test_rate_limit_reset(base_url: str):
    """Test that rate limits reset after the time window."""
    print("\n" + "="*80)
    print("Testing Rate Limit Reset (60 second window)")
    print("="*80)
    
    async with httpx.AsyncClient() as client:
        # Make requests until rate limited
        print("Making requests until rate limited...")
        for i in range(1, 25):
            result = await make_request(client, f"{base_url}/marketplace/listings")
            if result["status"] == 429:
                print(f"Rate limited at request {i}")
                reset_time = int(result.get('reset', 0))
                current_time = int(time.time())
                wait_time = reset_time - current_time + 1
                
                print(f"Waiting {wait_time} seconds for rate limit to reset...")
                await asyncio.sleep(wait_time)
                
                # Try again after reset
                result = await make_request(client, f"{base_url}/marketplace/listings")
                if result["status"] == 200:
                    print("✅ Rate limit successfully reset")
                else:
                    print(f"❌ Rate limit not reset (status: {result['status']})")
                break
            await asyncio.sleep(0.1)


async def main():
    """Run all rate limiting tests."""
    base_url = "http://localhost:8000"
    
    print("\n" + "="*80)
    print("Rate Limiting Test Suite")
    print("="*80)
    print(f"Base URL: {base_url}")
    print(f"Make sure the FastAPI server is running and Redis is available")
    print("="*80)
    
    # Test 1: Rate limit headers
    await test_rate_limit_headers(base_url)
    
    # Test 2: Public rate limit
    await test_public_rate_limit(base_url, num_requests=25)
    
    # Test 3: Authenticated rate limit (requires valid token)
    # Uncomment and provide a valid JWT token to test
    # token = "your-jwt-token-here"
    # await test_authenticated_rate_limit(base_url, token, num_requests=105)
    
    # Test 4: Rate limit reset
    # await test_rate_limit_reset(base_url)
    
    print("\n" + "="*80)
    print("Test Suite Complete")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
