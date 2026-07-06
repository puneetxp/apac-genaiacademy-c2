export interface WeatherForecast {
    id: number;
    updated_at: Date;
    date: string;
    temp_max: number;
    temp_min: number;
    condition: string;
    icon: string;
    rainfall_prob: number;
    precipitation_prob: number;
    wind_speed: number;
    humidity: number;
}

export interface SevereAlert {
    id: number;
    updated_at: Date;
    type: string;
    alert_type: string;
    severity: 'low' | 'moderate' | 'high' | 'critical';
    message: string;
    recommendation: string;
    issued_at: Date;
}
