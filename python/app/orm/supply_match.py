"""
SupplyMatch ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class SupplyMatch(Model):
    """SupplyMatch model for supply_matches table"""
    
    table = 'supply_matches'
    
    fillable = [
        'enable',
        'request_id',
        'listing_id',
        'farmer_id',
        'matched_quantity',
        'match_score',
        'price_offered',
        'status',
        'match_explanation',
        'is_aggregated',
        'aggregation_group_id',
        'farmer_confirmation_status',
        'farmer_confirmed_at',
        'buyer_accepted_at',
        'delivery_status',
        'delivery_notes',
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
