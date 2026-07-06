"""
User ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class User(Model):
    """User model for users table"""
    
    table = 'users'
    
    fillable = [
        'id',
        'created_at',
        'updated_at',
        'enable',
        'cognito_user_id',
        'firebase_id',
        'username',
        'name',
        'email',
        'phone',
        'google_id',
        'facebook_id',
        'password',
        'user_type',
        'preferred_language',
        'mfa_enabled',
        'latitude',
        'longitude',
        'pincode',
        'state',
        'district',
        'village',
        'address_line',
        'is_active',
        'is_verified',
    ]
    
    relations = {
            'farm': {
                'name': 'id',
                'key': 'user_id',
                'callback': lambda: __import__('app.orm.farms', fromlist=['Farms']).Farms
            },
    }
