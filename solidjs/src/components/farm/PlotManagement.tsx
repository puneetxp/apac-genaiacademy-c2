/**
 * Plot Management Component
 * Add, edit, and delete farm plots
 */

import { Component, Show, For, createSignal } from 'solid-js';
import { type FarmPlot, SOIL_TYPES } from '../../services/farm.service';
import { farmPlots, createPlot, deletePlot } from '../../stores/farm.store';

interface PlotManagementProps {
  farmId: number;
  farmName: string;
  onClose: () => void;
}

const PlotManagement: Component<PlotManagementProps> = (props) => {
  const [showAddForm, setShowAddForm] = createSignal(false);
  const [plotName, setPlotName] = createSignal('');
  const [plotArea, setPlotArea] = createSignal(0);
  const [plotSoilType, setPlotSoilType] = createSignal('');
  const [currentCrop, setCurrentCrop] = createSignal('');
  const [isLoading, setIsLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  const handleAddPlot = async (e: Event) => {
    e.preventDefault();
    setError(null);

    if (!plotName() || plotArea() <= 0) {
      setError('Please provide plot name and valid area');
      return;
    }

    setIsLoading(true);

    try {
      await createPlot({
        farm_id: props.farmId,
        plot_name: plotName(),
        area: plotArea(),
        soil_type: plotSoilType() || undefined,
        current_crop: currentCrop() || undefined,
      });

      // Reset form
      setPlotName('');
      setPlotArea(0);
      setPlotSoilType('');
      setCurrentCrop('');
      setShowAddForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add plot');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeletePlot = async (plotId: number) => {
    if (!confirm('Are you sure you want to delete this plot?')) {
      return;
    }

    try {
      await deletePlot(plotId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete plot');
    }
  };

  const totalPlotArea = () => {
    return farmPlots().reduce((sum, plot) => sum + plot.area, 0);
  };

  return (
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div class="sticky top-0 bg-white border-b p-6">
          <div class="flex justify-between items-start">
            <div>
              <h2 class="text-2xl font-bold text-gray-800">Manage Plots</h2>
              <p class="text-sm text-gray-600 mt-1">{props.farmName}</p>
            </div>
            <button
              onClick={props.onClose}
              class="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div class="p-6">
          <Show when={error()}>
            <div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error()}
            </div>
          </Show>

          {/* Summary */}
          <div class="mb-6 p-4 bg-green-50 rounded-lg">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-sm text-gray-600">Total Plots</p>
                <p class="text-2xl font-bold text-green-700">{farmPlots().length}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Total Plot Area</p>
                <p class="text-2xl font-bold text-green-700">{totalPlotArea().toFixed(2)} acres</p>
              </div>
            </div>
          </div>

          {/* Add Plot Button */}
          <Show when={!showAddForm()}>
            <button
              onClick={() => setShowAddForm(true)}
              class="w-full mb-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
            >
              + Add New Plot
            </button>
          </Show>

          {/* Add Plot Form */}
          <Show when={showAddForm()}>
            <form onSubmit={handleAddPlot} class="mb-6 p-4 border border-green-200 rounded-lg bg-green-50">
              <h3 class="text-lg font-semibold text-gray-800 mb-4">Add New Plot</h3>
              
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Plot Name *
                  </label>
                  <input
                    type="text"
                    value={plotName()}
                    onInput={(e) => setPlotName(e.currentTarget.value)}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., North Field"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Area (acres) *
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    value={plotArea() || ''}
                    onInput={(e) => setPlotArea(parseFloat(e.currentTarget.value) || 0)}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., 2.5"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Soil Type
                  </label>
                  <select
                    value={plotSoilType()}
                    onChange={(e) => setPlotSoilType(e.currentTarget.value)}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="">Select Soil Type</option>
                    <For each={SOIL_TYPES}>
                      {(type) => <option value={type}>{type}</option>}
                    </For>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Current Crop
                  </label>
                  <input
                    type="text"
                    value={currentCrop()}
                    onInput={(e) => setCurrentCrop(e.currentTarget.value)}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., Wheat"
                  />
                </div>
              </div>

              <div class="flex gap-3 mt-4">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  class="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading()}
                  class="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
                >
                  {isLoading() ? 'Adding...' : 'Add Plot'}
                </button>
              </div>
            </form>
          </Show>

          {/* Plots List */}
          <div class="space-y-3">
            <Show when={farmPlots().length === 0}>
              <div class="text-center py-8 text-gray-500">
                <p>No plots added yet</p>
                <p class="text-sm mt-2">Click "Add New Plot" to get started</p>
              </div>
            </Show>

            <For each={farmPlots()}>
              {(plot) => (
                <div class="p-4 border border-gray-200 rounded-lg hover:border-green-300 transition-colors">
                  <div class="flex justify-between items-start">
                    <div class="flex-1">
                      <h4 class="font-semibold text-gray-800">{plot.plot_name}</h4>
                      <div class="mt-2 grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span class="text-gray-600">Area:</span>
                          <span class="ml-2 font-medium">{plot.area} acres</span>
                        </div>
                        <Show when={plot.soil_type}>
                          <div>
                            <span class="text-gray-600">Soil:</span>
                            <span class="ml-2 font-medium">{plot.soil_type}</span>
                          </div>
                        </Show>
                        <Show when={plot.current_crop}>
                          <div class="col-span-2">
                            <span class="text-gray-600">Current Crop:</span>
                            <span class="ml-2 font-medium">{plot.current_crop}</span>
                          </div>
                        </Show>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeletePlot(plot.id)}
                      class="ml-4 px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 text-sm font-medium rounded transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </For>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlotManagement;
