import { ModelService } from "./ModelService";
import { Livestock } from "../Interface/Model/Livestock";
import { Livestock_health_record } from "../Interface/Model/Livestock_health_record";
import { Livestock_listing } from "../Interface/Model/Livestock_listing";
import { Livestock_marketplace_listing } from "../Interface/Model/Livestock_marketplace_listing";
import { Livestock_transaction } from "../Interface/Model/Livestock_transaction";

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
