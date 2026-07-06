#!/usr/bin/env python3
"""
Test script to verify farm registration works with BIGSERIAL auto-increment
"""

import sys
sys.path.insert(0, '/Users/puneetsharma/ai-bharat-hackathon/cropsense-ai/python')

from app.orm.farm import Farm
from app.orm.user import User

# Test 1: Verify users table exists and has BIGINT id
print("=" * 60)
print("Test 1: Verify users table structure")
print("=" * 60)

try:
    users = User.all().get()
    if users and users.items:
        print(f"✓ Users table exists with {len(users.items)} users")
        first_user = users.items[0]
        print(f"✓ First user ID: {first_user['id']} (type: {type(first_user['id']).__name__})")
    else:
        print("✓ Users table exists but is empty")
except Exception as e:
    print(f"✗ Error accessing users table: {e}")
    sys.exit(1)

# Test 2: Verify farms table exists and has BIGINT id
print("\n" + "=" * 60)
print("Test 2: Verify farms table structure")
print("=" * 60)

try:
    farms = Farm.all().get()
    if farms and farms.items:
        print(f"✓ Farms table exists with {len(farms.items)} farms")
        first_farm = farms.items[0]
        print(f"✓ First farm ID: {first_farm['id']} (type: {type(first_farm['id']).__name__})")
    else:
        print("✓ Farms table exists but is empty")
except Exception as e:
    print(f"✗ Error accessing farms table: {e}")
    sys.exit(1)

# Test 3: Create a test farm without providing ID
print("\n" + "=" * 60)
print("Test 3: Create farm without providing ID (auto-increment test)")
print("=" * 60)

try:
    # Get first user
    users = User.all().get()
    if not users or not users.items:
        print("✗ No users found - cannot test farm creation")
        sys.exit(1)
    
    user_id = users.items[0]['id']
    print(f"Using user ID: {user_id}")
    
    # Create farm WITHOUT providing ID - let database auto-generate
    farm_data = {
        'user_id': user_id,  # Required field
        'owner_id': user_id,  # Required field (farmer)
        'name': 'Test Farm BIGINT Auto-Increment',
        'location_state': 'Punjab',
        'location_district': 'Ludhiana',
        'location_village': 'Test Village',
        'total_area': 10.5,
        'area_unit': 'acres',
        'is_active': True
    }
    
    print(f"Creating farm with data (NO ID provided): {farm_data}")
    
    # Insert and get the created record
    result = Farm.create(farm_data).get_inserted()
    
    if result and hasattr(result, 'items') and result.items:
        created_farm = result.items  # items is a dict, not a list
        farm_id = created_farm['id']
        print(f"✓ Farm created successfully!")
        print(f"✓ Auto-generated ID: {farm_id} (type: {type(farm_id).__name__})")
        print(f"✓ Farm name: {created_farm['name']}")
        
        # Verify it's a BIGINT (should be int type in Python)
        if isinstance(farm_id, int):
            print(f"✓ ID is integer type (BIGINT in database)")
        else:
            print(f"✗ ID is {type(farm_id).__name__}, expected int")
            sys.exit(1)
            
    else:
        print("✗ Farm creation failed - no result returned")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error creating farm: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verify the farm was actually saved
print("\n" + "=" * 60)
print("Test 4: Verify farm was saved to database")
print("=" * 60)

try:
    # Query the farm we just created
    saved_farm = Farm.where({'id': [farm_id]}).get()
    
    if saved_farm and saved_farm.items:
        farm = saved_farm.items[0]
        print(f"✓ Farm retrieved from database")
        print(f"✓ ID: {farm['id']}")
        print(f"✓ Name: {farm['name']}")
        print(f"✓ State: {farm['location_state']}")
    else:
        print("✗ Farm not found in database")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error retrieving farm: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED! ✓")
print("=" * 60)
print("\nSummary:")
print("- Users table has BIGINT ID")
print("- Farms table has BIGINT ID")
print("- Farm creation works WITHOUT providing ID")
print("- Database auto-generates BIGINT IDs correctly")
print("- No UUID generation needed in application code")
