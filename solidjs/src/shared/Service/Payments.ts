import { ModelService } from "./ModelService";
import { Payment_milestone } from "../Interface/Model/Payment_milestone";

export const Payment_milestoneService = (new ModelService<Payment_milestone>())
    .seTable("payment_milestone")
    .seturl("api/payment_milestone");
