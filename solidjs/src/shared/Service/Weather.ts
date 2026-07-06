import { ModelService } from "./ModelService";
import { Weather_alert } from "../Interface/Model/Weather_alert";
import { WeatherForecast, SevereAlert } from "../Interface/Model/Weather";

export const Weather_alertService = (new ModelService<Weather_alert>())
    .seTable("weather_alert")
    .seturl("api/weather_alert");

export const WeatherForecastService = (new ModelService<WeatherForecast>())
    .seTable("weather_forecast")
    .seturl("api/weather/forecast");

export const SevereAlertService = (new ModelService<SevereAlert>())
    .seTable("severe_alert")
    .seturl("api/weather/severe");
