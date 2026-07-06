"""
Pytest configuration and fixtures for backend tests
"""

import pytest
import os
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment variables before importing app modules
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('POSTGRES_SERVER', 'localhost')
os.environ.setdefault('POSTGRES_USER', 'test')
os.environ.setdefault('POSTGRES_PASSWORD', 'test')
os.environ.setdefault('POSTGRES_DB', 'test')
os.environ.setdefault('COGNITO_USER_POOL_ID', 'test-pool-id')
os.environ.setdefault('COGNITO_CLIENT_ID', 'test-client-id')
os.environ.setdefault('COGNITO_CLIENT_SECRET', 'test-client-secret')
os.environ.setdefault('S3_BUCKET_NAME', 'test-bucket')
os.environ.setdefault('OPENWEATHER_API_KEY', 'test-api-key')

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Boolean, Text, DECIMAL
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Create test-specific Base for SQLAlchemy models
TestBase = declarative_base()


# Define SQLAlchemy ORM models for testing
class User(TestBase):
    __tablename__ = 'users'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String)
    full_name = Column(String)
    user_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Farm(TestBase):
    __tablename__ = 'farms'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(PG_UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    location_state = Column(String)
    location_district = Column(String)
    location_block = Column(String)
    total_area = Column(DECIMAL)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class FarmPlot(TestBase):
    __tablename__ = 'farm_plots'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(PG_UUID(as_uuid=True), nullable=False)
    plot_number = Column(String)
    area = Column(DECIMAL)
    soil_type = Column(String)
    irrigation_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Crop(TestBase):
    __tablename__ = 'crops'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id = Column(PG_UUID(as_uuid=True), nullable=False)
    crop_variety_id = Column(PG_UUID(as_uuid=True))
    planting_date = Column(Date)
    expected_harvest_date = Column(Date)
    area_planted = Column(DECIMAL)
    growth_stage = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class MarketplaceListing(TestBase):
    __tablename__ = 'marketplace_listings'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(PG_UUID(as_uuid=True), nullable=False)
    farmer_id = Column(PG_UUID(as_uuid=True), nullable=False)
    title = Column(String)
    description = Column(Text)
    crop_type = Column(String)
    crop_variety = Column(String)
    estimated_quantity = Column(DECIMAL)
    quantity_unit = Column(String)
    min_quantity = Column(DECIMAL)
    max_quantity = Column(DECIMAL)
    quality_grade = Column(String)
    quality_confidence = Column(DECIMAL)
    quality_description = Column(Text)
    expected_harvest_date = Column(Date)
    harvest_date_confidence = Column(DECIMAL)
    harvest_window_start = Column(Date)
    harvest_window_end = Column(Date)
    asking_price_per_unit = Column(DECIMAL)
    price_negotiable = Column(Boolean, default=True)
    currency = Column(String, default='INR')
    location_state = Column(String)
    location_district = Column(String)
    location_block = Column(String)
    contact_enabled = Column(Boolean, default=True)
    farmer_phone = Column(String)
    farmer_email = Column(String)
    preferred_contact_method = Column(String)
    market_demand_score = Column(DECIMAL)
    price_trend = Column(String)
    yoy_price_growth = Column(DECIMAL)
    status = Column(String, default='active')
    visibility = Column(String, default='public')
    advance_booking_allowed = Column(Boolean, default=True)
    advance_payment_required = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    interest_count = Column(Integer, default=0)
    contact_request_count = Column(Integer, default=0)
    listed_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    images = Column(Text)
    videos = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class BuyerInterest(TestBase):
    __tablename__ = 'buyer_interests'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(PG_UUID(as_uuid=True), nullable=False)
    buyer_id = Column(PG_UUID(as_uuid=True), nullable=False)
    interest_type = Column(String)
    quantity_interested = Column(DECIMAL)
    preferred_price = Column(DECIMAL)
    buyer_phone = Column(String)
    buyer_email = Column(String)
    buyer_company = Column(String)
    quality_requirements = Column(Text)
    delivery_requirements = Column(Text)
    payment_terms = Column(Text)
    message_to_farmer = Column(Text)
    contact_requested = Column(Boolean, default=False)
    contact_request_date = Column(DateTime)
    contact_approved = Column(Boolean, default=False)
    contact_approved_date = Column(DateTime)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class CropMarketData(TestBase):
    __tablename__ = 'crop_market_data'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_type = Column(String)
    state = Column(String)
    district = Column(String)
    year = Column(Integer)
    month = Column(Integer)
    season = Column(String)
    avg_price_per_quintal = Column(DECIMAL)
    market_demand_score = Column(DECIMAL)
    price_trend = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test
    Uses in-memory SQLite database for fast testing
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    TestBase.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        TestBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_engine():
    """
    Create a database engine for tests that need direct engine access
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    TestBase.metadata.create_all(bind=engine)
    
    try:
        yield engine
    finally:
        TestBase.metadata.drop_all(bind=engine)
        engine.dispose()
