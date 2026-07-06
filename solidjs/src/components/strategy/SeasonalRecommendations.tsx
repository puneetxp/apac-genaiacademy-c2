/**
 * Seasonal Recommendations Component
 * Display Kharif, Rabi, and Zaid season recommendations
 */

import { Component, Show, For } from 'solid-js';
import type { SeasonalRecommendation } from '../../services/strategy.service';

interface SeasonalRecommendationsProps {
  kharif: SeasonalRecommendation;
  rabi: SeasonalRecommendation;
  zaid?: {
    recommended_crop: string | null;
    expected_profit_per_acre: number;
  };
}

const SeasonalRecommendations: Component<SeasonalRecommendationsProps> = (props) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const SeasonCard: Component<{
    title: string;
    color: string;
    season: SeasonalRecommendation;
  }> = (cardProps) => (
    <div class={`recommendation-card bg-white rounded-lg shadow-md p-6 border-t-4 ${cardProps.color}`}>
      <h3 class="text-xl font-bold text-gray-800 mb-4">{cardProps.title}</h3>
      
      {/* Crop Name */}
      <div class="mb-4">
        <p class="text-2xl font-bold text-green-700">
          {cardProps.season.recommended_crop}
        </p>
        <p class="text-sm text-gray-600">{cardProps.season.variety}</p>
      </div>

      {/* Key Metrics */}
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p class="text-xs text-gray-500">Expected Yield</p>
          <p class="text-sm font-semibold text-gray-800">
            {cardProps.season.expected_yield_per_acre}
          </p>
        </div>
        <div>
          <p class="text-xs text-gray-500">Expected Profit</p>
          <p class="text-sm font-semibold text-green-600">
            {formatCurrency(cardProps.season.expected_profit_per_acre)}
          </p>
        </div>
        <div>
          <p class="text-xs text-gray-500">Investment</p>
          <p class="text-sm font-semibold text-blue-600">
            {formatCurrency(cardProps.season.investment_per_acre)}
          </p>
        </div>
        <div>
          <p class="text-xs text-gray-500">Confidence</p>
          <p class="text-sm font-semibold text-purple-600">
            {(cardProps.season.confidence_score * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      {/* Timing */}
      <div class="mb-4 bg-gray-50 rounded-lg p-3">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <p class="text-xs text-gray-500 mb-1">Planting Window</p>
            <p class="text-sm font-medium text-gray-800">
              {cardProps.season.planting_window}
            </p>
          </div>
          <div>
            <p class="text-xs text-gray-500 mb-1">Harvest Window</p>
            <p class="text-sm font-medium text-gray-800">
              {cardProps.season.harvest_window}
            </p>
          </div>
        </div>
      </div>

      {/* Success Factors */}
      <div>
        <p class="text-sm font-medium text-gray-700 mb-2">Key Success Factors:</p>
        <ul class="space-y-1">
          <For each={cardProps.season.key_success_factors}>
            {(factor) => (
              <li class="text-sm text-gray-600 flex items-start">
                <span class="text-green-500 mr-2">✓</span>
                <span>{factor}</span>
              </li>
            )}
          </For>
        </ul>
      </div>
    </div>
  );

  return (
    <div class="space-y-6">
      <h3 class="text-xl font-bold text-gray-800">Seasonal Recommendations</h3>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Kharif Season */}
        <SeasonCard
          title="Kharif Season (June-October)"
          color="border-green-500"
          season={props.kharif}
        />

        {/* Rabi Season */}
        <SeasonCard
          title="Rabi Season (November-April)"
          color="border-blue-500"
          season={props.rabi}
        />
      </div>

      {/* Zaid Season */}
      <Show when={props.zaid && props.zaid.recommended_crop}>
        <div class="recommendation-card bg-white rounded-lg shadow-md p-6 border-t-4 border-yellow-500">
          <h3 class="text-xl font-bold text-gray-800 mb-4">
            Zaid Season (May-June)
          </h3>
          <div class="flex justify-between items-center">
            <div>
              <p class="text-lg font-bold text-yellow-700">
                {props.zaid!.recommended_crop}
              </p>
              <p class="text-sm text-gray-600 mt-1">
                Quick cash crop or fodder option
              </p>
            </div>
            <div class="text-right">
              <p class="text-xs text-gray-500">Expected Profit</p>
              <p class="text-lg font-semibold text-green-600">
                {formatCurrency(props.zaid!.expected_profit_per_acre)}
              </p>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
};

export default SeasonalRecommendations;
