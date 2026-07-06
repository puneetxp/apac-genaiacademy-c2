import { Component, createSignal, Show, For, onMount } from 'solid-js';
import { marketIntelligenceService, MonthlySupply, PricePrediction } from '../../services/market-intelligence.service';

const SupplyPlanning: Component = () => {
  const [selectedCrop, setSelectedCrop] = createSignal('wheat');
  const [selectedState, setSelectedState] = createSignal('Punjab');
  const [selectedDistrict, setSelectedDistrict] = createSignal<string>('');
  const [monthsAhead, setMonthsAhead] = createSignal(3);
  
  const [supplyData, setSupplyData] = createSignal<MonthlySupply[]>([]);
  const [priceForecast, setPriceForecast] = createSignal<PricePrediction | null>(null);
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  const popularCrops = ['wheat', 'rice', 'cotton', 'sugarcane', 'maize', 'potato', 'onion', 'tomato'];
  const states = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka', 'Tamil Nadu'];

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load supply planning data
      const planningData = await marketIntelligenceService.getBuyerSupplyPlanning(
        'crop',
        selectedCrop(),
        selectedState(),
        selectedDistrict() || undefined,
        monthsAhead()
      );
      setSupplyData(planningData.monthly_supply || []);

      // Load price forecast
      const forecast = await marketIntelligenceService.predictPrice(
        'crop',
        selectedCrop(),
        selectedState(),
        selectedDistrict() || undefined,
        undefined,
        30
      );
      setPriceForecast(forecast);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load supply planning data');
    } finally {
      setLoading(false);
    }
  };

  onMount(() => {
    loadData();
  });

  const exportToPDF = () => {
    // Simple CSV export for now
    const headers = ['Month', 'Quantity (kg)', 'Avg Price (₹)', 'Grade A %', 'Grade B %', 'Grade C %', 'Suppliers'];
    const rows = supplyData().map(month => [
      month.month,
      month.expected_quantity,
      month.expected_avg_price,
      month.quality_distribution['A'] || 0,
      month.quality_distribution['B'] || 0,
      month.quality_distribution['C'] || 0,
      month.supplier_count
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `supply-planning-${selectedCrop()}-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getTotalSupply = () => {
    return supplyData().reduce((sum, month) => sum + month.expected_quantity, 0);
  };

  const getAvgPrice = () => {
    if (supplyData().length === 0) return 0;
    const total = supplyData().reduce((sum, month) => sum + month.expected_avg_price, 0);
    return total / supplyData().length;
  };

  const getTotalSuppliers = () => {
    return supplyData().reduce((sum, month) => sum + month.supplier_count, 0);
  };

  return (
    <div class="min-h-screen bg-gray-50 py-8">
      <div class="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            📦 Supply Planning Dashboard
          </h1>
          <p class="text-gray-600">
            Plan your procurement with upcoming supply forecasts and price predictions
          </p>
        </div>

        {/* Filters */}
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Crop
              </label>
              <select
                value={selectedCrop()}
                onChange={(e) => {
                  setSelectedCrop(e.target.value);
                  loadData();
                }}
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <For each={popularCrops}>
                  {(crop) => <option value={crop}>{crop.charAt(0).toUpperCase() + crop.slice(1)}</option>}
                </For>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                State
              </label>
              <select
                value={selectedState()}
                onChange={(e) => {
                  setSelectedState(e.target.value);
                  loadData();
                }}
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <For each={states}>
                  {(state) => <option value={state}>{state}</option>}
                </For>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                District (Optional)
              </label>
              <input
                type="text"
                value={selectedDistrict()}
                onInput={(e) => setSelectedDistrict(e.target.value)}
                placeholder="Enter district"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Planning Horizon
              </label>
              <select
                value={monthsAhead()}
                onChange={(e) => {
                  setMonthsAhead(parseInt(e.target.value));
                  loadData();
                }}
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={1}>1 month</option>
                <option value={3}>3 months</option>
                <option value={6}>6 months</option>
              </select>
            </div>
          </div>

          <div class="mt-4 flex justify-end">
            <button
              onClick={exportToPDF}
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              📄 Export Report
            </button>
          </div>
        </div>

        {/* Loading State */}
        <Show when={loading()}>
          <div class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600">Loading supply planning data...</p>
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
        <Show when={!loading() && !error()}>
          {/* Summary Cards */}
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-sm font-medium text-gray-600">Total Supply</h3>
                <span class="text-2xl">📦</span>
              </div>
              <p class="text-3xl font-bold text-gray-900">
                {getTotalSupply().toLocaleString()}
              </p>
              <p class="text-sm mt-2 text-gray-600">
                kg over {monthsAhead()} months
              </p>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-sm font-medium text-gray-600">Avg Price</h3>
                <span class="text-2xl">💰</span>
              </div>
              <p class="text-3xl font-bold text-gray-900">
                ₹{getAvgPrice().toFixed(2)}
              </p>
              <p class="text-sm mt-2 text-gray-600">
                per kg (forecast)
              </p>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-sm font-medium text-gray-600">Suppliers</h3>
                <span class="text-2xl">👥</span>
              </div>
              <p class="text-3xl font-bold text-gray-900">
                {getTotalSuppliers()}
              </p>
              <p class="text-sm mt-2 text-gray-600">
                farmers available
              </p>
            </div>

            <Show when={priceForecast()}>
              <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-medium text-gray-600">Price Trend</h3>
                  <span class="text-2xl">
                    {priceForecast()!.trend === 'rising' ? '📈' : priceForecast()!.trend === 'falling' ? '📉' : '➡️'}
                  </span>
                </div>
                <p class="text-3xl font-bold text-gray-900 capitalize">
                  {priceForecast()!.trend}
                </p>
                <p class="text-sm mt-2 text-gray-600">
                  {(priceForecast()!.confidence_score * 100).toFixed(0)}% confidence
                </p>
              </div>
            </Show>
          </div>

          {/* Monthly Supply Breakdown */}
          <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">
              📅 Monthly Supply Forecast
            </h3>
            
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b-2 border-gray-200">
                    <th class="text-left py-3 px-4 font-medium text-gray-700">Month</th>
                    <th class="text-right py-3 px-4 font-medium text-gray-700">Quantity (kg)</th>
                    <th class="text-right py-3 px-4 font-medium text-gray-700">Avg Price (₹)</th>
                    <th class="text-center py-3 px-4 font-medium text-gray-700">Quality Distribution</th>
                    <th class="text-right py-3 px-4 font-medium text-gray-700">Suppliers</th>
                  </tr>
                </thead>
                <tbody>
                  <For each={supplyData()}>
                    {(month) => (
                      <tr class="border-b border-gray-100 hover:bg-gray-50">
                        <td class="py-4 px-4 font-medium text-gray-900">
                          {month.month}
                        </td>
                        <td class="py-4 px-4 text-right text-gray-900">
                          {month.expected_quantity.toLocaleString()}
                        </td>
                        <td class="py-4 px-4 text-right text-gray-900">
                          ₹{month.expected_avg_price.toFixed(2)}
                        </td>
                        <td class="py-4 px-4">
                          <div class="flex gap-2 justify-center">
                            <span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                              A: {month.quality_distribution['A'] || 0}%
                            </span>
                            <span class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                              B: {month.quality_distribution['B'] || 0}%
                            </span>
                            <span class="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">
                              C: {month.quality_distribution['C'] || 0}%
                            </span>
                          </div>
                        </td>
                        <td class="py-4 px-4 text-right text-gray-900">
                          {month.supplier_count}
                        </td>
                      </tr>
                    )}
                  </For>
                </tbody>
              </table>
            </div>
          </div>

          {/* Price Forecast */}
          <Show when={priceForecast()}>
            <div class="bg-white rounded-lg shadow-md p-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4">
                💰 30-Day Price Forecast
              </h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div class="space-y-4">
                    <div class="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
                      <span class="text-sm font-medium text-gray-700">Predicted Price</span>
                      <span class="text-2xl font-bold text-blue-600">
                        ₹{priceForecast()!.predicted_price.toFixed(2)}
                      </span>
                    </div>

                    <div class="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <span class="text-sm font-medium text-gray-700">Price Range</span>
                      <span class="text-lg font-bold text-gray-900">
                        ₹{priceForecast()!.price_range.min.toFixed(2)} - ₹{priceForecast()!.price_range.max.toFixed(2)}
                      </span>
                    </div>

                    <div class="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <span class="text-sm font-medium text-gray-700">Confidence</span>
                      <div class="flex items-center gap-2">
                        <div class="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            class="bg-green-600 h-2 rounded-full"
                            style={{ width: `${priceForecast()!.confidence_score * 100}%` }}
                          />
                        </div>
                        <span class="text-sm font-bold text-gray-900">
                          {(priceForecast()!.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    <div class="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <span class="text-sm font-medium text-gray-700">Trend</span>
                      <span class={`text-lg font-bold capitalize ${
                        priceForecast()!.trend === 'rising' ? 'text-red-600' :
                        priceForecast()!.trend === 'falling' ? 'text-green-600' :
                        'text-gray-600'
                      }`}>
                        {priceForecast()!.trend}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 class="text-sm font-medium text-gray-700 mb-3">Key Factors</h4>
                  <div class="space-y-2">
                    <For each={priceForecast()!.factors}>
                      {(factor) => (
                        <div class="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                          <span class="text-blue-600 mt-0.5">•</span>
                          <span class="text-sm text-gray-700">{factor}</span>
                        </div>
                      )}
                    </For>
                  </div>
                </div>
              </div>
            </div>
          </Show>
        </Show>
      </div>
    </div>
  );
};

export default SupplyPlanning;
