"""
Farm ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class Farm(Model):
    """Farm model for farms table"""
    
    table = 'farms'
    
    fillable = [
        'enable',
        'name',
        'description',
        'location_state',
        'location_district',
        'location_block',
        'location_village',
        'latitude',
        'longitude',
        'total_area',
        'cultivable_area',
        'area_unit',
        'primary_soil_type',
        'soil_ph',
        'soil_characteristics',
        'irrigation_type',
        'water_availability',
        'previous_crops',
        'farming_experience_years',
        'investment_capacity_per_acre',
        'farm_profile_embedding',
        'is_active',
        'is_verified',
        'nitrogen',
        'phosphorus',
        'potassium',
        'ph_level',
        'organic_carbon',
        'electrical_conductivity',
        'sulfur',
        'zinc',
        'iron',
        'boron',
        'copper',
        'manganese',
        'soil_depth_class',
        'slope_class',
        'erosion_class',
        'soil_texture_class',
        'land_capability_class',
        'land_irrigability_class',
        'hydrological_soil_group',
        'shc_data_source',
        'shc_fetched_at',
        'shc_partial_data',
        'shc_unavailable_styles',
        'user_id',
        'owner_id',
    ]
    
    relations = {
            'user': {
                'name': 'user_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.users', fromlist=['Users']).Users
            },
            'owner': {
                'name': 'owner_id',
                'key': 'id',
                'callback': lambda: __import__('app.orm.users', fromlist=['Users']).Users
            },
    }
