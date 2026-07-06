/**
 * Livestock Marketplace Browse Page
 * Browse and search livestock marketplace listings
 */

import { Component, onMount, Show, For } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import {
  listings,
  pagination,
  filters,
  isLoading,
  error,
  loadListings,
  updateFilters,
  clearFilters,
} from '../../stores/livestock-marketplace.store';

const LivestockMarketplaceBrowsePage: Component = () => {
  const navigate = useNavigate();

  onMount(() => {
    loadListings();
  });

  const handleFilterChange = async (filterKey: string, value: any) => {
    const newFilters = { ...filters(), [filterKey]: value };
    await updateFilters(newFilters);
  };

  const handleClearFilters = async () => {
    await clearFilters();
  };

  const handlePageChange = async (page: number) => {
    await loadListings(page, pagination()?.page_size || 20);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return 'text-green-600 bg-green-100';
      case 'good':
        return 'text-blue-600 bg-blue-100';
      case 'fair':
        return 'text-yellow-600 bg-yellow-100';
      case 'poor':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div class="min-h-screen bg-gray-50">
      {/* Header */}
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Livestock Marketplace</h1>
          <button
            onClick={() => navigate('/dashboard')}
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Show when={error()}>
          <div class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error()}
          </div>
        </Show>

        {/* Filters */}
        <div class="mb-6 bg-white rounded-lg shadow-md p-6">
          <h2 class="text-lg font-semibold mb-4">Filters</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Species</label>
              <select
                value={filters().species || ''}
                onChange={(e) => handleFilterChange('species', e.target.value || undefined)}
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">All Species</option>
                <option value="cattle">Cattle</option>
                <option value="buffalo">Buffalo</option>
                <option value="goat">Goat</option>
                <option value="poultry">Poultry</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Listing Type</label>
              <select
                value={filters().listing_type || ''}
                onChange={(e) => handleFilterChange('listing_type', e.target.value || undefined)}
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">All Types</option>
                <option value="sale">For Sale</option>
                <option value="breeding_service">Breeding Service</option>
                <option value="milk_production">Milk Production</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Health Status</label>
              <select
                value={filters().health_status || ''}
                onChange={(e) => handleFilterChange('health_status', e.target.value || undefined)}
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">All Status</option>
                <option value="excellent">Excellent</option>
                <option value="good">Good</option>
                <option value="fair">Fair</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Min Price (₹)</label>
              <input
                type="number"
                value={filters().min_price || ''}
                onChange={(e) => handleFilterChange('min_price', e.target.value ? Number(e.target.value) : undefined)}
                placeholder="Min price"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Max Price (₹)</label>
              <input
                type="number"
                value={filters().max_price || ''}
                onChange={(e) => handleFilterChange('max_price', e.target.value ? Number(e.target.value) : undefined)}
                placeholder="Max price"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Min ROI (%)</label>
              <input
                type="number"
                value={filters().min_roi || ''}
                onChange={(e) => handleFilterChange('min_roi', e.target.value ? Number(e.target.value) : undefined)}
                placeholder="Min ROI"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>

          <div class="mt-4 flex justify-end">
            <button
              onClick={handleClearFilters}
              class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Results Count */}
        <Show when={pagination()}>
          <div class="mb-4 text-sm text-gray-600">
            Showing {((pagination()!.page - 1) * pagination()!.page_size) + 1} - {Math.min(pagination()!.page * pagination()!.page_size, pagination()!.total_items)} of {pagination()!.total_items} listings
          </div>
        </Show>

        {/* Listings Grid */}
        <Show
          when={!isLoading()}
          fallback={
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <For each={[1, 2, 3, 4, 5, 6]}>
                {() => <div class="bg-white rounded-lg shadow-md p-6 animate-pulse h-64" />}
              </For>
            </div>
          }
        >
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <For each={listings()}>
              {(listing) => (
                <div
                  class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => navigate(`/livestock-marketplace/${listing.id}`)}
                >
                  <div class="p-6">
                    {/* Listing Type Badge */}
                    <div class="flex justify-between items-start mb-3">
                      <span class="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                        {listing.listing_type.replace('_', ' ').toUpperCase()}
                      </span>
                      <span class={`px-2 py-1 text-xs font-semibold rounded ${getHealthStatusColor(listing.health_status)}`}>
                        {listing.health_status}
                      </span>
                    </div>

                    {/* Price */}
                    <div class="mb-3">
                      <div class="text-2xl font-bold text-gray-900">{formatCurrency(listing.asking_price)}</div>
                    </div>

                    {/* Details */}
                    <div class="space-y-2 text-sm text-gray-600">
                      <div class="flex justify-between">
                        <span>Age:</span>
                        <span class="font-medium">{listing.current_age_months} months</span>
                      </div>
                      <Show when={listing.current_weight_kg}>
                        <div class="flex justify-between">
                          <span>Weight:</span>
                          <span class="font-medium">{listing.current_weight_kg} kg</span>
                        </div>
                      </Show>
                      <Show when={listing.milk_production_liters_per_day}>
                        <div class="flex justify-between">
                          <span>Milk/day:</span>
                          <span class="font-medium">{listing.milk_production_liters_per_day} L</span>
                        </div>
                      </Show>
                    </div>

                    {/* ROI Metrics */}
                    <Show when={listing.current_roi_percentage !== null}>
                      <div class="mt-4 pt-4 border-t border-gray-200">
                        <div class="flex justify-between items-center">
                          <span class="text-sm text-gray-600">ROI:</span>
                          <span class={`text-sm font-bold ${listing.current_roi_percentage! >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {listing.current_roi_percentage!.toFixed(1)}%
                          </span>
                        </div>
                        <Show when={listing.projected_annual_profit}>
                          <div class="flex justify-between items-center mt-1">
                            <span class="text-sm text-gray-600">Projected Profit:</span>
                            <span class="text-sm font-medium text-gray-900">
                              {formatCurrency(listing.projected_annual_profit!)}/year
                            </span>
                          </div>
                        </Show>
                      </div>
                    </Show>

                    {/* Location */}
                    <div class="mt-4 pt-4 border-t border-gray-200">
                      <div class="flex items-center text-sm text-gray-600">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {listing.location_district}, {listing.location_state}
                      </div>
                    </div>

                    {/* View Count */}
                    <div class="mt-2 text-xs text-gray-500">
                      {listing.views_count} views
                    </div>
                  </div>
                </div>
              )}
            </For>
          </div>
        </Show>

        {/* Pagination */}
        <Show when={pagination() && pagination()!.total_pages > 1}>
          <div class="mt-8 flex justify-center items-center gap-2">
            <button
              onClick={() => handlePageChange(pagination()!.page - 1)}
              disabled={pagination()!.page === 1}
              class="px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            <span class="px-4 py-2 text-sm text-gray-700">
              Page {pagination()!.page} of {pagination()!.total_pages}
            </span>

            <button
              onClick={() => handlePageChange(pagination()!.page + 1)}
              disabled={pagination()!.page === pagination()!.total_pages}
              class="px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </Show>
      </main>
    </div>
  );
};

export default LivestockMarketplaceBrowsePage;
