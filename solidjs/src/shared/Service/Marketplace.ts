import { ModelService } from "./ModelService";
import { Marketplace_listing } from "../Interface/Model/Marketplace_listing";
import { Buyer_interest } from "../Interface/Model/Buyer_interest";

export const Marketplace_listingService = (new ModelService<Marketplace_listing>())
    .seTable("marketplace_listing")
    .seturl("api/marketplace_listing");

export const Buyer_interestService = (new ModelService<Buyer_interest>())
    .seTable("buyer_interest")
    .seturl("api/buyer_interest");
