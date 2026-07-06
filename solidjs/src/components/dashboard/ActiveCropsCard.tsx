/**
 * Active Crops Card Component
 * Displays active crops with growth stages and progress tracking
 */

import { Component, For, Show } from 'solid-js';
import type { ActiveCrop } from '../../services/dashboard.service';
import CropProgressIndicator from './CropProgressIndicator';
import HarvestCountdown from './HarvestCountdown';

interface ActiveCropsCardProps {
  crops: ActiveCrop[];
}

const ActiveCropsCard: Component<ActiveCropsCardProps> = (props) => {
  const getGrowthStageColor = (stage: string) => {
    switch (stage) {
      case 'ready':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'maturing':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'growing':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'planted':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'overdue':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getGrowthStageLabel = (stage: string) => {
    switch (stage) {
      case 'ready':
        return '🌾 Ready for Harvest';
      case 'maturing':
        return '🌱 Maturing';
      case 'growing':
        return '🌿 Growing';
      case 'planted':
        return '🌱 Recently Planted';
      case 'overdue':
        return '⚠️ Overdue';
      default:
        return stage;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">
        Active Crops
      </h2>
      
      <Show
        when={props.crops && props.crops.length > 0}
        fallback={
          <div class="text-center py-8 text-gray-500">
            <div class="text-4xl mb-2">🌾</div>
            <p>No active crops yet</p>
            <p class="text-sm mt-1">Start by creating an annual strategy</p>
          </div>
        }
      >
        <div class="space-y-4">
          <For each={props.crops}>
            {(crop) => (
              <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-3">
                  <div>
                    <h3 class="font-semibold text-gray-900">
                      {crop.crop_type}
                      <Show when={crop.crop_variety}>
                        <span class="text-sm text-gray-600 ml-2">
                          ({crop.crop_variety})
                        </span>
                      </Show>
                    </h3>
                    <p class="text-sm text-gray-600 mt-1">
                      Planted: {formatDate(crop.planting_date)}
                    </p>
                  </div>
                  <span class={`px-3 py-1 rounded-full text-xs font-medium border ${getGrowthStageColor(crop.growth_stage)}`}>
                    {getGrowthStageLabel(crop.growth_stage)}
                  </span>
                </div>

                {/* Crop Growth Progress Indicator */}
                <CropProgressIndicator 
                  plantingDate={crop.planting_date}
                  expectedHarvestDate={crop.expected_harvest_date}
                  growthStage={crop.growth_stage}
                />
                
                <div class="grid grid-cols-2 gap-4 mt-3 text-sm">
                  <div>
                    <span class="text-gray-500">Expected Harvest:</span>
                    <p class="font-medium text-gray-900">
                      {formatDate(crop.expected_harvest_date)}
                    </p>
                  </div>
                  <div>
                    <span class="text-gray-500">Estimated Quantity:</span>
                    <p class="font-medium text-gray-900">
                      {crop.estimated_quantity} {crop.quantity_unit}
                    </p>
                  </div>
                </div>

                {/* Harvest Countdown */}
                <HarvestCountdown 
                  daysUntilHarvest={crop.days_until_harvest}
                  growthStage={crop.growth_stage}
                />
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default ActiveCropsCard;
