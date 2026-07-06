/**
 * Buyer Interests Card Component
 * Displays recent buyer interests and connections
 */

import { Component, For, Show } from 'solid-js';
import type { BuyerInterest } from '../../services/dashboard.service';

interface BuyerInterestsCardProps {
  interests: BuyerInterest[];
}

const BuyerInterestsCard: Component<BuyerInterestsCardProps> = (props) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'contacted':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return '⏳';
      case 'contacted':
        return '📞';
      case 'completed':
        return '✅';
      case 'rejected':
        return '❌';
      default:
        return '📋';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-IN', {
      month: 'short',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">
        Recent Buyer Interests
      </h2>
      
      <Show
        when={props.interests && props.interests.length > 0}
        fallback={
          <div class="text-center py-8 text-gray-500">
            <div class="text-4xl mb-2">🤝</div>
            <p>No buyer interests yet</p>
            <p class="text-sm mt-1">List your crops in the marketplace</p>
          </div>
        }
      >
        <div class="space-y-3">
          <For each={props.interests}>
            {(interest) => (
              <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-2">
                  <div class="flex items-start gap-2">
                    <div class="text-2xl">{getStatusIcon(interest.status)}</div>
                    <div>
                      <h3 class="font-semibold text-gray-900">
                        {interest.buyer_name || 'Anonymous Buyer'}
                      </h3>
                      <Show when={interest.buyer_company}>
                        <p class="text-sm text-gray-600">{interest.buyer_company}</p>
                      </Show>
                    </div>
                  </div>
                  <span class={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(interest.status)}`}>
                    {interest.status}
                  </span>
                </div>
                
                <div class="ml-10 space-y-1 text-sm">
                  <p class="text-gray-700">
                    <span class="font-medium">Crop:</span> {interest.crop_type}
                  </p>
                  <p class="text-gray-700">
                    <span class="font-medium">Quantity:</span> {interest.quantity_interested} quintals
                  </p>
                  <Show when={interest.preferred_price}>
                    <p class="text-gray-700">
                      <span class="font-medium">Preferred Price:</span> {formatCurrency(interest.preferred_price!)}
                    </p>
                  </Show>
                  <p class="text-gray-500 text-xs mt-2">
                    {formatDate(interest.created_at)}
                  </p>
                </div>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default BuyerInterestsCard;
