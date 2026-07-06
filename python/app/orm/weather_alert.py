"""
WeatherAlert ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class WeatherAlert(Model):
    """WeatherAlert model for weather_alerts table"""
    
    table = 'weather_alerts'
    
    fillable = [
        'enable',
        'farm_id',
        'state',
        'district',
        'alert_type',
        'severity',
        'message',
        'recommendation',
        'valid_from',
        'valid_until',
        'is_active',
        'active_role_id',
    ]
    
    relations = {
            'active_role': {
                'name': 'active_role_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.active_roles', fromlist=['ActiveRoles']).ActiveRoles
            },
    }
