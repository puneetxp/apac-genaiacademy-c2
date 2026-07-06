/**
 * Farm Profile Dashboard Component
 * Display and manage farm information
 */

import { Component, Show, For, createSignal } from 'solid-js';
import { type Farm } from '../../services/farm.service';

interface FarmProfileDashboardProps {
  farm: Farm;
  onEdit: () => void;
  onDelete: () => void;
  onManagePlots: () => void;
  onGenerateStrategy: () => void;
}

const FarmProfileDashboard: Component<FarmProfileDashboardProps> = (props) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = createSignal(false);

  const handleDelete = () => {
    setShowDeleteConfirm(false);
    props.onDelete();
  };

  return (
    <div class="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div class="flex justify-between items-start mb-6">
        <div>
          <h2 class="text-2xl font-bold text-gray-800">{props.farm.name}</h2>
          <p class="text-sm text-gray-500 mt-1">
            {props.farm.district}, {props.farm.state}
          </p>
        </div>
        <div class="flex gap-2">
          <button
            onClick={props.onEdit}
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors"
          >
            Edit
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Farm Details Grid */}
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {/* Total Area */}
        <div class="p-4 bg-green-50 rounded-lg">
          <p class="text-sm text-gray-600 mb-1">Total Area</p>
          <p class="text-2xl font-bold text-green-700">{props.farm.total_area_acres} acres</p>
        </div>

        {/* Primary Soil Type */}
        <Show when={props.farm.primary_soil_type}>
          <div class="p-4 bg-blue-50 rounded-lg">
            <p class="text-sm text-gray-600 mb-1">Primary Soil Type</p>
            <p class="text-lg font-semibold text-blue-700">{props.farm.primary_soil_type}</p>
          </div>
        </Show>

        {/* Irrigation Type */}
        <Show when={props.farm.irrigation_type}>
          <div class="p-4 bg-purple-50 rounded-lg">
            <p class="text-sm text-gray-600 mb-1">Irrigation</p>
            <p class="text-lg font-semibold text-purple-700">{props.farm.irrigation_type}</p>
          </div>
        </Show>

        {/* Area Context Note */}
        <div class="p-4 bg-gray-50 rounded-lg col-span-full">
          <p class="text-sm text-gray-600 mb-1">Farm Information</p>
          <p class="text-sm font-medium text-gray-700">Detailed investment and crop history are managed per-plot.</p>
        </div>
      </div>

      {/* Soil Health & Nutrient Profile */}
      <div class="mb-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4 border-b pb-2 flex items-center gap-2">
          <span>🌱</span> Soil Health & Nutrient Profile
        </h3>
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
          <div class="bg-gray-50 rounded p-3 border border-gray-100">
            <p class="text-xs text-gray-500 mb-1">pH Level</p>
            <p class="font-semibold text-gray-800">{props.farm.ph_level?.toFixed(1) || 'N/A'}</p>
          </div>
          <div class="bg-red-50 rounded p-3 border border-red-100">
            <p class="text-xs text-red-600 mb-1">Nitrogen (N)</p>
            <p class="font-semibold text-red-800">{props.farm.nitrogen ? `${props.farm.nitrogen} kg/ha` : 'N/A'}</p>
          </div>
          <div class="bg-blue-50 rounded p-3 border border-blue-100">
            <p class="text-xs text-blue-600 mb-1">Phosphorus (P)</p>
            <p class="font-semibold text-blue-800">{props.farm.phosphorus ? `${props.farm.phosphorus} kg/ha` : 'N/A'}</p>
          </div>
          <div class="bg-orange-50 rounded p-3 border border-orange-100">
            <p class="text-xs text-orange-600 mb-1">Potassium (K)</p>
            <p class="font-semibold text-orange-800">{props.farm.potassium ? `${props.farm.potassium} kg/ha` : 'N/A'}</p>
          </div>
          <div class="bg-green-50 rounded p-3 border border-green-100">
            <p class="text-xs text-green-600 mb-1">Organic Carbon</p>
            <p class="font-semibold text-green-800">{props.farm.organic_carbon ? `${props.farm.organic_carbon}%` : 'N/A'}</p>
          </div>
          <div class="bg-purple-50 rounded p-3 border border-purple-100">
            <p class="text-xs text-purple-600 mb-1">Elec. Conductivity</p>
            <p class="font-semibold text-purple-800">{props.farm.electrical_conductivity ? `${props.farm.electrical_conductivity} dS/m` : 'N/A'}</p>
          </div>
          <div class="bg-yellow-50 rounded p-3 border border-yellow-100">
            <p class="text-xs text-yellow-700 mb-1">Sulfur</p>
            <p class="font-semibold text-yellow-800">{props.farm.sulfur ? `${props.farm.sulfur} ppm` : 'N/A'}</p>
          </div>
          <div class="bg-teal-50 rounded p-3 border border-teal-100">
            <p class="text-xs text-teal-600 mb-1">Zinc</p>
            <p class="font-semibold text-teal-800">{props.farm.zinc ? `${props.farm.zinc} ppm` : 'N/A'}</p>
          </div>
          <div class="bg-amber-50 rounded p-3 border border-amber-100">
            <p class="text-xs text-amber-700 mb-1">Iron</p>
            <p class="font-semibold text-amber-800">{props.farm.iron ? `${props.farm.iron} ppm` : 'N/A'}</p>
          </div>
          <div class="bg-sky-50 rounded p-3 border border-sky-100">
            <p class="text-xs text-sky-600 mb-1">Boron</p>
            <p class="font-semibold text-sky-800">{props.farm.boron ? `${props.farm.boron} ppm` : 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div class="border-t pt-4 space-y-3">
        <button
          onClick={props.onGenerateStrategy}
          class="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
        >
          🌾 Generate Annual Crop Strategy
        </button>
        <button
          onClick={props.onManagePlots}
          class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors"
        >
          Manage Plots
        </button>
      </div>

      {/* Delete Confirmation Modal */}
      <Show when={showDeleteConfirm()}>
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white rounded-lg p-6 max-w-md mx-4">
            <h3 class="text-xl font-bold text-gray-800 mb-4">
              Delete Farm?
            </h3>
            <p class="text-gray-600 mb-6">
              Are you sure you want to delete "{props.farm.name}"? This action cannot be undone.
            </p>
            <div class="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                class="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                class="flex-1 py-2 px-4 bg-red-600 hover:bg-red-700 text-white font-medium rounded-md transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
};

export default FarmProfileDashboard;
