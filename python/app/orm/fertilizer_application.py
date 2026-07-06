"""
FertilizerApplication ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class FertilizerApplication(Model):
    """FertilizerApplication model for fertilizer_applications table"""
    
    table = 'fertilizer_applications'
    
    fillable = [
        'enable',
        'farm_id',
        'plot_id',
        'crop_id',
        'application_date',
        'fertilizer_type',
        'category',
        'quantity_kg',
        'quantity_per_hectare',
        'area_applied_hectares',
        'nitrogen_kg',
        'phosphorus_kg',
        'potassium_kg',
        'cost_total',
        'cost_per_kg',
        'cost_per_hectare',
        'application_method',
        'growth_stage',
        'days_after_planting',
        'soil_test_before_id',
        'soil_test_after_id',
        'effectiveness_score',
        'soil_response_notes',
        'weather_conditions',
        'temperature_celsius',
        'rainfall_mm_24h',
        'recommended_by',
        'recommendation_id',
        'notes',
        'active_role_id',
        'active_role_id',
        'active_role_id',
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
