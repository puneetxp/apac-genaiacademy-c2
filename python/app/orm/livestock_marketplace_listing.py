"""
LivestockMarketplaceListing ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class LivestockMarketplaceListing(Model):
    """LivestockMarketplaceListing model for livestock_marketplace_listings table"""
    
    table = 'livestock_marketplace_listings'
    
    fillable = [
        'enable',
        'livestock_id',
        'farmer_id',
        'listing_type',
        'asking_price',
        'current_age_months',
        'current_weight_kg',
        'milk_production_liters_per_day',
        'breeding_history',
        'health_status',
        'vaccination_status',
        'total_investment',
        'total_revenue',
        'current_roi_percentage',
        'break_even_achieved',
        'break_even_date',
        'projected_annual_profit',
        'location_state',
        'location_district',
        'farmer_contact_phone',
        'farmer_contact_email',
        'listing_status',
        'views_count',
        'bedrock_analysis',
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
