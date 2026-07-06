/**
 * Listing Grid Component
 * Display marketplace listings in a grid layout
 */

import { Component, For, Show } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import type { MarketplaceListing } from '../../services/marketplace.service';
import { SkeletonCard } from '../ui/SkeletonScreen';

interface ListingGridProps {
  listings: MarketplaceListing[];
  isLoading: boolean;
}

const ListingGrid: Component<ListingGridProps> = (props) => {
  const navigate = useNavigate();

  const formatCurrency = (amount?: number) => {
    if (!amount) return 'Price on request';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getQualityColor = (grade: string) => {
    switch (grade.toUpperCase()) {
      case 'A':
        return 'bg-green-100 text-green-800';
      case 'B':
        return 'bg-yellow-100 text-yellow-800';
      case 'C':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleListingClick = (listingId: string) => {
    navigate(`/marketplace/${listingId}`);
  };

  return (
    <div>
      <Show when={props.isLoading}>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <For each={Array(6).fill(0)}>
            {() => <SkeletonCard />}
          </For>
        </div>
      </Show>

      <Show when={!props.isLoading && props.listings.length === 0}>
        <div class="bg-white rounded-lg shadow p-8 text-center">
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
          <h3 class="mt-2 text-lg font-medium text-gray-900">No listings found</h3>
          <p class="mt-1 text-sm text-gray-500">
            Try adjusting your filters or check back later.
          </p>
        </div>
      </Show>

      <Show when={!props.isLoading && props.listings.length > 0}>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <For each={props.listings}>
            {(listing) => (
              <div
                onClick={() => handleListingClick(listing.id)}
                class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer overflow-hidden"
              >
                {/* Header */}
                <div class="bg-gradient-to-r from-green-500 to-green-600 p-4 text-white">
                  <h3 class="text-lg font-bold truncate">{listing.crop_type}</h3>
                  <p class="text-sm opacity-90">{listing.crop_variety}</p>
                </div>

                {/* Content */}
                <div class="p-4 space-y-3">
                  {/* Quantity and Quality */}
                  <div class="flex justify-between items-center">
                    <div>
                      <p class="text-xs text-gray-500">Quantity</p>
                      <p class="text-lg font-semibold text-gray-800">
                        {listing.estimated_quantity} {listing.quantity_unit}
                      </p>
                    </div>
                    <div>
                      <span class={`px-3 py-1 rounded-full text-xs font-semibold ${getQualityColor(listing.quality_grade)}`}>
                        Grade {listing.quality_grade}
                      </span>
                    </div>
                  </div>

                  {/* Price */}
                  <div>
                    <p class="text-xs text-gray-500">Price per {listing.quantity_unit}</p>
                    <p class="text-lg font-bold text-green-600">
                      {formatCurrency(listing.asking_price_per_unit)}
                    </p>
                    <Show when={listing.price_negotiable}>
                      <p class="text-xs text-gray-500">Negotiable</p>
                    </Show>
                  </div>

                  {/* Harvest Date */}
                  <div>
                    <p class="text-xs text-gray-500">Expected Harvest</p>
                    <p class="text-sm font-medium text-gray-800">
                      {formatDate(listing.expected_harvest_date)}
                    </p>
                  </div>

                  {/* Location */}
                  <div class="flex items-center text-sm text-gray-600">
                    <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span>{listing.location.district}, {listing.location.state}</span>
                  </div>

                  {/* Market Intelligence */}
                  <Show when={listing.market_intelligence.demand_score}>
                    <div class="pt-3 border-t border-gray-200">
                      <div class="flex justify-between text-xs">
                        <span class="text-gray-500">Market Demand</span>
                        <span class="font-semibold text-blue-600">
                          {(listing.market_intelligence.demand_score! * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </Show>

                  {/* Stats */}
                  <div class="flex justify-between text-xs text-gray-500 pt-2 border-t border-gray-200">
                    <span>{listing.view_count} views</span>
                    <span>{listing.interest_count} interested</span>
                  </div>
                </div>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default ListingGrid;
