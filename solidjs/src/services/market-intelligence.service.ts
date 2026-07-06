/**
 * Market Intelligence Service
 * Handles API calls for market intelligence and predictive analytics
 */

import apiClient from '../lib/api-client';
import { buildUrl } from '~/config/api-registry';

export interface PriceTrend {
  date: string;
  avg_price: number;
  min_price: number;
  max_price: number;
  transaction_count: number;
}

export interface TrendAnalysis {
  item_type: string;
  item_name: string;
  state: string | null;
  district: string | null;
  period_days: number;
  current_avg_price: number;
  price_change_percent: number;
  trend_direction: 'rising' | 'falling' | 'stable';
  volatility: number;
  time_series: PriceTrend[];
}

export interface QualityPremium {
  grade: string;
  avg_price: number;
  premium_percent: number;
  transaction_count: number;
}

export interface DemandForecast {
  item_type: string;
  item_name: string;
  forecast_days: number;
  predicted_demand: number;
  confidence_score: number;
  trend: 'increasing' | 'decreasing' | 'stable';
}

export interface PricePrediction {
  item_type: string;
  item_name: string;
  state: string;
  district: string | null;
  forecast_days: number;
  predicted_price: number;
  confidence_score: number;
  price_range: {
    min: number;
    max: number;
  };
  trend: 'rising' | 'falling' | 'stable';
  factors: string[];
}

export interface SupplyDemandGap {
  item_name: string;
  item_type: string;
  gap_type: 'surplus' | 'shortage';
  severity: 'low' | 'medium' | 'high';
  supply_quantity: number;
  demand_quantity: number;
  gap_quantity: number;
  opportunity_description: string;
}

export interface OpportunityScore {
  item_type: string;
  item_name: string;
  state: string;
  district: string | null;
  overall_score: number;
  breakdown: {
    price_trend_score: number;
    demand_score: number;
    supply_gap_score: number;
    profitability_score: number;
  };
  recommendation: string;
  confidence: number;
}

export interface MonthlySupply {
  month: string;
  expected_quantity: number;
  expected_avg_price: number;
  quality_distribution: {
    [grade: string]: number;
  };
  supplier_count: number;
}

export interface MarketSummary {
  total_transactions: number;
  total_value: number;
  crops: {
    [cropName: string]: {
      transactions: number;
      total_volume: number;
      avg_price: number;
    };
  };
  livestock: {
    [livestockName: string]: {
      transactions: number;
      total_animals: number;
      avg_price: number;
    };
  };
}

class MarketIntelligenceService {
  /**
   * Get price trends for an item
   */
  async getPriceTrends(
    itemType: string,
    itemName: string,
    state?: string,
    district?: string,
    days: number = 90
  ): Promise<TrendAnalysis> {
    const params = new URLSearchParams({
      days: days.toString(),
    });
    if (state) params.append('state', state);
    if (district) params.append('district', district);

    const url = buildUrl('marketIntelligence', 'trends', { item_type: itemType, item_name: itemName });
    const response = await apiClient.get(
      `${url}?${params}`
    );
    return response.data;
  }

  /**
   * Get quality premiums by grade
   */
  async getQualityPremiums(
    itemType: string,
    itemName: string,
    state?: string,
    days: number = 90
  ): Promise<QualityPremium[]> {
    const params = new URLSearchParams({
      days: days.toString(),
    });
    if (state) params.append('state', state);

    const url = buildUrl('marketIntelligence', 'qualityPremiums', { item_type: itemType, item_name: itemName });
    const response = await apiClient.get(
      `${url}?${params}`
    );
    return response.data;
  }

  /**
   * Get demand forecast
   */
  async getDemandForecast(
    itemType: string,
    itemName: string,
    state?: string,
    daysAhead: number = 30
  ): Promise<DemandForecast> {
    const params = new URLSearchParams({
      days_ahead: daysAhead.toString(),
    });
    if (state) params.append('state', state);

    const url = buildUrl('marketIntelligence', 'demandForecast', { item_type: itemType, item_name: itemName });
    const response = await apiClient.get(
      `${url}?${params}`
    );
    return response.data;
  }

  /**
   * Get market summary statistics
   */
  async getMarketSummary(state?: string): Promise<MarketSummary> {
    const params = state ? `?state=${state}` : '';
    const url = buildUrl('marketIntelligence', 'summary');
    const response = await apiClient.get(`${url}${params}`);
    return response.data;
  }

  /**
   * Predict future prices using AI
   */
  async predictPrice(
    itemType: string,
    itemName: string,
    state: string,
    district?: string,
    variety?: string,
    forecastDays: number = 30
  ): Promise<PricePrediction> {
    const params = new URLSearchParams({
      item_type: itemType,
      item_name: itemName,
      state: state,
      forecast_days: forecastDays.toString(),
    });
    if (district) params.append('district', district);
    if (variety) params.append('variety', variety);

    const url = buildUrl('predictiveAnalytics', 'predictPrice');
    const response = await apiClient.post(`${url}?${params}`);
    return response.data;
  }

  /**
   * Predict future demand
   */
  async predictDemand(
    itemType: string,
    itemName: string,
    state: string,
    district?: string,
    forecastDays: number = 30
  ): Promise<any> {
    const params = new URLSearchParams({
      item_type: itemType,
      item_name: itemName,
      state: state,
      forecast_days: forecastDays.toString(),
    });
    if (district) params.append('district', district);

    const url = buildUrl('predictiveAnalytics', 'predictDemand');
    const response = await apiClient.get(`${url}?${params}`);
    return response.data;
  }

  /**
   * Get supply-demand gaps
   */
  async getSupplyDemandGaps(
    state: string,
    district?: string,
    itemType?: string
  ): Promise<SupplyDemandGap[]> {
    const params = new URLSearchParams({ state });
    if (district) params.append('district', district);
    if (itemType) params.append('item_type', itemType);

    const url = buildUrl('predictiveAnalytics', 'supplyDemandGaps');
    const response = await apiClient.get(`${url}?${params}`);
    return response.data.gaps || [];
  }

  /**
   * Get opportunity score for farmers
   */
  async getOpportunityScore(
    itemType: string,
    itemName: string,
    state: string,
    district?: string,
    variety?: string
  ): Promise<OpportunityScore> {
    const params = new URLSearchParams({
      item_type: itemType,
      item_name: itemName,
      state: state,
    });
    if (district) params.append('district', district);
    if (variety) params.append('variety', variety);

    const url = buildUrl('predictiveAnalytics', 'opportunityScore');
    const response = await apiClient.get(`${url}?${params}`);
    return response.data;
  }

  /**
   * Get buyer supply planning data
   */
  async getBuyerSupplyPlanning(
    itemType: string,
    itemName: string,
    state: string,
    district?: string,
    monthsAhead: number = 3
  ): Promise<{ monthly_supply: MonthlySupply[] }> {
    const params = new URLSearchParams({
      item_type: itemType,
      item_name: itemName,
      state: state,
      months_ahead: monthsAhead.toString(),
    });
    if (district) params.append('district', district);

    const url = buildUrl('predictiveAnalytics', 'buyerSupplyPlanning');
    const response = await apiClient.get(`${url}?${params}`);
    return response.data;
  }

  /**
   * Get Minimum Support Price (MSP) rates for crops
   */
  async getMspRates(
    cropName?: string,
    year?: number,
    season?: string
  ): Promise<any[]> {
    const params = new URLSearchParams();
    if (cropName) params.append('crop_name', cropName);
    if (year) params.append('year', year.toString());
    if (season) params.append('season', season);

    const url = buildUrl('marketIntelligence', 'msp');
    const response = await apiClient.get(`${url}?${params}`);
    return response.data.data || [];
  }
}

export const marketIntelligenceService = new MarketIntelligenceService();
