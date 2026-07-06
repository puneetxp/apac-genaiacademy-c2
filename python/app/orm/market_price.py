"""
MarketPrice ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class MarketPrice(Model):
    """MarketPrice model for market_prices table"""
    
    table = 'market_prices'
    
    fillable = [
        'enable',
        'listing_id',
        'booking_id',
        'transaction_id',
        'item_type',
        'item_name',
        'variety',
        'price_per_unit',
        'quantity',
        'total_value',
        'quality_grade',
        'quality_premium_percent',
        'state',
        'district',
        'transaction_date',
        'season',
        'source',
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
