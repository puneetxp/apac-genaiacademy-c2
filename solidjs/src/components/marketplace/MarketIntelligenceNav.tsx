import { Component } from 'solid-js';
import { A } from '@solidjs/router';

const MarketIntelligenceNav: Component = () => {
  return (
    <div class="bg-white rounded-lg shadow-md p-4 mb-6">
      <h3 class="text-sm font-medium text-gray-700 mb-3">Market Intelligence</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <A
          href="/marketplace/intelligence"
          class="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
        >
          <span class="text-2xl">🌾</span>
          <div>
            <p class="font-medium text-gray-900">Farmer Dashboard</p>
            <p class="text-xs text-gray-600">Market insights & opportunities</p>
          </div>
        </A>

        <A
          href="/marketplace/supply-planning"
          class="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
        >
          <span class="text-2xl">📦</span>
          <div>
            <p class="font-medium text-gray-900">Buyer Planning</p>
            <p class="text-xs text-gray-600">Supply forecasts & pricing</p>
          </div>
        </A>

        <A
          href="/admin/analytics"
          class="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors"
        >
          <span class="text-2xl">📊</span>
          <div>
            <p class="font-medium text-gray-900">Platform Analytics</p>
            <p class="text-xs text-gray-600">Transaction & user metrics</p>
          </div>
        </A>
      </div>
    </div>
  );
};

export default MarketIntelligenceNav;
