/**
 * Farm List Component
 * Display all farms for the current user
 */

import { Component, For, Show } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import type { Farm } from '../../services/farm.service';

interface FarmListProps {
  farms: Farm[];
  isLoading: boolean;
  onAddFarm: () => void;
}

const FarmList: Component<FarmListProps> = (props) => {
  const navigate = useNavigate();

  const handleFarmClick = (farmId: number) => {
    navigate(`/farm/${farmId}`);
  };

  return (
    <div class="space-y-4">
      {/* Header */}
      <div class="flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">My Farms</h2>
        <button
          onClick={props.onAddFarm}
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
        >
          + Add Farm
        </button>
      </div>

      {/* Loading State */}
      <Show when={props.isLoading}>
        <div class="text-center py-8">
          <p class="text-gray-600">Loading farms...</p>
        </div>
      </Show>

      {/* Empty State */}
      <Show when={!props.isLoading && props.farms.length === 0}>
        <div class="bg-white rounded-lg shadow p-8 text-center">
          <svg
            class="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
          <h3 class="mt-2 text-lg font-medium text-gray-900">No farms yet</h3>
          <p class="mt-1 text-sm text-gray-500">
            Get started by registering your first farm.
          </p>
          <button
            onClick={props.onAddFarm}
            class="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
          >
            Register Farm
          </button>
        </div>
      </Show>

      {/* Farm Grid */}
      <Show when={!props.isLoading && props.farms.length > 0}>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <For each={props.farms}>
            {(farm) => (
              <div
                onClick={() => handleFarmClick(farm.id)}
                class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer p-6"
              >
                <h3 class="text-lg font-semibold text-gray-800 mb-2">
                  {farm.name}
                </h3>
                <div class="space-y-1 text-sm text-gray-600">
                  <p>
                    <span class="font-medium">Location:</span> {farm.district},{' '}
                    {farm.state}
                  </p>
                  <p>
                    <span class="font-medium">Area:</span> {farm.total_area_acres} acres
                  </p>
                  <p>
                    <span class="font-medium">Soil:</span> {farm.primary_soil_type}
                  </p>
                  <p>
                    <span class="font-medium">Irrigation:</span> {farm.irrigation_type}
                  </p>
                </div>
                <div class="mt-4 flex justify-end">
                  <span class="text-sm text-green-600 font-medium">
                    View Details →
                  </span>
                </div>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default FarmList;
