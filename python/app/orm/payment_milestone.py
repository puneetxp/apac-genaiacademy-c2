"""
PaymentMilestone ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class PaymentMilestone(Model):
    """PaymentMilestone model for payment_milestones table"""
    
    table = 'payment_milestones'
    
    fillable = [
        'enable',
        'booking_id',
        'milestone_type',
        'amount',
        'due_date',
        'paid_date',
        'status',
        'payment_method',
        'transaction_id',
        'active_role_id',
    ]
    
    relations = {
            'active_role': {
                'name': 'active_role_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.active_roles', fromlist=['ActiveRoles']).ActiveRoles
            },
    }
