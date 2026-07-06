"""
LivestockHealthRecord ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class LivestockHealthRecord(Model):
    """LivestockHealthRecord model for livestock_health_records table"""
    
    table = 'livestock_health_records'
    
    fillable = [
        'enable',
        'livestock_id',
        'record_type',
        'record_date',
        'description',
        'veterinarian_name',
        'cost',
        'next_due_date',
        'notes',
        'active_role_id',
    ]
    
    relations = {
            'active_role': {
                'name': 'active_role_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.active_roles', fromlist=['ActiveRoles']).ActiveRoles
            },
    }
