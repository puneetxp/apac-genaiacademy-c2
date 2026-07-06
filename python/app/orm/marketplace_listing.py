"""
MarketplaceListing ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class MarketplaceListing(Model):
    """MarketplaceListing model for marketplace_listings table"""
    
    table = 'marketplace_listings'
    
    fillable = [
        'enable',
        'farm_id',
        'farmer_id',
        'crop_type',
        'crop_variety',
        'expected_harvest_date',
        'estimated_quantity',
        'available_quantity',
        'quality_grade',
        'location_state',
        'location_district',
        'farmer_contact_phone',
        'farmer_contact_email',
        'status',
        'delivery_latitude',
        'delivery_longitude',
        'delivery_pincode',
        'delivery_village',
        'delivery_address_line',
        'embedding',
        'embedding_cache_key',
        'price_per_unit',
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
