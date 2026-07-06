import { Component, createSignal, onMount, Show, For } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import apiClient from '../../lib/api-client';

interface Crop {
  id: number;
  crop_name: string;
  crop_variety: string;
  season: string;
  planting_date: string;
  expected_harvest_date: string;
  area: number;
  expected_yield: number;
  expected_profit: number;
  actual_yield?: number;
  actual_profit?: number;
  status: string;
  farm_name: string;
  plot_name: string;
  created_at: string;
}

const MyCrops: Component = () => {
  const navigate = useNavigate();
  const [crops, setCrops] = createSignal<Crop[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal('');

  onMount(async () => {
    await loadCrops();
  });

  const loadCrops = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await apiClient.get('/api/v1/crops/my-crops', {
        cache: false,
      });
      const data = response.data;

      if (data?.success && data?.crops) {
        setCrops(data.crops);
      }
    } catch (err: any) {
      console.error('Error loading crops:', err);
      setError(err.message || 'Failed to load crops');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'planted':
        return 'bg-blue-100 text-blue-800';
      case 'growing':
        return 'bg-green-100 text-green-800';
      case 'flowering':
        return 'bg-purple-100 text-purple-800';
      case 'maturing':
        return 'bg-yellow-100 text-yellow-800';
      case 'harvested':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div class="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <button
                onClick={() => navigate('/dashboard')}
                class="mr-4 text-gray-600 hover:text-gray-900"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <h1 class="text-2xl font-bold text-gray-900">My Crops</h1>
            </div>
            <button
              onClick={() => navigate('/plots/create')}
              class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              + Add Crop
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Show when={loading()}>
          <div class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
          </div>
        </Show>

        <Show when={error()}>
          <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p class="text-red-800">{error()}</p>
          </div>
        </Show>

        <Show when={!loading() && !error()}>
          <Show
            when={crops().length > 0}
            fallback={
              <div class="bg-white rounded-lg shadow p-8 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                <h3 class="mt-2 text-lg font-medium text-gray-900">No crops yet</h3>
                <p class="mt-1 text-sm text-gray-500">Get started by adding your first crop.</p>
                <div class="mt-6">
                  <button
                    onClick={() => navigate('/plots/create')}
                    class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                  >
                    Add Crop
                  </button>
                </div>
              </div>
            }
          >
            {/* Summary Cards */}
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div class="bg-white rounded-lg shadow p-4">
                <div class="text-sm text-gray-600">Total Crops</div>
                <div class="text-2xl font-bold text-gray-900">{crops().length}</div>
              </div>
              <div class="bg-white rounded-lg shadow p-4">
                <div class="text-sm text-gray-600">Total Area</div>
                <div class="text-2xl font-bold text-gray-900">
                  {crops().reduce((sum, crop) => sum + crop.area, 0).toFixed(2)} acres
                </div>
              </div>
              <div class="bg-white rounded-lg shadow p-4">
                <div class="text-sm text-gray-600">Expected Profit</div>
                <div class="text-2xl font-bold text-green-600">
                  {formatCurrency(crops().reduce((sum, crop) => sum + crop.expected_profit, 0))}
                </div>
              </div>
            </div>

            {/* Crops List */}
            <div class="space-y-4">
              <For each={crops()}>
                {(crop) => (
                  <div class="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
                    <div class="p-6">
                      <div class="flex items-start justify-between">
                        <div class="flex-1">
                          <div class="flex items-center gap-3 mb-2">
                            <h3 class="text-lg font-semibold text-gray-900">
                              {crop.crop_name}
                            </h3>
                            <span class={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(crop.status)}`}>
                              {crop.status}
                            </span>
                          </div>
                          
                          <div class="text-sm text-gray-600 mb-3">
                            {crop.crop_variety && <span>{crop.crop_variety} • </span>}
                            <span class="capitalize">{crop.season} Season</span>
                          </div>

                          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <div class="text-gray-500">Farm</div>
                              <div class="font-medium text-gray-900">{crop.farm_name || 'N/A'}</div>
                            </div>
                            <div>
                              <div class="text-gray-500">Plot</div>
                              <div class="font-medium text-gray-900">{crop.plot_name || 'N/A'}</div>
                            </div>
                            <div>
                              <div class="text-gray-500">Area</div>
                              <div class="font-medium text-gray-900">{crop.area} acres</div>
                            </div>
                            <div>
                              <div class="text-gray-500">Expected Yield</div>
                              <div class="font-medium text-gray-900">{crop.expected_yield} quintals</div>
                            </div>
                          </div>

                          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mt-3">
                            <div>
                              <div class="text-gray-500">Planted</div>
                              <div class="font-medium text-gray-900">{formatDate(crop.planting_date)}</div>
                            </div>
                            <div>
                              <div class="text-gray-500">Expected Harvest</div>
                              <div class="font-medium text-gray-900">{formatDate(crop.expected_harvest_date)}</div>
                            </div>
                            <div>
                              <div class="text-gray-500">Expected Profit</div>
                              <div class="font-medium text-green-600">{formatCurrency(crop.expected_profit)}</div>
                            </div>
                            <Show when={crop.actual_profit}>
                              <div>
                                <div class="text-gray-500">Actual Profit</div>
                                <div class="font-medium text-green-600">{formatCurrency(crop.actual_profit!)}</div>
                              </div>
                            </Show>
                          </div>
                        </div>

                        <button
                          onClick={() => navigate(`/crops/${crop.id}`)}
                          class="ml-4 text-green-600 hover:text-green-700"
                        >
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </For>
            </div>
          </Show>
        </Show>
      </div>
    </div>
  );
};

export default MyCrops;
