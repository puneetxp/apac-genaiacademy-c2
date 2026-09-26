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
    ]
    
    relations = {
            'marketplace_listing': {
                'name': 'listing_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.marketplace_listing', fromlist=['MarketplaceListing']).MarketplaceListing
            },
            'buyer': {
                'name': 'buyer_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.user', fromlist=['User']).User
            },
            'farmer': {
                'name': 'farmer_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.user', fromlist=['User']).User
            },
            'market_price': {
                'name': 'id',
                'key': 'booking_id',
                'callback': lambda: __import__('app.orm.market_price', fromlist=['MarketPrice']).MarketPrice
            },
            'payment_milestone': {
                'name': 'id',
                'key': 'booking_id',
                'callback': lambda: __import__('app.orm.payment_milestone', fromlist=['PaymentMilestone']).PaymentMilestone
            },
            'quality_verification': {
                'name': 'id',
                'key': 'booking_id',
                'callback': lambda: __import__('app.orm.quality_verification', fromlist=['QualityVerification']).QualityVerification
            },
    }
