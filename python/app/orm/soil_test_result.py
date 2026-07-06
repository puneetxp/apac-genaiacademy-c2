"""
SoilTestResult ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class SoilTestResult(Model):
    """SoilTestResult model for soil_test_results table"""
    
    table = 'soil_test_results'
    
    fillable = [
        'enable',
        'farm_id',
        'plot_id',
        'test_date',
        'lab_name',
        'lab_reference_number',
        'nitrogen_kg_per_ha',
        'phosphorus_kg_per_ha',
        'potassium_kg_per_ha',
        'ph_level',
        'organic_carbon_percent',
        'organic_matter_percent',
        'electrical_conductivity',
        'sulfur_ppm',
        'zinc_ppm',
        'iron_ppm',
        'manganese_ppm',
        'copper_ppm',
        'boron_ppm',
        'soil_health_score',
        'test_method',
        'raw_data_json',
        'recommendations',
        'notes',
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
