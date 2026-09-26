/**
 * Farm Selection Page for Strategy Request
 * Allows user to select which farm to generate strategy for
 */

import { Component, createSignal, onMount, Show } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { FarmService, type Farm } from '../../services/farm.service';

const SelectFarmPage: Component = () => {
  const navigate = useNavigate();
  const [farms, setFarms] = createSignal<Farm[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [selectedFarmId, setSelectedFarmId] = createSignal<string>('');

  onMount(async () => {
    try {
      const farmsList = await FarmService.getFarms();
      setFarms(farmsList);
      
      // If only one farm, auto-select it
      if (farmsList.length === 1) {
        setSelectedFarmId(farmsList[0].id.toString());
      }
    } catch (error) {
      console.error('Failed to load farms:', error);
      // Set empty farms array on error so the component still renders
      setFarms([]);
    } finally {
      setLoading(false);
    }
  });

  const handleSubmit = (e: Event) => {
    e.preventDefault();
    const farmId = selectedFarmId();
    if (farmId) {
      navigate(`/strategy/request?farmId=${farmId}`);
    }
  };

  return (
    <div class="min-h-screen bg-gray-50">
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 class="text-2xl font-bold text-gray-900">Select Farm for AI Strategy</h1>
        </div>
      </header>

      <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-lg shadow-md p-6">
          <Show when={loading()}>
            <p class="text-gray-600">Loading your farms...</p>
          </Show>

          <Show when={!loading() && farms().length === 0}>
            <div class="text-center py-8">
              <p class="text-gray-600 mb-4">You don't have any farms registered yet.</p>
              <button
                onClick={() => navigate('/farm/register')}
                class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Register Your First Farm
              </button>
            </div>
          </Show>

          <Show when={!loading() && farms().length > 0}>
            <form onSubmit={handleSubmit} class="space-y-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Select Farm <span class="text-red-500">*</span>
                </label>
                <select
                  name="farm_id"
                  value={selectedFarmId()}
                  onChange={(e) => setSelectedFarmId(e.currentTarget.value)}
                  required
                  class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Select a farm</option>
                  {farms().map((farm) => (
                    <option value={farm.id}>
                      {farm.name} - {farm.district}, {farm.state}
                    </option>
                  ))}
                </select>
                <p class="mt-2 text-sm text-gray-500">
                  Choose the farm you want to generate an annual crop strategy for
                </p>
              </div>

              <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
                <h3 class="text-sm font-semibold text-blue-900 mb-2">
                  What you'll get:
                </h3>
                <ul class="text-sm text-blue-800 space-y-1">
                  <li>• AI-powered crop recommendations for all 3 seasons</li>
                  <li>• Expected yields and profit estimates</li>
                  <li>• Month-by-month action plan</li>
                  <li>• Risk assessment and alternatives</li>
                </ul>
              </div>

              <div class="flex gap-3">
                <button
                  type="button"
                  onClick={() => navigate('/dashboard')}
                  class="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!selectedFarmId()}
                  class="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors"
                >
                  Get AI Recommendations
                </button>
              </div>
            </form>
          </Show>
        </div>
      </main>
    </div>
  );
};

export default SelectFarmPage;
