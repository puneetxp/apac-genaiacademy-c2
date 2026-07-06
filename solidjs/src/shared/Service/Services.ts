import { ModelService } from "./ModelService";import { Active_role } from "../Interface/Model/Active_role";
import { Advance_booking } from "../Interface/Model/Advance_booking";
import { Ai_usage_quota } from "../Interface/Model/Ai_usage_quota";
import { Annual_strategy } from "../Interface/Model/Annual_strategy";
import { Buyer_interest } from "../Interface/Model/Buyer_interest";
import { Crop } from "../Interface/Model/Crop";
import { Crop_expense } from "../Interface/Model/Crop_expense";
import { Crop_market_data } from "../Interface/Model/Crop_market_data";
import { Crop_milestone } from "../Interface/Model/Crop_milestone";
import { Farm } from "../Interface/Model/Farm";
import { Farm_plot } from "../Interface/Model/Farm_plot";
import { Fertilizer_application } from "../Interface/Model/Fertilizer_application";
import { Livestock } from "../Interface/Model/Livestock";
import { Livestock_health_record } from "../Interface/Model/Livestock_health_record";
import { Livestock_listing } from "../Interface/Model/Livestock_listing";
import { Livestock_marketplace_listing } from "../Interface/Model/Livestock_marketplace_listing";
import { Livestock_transaction } from "../Interface/Model/Livestock_transaction";
import { Market_price } from "../Interface/Model/Market_price";
import { Marketplace_listing } from "../Interface/Model/Marketplace_listing";
import { Payment_milestone } from "../Interface/Model/Payment_milestone";
import { Pest_disease_alert } from "../Interface/Model/Pest_disease_alert";
import { Pest_disease_data } from "../Interface/Model/Pest_disease_data";
import { Price_prediction } from "../Interface/Model/Price_prediction";
import { Quality_verification } from "../Interface/Model/Quality_verification";
import { Role } from "../Interface/Model/Role";
import { Shc_state_district_code } from "../Interface/Model/Shc_state_district_code";
import { Slusi_ingestion_run } from "../Interface/Model/Slusi_ingestion_run";
import { Slusi_lcc_report } from "../Interface/Model/Slusi_lcc_report";
import { Slusi_microwatershed_map } from "../Interface/Model/Slusi_microwatershed_map";
import { Soil_test_result } from "../Interface/Model/Soil_test_result";
import { Supply_match } from "../Interface/Model/Supply_match";
import { Supply_request } from "../Interface/Model/Supply_request";
import { Transport_booking } from "../Interface/Model/Transport_booking";
import { Transport_provider } from "../Interface/Model/Transport_provider";
import { User } from "../Interface/Model/User";
import { Weather_alert } from "../Interface/Model/Weather_alert";export const Active_roleService = (new ModelService<Active_role>())
    .seTable("active_role")
    .seturl("api/active_role");
export const Advance_bookingService = (new ModelService<Advance_booking>())
    .seTable("advance_booking")
    .seturl("api/advance_booking");
export const Ai_usage_quotaService = (new ModelService<Ai_usage_quota>())
    .seTable("ai_usage_quota")
    .seturl("api/ai_usage_quota");
export const Annual_strategyService = (new ModelService<Annual_strategy>())
    .seTable("annual_strategy")
    .seturl("api/annual_strategy");
export const Buyer_interestService = (new ModelService<Buyer_interest>())
    .seTable("buyer_interest")
    .seturl("api/buyer_interest");
export const CropService = (new ModelService<Crop>())
    .seTable("crop")
    .seturl("api/crop");
export const Crop_expenseService = (new ModelService<Crop_expense>())
    .seTable("crop_expense")
    .seturl("api/crop_expense");
export const Crop_market_dataService = (new ModelService<Crop_market_data>())
    .seTable("crop_market_data")
    .seturl("api/crop_market_data");
export const Crop_milestoneService = (new ModelService<Crop_milestone>())
    .seTable("crop_milestone")
    .seturl("api/crop_milestone");
export const FarmService = (new ModelService<Farm>())
    .seTable("farm")
    .seturl("api/farm");
export const Farm_plotService = (new ModelService<Farm_plot>())
    .seTable("farm_plot")
    .seturl("api/farm_plot");
export const Fertilizer_applicationService = (new ModelService<Fertilizer_application>())
    .seTable("fertilizer_application")
    .seturl("api/fertilizer_application");
export const LivestockService = (new ModelService<Livestock>())
    .seTable("livestock")
    .seturl("api/livestock");
export const Livestock_health_recordService = (new ModelService<Livestock_health_record>())
    .seTable("livestock_health_record")
    .seturl("api/livestock_health_record");
export const Livestock_listingService = (new ModelService<Livestock_listing>())
    .seTable("livestock_listing")
    .seturl("api/livestock_listing");
export const Livestock_marketplace_listingService = (new ModelService<Livestock_marketplace_listing>())
    .seTable("livestock_marketplace_listing")
    .seturl("api/livestock_marketplace_listing");
export const Livestock_transactionService = (new ModelService<Livestock_transaction>())
    .seTable("livestock_transaction")
    .seturl("api/livestock_transaction");
export const Market_priceService = (new ModelService<Market_price>())
    .seTable("market_price")
    .seturl("api/market_price");
export const Marketplace_listingService = (new ModelService<Marketplace_listing>())
    .seTable("marketplace_listing")
    .seturl("api/marketplace_listing");
export const Payment_milestoneService = (new ModelService<Payment_milestone>())
    .seTable("payment_milestone")
    .seturl("api/payment_milestone");
export const Pest_disease_alertService = (new ModelService<Pest_disease_alert>())
    .seTable("pest_disease_alert")
    .seturl("api/pest_disease_alert");
export const Pest_disease_dataService = (new ModelService<Pest_disease_data>())
    .seTable("pest_disease_data")
    .seturl("api/pest_disease_data");
export const Price_predictionService = (new ModelService<Price_prediction>())
    .seTable("price_prediction")
    .seturl("api/price_prediction");
export const Quality_verificationService = (new ModelService<Quality_verification>())
    .seTable("quality_verification")
    .seturl("api/quality_verification");
export const RoleService = (new ModelService<Role>())
    .seTable("role")
    .seturl("api/role");
export const Shc_state_district_codeService = (new ModelService<Shc_state_district_code>())
    .seTable("shc_state_district_code")
    .seturl("api/shc_state_district_code");
export const Slusi_ingestion_runService = (new ModelService<Slusi_ingestion_run>())
    .seTable("slusi_ingestion_run")
    .seturl("api/slusi_ingestion_run");
export const Slusi_lcc_reportService = (new ModelService<Slusi_lcc_report>())
    .seTable("slusi_lcc_report")
    .seturl("api/slusi_lcc_report");
export const Slusi_microwatershed_mapService = (new ModelService<Slusi_microwatershed_map>())
    .seTable("slusi_microwatershed_map")
    .seturl("api/slusi_microwatershed_map");
export const Soil_test_resultService = (new ModelService<Soil_test_result>())
    .seTable("soil_test_result")
    .seturl("api/soil_test_result");
export const Supply_matchService = (new ModelService<Supply_match>())
    .seTable("supply_match")
    .seturl("api/supply_match");
export const Supply_requestService = (new ModelService<Supply_request>())
    .seTable("supply_request")
    .seturl("api/supply_request");
export const Transport_bookingService = (new ModelService<Transport_booking>())
    .seTable("transport_booking")
    .seturl("api/transport_booking");
export const Transport_providerService = (new ModelService<Transport_provider>())
    .seTable("transport_provider")
    .seturl("api/transport_provider");
export const UserService = (new ModelService<User>())
    .seTable("user")
    .seturl("api/user");
export const Weather_alertService = (new ModelService<Weather_alert>())
    .seTable("weather_alert")
    .seturl("api/weather_alert");

export * from "./Weather";
export * from "./Soil";
export * from "./Notification";