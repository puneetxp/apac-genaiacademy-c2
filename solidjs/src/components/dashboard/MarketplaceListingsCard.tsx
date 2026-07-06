/**
 * Marketplace Listings Card Component
 * Displays active marketplace listings
 */

import { Component, For, Show } from 'solid-js';
import { useNavigate } from '@solidjs/router';

interface MarketplaceListingsCardProps {
  listings: any[];
}

const MarketplaceListingsCard: Component<MarketplaceListingsCardProps> = (props) => {
  const navigate = useNavigate();

  const getQualityColor = (grade: string) => {
    switch (grade) {
      case 'A':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'B':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'C':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleViewListing = (listingId: string) => {
    navigate(`/marketplace/detail/${listingId}`);
  };

  return (
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-gray-800">
          My Marketplace Listings
        </h2>
        <button
          onClick={() => navigate('/marketplace')}
          class="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          View All →
        </button>
      </div>
      
      <Show
        when={props.listings && props.listings.length > 0}
        fallback={
          <div class="text-center py-8 text-gray-500">
            <div class="text-4xl mb-2">🛒</div>
            <p>No active listings</p>
            <p class="text-sm mt-1">Create a listing to connect with buyers</p>
          </div>
        }
      >
        <div class="space-y-3">
          <For each={props.listings.slice(0, 5)}>
            {(listing) => (
              <div 
                class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleViewListing(listing.id)}
              >
                <div class="flex justify-between items-start mb-2">
                  <div>
                    <h3 class="font-semibold text-gray-900">{listing.crop_type}</h3>
                    <Show when={listing.crop_variety}>
                      <p class="text-sm text-gray-600">{listing.crop_variety}</p>
                    </Show>
                  </div>
                  <span class={`px-2 py-1 rounded text-xs font-medium border ${getQualityColor(listing.quality_grade)}`}>
                    Grade {listing.quality_grade}
                  </span>
                </div>
                
                <div class="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span class="text-gray-500">Harvest Date:</span>
                    <p class="font-medium text-gray-900">
                      {formatDate(listing.expected_harvest_date)}
                    </p>
                  </div>
                  <div>
                    <span class="text-gray-500">Quantity:</span>
                    <p class="font-medium text-gray-900">
                      {listing.estimated_quantity} {listing.quantity_unit}
                    </p>
                  </div>
                  <Show when={listing.asking_price_per_unit}>
                    <div>
                      <span class="text-gray-500">Price:</span>
                      <p class="font-medium text-gray-900">
                        {formatCurrency(listing.asking_price_per_unit!)} / {listing.quantity_unit}
                      </p>
                    </div>
                  </Show>
                  <div>
                    <span class="text-gray-500">Interests:</span>
                    <p class="font-medium text-gray-900">
                      {listing.interest_count || 0} buyer(s)
                    </p>
                  </div>
                </div>
                
                <div class="mt-3 pt-3 border-t border-gray-200 flex justify-between items-center text-xs text-gray-500">
                  <span>👁️ {listing.view_count || 0} views</span>
                  <span>Listed {formatDate(listing.listed_at)}</span>
                </div>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default MarketplaceListingsCard;
