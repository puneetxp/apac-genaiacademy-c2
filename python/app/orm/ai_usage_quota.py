"""
AiUsageQuota ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class AiUsageQuota(Model):
    """AiUsageQuota model for ai_usage_quota table"""
    
    table = 'ai_usage_quota'
    
    fillable = [
        'enable',
        'user_id',
        'date',
        'gps_enhanced_requests',
        'pincode_requests',
        'last_reset',
        'quota_limit',
        'active_role_id',
    ]
    
    relations = {
            'active_role': {
                'name': 'active_role_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.active_roles', fromlist=['ActiveRoles']).ActiveRoles
            },
    }
