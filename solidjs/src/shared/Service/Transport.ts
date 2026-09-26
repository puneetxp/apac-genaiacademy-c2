import { ModelService } from "./ModelService";
import { Transport_booking } from "../Interface/Model/Transport_booking";
import { Transport_provider } from "../Interface/Model/Transport_provider";

export const Transport_bookingService = (new ModelService<Transport_booking>())
    .seTable("transport_booking")
    .seturl("/islogin/transport_booking/");

export const Transport_providerService = (new ModelService<Transport_provider>())
    .seTable("transport_provider")
    .seturl("/islogin/transport_provider/");
