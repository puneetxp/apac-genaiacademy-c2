"""
PestDiseaseAlert ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class PestDiseaseAlert(Model):
    """PestDiseaseAlert model for pest_disease_alerts table"""
    
    table = 'pest_disease_alerts'
    
    fillable = [
        'enable',
        'crop_id',
        'farm_id',
        'pest_disease_name',
        'alert_type',
        'severity',
        'description',
        'crop_stage',
        'weather_conditions',
        'organic_recommendations',
        'chemical_recommendations',
        'prevention_measures',
        'timing_instructions',
        'notification_sent',
        'notification_sent_at',
        'is_resolved',
        'resolved_at',
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
