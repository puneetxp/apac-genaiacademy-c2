"""
Manual test script for advance booking system
Tests Task 27.2: Build advance booking system
"""

import sys
import os
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.advance_booking_service import AdvanceBookingService


def setup_database():
    """Setup database connection"""
    DATABASE_URL = 'postgresql://puneetsharma:password@localhost:5432/cropsense_dev'
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def create_test_data(db):
    """Create test data for booking tests"""
    print("Creating test data...")
    
    # Create test farmer
    query = text("""
        INSERT INTO users (email, name, phone, role)
        VALUES (:email, :name, :phone, :role)
        ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
        RETURNING id
    """)
    
    result = db.execute(query, {
        'email': 'test_farmer@example.com',
        'name': 'Test Farmer',
        'phone': '+919876543210',
        'role': 'farmer'
    })
    
    farmer_id = str(result.fetchone()[0])
    print(f"Created farmer: {farmer_id}")
    
    # Create test buyer
    result = db.execute(query, {
        'email': 'test_buyer@example.com',
        'name': 'Test Buyer',
        'phone': '+919876543211',
        'role': 'buyer'
    })
    
    buyer_id = str(result.fetchone()[0])
    print(f"Created buyer: {buyer_id}")
    
    # Create test farm
    farm_query = text("""
        INSERT INTO farms (farmer_id, name, total_area, location_state, location_district)
        VALUES (:farmer_id, :name, :total_area, :state, :district)
        RETURNING id
    """)
    
    result = db.execute(farm_query, {
        'farmer_id': farmer_id,
        'name': 'Test Farm',
        'total_area': 10,
        'state': 'Punjab',
        'district': 'Ludhiana'
    })
    
    farm_id = str(result.fetchone()[0])
    print(f"Created farm: {farm_id}")
    
    # Create test crop
    crop_query = text("""
        INSERT INTO crops (farm_id, farmer_id, crop_type, crop_variety, planting_date, expected_harvest_date)
        VALUES (:farm_id, :farmer_id, :crop_type, :variety, :planting_date, :harvest_date)
        RETURNING id
    """)
    
    result = db.execute(crop_query, {
        'farm_id': farm_id,
        'farmer_id': farmer_id,
        'crop_type': 'Wheat',
        'variety': 'HD-2967',
        'planting_date': date.today() - timedelta(days=90),
        'harvest_date': date.today() + timedelta(days=30)
    })
    
    crop_id = str(result.fetchone()[0])
    print(f"Created crop: {crop_id}")
    
    # Create test listing
    listing_query = text("""
        INSERT INTO listings (
            crop_id, farmer_id, title, crop_type, crop_variety,
            estimated_quantity, available_quantity, expected_harvest_date,
            location_state, location_district, status
        ) VALUES (
            :crop_id, :farmer_id, :title, :crop_type, :variety,
            :estimated_qty, :available_qty, :harvest_date,
            :state, :district, :status
        ) RETURNING id
    """)
    
    result = db.execute(listing_query, {
        'crop_id': crop_id,
        'farmer_id': farmer_id,
        'title': 'Premium Wheat for Sale',
        'crop_type': 'Wheat',
        'variety': 'HD-2967',
        'estimated_qty': 1000,
        'available_qty': 1000,
        'harvest_date': date.today() + timedelta(days=30),
        'state': 'Punjab',
        'district': 'Ludhiana',
        'status': 'active'
    })
    
    listing_id = str(result.fetchone()[0])
    print(f"Created listing: {listing_id}")
    
    db.commit()
    
    return {
        'farmer_id': farmer_id,
        'buyer_id': buyer_id,
        'farm_id': farm_id,
        'crop_id': crop_id,
        'listing_id': listing_id
    }


def test_create_booking(db, test_data):
    """Test creating an advance booking"""
    print("\n=== Test 1: Create Booking ===")
    
    service = AdvanceBookingService(db)
    
    try:
        booking = service.create_booking(
            listing_id=test_data['listing_id'],
            buyer_id=test_data['buyer_id'],
            quantity_booked=Decimal('100'),
            price_per_unit=Decimal('25.50'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A', 'organic_certified': False},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        print(f"✓ Booking created successfully")
        print(f"  Booking ID: {booking['booking_id']}")
        print(f"  Quantity: {booking['quantity_booked']} kg")
        print(f"  Total Amount: ₹{booking['total_amount']}")
        print(f"  Advance Payment: ₹{booking['advance_payment_amount']}")
        print(f"  Status: {booking['status']}")
        print(f"  Payment Milestones: {len(booking['payment_schedule'])}")
        
        return booking['booking_id']
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return None


def test_confirm_booking(db, booking_id, test_data):
    """Test confirming a booking and updating available quantity"""
    print("\n=== Test 2: Confirm Booking ===")
    
    service = AdvanceBookingService(db)
    
    # Get initial available quantity
    query = text("SELECT available_quantity FROM listings WHERE id = :listing_id")
    result = db.execute(query, {'listing_id': test_data['listing_id']})
    initial_qty = float(result.fetchone()[0])
    print(f"Initial available quantity: {initial_qty} kg")
    
    try:
        result = service.confirm_booking(booking_id)
        
        print(f"✓ Booking confirmed successfully")
        print(f"  Booking ID: {result['booking_id']}")
        print(f"  Status: {result['status']}")
        print(f"  New Available Quantity: {result['new_available_quantity']} kg")
        print(f"  Quantity Reduced By: {initial_qty - result['new_available_quantity']} kg")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False


def test_cancel_booking(db, booking_id, test_data):
    """Test cancelling a booking and restoring available quantity"""
    print("\n=== Test 3: Cancel Booking ===")
    
    service = AdvanceBookingService(db)
    
    # Get current available quantity
    query = text("SELECT available_quantity FROM listings WHERE id = :listing_id")
    result = db.execute(query, {'listing_id': test_data['listing_id']})
    current_qty = float(result.fetchone()[0])
    print(f"Current available quantity: {current_qty} kg")
    
    try:
        result = service.cancel_booking(booking_id)
        
        print(f"✓ Booking cancelled successfully")
        print(f"  Booking ID: {result['booking_id']}")
        print(f"  Status: {result['status']}")
        if result['new_available_quantity']:
            print(f"  New Available Quantity: {result['new_available_quantity']} kg")
            print(f"  Quantity Restored By: {result['new_available_quantity'] - current_qty} kg")
        else:
            print(f"  No quantity change (booking was not confirmed)")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False


def test_quantity_validation(db, test_data):
    """Test that booking fails when quantity exceeds available"""
    print("\n=== Test 4: Quantity Validation ===")
    
    service = AdvanceBookingService(db)
    
    try:
        booking = service.create_booking(
            listing_id=test_data['listing_id'],
            buyer_id=test_data['buyer_id'],
            quantity_booked=Decimal('2000'),  # More than available 1000
            price_per_unit=Decimal('25.00'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        print(f"✗ Test failed: Booking should have been rejected")
        return False
        
    except ValueError as e:
        if "exceeds available quantity" in str(e):
            print(f"✓ Validation passed: {str(e)}")
            return True
        else:
            print(f"✗ Unexpected error: {str(e)}")
            return False


def cleanup_test_data(db, test_data):
    """Clean up test data"""
    print("\n=== Cleaning up test data ===")
    
    try:
        # Delete in reverse order of creation
        db.execute(text("DELETE FROM advance_bookings WHERE listing_id = :listing_id"), 
                   {'listing_id': test_data['listing_id']})
        db.execute(text("DELETE FROM listings WHERE id = :listing_id"), 
                   {'listing_id': test_data['listing_id']})
        db.execute(text("DELETE FROM crops WHERE id = :crop_id"), 
                   {'crop_id': test_data['crop_id']})
        db.execute(text("DELETE FROM farms WHERE id = :farm_id"), 
                   {'farm_id': test_data['farm_id']})
        db.execute(text("DELETE FROM users WHERE id IN (:farmer_id, :buyer_id)"), 
                   {'farmer_id': test_data['farmer_id'], 'buyer_id': test_data['buyer_id']})
        
        db.commit()
        print("✓ Test data cleaned up")
        
    except Exception as e:
        print(f"✗ Cleanup failed: {str(e)}")
        db.rollback()


def main():
    """Run all tests"""
    print("=" * 60)
    print("Advance Booking System - Manual Tests")
    print("Task 27.2: Build advance booking system")
    print("=" * 60)
    
    db = setup_database()
    
    try:
        # Create test data
        test_data = create_test_data(db)
        
        # Run tests
        booking_id = test_create_booking(db, test_data)
        
        if booking_id:
            test_confirm_booking(db, booking_id, test_data)
            test_cancel_booking(db, booking_id, test_data)
        
        test_quantity_validation(db, test_data)
        
        # Cleanup
        cleanup_test_data(db, test_data)
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        
    finally:
        db.close()


if __name__ == '__main__':
    main()
