"""
Crop ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class Crop(Model):
    """Crop model for crops table"""
    
    table = 'crops'
    
    fillable = [
        'enable',
        'farm_plot_id',
        'strategy_id',
        'crop_name',
        'crop_variety',
        'season',
        'planting_date',
        'expected_harvest_date',
        'area',
        'expected_yield',
        'expected_profit',
        'actual_yield',
        'actual_profit',
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
