"""
Unit tests for transport coordination service.
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.model import Base
from app.orm.livestock_transaction import LivestockTransaction
from app.orm.transport_booking import TransportBooking
from app.orm.transport_provider import TransportProvider
from app.orm.user import User
from app.services.transport_service import TransportService

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    """Create a test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def sample_provider(db_session: AsyncSession):
    """Create a sample transport provider."""
    service = TransportService(db_session)

    provider = await service.register_provider(
        user_id=1,
        company_name="Test Transport Co.",
        contact_person="John Doe",
        contact_phone="9876543210",
        contact_email="john@test.com",
        service_areas=["Maharashtra", "Gujarat"],
        vehicle_types=["truck", "specialized_livestock"],
        livestock_specialization=["cattle", "buffalo"],
        base_rate_per_km=15.0,
        minimum_charge=500.0,
        max_capacity_animals=10,
        insurance_available=True,
        insurance_rate_percentage=2.5,
        license_number="MH01AB1234",
    )

    return provider


@pytest.mark.asyncio
async def test_register_provider(db_session: AsyncSession):
    """Test transport provider registration."""
    service = TransportService(db_session)

    provider = await service.register_provider(
        user_id=1,
        company_name="Test Transport",
        contact_person="Jane Smith",
        contact_phone="9876543210",
        service_areas=["Maharashtra"],
        vehicle_types=["truck"],
        base_rate_per_km=12.0,
        minimum_charge=400.0,
        max_capacity_animals=8,
    )

    assert provider.id is not None
    assert provider.company_name == "Test Transport"
    assert provider.contact_person == "Jane Smith"
    assert provider.base_rate_per_km == 12.0
    assert provider.status == "active"
    assert provider.rating == 0.0
    assert provider.completed_transports == 0


@pytest.mark.asyncio
async def test_get_provider(db_session: AsyncSession, sample_provider: TransportProvider):
    """Test getting provider by ID."""
    service = TransportService(db_session)

    provider = await service.get_provider(sample_provider.id)

    assert provider is not None
    assert provider.id == sample_provider.id
    assert provider.company_name == "Test Transport Co."


@pytest.mark.asyncio
async def test_search_providers(db_session: AsyncSession, sample_provider: TransportProvider):
    """Test searching for providers."""
    service = TransportService(db_session)

    # Search by livestock type
    providers = await service.search_providers(livestock_type="cattle")
    assert len(providers) == 1
    assert providers[0].id == sample_provider.id

    # Search by capacity
    providers = await service.search_providers(min_capacity=5)
    assert len(providers) == 1

    # Search with insurance requirement
    providers = await service.search_providers(insurance_required=True)
    assert len(providers) == 1

    # Search for non-matching criteria
    providers = await service.search_providers(livestock_type="poultry")
    assert len(providers) == 0


@pytest.mark.asyncio
async def test_calculate_distance():
    """Test distance calculation using Haversine formula."""
    service = TransportService(None)

    # Mumbai to Pune (approximate)
    mumbai_lat, mumbai_lon = 19.0760, 72.8777
    pune_lat, pune_lon = 18.5204, 73.8567

    distance = service.calculate_distance(mumbai_lat, mumbai_lon, pune_lat, pune_lon)

    # Distance should be approximately 150 km
    assert 140 <= distance <= 160

    # Test with missing coordinates
    distance = service.calculate_distance(None, None, None, None)
    assert distance == 100.0  # Default value


@pytest.mark.asyncio
async def test_calculate_transport_cost(sample_provider: TransportProvider):
    """Test transport cost calculation."""
    service = TransportService(None)

    # Test basic cost calculation
    costs = service.calculate_transport_cost(
        provider=sample_provider,
        distance_km=100.0,
        livestock_type="cattle",
        livestock_count=2,
        animal_value=50000.0,
        insurance_opted=False,
    )

    # Base cost: 100 km * 15 INR/km = 1500 INR
    # Cattle multiplier: 1.0
    # No quantity discount (< 5 animals)
    assert costs["transport_cost"] == 1500.0
    assert costs["insurance_cost"] == 0.0
    assert costs["total_cost"] == 1500.0

    # Test with insurance
    costs = service.calculate_transport_cost(
        provider=sample_provider,
        distance_km=100.0,
        livestock_type="cattle",
        livestock_count=2,
        animal_value=50000.0,
        insurance_opted=True,
    )

    # Insurance: 50000 * 2.5% = 1250 INR
    assert costs["insurance_cost"] == 1250.0
    assert costs["total_cost"] == 2750.0

    # Test with minimum charge
    costs = service.calculate_transport_cost(
        provider=sample_provider,
        distance_km=10.0,  # Only 10 km
        livestock_type="cattle",
        livestock_count=1,
        animal_value=20000.0,
        insurance_opted=False,
    )

    # Should apply minimum charge of 500 INR
    assert costs["transport_cost"] == 500.0

    # Test livestock type multiplier (goat = 0.8)
    costs = service.calculate_transport_cost(
        provider=sample_provider,
        distance_km=100.0,
        livestock_type="goat",
        livestock_count=3,
        animal_value=30000.0,
        insurance_opted=False,
    )

    # Base: 100 * 15 = 1500, Goat multiplier: 0.8 = 1200
    assert costs["transport_cost"] == 1200.0

    # Test quantity discount (> 5 animals = 5% discount)
    costs = service.calculate_transport_cost(
        provider=sample_provider,
        distance_km=100.0,
        livestock_type="cattle",
        livestock_count=6,
        animal_value=100000.0,
        insurance_opted=False,
    )

    # Base: 1500, with 5% discount = 1425
    assert costs["transport_cost"] == 1425.0


@pytest.mark.asyncio
async def test_create_booking(db_session: AsyncSession, sample_provider: TransportProvider):
    """Test creating a transport booking."""
    service = TransportService(db_session)

    scheduled_pickup = datetime.utcnow() + timedelta(days=2)

    booking = await service.create_booking(
        transaction_id=1,
        provider_id=sample_provider.id,
        requester_id=1,
        pickup_address="Farm A, Village X, Maharashtra",
        pickup_latitude=19.0760,
        pickup_longitude=72.8777,
        delivery_address="Market B, City Y, Gujarat",
        delivery_latitude=23.0225,
        delivery_longitude=72.5714,
        livestock_type="cattle",
        livestock_count=3,
        animal_value=75000.0,
        scheduled_pickup_date=scheduled_pickup,
        insurance_opted=True,
        special_instructions="Handle with care",
    )

    assert booking.id is not None
    assert booking.transaction_id == 1
    assert booking.provider_id == sample_provider.id
    assert booking.livestock_type == "cattle"
    assert booking.livestock_count == 3
    assert booking.status == "pending"
    assert booking.insurance_opted is True
    assert booking.distance_km > 0
    assert booking.transport_cost > 0
    assert booking.insurance_cost > 0
    assert booking.total_cost > 0
    assert booking.special_instructions == "Handle with care"

    # Check tracking updates
    import json

    updates = json.loads(booking.tracking_updates)
    assert len(updates) == 1
    assert updates[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_update_booking_status(db_session: AsyncSession, sample_provider: TransportProvider):
    """Test updating booking status."""
    service = TransportService(db_session)

    # Create booking
    booking = await service.create_booking(
        transaction_id=1,
        provider_id=sample_provider.id,
        requester_id=1,
        pickup_address="Farm A",
        delivery_address="Market B",
        livestock_type="cattle",
        livestock_count=2,
        animal_value=50000.0,
        scheduled_pickup_date=datetime.utcnow() + timedelta(days=1),
        insurance_opted=False,
    )

    # Update to confirmed
    updated = await service.update_booking_status(
        booking.id, "confirmed", "Provider confirmed the booking"
    )

    assert updated.status == "confirmed"

    import json

    updates = json.loads(updated.tracking_updates)
    assert len(updates) == 2
    assert updates[-1]["status"] == "confirmed"

    # Update to in_transit with actual pickup date
    pickup_date = datetime.utcnow()
    updated = await service.update_booking_status(
        booking.id, "in_transit", "Animals picked up and in transit", actual_pickup_date=pickup_date
    )

    assert updated.status == "in_transit"
    assert updated.actual_pickup_date is not None


@pytest.mark.asyncio
async def test_add_rating_and_review(db_session: AsyncSession, sample_provider: TransportProvider):
    """Test adding rating and review."""
    service = TransportService(db_session)

    # Create and complete booking
    booking = await service.create_booking(
        transaction_id=1,
        provider_id=sample_provider.id,
        requester_id=1,
        pickup_address="Farm A",
        delivery_address="Market B",
        livestock_type="cattle",
        livestock_count=2,
        animal_value=50000.0,
        scheduled_pickup_date=datetime.utcnow() + timedelta(days=1),
        insurance_opted=False,
    )

    # Update to delivered
    await service.update_booking_status(
        booking.id,
        "delivered",
        "Animals delivered successfully",
        actual_delivery_date=datetime.utcnow(),
    )

    # Add rating
    rated_booking = await service.add_rating_and_review(
        booking.id, rating=5, review="Excellent service, very professional"
    )

    assert rated_booking.rating == 5
    assert rated_booking.review == "Excellent service, very professional"
    assert rated_booking.reviewed_at is not None

    # Check provider rating updated
    provider = await service.get_provider(sample_provider.id)
    assert provider.rating == 5.0
    assert provider.total_ratings == 1
    assert provider.completed_transports == 1


@pytest.mark.asyncio
async def test_cancel_booking(db_session: AsyncSession, sample_provider: TransportProvider):
    """Test cancelling a booking."""
    service = TransportService(db_session)

    booking = await service.create_booking(
        transaction_id=1,
        provider_id=sample_provider.id,
        requester_id=1,
        pickup_address="Farm A",
        delivery_address="Market B",
        livestock_type="cattle",
        livestock_count=2,
        animal_value=50000.0,
        scheduled_pickup_date=datetime.utcnow() + timedelta(days=1),
        insurance_opted=False,
    )

    cancelled = await service.cancel_booking(booking.id, "Change of plans")

    assert cancelled.status == "cancelled"
    assert cancelled.cancelled_at is not None
    assert cancelled.cancellation_reason == "Change of plans"

    import json

    updates = json.loads(cancelled.tracking_updates)
    assert updates[-1]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_get_bookings_for_transaction(
    db_session: AsyncSession, sample_provider: TransportProvider
):
    """Test getting all bookings for a transaction."""
    service = TransportService(db_session)

    # Create multiple bookings for same transaction
    for i in range(3):
        await service.create_booking(
            transaction_id=1,
            provider_id=sample_provider.id,
            requester_id=1,
            pickup_address=f"Farm {i}",
            delivery_address=f"Market {i}",
            livestock_type="cattle",
            livestock_count=2,
            animal_value=50000.0,
            scheduled_pickup_date=datetime.utcnow() + timedelta(days=i + 1),
            insurance_opted=False,
        )

    bookings = await service.get_bookings_for_transaction(1)
    assert len(bookings) == 3


@pytest.mark.asyncio
async def test_get_provider_bookings(db_session: AsyncSession, sample_provider: TransportProvider):
    """Test getting all bookings for a provider."""
    service = TransportService(db_session)

    # Create bookings with different statuses
    booking1 = await service.create_booking(
        transaction_id=1,
        provider_id=sample_provider.id,
        requester_id=1,
        pickup_address="Farm A",
        delivery_address="Market A",
        livestock_type="cattle",
        livestock_count=2,
        animal_value=50000.0,
        scheduled_pickup_date=datetime.utcnow() + timedelta(days=1),
        insurance_opted=False,
    )

    booking2 = await service.create_booking(
        transaction_id=2,
        provider_id=sample_provider.id,
        requester_id=1,
        pickup_address="Farm B",
        delivery_address="Market B",
        livestock_type="goat",
        livestock_count=5,
        animal_value=30000.0,
        scheduled_pickup_date=datetime.utcnow() + timedelta(days=2),
        insurance_opted=False,
    )

    # Update one to confirmed
    await service.update_booking_status(booking1.id, "confirmed")

    # Get all bookings
    all_bookings = await service.get_provider_bookings(sample_provider.id)
    assert len(all_bookings) == 2

    # Get only confirmed bookings
    confirmed_bookings = await service.get_provider_bookings(sample_provider.id, status="confirmed")
    assert len(confirmed_bookings) == 1
    assert confirmed_bookings[0].id == booking1.id
