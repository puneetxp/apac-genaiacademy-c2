import { Component, createSignal, Show, For, onMount } from 'solid-js';
import { marketIntelligenceService, TrendAnalysis, OpportunityScore, SupplyDemandGap } from '../../services/market-intelligence.service';

const MarketIntelligence: Component = () => {
  const [selectedCrop, setSelectedCrop] = createSignal('wheat');
  const [selectedState, setSelectedState] = createSignal('Punjab');
  const [selectedDistrict, setSelectedDistrict] = createSignal<string>('');
  const [timeRange, setTimeRange] = createSignal(90);
  
  const [trends, setTrends] = createSignal<TrendAnalysis | null>(null);
  const [opportunities, setOpportunities] = createSignal<OpportunityScore | null>(null);
  const [gaps, setGaps] = createSignal<SupplyDemandGap[]>([]);
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  const popularCrops = ['wheat', 'rice', 'cotton', 'sugarcane', 'maize', 'potato', 'onion', 'tomato'];
  const states = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka', 'Tamil Nadu'];

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load price trends
      const trendsData = await marketIntelligenceService.getPriceTrends(
        'crop',
        selectedCrop(),
        selectedState(),
        selectedDistrict() || undefined,
        timeRange()
      );
      setTrends(trendsData);

      // Load opportunity score
      const opportunityData = await marketIntelligenceService.getOpportunityScore(
        'crop',
        selectedCrop(),
        selectedState(),
        selectedDistrict() || undefined
      );
      setOpportunities(opportunityData);

      // Load supply-demand gaps
      const gapsData = await marketIntelligenceService.getSupplyDemandGaps(
        selectedState(),
        selectedDistrict() || undefined,
        'crop'
      );
      setGaps(gapsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load market data');
    } finally {
      setLoading(false);
    }
  };

  onMount(() => {
    loadData();
  });

  const exportData = () => {
    const data = {
      crop: selectedCrop(),
      state: selectedState(),
      district: selectedDistrict(),
      trends: trends(),
      opportunities: opportunities(),
      gaps: gaps(),
      exportedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `market-intelligence-${selectedCrop()}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'rising': return '📈';
      case 'falling': return '📉';
      default: return '➡️';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div class="min-h-screen bg-gray-50 py-8">
      <div class="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            🌾 Market Intelligence Dashboard
          </h1>
          <p class="text-gray-600">
            Real-time market insights and AI-powered predictions for farmers
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
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
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
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
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
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

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
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
                <option value={180}>Last 6 months</option>
                <option value={365}>Last year</option>
              </select>
            </div>
          </div>

          <div class="mt-4 flex justify-end">
            <button
              onClick={exportData}
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              📥 Export Data
            </button>
          </div>
        </div>

        {/* Loading State */}
        <Show when={loading()}>
          <div class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
            <p class="mt-4 text-gray-600">Loading market intelligence...</p>
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
          {/* Key Metrics */}
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Current Price */}
            <Show when={trends()}>
              <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-medium text-gray-600">Current Avg Price</h3>
                  <span class="text-2xl">{getTrendIcon(trends()!.trend_direction)}</span>
                </div>
                <p class="text-3xl font-bold text-gray-900">
                  ₹{trends()!.current_avg_price.toFixed(2)}
                </p>
                <p class={`text-sm mt-2 ${trends()!.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {trends()!.price_change_percent >= 0 ? '+' : ''}{trends()!.price_change_percent.toFixed(1)}% from {timeRange()} days ago
                </p>
              </div>
            </Show>

            {/* Opportunity Score */}
            <Show when={opportunities()}>
              <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-medium text-gray-600">Opportunity Score</h3>
                  <span class="text-2xl">🎯</span>
                </div>
                <p class={`text-3xl font-bold ${getScoreColor(opportunities()!.overall_score)}`}>
                  {opportunities()!.overall_score.toFixed(0)}/100
                </p>
                <p class="text-sm mt-2 text-gray-600">
                  {opportunities()!.recommendation}
                </p>
              </div>
            </Show>

            {/* Market Gaps */}
            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-sm font-medium text-gray-600">Supply-Demand Gaps</h3>
                <span class="text-2xl">⚖️</span>
              </div>
              <p class="text-3xl font-bold text-gray-900">
                {gaps().length}
              </p>
              <p class="text-sm mt-2 text-gray-600">
                Market opportunities identified
              </p>
            </div>
          </div>

          {/* Price Trend Chart */}
          <Show when={trends()}>
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4">
                📊 Price Trends - {selectedCrop().charAt(0).toUpperCase() + selectedCrop().slice(1)}
              </h3>
              
              <div class="space-y-2">
                <For each={trends()!.time_series.slice(-10)}>
                  {(point) => (
                    <div class="flex items-center gap-4">
                      <span class="text-sm text-gray-600 w-24">
                        {new Date(point.date).toLocaleDateString()}
                      </span>
                      <div class="flex-1 bg-gray-100 rounded-full h-8 relative">
                        <div
                          class="bg-green-500 h-8 rounded-full flex items-center justify-end px-3"
                          style={{ width: `${Math.min((point.avg_price / trends()!.current_avg_price) * 100, 100)}%` }}
                        >
                          <span class="text-sm font-medium text-white">
                            ₹{point.avg_price.toFixed(2)}
                          </span>
                        </div>
                      </div>
                      <span class="text-sm text-gray-500 w-20">
                        {point.transaction_count} txns
                      </span>
                    </div>
                  )}
                </For>
              </div>

              <div class="mt-4 grid grid-cols-3 gap-4 pt-4 border-t">
                <div>
                  <p class="text-sm text-gray-600">Volatility</p>
                  <p class="text-lg font-bold text-gray-900">{(trends()!.volatility * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Trend</p>
                  <p class="text-lg font-bold text-gray-900 capitalize">{trends()!.trend_direction}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Transactions</p>
                  <p class="text-lg font-bold text-gray-900">
                    {trends()!.time_series.reduce((sum, p) => sum + p.transaction_count, 0)}
                  </p>
                </div>
              </div>
            </div>
          </Show>

          {/* Opportunity Breakdown */}
          <Show when={opportunities()}>
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4">
                🎯 Opportunity Score Breakdown
              </h3>
              
              <div class="space-y-4">
                <div>
                  <div class="flex justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">Price Trend (30%)</span>
                    <span class="text-sm font-bold text-gray-900">
                      {opportunities()!.breakdown.price_trend_score.toFixed(0)}/100
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-green-600 h-2 rounded-full"
                      style={{ width: `${opportunities()!.breakdown.price_trend_score}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div class="flex justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">Demand Level (30%)</span>
                    <span class="text-sm font-bold text-gray-900">
                      {opportunities()!.breakdown.demand_score.toFixed(0)}/100
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${opportunities()!.breakdown.demand_score}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div class="flex justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">Supply Gap (20%)</span>
                    <span class="text-sm font-bold text-gray-900">
                      {opportunities()!.breakdown.supply_gap_score.toFixed(0)}/100
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-yellow-600 h-2 rounded-full"
                      style={{ width: `${opportunities()!.breakdown.supply_gap_score}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div class="flex justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">Profitability (20%)</span>
                    <span class="text-sm font-bold text-gray-900">
                      {opportunities()!.breakdown.profitability_score.toFixed(0)}/100
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-purple-600 h-2 rounded-full"
                      style={{ width: `${opportunities()!.breakdown.profitability_score}%` }}
                    />
                  </div>
                </div>
              </div>

              <div class="mt-4 p-4 bg-green-50 rounded-lg">
                <p class="text-sm font-medium text-green-900">
                  💡 Recommendation
                </p>
                <p class="text-sm text-green-700 mt-1">
                  {opportunities()!.recommendation}
                </p>
                <Show when={opportunities()!.confidence > 0}>
                  <p class="text-xs text-green-600 mt-2">
                    Confidence: {(opportunities()!.confidence * 100).toFixed(0)}%
                  </p>
                </Show>
              </div>
            </div>
          </Show>

          {/* Supply-Demand Gaps */}
          <Show when={gaps().length > 0}>
            <div class="bg-white rounded-lg shadow-md p-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4">
                ⚖️ Supply-Demand Gaps in {selectedState()}
              </h3>
              
              <div class="space-y-3">
                <For each={gaps()}>
                  {(gap) => (
                    <div class={`p-4 rounded-lg border-l-4 ${
                      gap.gap_type === 'shortage' ? 'bg-red-50 border-red-500' : 'bg-blue-50 border-blue-500'
                    }`}>
                      <div class="flex justify-between items-start">
                        <div>
                          <h4 class="font-bold text-gray-900 capitalize">
                            {gap.item_name}
                          </h4>
                          <p class="text-sm text-gray-600 mt-1">
                            {gap.opportunity_description}
                          </p>
                        </div>
                        <span class={`px-3 py-1 rounded-full text-xs font-medium ${
                          gap.severity === 'high' ? 'bg-red-100 text-red-800' :
                          gap.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {gap.severity.toUpperCase()}
                        </span>
                      </div>
                      
                      <div class="mt-3 grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p class="text-gray-600">Supply</p>
                          <p class="font-bold text-gray-900">{gap.supply_quantity.toFixed(0)} kg</p>
                        </div>
                        <div>
                          <p class="text-gray-600">Demand</p>
                          <p class="font-bold text-gray-900">{gap.demand_quantity.toFixed(0)} kg</p>
                        </div>
                        <div>
                          <p class="text-gray-600">Gap</p>
                          <p class={`font-bold ${gap.gap_type === 'shortage' ? 'text-red-600' : 'text-blue-600'}`}>
                            {gap.gap_type === 'shortage' ? '-' : '+'}{gap.gap_quantity.toFixed(0)} kg
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </For>
              </div>
            </div>
          </Show>
        </Show>
      </div>
    </div>
  );
};

export default MarketIntelligence;
