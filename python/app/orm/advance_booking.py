"""
AdvanceBooking ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class AdvanceBooking(Model):
    """AdvanceBooking model for advance_bookings table"""
    
    table = 'advance_bookings'
    
    fillable = [
        'enable',
        'listing_id',
        'buyer_id',
        'farmer_id',
        'quantity_booked',
        'price_per_unit',
        'total_amount',
        'advance_payment_percent',
        'advance_payment_amount',
        'booking_date',
        'expected_delivery_date',
        'status',
        'quality_standards',
        'contract_terms',
        'active_role_id',
        'active_role_id',
        'active_role_id',
    ]
    
    relations = {
            'active_role': {
                'name': 'active_role_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.active_roles', fromlist=['ActiveRoles']).ActiveRoles
            },
    }
