"""
ORM model for breeding_records table
"""

from app.core.model import Model


class BreedingRecord(Model):
    """ORM model for breeding_records table"""
    
    table = "breeding_records"
    
    fillable = [
        'enable', 'livestock_id', 'farmer_id', 'breeding_type', 'breeding_date',
        'mate_id', 'mate_breed', 'expected_delivery_date', 'actual_delivery_date',
        'pregnancy_status', 'number_of_offspring', 'breeding_cost',
        'veterinarian_name', 'notes'
    ]
    
    relations = {
        'livestock': {
            'table': 'livestock',
            'name': 'livestock_id',
            'key': 'id',
            'callback': 'Livestock'
        },
        'farmer': {
            'table': 'users',
            'name': 'farmer_id',
            'key': 'id',
            'callback': 'User'
        },
        'mate': {
            'table': 'livestock',
            'name': 'mate_id',
            'key': 'id',
            'callback': 'Livestock'
        },
    }
