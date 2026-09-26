"""
QualityVerification ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class QualityVerification(Model):
    """QualityVerification model for quality_verifications table"""
    
    table = 'quality_verifications'
    
    fillable = [
        'enable',
        'booking_id',
        'verification_date',
        'verifier_type',
        'quality_grade',
        'quality_metrics',
        'photos',
        'passed',
        'notes',
    ]
    
    relations = {
            'advance_booking': {
                'name': 'booking_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.advance_booking', fromlist=['AdvanceBooking']).AdvanceBooking
            },
    }
