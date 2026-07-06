import { ModelService } from "./ModelService";
import { Notification } from "../Interface/Model/Notification";

export const NotificationService = (new ModelService<Notification>())
    .seTable("notification")
    .seturl("api/notifications");
