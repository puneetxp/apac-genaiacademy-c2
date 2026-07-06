import { Component, createSignal, Show, For, onMount } from 'solid-js';
import { marketIntelligenceService, MarketSummary } from '../../services/market-intelligence.service';

interface RegionalStats {
  state: string;
  transactions: number;
  volume: number;
  revenue: number;
  avgPrice: number;
}

const PlatformAnalytics: Component = () => {
  const [timeRange, setTimeRange] = createSignal(30);
  const [selectedState, setSelectedState] = createSignal<string>('all');
  
  const [summary, setSummary] = createSignal<MarketSummary | null>(null);
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  const states = ['all', 'Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka', 'Tamil Nadu'];

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const summaryData = await marketIntelligenceService.getMarketSummary(
        selectedState() === 'all' ? undefined : selectedState()
      );
      setSummary(summaryData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  onMount(() => {
    loadData();
  });

  const getTopCrops = () => {
    if (!summary()) return [];
    return Object.entries(summary()!.crops)
      .sort((a, b) => b[1].total_volume - a[1].total_volume)
      .slice(0, 5);
  };

  const getTopLivestock = () => {
    if (!summary()) return [];
    return Object.entries(summary()!.livestock)
      .sort((a, b) => b[1].total_animals - a[1].total_animals)
      .slice(0, 5);
  };

  const exportReport = () => {
    const data = {
      timeRange: timeRange(),
      state: selectedState(),
      summary: summary(),
      exportedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `platform-analytics-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div class="min-h-screen bg-gray-50 py-8">
      <div class="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            📊 Platform Analytics Dashboard
          </h1>
          <p class="text-gray-600">
            Monitor transaction volume, quality trends, and user adoption metrics
          </p>
        </div>

        {/* Filters */}
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Time Range
              </label>
              <select
                value={timeRange()}
                onChange={(e) => {
                  setTimeRange(parseInt(e.target.value));
                  loadData();
                }}
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
                <option value={365}>Last year</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Region
              </label>
              <select
                value={selectedState()}
                onChange={(e) => {
                  setSelectedState(e.target.value);
                  loadData();
                }}
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <For each={states}>
                  {(state) => (
                    <option value={state}>
                      {state === 'all' ? 'All States' : state}
                    </option>
                  )}
                </For>
              </select>
            </div>

            <div class="flex items-end">
              <button
                onClick={exportReport}
                class="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                📥 Export Report
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        <Show when={loading()}>
          <div class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            <p class="mt-4 text-gray-600">Loading analytics...</p>
          </div>
        </Show>

        {/* Error State */}
        <Show when={error()}>
          <div class="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg mb-6">
            <p class="font-medium">Error loading data</p>
            <p class="text-sm">{error()}</p>
          </div>
        </Show>

        {/* Dashboard Content */}
        <Show when={!loading() && !error() && summary()}>
          {/* Key Metrics */}
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-sm font-medium text-gray-600">Total Transactions</h3>
                <span class="text-2xl">📝</span>
              </div>
              <p class="text-3xl font-bold text-gray-900">
                {summary()!.total_transactions.toLocaleString()}
              </p>
              <p class="text-sm mt-2 text-gray-600">
                All marketplace activity
              </p>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-sm font-medium text-gray-600">Total Revenue</h3>
                <span class="text-2xl">💰</span>
              </div>
              <p class="text-3xl font-bold text-gray-900">
                ₹{(summary()!.total_value / 100000).toFixed(2)}L
              </p>
              <p class="text-sm mt-2 text-gray-600">
                Gross transaction value
              </p>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-sm font-medium text-gray-600">Crop Varieties</h3>
                <span class="text-2xl">🌾</span>
              </div>
              <p class="text-3xl font-bold text-gray-900">
                {Object.keys(summary()!.crops).length}
              </p>
              <p class="text-sm mt-2 text-gray-600">
                Active crop types
              </p>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-sm font-medium text-gray-600">Livestock Types</h3>
                <span class="text-2xl">🐄</span>
              </div>
              <p class="text-3xl font-bold text-gray-900">
                {Object.keys(summary()!.livestock).length}
              </p>
              <p class="text-sm mt-2 text-gray-600">
                Active livestock types
              </p>
            </div>
          </div>

          {/* Top Crops */}
          <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">
              🌾 Top Crops by Volume
            </h3>
            
            <div class="space-y-3">
              <For each={getTopCrops()}>
                {([cropName, data]) => (
                  <div class="flex items-center gap-4">
                    <div class="w-32">
                      <p class="font-medium text-gray-900 capitalize">{cropName}</p>
                      <p class="text-sm text-gray-600">{data.transactions} txns</p>
                    </div>
                    
                    <div class="flex-1">
                      <div class="flex justify-between mb-1">
                        <span class="text-sm text-gray-600">Volume</span>
                        <span class="text-sm font-bold text-gray-900">
                          {data.total_volume.toLocaleString()} kg
                        </span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div
                          class="bg-green-600 h-2 rounded-full"
                          style={{ 
                            width: `${Math.min((data.total_volume / getTopCrops()[0][1].total_volume) * 100, 100)}%` 
                          }}
                        />
                      </div>
                    </div>
                    
                    <div class="w-24 text-right">
                      <p class="text-sm text-gray-600">Avg Price</p>
                      <p class="font-bold text-gray-900">₹{data.avg_price.toFixed(2)}</p>
                    </div>
                  </div>
                )}
              </For>
            </div>
          </div>

          {/* Top Livestock */}
          <Show when={getTopLivestock().length > 0}>
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4">
                🐄 Top Livestock by Volume
              </h3>
              
              <div class="space-y-3">
                <For each={getTopLivestock()}>
                  {([livestockName, data]) => (
                    <div class="flex items-center gap-4">
                      <div class="w-32">
                        <p class="font-medium text-gray-900 capitalize">{livestockName}</p>
                        <p class="text-sm text-gray-600">{data.transactions} txns</p>
                      </div>
                      
                      <div class="flex-1">
                        <div class="flex justify-between mb-1">
                          <span class="text-sm text-gray-600">Animals</span>
                          <span class="text-sm font-bold text-gray-900">
                            {data.total_animals.toLocaleString()}
                          </span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                          <div
                            class="bg-blue-600 h-2 rounded-full"
                            style={{ 
                              width: `${Math.min((data.total_animals / getTopLivestock()[0][1].total_animals) * 100, 100)}%` 
                            }}
                          />
                        </div>
                      </div>
                      
                      <div class="w-24 text-right">
                        <p class="text-sm text-gray-600">Avg Price</p>
                        <p class="font-bold text-gray-900">₹{data.avg_price.toFixed(2)}</p>
                      </div>
                    </div>
                  )}
                </For>
              </div>
            </div>
          </Show>

          {/* Detailed Tables */}
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* All Crops */}
            <div class="bg-white rounded-lg shadow-md p-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4">
                All Crops
              </h3>
              
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b-2 border-gray-200">
                      <th class="text-left py-2 font-medium text-gray-700">Crop</th>
                      <th class="text-right py-2 font-medium text-gray-700">Volume</th>
                      <th class="text-right py-2 font-medium text-gray-700">Avg Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    <For each={Object.entries(summary()!.crops)}>
                      {([cropName, data]) => (
                        <tr class="border-b border-gray-100">
                          <td class="py-2 capitalize">{cropName}</td>
                          <td class="py-2 text-right">{data.total_volume.toLocaleString()} kg</td>
                          <td class="py-2 text-right">₹{data.avg_price.toFixed(2)}</td>
                        </tr>
                      )}
                    </For>
                  </tbody>
                </table>
              </div>
            </div>

            {/* All Livestock */}
            <div class="bg-white rounded-lg shadow-md p-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4">
                All Livestock
              </h3>
              
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b-2 border-gray-200">
                      <th class="text-left py-2 font-medium text-gray-700">Type</th>
                      <th class="text-right py-2 font-medium text-gray-700">Animals</th>
                      <th class="text-right py-2 font-medium text-gray-700">Avg Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    <For each={Object.entries(summary()!.livestock)}>
                      {([livestockName, data]) => (
                        <tr class="border-b border-gray-100">
                          <td class="py-2 capitalize">{livestockName}</td>
                          <td class="py-2 text-right">{data.total_animals.toLocaleString()}</td>
                          <td class="py-2 text-right">₹{data.avg_price.toFixed(2)}</td>
                        </tr>
                      )}
                    </For>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Show>
      </div>
    </div>
  );
};

export default PlatformAnalytics;
