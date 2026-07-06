/**
 * Listing Detail Component
 * Display detailed information about a marketplace listing
 */

import { Component, Show } from 'solid-js';

interface ListingDetailProps {
  listing: any;
  onContactFarmer: () => void;
}

const ListingDetail: Component<ListingDetailProps> = (props) => {
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
      month: 'long',
      day: 'numeric',
    });
  };

  const getQualityColor = (grade: string) => {
    switch (grade.toUpperCase()) {
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

  return (
    <div class="space-y-6">
      {/* Header */}
      <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
        <h1 class="text-3xl font-bold mb-2">{props.listing.crop_type}</h1>
        <p class="text-lg opacity-90">{props.listing.crop_variety}</p>
        <div class="mt-4 flex items-center gap-4">
          <span class={`px-4 py-2 rounded-full text-sm font-semibold border-2 ${getQualityColor(props.listing.quality_grade)}`}>
            Grade {props.listing.quality_grade}
          </span>
          <Show when={props.listing.quality_confidence}>
            <span class="text-sm opacity-90">
              {(props.listing.quality_confidence * 100).toFixed(0)}% confidence
            </span>
          </Show>
        </div>
      </div>

      {/* Main Details */}
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">Listing Details</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Quantity */}
          <div>
            <p class="text-sm text-gray-500 mb-1">Available Quantity</p>
            <p class="text-2xl font-bold text-gray-800">
              {props.listing.estimated_quantity} {props.listing.quantity_unit}
            </p>
          </div>

          {/* Price */}
          <div>
            <p class="text-sm text-gray-500 mb-1">Price per {props.listing.quantity_unit}</p>
            <p class="text-2xl font-bold text-green-600">
              {formatCurrency(props.listing.asking_price_per_unit)}
            </p>
            <Show when={props.listing.price_negotiable}>
              <p class="text-sm text-gray-600 mt-1">Negotiable</p>
            </Show>
          </div>

          {/* Harvest Date */}
          <div>
            <p class="text-sm text-gray-500 mb-1">Expected Harvest Date</p>
            <p class="text-lg font-semibold text-gray-800">
              {formatDate(props.listing.expected_harvest_date)}
            </p>
          </div>

          {/* Harvest Window */}
          <Show when={props.listing.harvest_window?.start && props.listing.harvest_window?.end}>
            <div>
              <p class="text-sm text-gray-500 mb-1">Harvest Window</p>
              <p class="text-sm text-gray-800">
                {formatDate(props.listing.harvest_window.start)} - {formatDate(props.listing.harvest_window.end)}
              </p>
            </div>
          </Show>
        </div>

        {/* Description */}
        <Show when={props.listing.description}>
          <div class="mt-6 pt-6 border-t border-gray-200">
            <p class="text-sm text-gray-500 mb-2">Description</p>
            <p class="text-gray-700">{props.listing.description}</p>
          </div>
        </Show>
      </div>

      {/* Location */}
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">Location</h2>
        <div class="flex items-start gap-3">
          <svg class="w-6 h-6 text-green-600 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <div>
            <p class="text-lg font-semibold text-gray-800">{props.listing.location.district}</p>
            <p class="text-gray-600">{props.listing.location.state}</p>
            <Show when={props.listing.location.block}>
              <p class="text-sm text-gray-500">{props.listing.location.block}</p>
            </Show>
          </div>
        </div>
      </div>

      {/* Market Intelligence */}
      <Show when={props.listing.market_intelligence}>
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">Market Intelligence</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Show when={props.listing.market_intelligence.demand_score}>
              <div class="bg-blue-50 rounded-lg p-4">
                <p class="text-sm text-blue-600 mb-1">Market Demand</p>
                <p class="text-2xl font-bold text-blue-800">
                  {(props.listing.market_intelligence.demand_score * 100).toFixed(0)}%
                </p>
              </div>
            </Show>

            <Show when={props.listing.market_intelligence.price_trend}>
              <div class="bg-purple-50 rounded-lg p-4">
                <p class="text-sm text-purple-600 mb-1">Price Trend</p>
                <p class="text-lg font-semibold text-purple-800 capitalize">
                  {props.listing.market_intelligence.price_trend}
                </p>
              </div>
            </Show>

            <Show when={props.listing.market_intelligence.yoy_growth}>
              <div class="bg-green-50 rounded-lg p-4">
                <p class="text-sm text-green-600 mb-1">YoY Growth</p>
                <p class="text-2xl font-bold text-green-800">
                  {props.listing.market_intelligence.yoy_growth > 0 ? '+' : ''}
                  {props.listing.market_intelligence.yoy_growth.toFixed(1)}%
                </p>
              </div>
            </Show>
          </div>
        </div>
      </Show>

      {/* Production Predictions */}
      <Show when={props.listing.production_predictions}>
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">Production Predictions</h2>
          <div class="space-y-3">
            <Show when={props.listing.production_predictions.expected_yield}>
              <div class="flex justify-between">
                <span class="text-gray-600">Expected Yield</span>
                <span class="font-semibold text-gray-800">
                  {props.listing.production_predictions.expected_yield}
                </span>
              </div>
            </Show>
            <Show when={props.listing.production_predictions.confidence_score}>
              <div class="flex justify-between">
                <span class="text-gray-600">Confidence Score</span>
                <span class="font-semibold text-gray-800">
                  {(props.listing.production_predictions.confidence_score * 100).toFixed(0)}%
                </span>
              </div>
            </Show>
          </div>
        </div>
      </Show>

      {/* Contact Farmer */}
      <Show when={props.listing.contact?.enabled}>
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">Contact Farmer</h2>
          <p class="text-gray-600 mb-4">
            Interested in this listing? Contact the farmer directly to discuss details and arrange purchase.
          </p>
          <button
            onClick={props.onContactFarmer}
            class="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-md transition-colors"
          >
            Express Interest & Contact Farmer
          </button>
        </div>
      </Show>

      {/* Stats */}
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="flex justify-between text-sm text-gray-600">
          <span>{props.listing.view_count} views</span>
          <span>{props.listing.interest_count} buyers interested</span>
          <span>Listed {formatDate(props.listing.listed_at)}</span>
        </div>
      </div>
    </div>
  );
};

export default ListingDetail;
