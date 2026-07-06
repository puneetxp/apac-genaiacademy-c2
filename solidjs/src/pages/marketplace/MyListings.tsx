import { Component, createResource, Show, For } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import apiClient from '../../lib/api-client';

const fetchMyListings = async () => {
  const response = await apiClient.get('/api/v1/marketplace/listings/my-listings', {
    cache: false,
    requiresAuth: true
  });
  return response.data.listings || [];
};

const MyListingsPage: Component = () => {
  const navigate = useNavigate();
  const [listings] = createResource(fetchMyListings);

  return (
    <div class="min-h-screen bg-gray-50 flex flex-col">
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <span>📝</span> My Listings
          </h1>
          <button
            onClick={() => navigate('/dashboard')}
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </header>

      <main class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        <Show when={listings.loading}>
          <div class="text-center py-12">
            <p class="text-gray-600">Loading your listings...</p>
          </div>
        </Show>

        <Show when={listings.error}>
          <div class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
            Failed to load listings. Please try again later.
          </div>
        </Show>

        <Show when={!listings.loading && listings()?.length === 0}>
          <div class="text-center py-12 bg-white rounded-lg shadow">
            <p class="text-gray-600 mb-4">You don't have any marketplace listings yet.</p>
            <button
              onClick={() => navigate('/crops/plan')}
              class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md shadow-sm transition-colors"
            >
              Start Selling
            </button>
          </div>
        </Show>

        <Show when={listings()?.length > 0}>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <For each={listings()}>
              {(listing: any) => (
                <div class="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6 flex flex-col h-full border border-gray-100">
                  <div class="flex justify-between items-start mb-4">
                    <div>
                      <h3 class="font-bold text-lg text-gray-900">{listing.title || listing.crop_type}</h3>
                      <p class="text-sm text-gray-500">{listing.crop_variety}</p>
                    </div>
                    <span class={`text-[10px] font-bold px-2 py-1 uppercase rounded-full ${
                      listing.status === 'active' ? 'bg-green-100 text-green-800' :
                      listing.status === 'sold' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {listing.status}
                    </span>
                  </div>

                  <div class="space-y-2 flex-grow">
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-500">Quantity</span>
                      <span class="font-medium">{listing.estimated_quantity} {listing.quantity_unit}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-500">Price (per unit)</span>
                      <span class="font-medium text-green-700">₹{listing.asking_price_per_unit || 'Negotiable'}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-500">Location</span>
                      <span class="font-medium">{listing.location.district}, {listing.location.state}</span>
                    </div>
                  </div>

                  <div class="mt-4 pt-4 border-t flex justify-between items-center text-xs text-gray-500">
                    <div>👀 {listing.view_count || 0} views</div>
                    <div class="text-orange-600 font-medium">{listing.interest_count || 0} inquiries</div>
                  </div>
                  
                  <button 
                    onClick={() => navigate(`/marketplace/${listing.id}`)}
                    class="mt-4 w-full py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 border border-gray-200 rounded text-sm font-medium transition-colors"
                  >
                    View Details
                  </button>
                </div>
              )}
            </For>
          </div>
        </Show>
      </main>
    </div>
  );
};

export default MyListingsPage;
