/**
 * Marketplace Browse Page
 * Browse and search marketplace listings
 */

import { Component, onMount, Show, lazy, Suspense } from 'solid-js';
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
} from '../../stores/marketplace.store';

// Lazy load marketplace components
const ListingGrid = lazy(() => import('../../components/marketplace/ListingGrid'));
const SearchFilters = lazy(() => import('../../components/marketplace/SearchFilters'));

const MarketplaceBrowsePage: Component = () => {
  const navigate = useNavigate();

  onMount(() => {
    loadListings();
  });

  const handleFilterChange = async (newFilters: any) => {
    await updateFilters(newFilters);
  };

  const handleClearFilters = async () => {
    await clearFilters();
  };

  const handlePageChange = async (page: number) => {
    await loadListings(page, pagination()?.page_size || 20);
  };

  return (
    <div class="min-h-screen bg-gray-50">
      {/* Header */}
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Marketplace</h1>
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

        {/* Search and Filters */}
        <div class="mb-6">
          <Suspense fallback={<div class="bg-white rounded-lg shadow-md p-6 animate-pulse h-32" />}>
            <SearchFilters
              filters={filters()}
              onFilterChange={handleFilterChange}
              onClearFilters={handleClearFilters}
            />
          </Suspense>
        </div>

        {/* Results Count */}
        <Show when={pagination()}>
          <div class="mb-4 text-sm text-gray-600">
            Showing {((pagination()!.page - 1) * pagination()!.page_size) + 1} - {Math.min(pagination()!.page * pagination()!.page_size, pagination()!.total_items)} of {pagination()!.total_items} listings
          </div>
        </Show>

        {/* Listings Grid */}
        <Suspense fallback={<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(() => (
            <div class="bg-white rounded-lg shadow-md p-6 animate-pulse h-64" />
          ))}
        </div>}>
          <ListingGrid listings={listings()} isLoading={isLoading()} />
        </Suspense>

        {/* Pagination */}
        <Show when={pagination() && pagination()!.total_pages > 1}>
          <div class="mt-8 flex justify-center items-center gap-2">
            <button
              onClick={() => handlePageChange(pagination()!.page - 1)}
              disabled={!pagination()!.has_prev}
              class="px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            <span class="px-4 py-2 text-sm text-gray-700">
              Page {pagination()!.page} of {pagination()!.total_pages}
            </span>

            <button
              onClick={() => handlePageChange(pagination()!.page + 1)}
              disabled={!pagination()!.has_next}
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

export default MarketplaceBrowsePage;
