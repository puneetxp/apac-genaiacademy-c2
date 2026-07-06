#!/usr/bin/env python3
"""
Create test user for E2E tests
Run this script to create the testfarmer user needed for E2E testing
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.orm.user_sqlalchemy import User
from app.core.password import hash_password
import uuid
from datetime import datetime

def create_test_user():
    """Create test user for E2E tests"""
    
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "testfarmer").first()
        
        if existing_user:
            print("✅ Test user 'testfarmer' already exists")
            print(f"   User ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            print(f"   Full Name: {existing_user.name}")
            return True
        
        # Create new test user
        print("👤 Creating test user 'testfarmer'...")
        
        test_user = User(
            cognito_user_id="testfarmer_001",
            username="testfarmer",
            email="test.farmer@example.com",
            name="Test Farmer",
            phone="+919876543210",
            password=hash_password("TestPass123!"),
            user_type="farmer",
            is_active=1,
            is_verified=1,
            enable=1
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Test user created successfully!")
        print(f"   Username: {test_user.username}")
        print(f"   Password: TestPass123!")
        print(f"   Email: {test_user.email}")
        print(f"   Full Name: {test_user.name}")
        print(f"   Phone: {test_user.phone}")
        print(f"   User ID: {test_user.id}")
        print(f"   User Type: {test_user.user_type}")
        print(f"   Active: {test_user.is_active}")
        print(f"   Verified: {test_user.is_verified}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()


def verify_test_user():
    """Verify test user can be retrieved"""
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.username == "testfarmer").first()
        
        if user:
            print("\n🔍 Verification:")
            print(f"   ✅ User found in database")
            print(f"   ✅ Username: {user.username}")
            print(f"   ✅ Email: {user.email}")
            print(f"   ✅ Active: {user.is_active}")
            print(f"   ✅ Verified: {user.is_verified}")
            return True
        else:
            print("\n❌ Verification failed: User not found")
            return False
            
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("E2E Test User Setup")
    print("=" * 60)
    print()
    
    # Create test user
    success = create_test_user()
    
    if success:
        # Verify user was created
        verify_test_user()
        
        print()
        print("=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print()
        print("You can now run E2E tests:")
        print("  cd ../e2e")
        print("  npm test")
        print()
        print("Or test login via API:")
        print("  curl -X POST http://localhost:8000/auth/signin \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{\"username\": \"testfarmer\", \"password\": \"TestPass123!\"}'")
        print()
    else:
        print()
        print("=" * 60)
        print("❌ Setup Failed")
        print("=" * 60)
        print()
        print("Please check:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'cropsense_dev' exists")
        print("  3. Database credentials in .env are correct")
        print()
        sys.exit(1)
