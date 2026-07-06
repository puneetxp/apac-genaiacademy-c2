"""
CropMilestone ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class CropMilestone(Model):
    """CropMilestone model for crop_milestones table"""
    
    table = 'crop_milestones'
    
    fillable = [
        'enable',
        'crop_id',
        'stage',
        'expected_start_date',
        'expected_end_date',
        'actual_start_date',
        'actual_end_date',
        'status',
        'progress_percentage',
        'recommendations',
        'notes',
        'alert_sent',
        'active_role_id',
    ]
    
    relations = {
            'active_role': {
                'name': 'active_role_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.active_roles', fromlist=['ActiveRoles']).ActiveRoles
            },
    }
