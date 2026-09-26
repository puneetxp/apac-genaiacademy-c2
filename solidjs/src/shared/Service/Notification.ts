import { ModelService } from "./ModelService";
import { Notification } from "../Interface/Model/Notification";

export const NotificationService = (new ModelService<Notification>())
    .seTable("user_notification")
    // In-app inbox rows (table user_notifications), scoped to the signed-in user
    .seturl("/islogin/user_notification/");
