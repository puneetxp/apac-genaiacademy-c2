/**
 * Marketplace Browse Page with Infinite Scroll
 * Browse marketplace listings with progressive loading
 */

import { Component, onMount, Show, lazy, Suspense, createSignal, For } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { createInfiniteScroll, createIntersectionObserver } from '../../utils/infiniteScroll';
import { prefetchOnHover, prefetchRelatedListings } from '../../utils/prefetch';
import { SkeletonLoader, ListingCardSkeleton } from '../../components/ui/SkeletonLoader';
import { MarketplaceService } from '../../services/marketplace.service';
import type { BrowseListing as MarketplaceListing } from '../../services/marketplace.service';

// Lazy load marketplace components
const SearchFilters = lazy(() => import('../../components/marketplace/SearchFilters'));

const MarketplaceBrowseInfinitePage: Component = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = createSignal<any>({});
  const [sentinelRef, setSentinelRef] = createSignal<HTMLDivElement | null>(null);

  // Infinite scroll setup
  const {
    items: listings,
    loading,
    hasMore,
    error,
    loadMore,
    reset,
  } = createInfiniteScroll<MarketplaceListing>(
    async (page, pageSize) => {
      const response = await MarketplaceService.searchListings({
        ...filters(),
        page,
        page_size: pageSize,
      });
      return response.items || [];
    },
    { pageSize: 20 }
  );

  // Setup intersection observer for infinite scroll
  createIntersectionObserver(
    sentinelRef,
    () => {
      if (!loading() && hasMore()) {
        loadMore();
      }
    },
    { rootMargin: '100px' }
  );

  const handleFilterChange = async (newFilters: any) => {
    setFilters(newFilters);
    reset();
  };

  const handleClearFilters = async () => {
    setFilters({});
    reset();
  };

  const handleListingHover = (listingId: number) => {
    // Prefetch related listings when user hovers over a listing
    prefetchRelatedListings(listingId, (id) =>
      MarketplaceService.getRelatedListings(id)
    );
  };

  const handleListingClick = (listingId: number) => {
    navigate(`/marketplace/${listingId}`);
  };

  return (
    <div class="min-h-screen bg-gray-50">
      {/* Header */}
      <header class="bg-white shadow sticky top-0 z-10">
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
          <Suspense fallback={<SkeletonLoader type="card" count={1} />}>
            <SearchFilters
              filters={filters()}
              onFilterChange={handleFilterChange}
              onClearFilters={handleClearFilters}
            />
          </Suspense>
        </div>

        {/* Results Count */}
        <Show when={listings().length > 0}>
          <div class="mb-4 text-sm text-gray-600">
            Showing {listings().length} listings
            <Show when={hasMore()}>
              <span class="text-gray-400"> (scroll for more)</span>
            </Show>
          </div>
        </Show>

        {/* Listings Grid with Infinite Scroll */}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <For each={listings()}>
            {(listing) => (
              <div
                class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleListingClick(Number(listing.id))}
                onMouseEnter={() => handleListingHover(Number(listing.id))}
              >
                <h3 class="text-lg font-semibold text-gray-900 mb-2">
                  {listing.crop_type}
                </h3>
                <div class="space-y-2 text-sm text-gray-600">
                  <div class="flex justify-between">
                    <span>Variety:</span>
                    <span class="font-medium">{listing.variety}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Quantity:</span>
                    <span class="font-medium">{listing.estimated_quantity} kg</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Quality:</span>
                    <span class="font-medium">{listing.quality_grade}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Harvest Date:</span>
                    <span class="font-medium">
                      {new Date(listing.expected_harvest_date).toLocaleDateString()}
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span>Location:</span>
                    <span class="font-medium">{listing.district}, {listing.state}</span>
                  </div>
                </div>
                <div class="mt-4 pt-4 border-t border-gray-200">
                  <button
                    class="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleListingClick(Number(listing.id));
                    }}
                  >
                    View Details
                  </button>
                </div>
              </div>
            )}
          </For>

          {/* Loading Skeletons */}
          <Show when={loading()}>
            <For each={[1, 2, 3]}>
              {() => <ListingCardSkeleton />}
            </For>
          </Show>
        </div>

        {/* Empty State */}
        <Show when={!loading() && listings().length === 0}>
          <div class="text-center py-12">
            <svg
              class="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
              />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No listings found</h3>
            <p class="mt-1 text-sm text-gray-500">
              Try adjusting your filters or check back later.
            </p>
          </div>
        </Show>

        {/* Intersection Observer Sentinel */}
        <div ref={setSentinelRef} class="h-4" />

        {/* End of Results Message */}
        <Show when={!hasMore() && listings().length > 0}>
          <div class="text-center py-8 text-sm text-gray-500">
            You've reached the end of the listings
          </div>
        </Show>
      </main>
    </div>
  );
};

export default MarketplaceBrowseInfinitePage;
