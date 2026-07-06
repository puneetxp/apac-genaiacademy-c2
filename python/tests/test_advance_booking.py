"""
Unit tests for advance booking system
Tests Task 27.2: Build advance booking system
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session, sessionmaker
import os


# Use actual test database
DATABASE_URL = os.getenv(
    'TEST_DATABASE_URL',
    'postgresql://puneetsharma:password@localhost:5432/cropsense_dev'
)


@pytest.fixture(scope="module")
def test_db():
    """Create test database session"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db
    
    # Cleanup: rollback any uncommitted changes
    db.rollback()
    db.close()


@pytest.fixture
def db_session(test_db):
    """Get database session for tests"""
    # Start a transaction
    test_db.begin_nested()
    
    yield test_db
    
    # Rollback transaction after test
    test_db.rollback()


@pytest.fixture
def booking_service(db_session):
    """Get booking service instance"""
    from app.services.advance_booking_service import AdvanceBookingService
    return AdvanceBookingService(db_session)


@pytest.fixture
def test_user(db_session):
    """Create test user (farmer)"""
    query = text("""
        INSERT INTO users (email, name, phone, role)
        VALUES (:email, :name, :phone, :role)
        RETURNING id
    """)
    
    result = db_session.execute(query, {
        'email': 'farmer@test.com',
        'name': 'Test Farmer',
        'phone': '+919876543210',
        'role': 'farmer'
    })
    
    user_id = str(result.fetchone()[0])
    db_session.commit()
    
    return user_id


@pytest.fixture
def test_buyer(db_session):
    """Create test buyer"""
    query = text("""
        INSERT INTO users (email, name, phone, role)
        VALUES (:email, :name, :phone, :role)
        RETURNING id
    """)
    
    result = db_session.execute(query, {
        'email': 'buyer@test.com',
        'name': 'Test Buyer',
        'phone': '+919876543211',
        'role': 'buyer'
    })
    
    buyer_id = str(result.fetchone()[0])
    db_session.commit()
    
    return buyer_id


@pytest.fixture
def test_farm(db_session, test_user):
    """Create test farm"""
    query = text("""
        INSERT INTO farms (farmer_id, name, total_area, location_state, location_district)
        VALUES (:farmer_id, :name, :total_area, :state, :district)
        RETURNING id
    """)
    
    result = db_session.execute(query, {
        'farmer_id': test_user,
        'name': 'Test Farm',
        'total_area': 10,
        'state': 'Punjab',
        'district': 'Ludhiana'
    })
    
    farm_id = str(result.fetchone()[0])
    db_session.commit()
    
    return farm_id


@pytest.fixture
def test_crop(db_session, test_farm, test_user):
    """Create test crop"""
    query = text("""
        INSERT INTO crops (farm_id, farmer_id, crop_type, crop_variety, planting_date, expected_harvest_date)
        VALUES (:farm_id, :farmer_id, :crop_type, :variety, :planting_date, :harvest_date)
        RETURNING id
    """)
    
    result = db_session.execute(query, {
        'farm_id': test_farm,
        'farmer_id': test_user,
        'crop_type': 'Wheat',
        'variety': 'HD-2967',
        'planting_date': date.today() - timedelta(days=90),
        'harvest_date': date.today() + timedelta(days=30)
    })
    
    crop_id = str(result.fetchone()[0])
    db_session.commit()
    
    return crop_id


@pytest.fixture
def test_listing(db_session, test_crop, test_user):
    """Create test marketplace listing"""
    query = text("""
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
    
    result = db_session.execute(query, {
        'crop_id': test_crop,
        'farmer_id': test_user,
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
    db_session.commit()
    
    return listing_id


class TestAdvanceBookingCreation:
    """Test advance booking creation"""
    
    def test_create_booking_success(self, booking_service, test_listing, test_buyer):
        """Test successful booking creation"""
        booking = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('100'),
            price_per_unit=Decimal('25.50'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A', 'organic_certified': False},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        assert booking is not None
        assert booking['quantity_booked'] == 100.0
        assert booking['total_amount'] == 2550.0  # 100 * 25.50
        assert booking['advance_payment_amount'] == 510.0  # 20% of 2550
        assert booking['status'] == 'pending'
        assert len(booking['payment_schedule']) == 4  # advance, quality, delivery, final
    
    def test_create_booking_calculates_advance_payment(self, booking_service, test_listing, test_buyer):
        """Test advance payment calculation"""
        booking = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('200'),
            price_per_unit=Decimal('30.00'),
            advance_payment_percent=30,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'CIF'}
        )
        
        # Total: 200 * 30 = 6000
        # Advance: 30% of 6000 = 1800
        assert booking['total_amount'] == 6000.0
        assert booking['advance_payment_amount'] == 1800.0
    
    def test_create_booking_exceeds_available_quantity(self, booking_service, test_listing, test_buyer):
        """Test booking fails when quantity exceeds available"""
        with pytest.raises(ValueError, match="exceeds available quantity"):
            booking_service.create_booking(
                listing_id=test_listing,
                buyer_id=test_buyer,
                quantity_booked=Decimal('1500'),  # More than available 1000
                price_per_unit=Decimal('25.00'),
                advance_payment_percent=20,
                expected_delivery_date=date.today() + timedelta(days=35),
                quality_standards={'grade': 'A'},
                contract_terms={'delivery_terms': 'FOB'}
            )
    
    def test_create_booking_invalid_listing(self, booking_service, test_buyer):
        """Test booking fails with invalid listing ID"""
        with pytest.raises(ValueError, match="not found"):
            booking_service.create_booking(
                listing_id='00000000-0000-0000-0000-000000000000',
                buyer_id=test_buyer,
                quantity_booked=Decimal('100'),
                price_per_unit=Decimal('25.00'),
                advance_payment_percent=20,
                expected_delivery_date=date.today() + timedelta(days=35),
                quality_standards={'grade': 'A'},
                contract_terms={'delivery_terms': 'FOB'}
            )


class TestBookingConfirmation:
    """Test booking confirmation and quantity updates"""
    
    def test_confirm_booking_updates_available_quantity(
        self, booking_service, test_listing, test_buyer, db_session
    ):
        """Test confirming booking reduces available quantity"""
        # Create booking
        booking = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('100'),
            price_per_unit=Decimal('25.00'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        booking_id = booking['booking_id']
        
        # Get initial available quantity
        query = text("SELECT available_quantity FROM listings WHERE id = :listing_id")
        result = db_session.execute(query, {'listing_id': test_listing})
        initial_qty = float(result.fetchone()[0])
        
        # Confirm booking
        result = booking_service.confirm_booking(booking_id)
        
        assert result['status'] == 'confirmed'
        assert result['new_available_quantity'] == initial_qty - 100.0
    
    def test_confirm_booking_already_confirmed(
        self, booking_service, test_listing, test_buyer
    ):
        """Test confirming already confirmed booking fails"""
        # Create and confirm booking
        booking = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('100'),
            price_per_unit=Decimal('25.00'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        booking_id = booking['booking_id']
        booking_service.confirm_booking(booking_id)
        
        # Try to confirm again
        with pytest.raises(ValueError, match="not in pending status"):
            booking_service.confirm_booking(booking_id)


class TestBookingCancellation:
    """Test booking cancellation"""
    
    def test_cancel_confirmed_booking_restores_quantity(
        self, booking_service, test_listing, test_buyer, db_session
    ):
        """Test cancelling confirmed booking restores available quantity"""
        # Create and confirm booking
        booking = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('100'),
            price_per_unit=Decimal('25.00'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        booking_id = booking['booking_id']
        booking_service.confirm_booking(booking_id)
        
        # Get quantity after confirmation
        query = text("SELECT available_quantity FROM listings WHERE id = :listing_id")
        result = db_session.execute(query, {'listing_id': test_listing})
        qty_after_confirm = float(result.fetchone()[0])
        
        # Cancel booking
        result = booking_service.cancel_booking(booking_id)
        
        assert result['status'] == 'cancelled'
        assert result['new_available_quantity'] == qty_after_confirm + 100.0
    
    def test_cancel_pending_booking_no_quantity_change(
        self, booking_service, test_listing, test_buyer
    ):
        """Test cancelling pending booking doesn't change quantity"""
        # Create booking (don't confirm)
        booking = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('100'),
            price_per_unit=Decimal('25.00'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        booking_id = booking['booking_id']
        
        # Cancel booking
        result = booking_service.cancel_booking(booking_id)
        
        assert result['status'] == 'cancelled'
        assert result['new_available_quantity'] is None  # No quantity change


class TestBookingRetrieval:
    """Test booking retrieval operations"""
    
    def test_get_booking_by_id(self, booking_service, test_listing, test_buyer):
        """Test retrieving booking by ID"""
        # Create booking
        booking = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('100'),
            price_per_unit=Decimal('25.00'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        booking_id = booking['booking_id']
        
        # Retrieve booking
        retrieved = booking_service.get_booking(booking_id)
        
        assert retrieved is not None
        assert retrieved['id'] == booking_id
        assert retrieved['quantity_booked'] == 100.0
    
    def test_list_bookings_by_buyer(self, booking_service, test_listing, test_buyer):
        """Test listing bookings filtered by buyer"""
        # Create multiple bookings
        for i in range(3):
            booking_service.create_booking(
                listing_id=test_listing,
                buyer_id=test_buyer,
                quantity_booked=Decimal('50'),
                price_per_unit=Decimal('25.00'),
                advance_payment_percent=20,
                expected_delivery_date=date.today() + timedelta(days=35),
                quality_standards={'grade': 'A'},
                contract_terms={'delivery_terms': 'FOB'}
            )
        
        # List bookings
        bookings = booking_service.list_bookings(buyer_id=test_buyer)
        
        assert len(bookings) == 3
        assert all(b['buyer_id'] == test_buyer for b in bookings)
    
    def test_list_bookings_by_status(self, booking_service, test_listing, test_buyer):
        """Test listing bookings filtered by status"""
        # Create and confirm one booking
        booking1 = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('50'),
            price_per_unit=Decimal('25.00'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        booking_service.confirm_booking(booking1['booking_id'])
        
        # Create another pending booking
        booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('50'),
            price_per_unit=Decimal('25.00'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        # List confirmed bookings
        confirmed = booking_service.list_bookings(status='confirmed')
        assert len(confirmed) >= 1
        assert all(b['status'] == 'confirmed' for b in confirmed)
        
        # List pending bookings
        pending = booking_service.list_bookings(status='pending')
        assert len(pending) >= 1
        assert all(b['status'] == 'pending' for b in pending)


class TestPaymentMilestones:
    """Test payment milestone creation"""
    
    def test_payment_milestones_created(self, booking_service, test_listing, test_buyer):
        """Test payment milestones are created with booking"""
        booking = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('100'),
            price_per_unit=Decimal('25.00'),
            advance_payment_percent=20,
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        milestones = booking['payment_schedule']
        
        # Should have 4 milestones: advance, quality, delivery, final
        assert len(milestones) == 4
        
        # Check milestone types
        types = [m['milestone_type'] for m in milestones]
        assert 'advance' in types
        assert 'quality_check' in types
        assert 'delivery' in types
        assert 'final' in types
    
    def test_payment_milestone_amounts(self, booking_service, test_listing, test_buyer):
        """Test payment milestone amounts are calculated correctly"""
        booking = booking_service.create_booking(
            listing_id=test_listing,
            buyer_id=test_buyer,
            quantity_booked=Decimal('100'),
            price_per_unit=Decimal('100.00'),  # Total: 10,000
            advance_payment_percent=30,  # 3,000
            expected_delivery_date=date.today() + timedelta(days=35),
            quality_standards={'grade': 'A'},
            contract_terms={'delivery_terms': 'FOB'}
        )
        
        milestones = booking['payment_schedule']
        
        # Find each milestone
        advance = next(m for m in milestones if m['milestone_type'] == 'advance')
        quality = next(m for m in milestones if m['milestone_type'] == 'quality_check')
        delivery = next(m for m in milestones if m['milestone_type'] == 'delivery')
        final = next(m for m in milestones if m['milestone_type'] == 'final')
        
        # Check amounts
        assert advance['amount'] == 3000.0  # 30% of 10,000
        assert quality['amount'] == 2000.0  # 20% of 10,000
        assert delivery['amount'] == 2000.0  # 20% of 10,000
        assert final['amount'] == 3000.0  # Remaining 30%
        
        # Total should equal booking total
        total_milestones = sum(m['amount'] for m in milestones)
        assert total_milestones == booking['total_amount']
