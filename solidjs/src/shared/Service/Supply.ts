import { ModelService } from "./ModelService";
import { Supply_match } from "../Interface/Model/Supply_match";
import { Supply_request } from "../Interface/Model/Supply_request";

export const Supply_matchService = (new ModelService<Supply_match>())
    .seTable("supply_match")
    .seturl("api/supply_match");

export const Supply_requestService = (new ModelService<Supply_request>())
    .seTable("supply_request")
    .seturl("api/supply_request");
