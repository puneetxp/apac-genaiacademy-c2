"""
ActiveRole ORM Model
Auto-generated from JSON schema
"""

from app.core.model import Model


class ActiveRole(Model):
    """ActiveRole model for active_roles table"""
    
    table = 'active_roles'
    
    fillable = [
        'enable',
        'user_id',
        'role_id',
        'active_role_id',
        'active_role_id',
    ]
    
    relations = {
            'active_role': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.active_roles', fromlist=['ActiveRoles']).ActiveRoles
            },
            'advance_booking': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.advance_bookings', fromlist=['AdvanceBookings']).AdvanceBookings
            },
            'ai_usage_quota': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.ai_usage_quota', fromlist=['AiUsageQuota']).AiUsageQuota
            },
            'annual_strategy': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.annual_strategies', fromlist=['AnnualStrategies']).AnnualStrategies
            },
            'buyer_interest': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.buyer_interests', fromlist=['BuyerInterests']).BuyerInterests
            },
            'crop': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.crops', fromlist=['Crops']).Crops
            },
            'crop_expense': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.crop_expenses', fromlist=['CropExpenses']).CropExpenses
            },
            'crop_milestone': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.crop_milestones', fromlist=['CropMilestones']).CropMilestones
            },
            'farm_plot': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.farm_plots', fromlist=['FarmPlots']).FarmPlots
            },
            'fertilizer_application': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.fertilizer_applications', fromlist=['FertilizerApplications']).FertilizerApplications
            },
            'livestock': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.livestock', fromlist=['Livestock']).Livestock
            },
            'livestock_health_record': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.livestock_health_records', fromlist=['LivestockHealthRecords']).LivestockHealthRecords
            },
            'livestock_listing': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.livestock_listings', fromlist=['LivestockListings']).LivestockListings
            },
            'livestock_marketplace_listing': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.livestock_marketplace_listings', fromlist=['LivestockMarketplaceListings']).LivestockMarketplaceListings
            },
            'livestock_transaction': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.livestock_transactions', fromlist=['LivestockTransactions']).LivestockTransactions
            },
            'market_price': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.market_prices', fromlist=['MarketPrices']).MarketPrices
            },
            'marketplace_listing': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.marketplace_listings', fromlist=['MarketplaceListings']).MarketplaceListings
            },
            'payment_milestone': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.payment_milestones', fromlist=['PaymentMilestones']).PaymentMilestones
            },
            'pest_disease_alert': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.pest_disease_alerts', fromlist=['PestDiseaseAlerts']).PestDiseaseAlerts
            },
            'quality_verification': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.quality_verifications', fromlist=['QualityVerifications']).QualityVerifications
            },
            'soil_test_result': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.soil_test_results', fromlist=['SoilTestResults']).SoilTestResults
            },
            'supply_match': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.supply_matches', fromlist=['SupplyMatches']).SupplyMatches
            },
            'supply_request': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.supply_requests', fromlist=['SupplyRequests']).SupplyRequests
            },
            'transport_booking': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.transport_bookings', fromlist=['TransportBookings']).TransportBookings
            },
            'transport_provider': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.transport_providers', fromlist=['TransportProviders']).TransportProviders
            },
            'weather_alert': {
                'name': 'id',
                'key': 'active_role_id',
                'callback': lambda: __import__('app.orm.weather_alerts', fromlist=['WeatherAlerts']).WeatherAlerts
            },
    }
