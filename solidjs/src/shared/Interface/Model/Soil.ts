export interface SoilHealth {
    id: number;
    updated_at: Date;
    plot_id: number;
    health_score: number;
    ph_level: number;
    organic_carbon: number;
    nitrogen: number;
    phosphorus: number;
    potassium: number;
    last_test_date: Date;
}

export interface SoilMap {
    id: number;
    updated_at: Date;
    plot_id: number;
    map_url: string;
    layer_type: 'moisture' | 'ndvi' | 'organic_matter';
    captured_at: Date;
}

export interface FertilizerRecommendation {
    id: number;
    updated_at: Date;
    plot_id: number;
    crop_type: string;
    growth_stage: string;
    recommended_fertilizers: Array<{
        name: string;
        dosage: string;
        timing: string;
        application_method: string;
    }>;
}
