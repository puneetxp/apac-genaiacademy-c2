"""
Livestock ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class Livestock(Model):
    """Livestock model for livestock table"""
    
    table = 'livestock'
    
    fillable = [
        'enable',
        'farm_id',
        'farmer_id',
        'species',
        'breed',
        'quantity',
        'purchase_price',
        'purchase_date',
        'purpose',
        'expected_roi',
        'break_even_date',
        'status',
        'latitude',
        'longitude',
        'pincode',
        'state',
        'district',
        'village',
        'address_line',
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
