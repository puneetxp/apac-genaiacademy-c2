"""
Role ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class Role(Model):
    """Role model for roles table"""
    
    table = 'roles'
    
    fillable = [
        'enable',
        'name',
    ]
