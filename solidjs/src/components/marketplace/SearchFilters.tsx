/**
 * Search Filters Component
 * Marketplace search and filter controls
 */

import { Component, createSignal, For } from 'solid-js';
import type { ListingFilters } from '../../services/marketplace.service';
import { INDIAN_STATES } from '../../services/farm.service';

interface SearchFiltersProps {
  filters: ListingFilters;
  onFilterChange: (filters: ListingFilters) => void;
  onClearFilters: () => void;
}

const QUALITY_GRADES = ['A', 'B', 'C'];
const SORT_OPTIONS = [
  { value: 'harvest_date', label: 'Harvest Date' },
  { value: 'quantity', label: 'Quantity' },
  { value: 'quality_grade', label: 'Quality Grade' },
  { value: 'price', label: 'Price' },
];

const SearchFilters: Component<SearchFiltersProps> = (props) => {
  const [localFilters, setLocalFilters] = createSignal<ListingFilters>(props.filters);
  const [isExpanded, setIsExpanded] = createSignal(false);

  const updateFilter = (key: keyof ListingFilters, value: any) => {
    const updated = { ...localFilters(), [key]: value || undefined };
    setLocalFilters(updated);
  };

  const handleApplyFilters = () => {
    props.onFilterChange(localFilters());
    setIsExpanded(false);
  };

  const handleClearFilters = () => {
    setLocalFilters({});
    props.onClearFilters();
    setIsExpanded(false);
  };

  return (
    <div class="bg-white rounded-lg shadow-md p-4">
      {/* Search Bar */}
      <div class="flex gap-2 mb-4">
        <input
          type="text"
          value={localFilters().crop_type || ''}
          onInput={(e) => updateFilter('crop_type', e.currentTarget.value)}
          placeholder="Search by crop type..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <button
          onClick={handleApplyFilters}
          class="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
        >
          Search
        </button>
      </div>

      {/* Toggle Advanced Filters */}
      <button
        onClick={() => setIsExpanded(!isExpanded())}
        class="text-sm text-green-600 hover:text-green-700 font-medium flex items-center gap-1"
      >
        {isExpanded() ? '▼' : '▶'} Advanced Filters
      </button>

      {/* Advanced Filters */}
      <div class={`mt-4 space-y-4 ${isExpanded() ? 'block' : 'hidden'}`}>
        {/* Location Filters */}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              State
            </label>
            <select
              value={localFilters().state || ''}
              onChange={(e) => updateFilter('state', e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">All States</option>
              <For each={INDIAN_STATES}>
                {(state) => <option value={state}>{state}</option>}
              </For>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              District
            </label>
            <input
              type="text"
              value={localFilters().district || ''}
              onInput={(e) => updateFilter('district', e.currentTarget.value)}
              placeholder="Enter district"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Quantity Range */}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Min Quantity (quintals)
            </label>
            <input
              type="number"
              value={localFilters().min_quantity || ''}
              onInput={(e) => updateFilter('min_quantity', parseFloat(e.currentTarget.value) || undefined)}
              placeholder="Min"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Max Quantity (quintals)
            </label>
            <input
              type="number"
              value={localFilters().max_quantity || ''}
              onInput={(e) => updateFilter('max_quantity', parseFloat(e.currentTarget.value) || undefined)}
              placeholder="Max"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Harvest Date Range */}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Harvest From
            </label>
            <input
              type="date"
              value={localFilters().harvest_from || ''}
              onInput={(e) => updateFilter('harvest_from', e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Harvest To
            </label>
            <input
              type="date"
              value={localFilters().harvest_to || ''}
              onInput={(e) => updateFilter('harvest_to', e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Quality Grade */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Quality Grade
          </label>
          <select
            value={localFilters().quality_grade || ''}
            onChange={(e) => updateFilter('quality_grade', e.currentTarget.value)}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">All Grades</option>
            <For each={QUALITY_GRADES}>
              {(grade) => <option value={grade}>Grade {grade}</option>}
            </For>
          </select>
        </div>

        {/* Price Range */}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Min Price (₹)
            </label>
            <input
              type="number"
              value={localFilters().min_price || ''}
              onInput={(e) => updateFilter('min_price', parseFloat(e.currentTarget.value) || undefined)}
              placeholder="Min"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Max Price (₹)
            </label>
            <input
              type="number"
              value={localFilters().max_price || ''}
              onInput={(e) => updateFilter('max_price', parseFloat(e.currentTarget.value) || undefined)}
              placeholder="Max"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div class="flex gap-3 pt-4">
          <button
            onClick={handleClearFilters}
            class="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
          >
            Clear Filters
          </button>
          <button
            onClick={handleApplyFilters}
            class="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchFilters;
