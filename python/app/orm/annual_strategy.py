"""
AnnualStrategy ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class AnnualStrategy(Model):
    """AnnualStrategy model for annual_strategies table"""
    
    table = 'annual_strategies'
    
    fillable = [
        'enable',
        'farm_id',
        'farmer_id',
        'year',
        'kharif_crop',
        'kharif_profit_estimate',
        'kharif_confidence_score',
        'rabi_crop',
        'rabi_profit_estimate',
        'rabi_confidence_score',
        'zaid_crop',
        'zaid_profit_estimate',
        'zaid_confidence_score',
        'total_annual_profit',
        'implementation_timeline',
        'alternative_options',
        'risk_mitigation',
        'bedrock_response',
        'status',
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
