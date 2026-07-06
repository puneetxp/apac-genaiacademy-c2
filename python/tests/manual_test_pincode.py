"""
Manual test script for pincode lookup service

Run this to verify the pincode lookup service works correctly.
"""

import asyncio
import sys
sys.path.insert(0, '/Users/puneetsharma/ai-bharat-hackathon/cropsense-ai/python')

from app.services.pincode_lookup_service import PincodeLookupService


async def test_pincode_lookup():
    """Test pincode lookup with real API"""
    service = PincodeLookupService(redis_client=None)
    
    print("Testing Pincode Lookup Service")
    print("=" * 50)
    
    # Test 1: Valid Delhi pincode
    print("\nTest 1: Looking up Delhi pincode 110001...")
    result = await service.lookup_pincode("110001")
    if result:
        print(f"✓ Success!")
        print(f"  State: {result['state']}")
        print(f"  District: {result['district']}")
        print(f"  Villages: {', '.join(result['villages'][:3])}...")
    else:
        print("✗ Failed to lookup pincode")
    
    # Test 2: Valid Mumbai pincode
    print("\nTest 2: Looking up Mumbai pincode 400001...")
    result = await service.lookup_pincode("400001")
    if result:
        print(f"✓ Success!")
        print(f"  State: {result['state']}")
        print(f"  District: {result['district']}")
        print(f"  Villages: {', '.join(result['villages'][:3])}...")
    else:
        print("✗ Failed to lookup pincode")
    
    # Test 3: Invalid pincode
    print("\nTest 3: Looking up invalid pincode 999999...")
    result = await service.lookup_pincode("999999")
    if result is None:
        print("✓ Correctly returned None for invalid pincode")
    else:
        print("✗ Should have returned None")
    
    # Test 4: Address validation
    print("\nTest 4: Validating address...")
    is_valid = await service.validate_address(
        pincode="110001",
        state="Delhi",
        district="Central Delhi",
        village="Connaught Place"
    )
    if is_valid:
        print("✓ Address validation passed")
    else:
        print("✗ Address validation failed")
    
    # Test 5: Address validation with wrong state
    print("\nTest 5: Validating address with wrong state...")
    is_valid = await service.validate_address(
        pincode="110001",
        state="Maharashtra",
        district="Central Delhi",
        village="Connaught Place"
    )
    if not is_valid:
        print("✓ Correctly rejected invalid address")
    else:
        print("✗ Should have rejected invalid address")
    
    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_pincode_lookup())
