"""
CropExpense ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class CropExpense(Model):
    """CropExpense model for crop_expenses table"""
    
    table = 'crop_expenses'
    
    fillable = [
        'enable',
        'crop_id',
        'category',
        'amount',
        'description',
        'expense_date',
        'active_role_id',
    ]
    
    relations = {
            'active_role': {
                'name': 'active_role_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.active_roles', fromlist=['ActiveRoles']).ActiveRoles
            },
    }
