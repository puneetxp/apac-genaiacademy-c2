"""
Transport coordination service for livestock marketplace.
Handles transport provider management, booking, cost calculation, and tracking.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
import json
import math

from app.orm.transport_provider import TransportProvider
from app.orm.transport_booking import TransportBooking
from app.orm.livestock_transaction import LivestockTransaction
from app.orm.user import User


class TransportService:
    """Service for managing livestock transport coordination."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Transport Provider Management
    
    async def register_provider(
        self,
        user_id: int,
        company_name: str,
        contact_person: str,
        contact_phone: str,
        service_areas: List[str],
        vehicle_types: List[str],
        base_rate_per_km: float,
        minimum_charge: float,
        max_capacity_animals: int,
        contact_email: Optional[str] = None,
        livestock_specialization: Optional[List[str]] = None,
        insurance_available: bool = False,
        insurance_rate_percentage: Optional[float] = None,
        license_number: Optional[str] = None,
        verification_documents: Optional[List[str]] = None
    ) -> TransportProvider:
        """Register a new transport provider."""
        provider = TransportProvider(
            user_id=user_id,
            company_name=company_name,
            contact_person=contact_person,
            contact_phone=contact_phone,
            contact_email=contact_email,
            service_areas=json.dumps(service_areas),
            vehicle_types=json.dumps(vehicle_types),
            livestock_specialization=json.dumps(livestock_specialization) if livestock_specialization else None,
            base_rate_per_km=base_rate_per_km,
            minimum_charge=minimum_charge,
            insurance_available=insurance_available,
            insurance_rate_percentage=insurance_rate_percentage,
            max_capacity_animals=max_capacity_animals,
            license_number=license_number,
            verification_documents=json.dumps(verification_documents) if verification_documents else None,
            status='active'
        )
        
        self.db.add(provider)
        await self.db.commit()
        await self.db.refresh(provider)
        return provider
    
    async def get_provider(self, provider_id: int) -> Optional[TransportProvider]:
        """Get transport provider by ID."""
        result = await self.db.execute(
            select(TransportProvider).where(TransportProvider.id == provider_id)
        )
        return result.scalar_one_or_none()
    
    async def search_providers(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        livestock_type: Optional[str] = None,
        min_capacity: Optional[int] = None,
        insurance_required: bool = False,
        verified_only: bool = False
    ) -> List[TransportProvider]:
        """Search for transport providers based on criteria."""
        query = select(TransportProvider).where(TransportProvider.status == 'active')
        
        if verified_only:
            query = query.where(TransportProvider.verified == True)
        
        if insurance_required:
            query = query.where(TransportProvider.insurance_available == True)
        
        if min_capacity:
            query = query.where(TransportProvider.max_capacity_animals >= min_capacity)
        
        # Order by rating and completed transports
        query = query.order_by(
            TransportProvider.rating.desc(),
            TransportProvider.completed_transports.desc()
        )
        
        result = await self.db.execute(query)
        providers = result.scalars().all()
        
        # Filter by service area and livestock specialization (JSON fields)
        filtered_providers = []
        for provider in providers:
            service_areas = json.loads(provider.service_areas) if provider.service_areas else []
            
            # Check if provider serves the requested area
            if state and not any(state.lower() in area.lower() for area in service_areas):
                continue
            
            if district and not any(district.lower() in area.lower() for area in service_areas):
                continue
            
            # Check livestock specialization
            if livestock_type and provider.livestock_specialization:
                specializations = json.loads(provider.livestock_specialization)
                if livestock_type not in specializations:
                    continue
            
            filtered_providers.append(provider)
        
        return filtered_providers
    
    async def update_provider(
        self,
        provider_id: int,
        **updates
    ) -> Optional[TransportProvider]:
        """Update transport provider details."""
        provider = await self.get_provider(provider_id)
        if not provider:
            return None
        
        # Handle JSON fields
        if 'service_areas' in updates and isinstance(updates['service_areas'], list):
            updates['service_areas'] = json.dumps(updates['service_areas'])
        
        if 'vehicle_types' in updates and isinstance(updates['vehicle_types'], list):
            updates['vehicle_types'] = json.dumps(updates['vehicle_types'])
        
        if 'livestock_specialization' in updates and isinstance(updates['livestock_specialization'], list):
            updates['livestock_specialization'] = json.dumps(updates['livestock_specialization'])
        
        if 'verification_documents' in updates and isinstance(updates['verification_documents'], list):
            updates['verification_documents'] = json.dumps(updates['verification_documents'])
        
        for key, value in updates.items():
            if hasattr(provider, key):
                setattr(provider, key, value)
        
        await self.db.commit()
        await self.db.refresh(provider)
        return provider
    
    # Transport Booking Management
    
    def calculate_distance(
        self,
        pickup_lat: Optional[float],
        pickup_lon: Optional[float],
        delivery_lat: Optional[float],
        delivery_lon: Optional[float]
    ) -> float:
        """
        Calculate distance between two points using Haversine formula.
        Returns distance in kilometers.
        """
        if not all([pickup_lat, pickup_lon, delivery_lat, delivery_lon]):
            # Default to 100km if GPS coordinates not available
            return 100.0
        
        # Haversine formula
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(pickup_lat)
        lat2_rad = math.radians(delivery_lat)
        delta_lat = math.radians(delivery_lat - pickup_lat)
        delta_lon = math.radians(delivery_lon - pickup_lon)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return round(distance, 2)
    
    def calculate_transport_cost(
        self,
        provider: TransportProvider,
        distance_km: float,
        livestock_type: str,
        livestock_count: int,
        animal_value: float,
        insurance_opted: bool = False
    ) -> Dict[str, float]:
        """
        Calculate transport cost based on distance, livestock type, and provider rates.
        Returns dict with transport_cost, insurance_cost, and total_cost.
        """
        # Base transport cost
        base_cost = distance_km * provider.base_rate_per_km
        
        # Apply minimum charge
        transport_cost = max(base_cost, provider.minimum_charge)
        
        # Livestock type multipliers (more delicate animals cost more)
        type_multipliers = {
            'cattle': 1.0,
            'buffalo': 1.0,
            'goat': 0.8,
            'sheep': 0.8,
            'poultry': 0.6
        }
        
        multiplier = type_multipliers.get(livestock_type.lower(), 1.0)
        transport_cost *= multiplier
        
        # Quantity adjustment (slight discount for bulk)
        if livestock_count > 5:
            transport_cost *= 0.95  # 5% discount
        elif livestock_count > 10:
            transport_cost *= 0.90  # 10% discount
        
        transport_cost = round(transport_cost, 2)
        
        # Calculate insurance cost
        insurance_cost = 0.0
        if insurance_opted and provider.insurance_available:
            insurance_cost = (animal_value * provider.insurance_rate_percentage) / 100
            insurance_cost = round(insurance_cost, 2)
        
        total_cost = transport_cost + insurance_cost
        
        return {
            'transport_cost': transport_cost,
            'insurance_cost': insurance_cost,
            'total_cost': total_cost
        }
    
    async def create_booking(
        self,
        transaction_id: int,
        provider_id: int,
        requester_id: int,
        pickup_address: str,
        delivery_address: str,
        livestock_type: str,
        livestock_count: int,
        animal_value: float,
        scheduled_pickup_date: datetime,
        pickup_latitude: Optional[float] = None,
        pickup_longitude: Optional[float] = None,
        delivery_latitude: Optional[float] = None,
        delivery_longitude: Optional[float] = None,
        insurance_opted: bool = False,
        special_instructions: Optional[str] = None
    ) -> TransportBooking:
        """Create a new transport booking."""
        # Get provider details
        provider = await self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Transport provider {provider_id} not found")
        
        # Calculate distance
        distance_km = self.calculate_distance(
            pickup_latitude, pickup_longitude,
            delivery_latitude, delivery_longitude
        )
        
        # Calculate costs
        costs = self.calculate_transport_cost(
            provider, distance_km, livestock_type,
            livestock_count, animal_value, insurance_opted
        )
        
        # Estimate delivery date (assume 50 km/hour average speed + 1 day buffer)
        travel_hours = distance_km / 50
        estimated_delivery_date = scheduled_pickup_date + timedelta(
            hours=travel_hours + 24  # Add 1 day buffer
        )
        
        # Create booking
        booking = TransportBooking(
            transaction_id=transaction_id,
            provider_id=provider_id,
            requester_id=requester_id,
            pickup_address=pickup_address,
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            delivery_address=delivery_address,
            delivery_latitude=delivery_latitude,
            delivery_longitude=delivery_longitude,
            distance_km=distance_km,
            livestock_type=livestock_type,
            livestock_count=livestock_count,
            animal_value=animal_value,
            transport_cost=costs['transport_cost'],
            insurance_opted=insurance_opted,
            insurance_cost=costs['insurance_cost'] if insurance_opted else None,
            total_cost=costs['total_cost'],
            scheduled_pickup_date=scheduled_pickup_date,
            estimated_delivery_date=estimated_delivery_date,
            special_instructions=special_instructions,
            status='pending',
            tracking_updates=json.dumps([{
                'status': 'pending',
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Booking created, awaiting provider confirmation'
            }])
        )
        
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking
    
    async def get_booking(self, booking_id: int) -> Optional[TransportBooking]:
        """Get transport booking by ID with related data."""
        result = await self.db.execute(
            select(TransportBooking)
            .options(
                selectinload(TransportBooking.provider),
                selectinload(TransportBooking.transaction)
            )
            .where(TransportBooking.id == booking_id)
        )
        return result.scalar_one_or_none()
    
    async def update_booking_status(
        self,
        booking_id: int,
        status: str,
        message: Optional[str] = None,
        actual_pickup_date: Optional[datetime] = None,
        actual_delivery_date: Optional[datetime] = None
    ) -> Optional[TransportBooking]:
        """Update transport booking status with tracking update."""
        booking = await self.get_booking(booking_id)
        if not booking:
            return None
        
        # Update status
        booking.status = status
        
        # Update actual dates
        if actual_pickup_date:
            booking.actual_pickup_date = actual_pickup_date
        
        if actual_delivery_date:
            booking.actual_delivery_date = actual_delivery_date
        
        # Add tracking update
        tracking_updates = json.loads(booking.tracking_updates) if booking.tracking_updates else []
        tracking_updates.append({
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'message': message or f'Status updated to {status}'
        })
        booking.tracking_updates = json.dumps(tracking_updates)
        
        await self.db.commit()
        await self.db.refresh(booking)
        return booking
    
    async def add_rating_and_review(
        self,
        booking_id: int,
        rating: int,
        review: Optional[str] = None
    ) -> Optional[TransportBooking]:
        """Add rating and review for completed transport."""
        booking = await self.get_booking(booking_id)
        if not booking or booking.status != 'delivered':
            return None
        
        # Update booking
        booking.rating = rating
        booking.review = review
        booking.reviewed_at = datetime.utcnow()
        
        # Update provider rating
        provider = booking.provider
        if provider:
            total_rating = (provider.rating * provider.total_ratings) + rating
            provider.total_ratings += 1
            provider.rating = round(total_rating / provider.total_ratings, 2)
            provider.completed_transports += 1
        
        await self.db.commit()
        await self.db.refresh(booking)
        return booking
    
    async def get_bookings_for_transaction(
        self,
        transaction_id: int
    ) -> List[TransportBooking]:
        """Get all transport bookings for a transaction."""
        result = await self.db.execute(
            select(TransportBooking)
            .options(selectinload(TransportBooking.provider))
            .where(TransportBooking.transaction_id == transaction_id)
            .order_by(TransportBooking.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_provider_bookings(
        self,
        provider_id: int,
        status: Optional[str] = None
    ) -> List[TransportBooking]:
        """Get all bookings for a provider."""
        query = select(TransportBooking).where(
            TransportBooking.provider_id == provider_id
        )
        
        if status:
            query = query.where(TransportBooking.status == status)
        
        query = query.order_by(TransportBooking.scheduled_pickup_date.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def cancel_booking(
        self,
        booking_id: int,
        cancellation_reason: str
    ) -> Optional[TransportBooking]:
        """Cancel a transport booking."""
        booking = await self.get_booking(booking_id)
        if not booking or booking.status in ['delivered', 'cancelled']:
            return None
        
        booking.status = 'cancelled'
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = cancellation_reason
        
        # Add tracking update
        tracking_updates = json.loads(booking.tracking_updates) if booking.tracking_updates else []
        tracking_updates.append({
            'status': 'cancelled',
            'timestamp': datetime.utcnow().isoformat(),
            'message': f'Booking cancelled: {cancellation_reason}'
        })
        booking.tracking_updates = json.dumps(tracking_updates)
        
        await self.db.commit()
        await self.db.refresh(booking)
        return booking
