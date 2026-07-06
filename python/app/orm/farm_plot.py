"""
FarmPlot ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class FarmPlot(Model):
    """FarmPlot model for farm_plots table"""
    
    table = 'farm_plots'
    
    fillable = [
        'enable',
        'farm_id',
        'plot_name',
        'area',
        'soil_type',
        'irrigation_type',
        'state',
        'district',
        'previous_crops',
        'investment_capacity',
        'nitrogen',
        'phosphorus',
        'potassium',
        'ph_level',
        'organic_carbon',
        'electrical_conductivity',
        'sulfur',
        'zinc',
        'iron',
        'boron',
        'active_role_id',
    ]
    
    relations = {
            'active_role': {
                'name': 'active_role_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.active_roles', fromlist=['ActiveRoles']).ActiveRoles
            },
    }
