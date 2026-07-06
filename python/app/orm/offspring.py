"""
ORM model for offspring table
"""

from app.core.model import Model


class Offspring(Model):
    """ORM model for offspring table"""
    
    table = "offspring"
    
    fillable = [
        'enable', 'breeding_record_id', 'livestock_id', 'farmer_id', 'birth_date',
        'gender', 'birth_weight', 'health_status', 'current_weight', 'growth_rate',
        'weaning_date', 'sale_date', 'sale_price', 'notes'
    ]
    
    relations = {
        'breeding_record': {
            'table': 'breeding_records',
            'name': 'breeding_record_id',
            'key': 'id',
            'callback': 'BreedingRecord'
        },
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
    }
