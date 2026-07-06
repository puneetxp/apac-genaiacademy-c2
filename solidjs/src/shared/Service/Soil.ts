import { ModelService } from "./ModelService";
import { SoilHealth, SoilMap, FertilizerRecommendation } from "../Interface/Model/Soil";

export const SoilHealthService = (new ModelService<SoilHealth>())
    .seTable("soil_health")
    .seturl("api/soil/health");

export const SoilMapService = (new ModelService<SoilMap>())
    .seTable("soil_map")
    .seturl("api/soil/map");

export const FertilizerRecommendationService = (new ModelService<FertilizerRecommendation>())
    .seTable("fertilizer_recommendation")
    .seturl("api/soil/fertilizer-recommendations");
