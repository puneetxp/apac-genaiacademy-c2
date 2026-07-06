"""Router registry for the generated FastAPI application."""
from __future__ import annotations

from app.api.isuper.active_role.active_role import router as isuper_active_role_router
from app.api.islogin.active_role.active_role import router as islogin_active_role_router
from app.api.isuper.advance_booking.advance_booking import router as isuper_advance_booking_router
from app.api.islogin.advance_booking.advance_booking import router as islogin_advance_booking_router
from app.api.isuper.ai_usage_quota.ai_usage_quota import router as isuper_ai_usage_quota_router
from app.api.islogin.ai_usage_quota.ai_usage_quota import router as islogin_ai_usage_quota_router
from app.api.isuper.annual_strategy.annual_strategy import router as isuper_annual_strategy_router
from app.api.islogin.annual_strategy.annual_strategy import router as islogin_annual_strategy_router
from app.api.isuper.buyer_interest.buyer_interest import router as isuper_buyer_interest_router
from app.api.islogin.buyer_interest.buyer_interest import router as islogin_buyer_interest_router
from app.api.isuper.crop.crop import router as isuper_crop_router
from app.api.islogin.crop.crop import router as islogin_crop_router
from app.api.isuper.crop_expense.crop_expense import router as isuper_crop_expense_router
from app.api.islogin.crop_expense.crop_expense import router as islogin_crop_expense_router
from app.api.isuper.crop_market_data.crop_market_data import router as isuper_crop_market_data_router
from app.api.ipublic.crop_market_data.crop_market_data import router as ipublic_crop_market_data_router
from app.api.isuper.crop_milestone.crop_milestone import router as isuper_crop_milestone_router
from app.api.islogin.crop_milestone.crop_milestone import router as islogin_crop_milestone_router
from app.api.isuper.farm.farm import router as isuper_farm_router
from app.api.islogin.farm.farm import router as islogin_farm_router
from app.api.isuper.farm_plot.farm_plot import router as isuper_farm_plot_router
from app.api.islogin.farm_plot.farm_plot import router as islogin_farm_plot_router
from app.api.isuper.fertilizer_application.fertilizer_application import router as isuper_fertilizer_application_router
from app.api.islogin.fertilizer_application.fertilizer_application import router as islogin_fertilizer_application_router
from app.api.isuper.livestock.livestock import router as isuper_livestock_router
from app.api.islogin.livestock.livestock import router as islogin_livestock_router
from app.api.isuper.livestock_health_record.livestock_health_record import router as isuper_livestock_health_record_router
from app.api.islogin.livestock_health_record.livestock_health_record import router as islogin_livestock_health_record_router
from app.api.isuper.livestock_listing.livestock_listing import router as isuper_livestock_listing_router
from app.api.islogin.livestock_listing.livestock_listing import router as islogin_livestock_listing_router
from app.api.ipublic.livestock_listing.livestock_listing import router as ipublic_livestock_listing_router
from app.api.isuper.livestock_marketplace_listing.livestock_marketplace_listing import router as isuper_livestock_marketplace_listing_router
from app.api.islogin.livestock_marketplace_listing.livestock_marketplace_listing import router as islogin_livestock_marketplace_listing_router
from app.api.isuper.livestock_transaction.livestock_transaction import router as isuper_livestock_transaction_router
from app.api.islogin.livestock_transaction.livestock_transaction import router as islogin_livestock_transaction_router
from app.api.isuper.market_price.market_price import router as isuper_market_price_router
from app.api.islogin.market_price.market_price import router as islogin_market_price_router
from app.api.ipublic.market_price.market_price import router as ipublic_market_price_router
from app.api.isuper.marketplace_listing.marketplace_listing import router as isuper_marketplace_listing_router
from app.api.islogin.marketplace_listing.marketplace_listing import router as islogin_marketplace_listing_router
from app.api.ipublic.marketplace_listing.marketplace_listing import router as ipublic_marketplace_listing_router
from app.api.isuper.payment_milestone.payment_milestone import router as isuper_payment_milestone_router
from app.api.islogin.payment_milestone.payment_milestone import router as islogin_payment_milestone_router
from app.api.isuper.pest_disease_alert.pest_disease_alert import router as isuper_pest_disease_alert_router
from app.api.islogin.pest_disease_alert.pest_disease_alert import router as islogin_pest_disease_alert_router
from app.api.isuper.pest_disease_data.pest_disease_data import router as isuper_pest_disease_data_router
from app.api.islogin.pest_disease_data.pest_disease_data import router as islogin_pest_disease_data_router
from app.api.isuper.price_prediction.price_prediction import router as isuper_price_prediction_router
from app.api.islogin.price_prediction.price_prediction import router as islogin_price_prediction_router
from app.api.ipublic.price_prediction.price_prediction import router as ipublic_price_prediction_router
from app.api.isuper.quality_verification.quality_verification import router as isuper_quality_verification_router
from app.api.islogin.quality_verification.quality_verification import router as islogin_quality_verification_router
from app.api.isuper.role.role import router as isuper_role_router
from app.api.isuper.shc_state_district_code.shc_state_district_code import router as isuper_shc_state_district_code_router
from app.api.islogin.shc_state_district_code.shc_state_district_code import router as islogin_shc_state_district_code_router
from app.api.isuper.slusi_ingestion_run.slusi_ingestion_run import router as isuper_slusi_ingestion_run_router
from app.api.isuper.slusi_lcc_report.slusi_lcc_report import router as isuper_slusi_lcc_report_router
from app.api.islogin.slusi_lcc_report.slusi_lcc_report import router as islogin_slusi_lcc_report_router
from app.api.isuper.slusi_microwatershed_map.slusi_microwatershed_map import router as isuper_slusi_microwatershed_map_router
from app.api.islogin.slusi_microwatershed_map.slusi_microwatershed_map import router as islogin_slusi_microwatershed_map_router
from app.api.isuper.soil_test_result.soil_test_result import router as isuper_soil_test_result_router
from app.api.islogin.soil_test_result.soil_test_result import router as islogin_soil_test_result_router
from app.api.isuper.supply_match.supply_match import router as isuper_supply_match_router
from app.api.islogin.supply_match.supply_match import router as islogin_supply_match_router
from app.api.isuper.supply_request.supply_request import router as isuper_supply_request_router
from app.api.islogin.supply_request.supply_request import router as islogin_supply_request_router
from app.api.isuper.transport_booking.transport_booking import router as isuper_transport_booking_router
from app.api.islogin.transport_booking.transport_booking import router as islogin_transport_booking_router
from app.api.isuper.transport_provider.transport_provider import router as isuper_transport_provider_router
from app.api.islogin.transport_provider.transport_provider import router as islogin_transport_provider_router
from app.api.ipublic.transport_provider.transport_provider import router as ipublic_transport_provider_router
from app.api.isuper.user.user import router as isuper_user_router
from app.api.islogin.user.user import router as islogin_user_router
from app.api.isuper.weather_alert.weather_alert import router as isuper_weather_alert_router
from app.api.islogin.weather_alert.weather_alert import router as islogin_weather_alert_router

all_routers = [
    isuper_active_role_router,
    islogin_active_role_router,
    isuper_advance_booking_router,
    islogin_advance_booking_router,
    isuper_ai_usage_quota_router,
    islogin_ai_usage_quota_router,
    isuper_annual_strategy_router,
    islogin_annual_strategy_router,
    isuper_buyer_interest_router,
    islogin_buyer_interest_router,
    isuper_crop_router,
    islogin_crop_router,
    isuper_crop_expense_router,
    islogin_crop_expense_router,
    isuper_crop_market_data_router,
    ipublic_crop_market_data_router,
    isuper_crop_milestone_router,
    islogin_crop_milestone_router,
    isuper_farm_router,
    islogin_farm_router,
    isuper_farm_plot_router,
    islogin_farm_plot_router,
    isuper_fertilizer_application_router,
    islogin_fertilizer_application_router,
    isuper_livestock_router,
    islogin_livestock_router,
    isuper_livestock_health_record_router,
    islogin_livestock_health_record_router,
    isuper_livestock_listing_router,
    islogin_livestock_listing_router,
    ipublic_livestock_listing_router,
    isuper_livestock_marketplace_listing_router,
    islogin_livestock_marketplace_listing_router,
    isuper_livestock_transaction_router,
    islogin_livestock_transaction_router,
    isuper_market_price_router,
    islogin_market_price_router,
    ipublic_market_price_router,
    isuper_marketplace_listing_router,
    islogin_marketplace_listing_router,
    ipublic_marketplace_listing_router,
    isuper_payment_milestone_router,
    islogin_payment_milestone_router,
    isuper_pest_disease_alert_router,
    islogin_pest_disease_alert_router,
    isuper_pest_disease_data_router,
    islogin_pest_disease_data_router,
    isuper_price_prediction_router,
    islogin_price_prediction_router,
    ipublic_price_prediction_router,
    isuper_quality_verification_router,
    islogin_quality_verification_router,
    isuper_role_router,
    isuper_shc_state_district_code_router,
    islogin_shc_state_district_code_router,
    isuper_slusi_ingestion_run_router,
    isuper_slusi_lcc_report_router,
    islogin_slusi_lcc_report_router,
    isuper_slusi_microwatershed_map_router,
    islogin_slusi_microwatershed_map_router,
    isuper_soil_test_result_router,
    islogin_soil_test_result_router,
    isuper_supply_match_router,
    islogin_supply_match_router,
    isuper_supply_request_router,
    islogin_supply_request_router,
    isuper_transport_booking_router,
    islogin_transport_booking_router,
    isuper_transport_provider_router,
    islogin_transport_provider_router,
    ipublic_transport_provider_router,
    isuper_user_router,
    islogin_user_router,
    isuper_weather_alert_router,
    islogin_weather_alert_router,
]
