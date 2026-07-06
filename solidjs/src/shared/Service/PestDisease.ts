import { ModelService } from "./ModelService";
import { Pest_disease_data } from "../Interface/Model/Pest_disease_data";
import { Pest_disease_alert } from "../Interface/Model/Pest_disease_alert";

export const Pest_disease_dataService = (new ModelService<Pest_disease_data>())
    .seTable("pest_disease_data")
    .seturl("api/pest-disease/identify");

export const Pest_disease_alertService = (new ModelService<Pest_disease_alert>())
    .seTable("pest_disease_alert")
    .seturl("api/pest-disease/alerts");
