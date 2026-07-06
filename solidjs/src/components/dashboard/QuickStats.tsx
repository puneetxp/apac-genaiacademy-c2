/**
 * Quick Stats Component
 * Displays key metrics at a glance
 */

import { Component } from 'solid-js';
import { A } from '@solidjs/router';
import type { DashboardStats } from '../../services/dashboard.service';

interface QuickStatsProps {
  stats: DashboardStats;
}

const QuickStats: Component<QuickStatsProps> = (props) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      {/* Total Profit Potential */}
      <A
        href="/strategy/results"
        class="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-4 text-white shadow-lg focus:outline-none focus:ring-4 focus:ring-green-200 transition-transform hover:-translate-y-0.5"
      >
        <div class="text-sm opacity-90 mb-1">Profit Potential</div>
        <div class="text-2xl font-bold">{formatCurrency(props.stats?.total_profit_potential || 0)}</div>
        <div class="text-xs opacity-75 mt-1">Annual estimate</div>
      </A>

      {/* Active Crops */}
      <A
        href="/crops/my-crops"
        class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-4 text-white shadow-lg focus:outline-none focus:ring-4 focus:ring-blue-200 transition-transform hover:-translate-y-0.5"
      >
        <div class="text-sm opacity-90 mb-1">Active Crops</div>
        <div class="text-2xl font-bold">{props.stats?.active_crops || 0}</div>
        <div class="text-xs opacity-75 mt-1">Currently growing</div>
      </A>

      {/* Active Listings */}
      <A
        href="/marketplace/my-listings"
        class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-4 text-white shadow-lg focus:outline-none focus:ring-4 focus:ring-purple-200 transition-transform hover:-translate-y-0.5"
      >
        <div class="text-sm opacity-90 mb-1">Active Listings</div>
        <div class="text-2xl font-bold">{props.stats?.active_listings || 0}</div>
        <div class="text-xs opacity-75 mt-1">In marketplace</div>
      </A>

      {/* Buyer Interests */}
      <A
        href="/marketplace/buyer-dashboard"
        class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-4 text-white shadow-lg focus:outline-none focus:ring-4 focus:ring-orange-200 transition-transform hover:-translate-y-0.5"
      >
        <div class="text-sm opacity-90 mb-1">Buyer Interests</div>
        <div class="text-2xl font-bold">{props.stats?.buyer_interests || 0}</div>
        <div class="text-xs opacity-75 mt-1">Pending connections</div>
      </A>

      {/* Pending Tasks */}
      <A
        href="/strategy/request"
        class="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-4 text-white shadow-lg focus:outline-none focus:ring-4 focus:ring-red-200 transition-transform hover:-translate-y-0.5"
      >
        <div class="text-sm opacity-90 mb-1">Pending Tasks</div>
        <div class="text-2xl font-bold">{props.stats?.pending_tasks || 0}</div>
        <div class="text-xs opacity-75 mt-1">Action items</div>
      </A>
    </div>
  );
};

export default QuickStats;
