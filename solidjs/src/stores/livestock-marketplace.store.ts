/**
 * Livestock Marketplace Store
 * State management for livestock marketplace listings
 */

import { createSignal } from 'solid-js';
import {
  LivestockMarketplaceService,
  type LivestockMarketplaceListing,
  type LivestockListingFilters,
  type LivestockListingsResponse,
} from '../services/livestock-marketplace.service';

// State signals
const [listings, setListings] = createSignal<LivestockMarketplaceListing[]>([]);
const [currentListing, setCurrentListing] = createSignal<LivestockMarketplaceListing | null>(null);
const [filters, setFilters] = createSignal<LivestockListingFilters>({});
const [pagination, setPagination] = createSignal<{
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
} | null>(null);
const [isLoading, setIsLoading] = createSignal(false);
const [error, setError] = createSignal<string | null>(null);

/**
 * Load livestock marketplace listings
 */
async function loadListings(page: number = 1, pageSize: number = 20) {
  setIsLoading(true);
  setError(null);

  try {
    const response: LivestockListingsResponse = await LivestockMarketplaceService.getListings(
      filters(),
      page,
      pageSize
    );

    setListings(response.listings);
    setPagination({
      page: response.page,
      page_size: response.page_size,
      total_items: response.total,
      total_pages: response.total_pages,
    });
  } catch (err: any) {
    console.error('Failed to load livestock listings:', err);
    setError(err.message || 'Failed to load livestock listings');
  } finally {
    setIsLoading(false);
  }
}

/**
 * Load single listing detail
 */
async function loadListingDetail(listingId: number) {
  setIsLoading(true);
  setError(null);

  try {
    const listing = await LivestockMarketplaceService.getListingDetail(listingId);
    setCurrentListing(listing);
  } catch (err: any) {
    console.error('Failed to load listing detail:', err);
    setError(err.message || 'Failed to load listing detail');
  } finally {
    setIsLoading(false);
  }
}

/**
 * Create new livestock listing
 */
async function createListing(listingData: Partial<LivestockMarketplaceListing>) {
  setIsLoading(true);
  setError(null);

  try {
    const newListing = await LivestockMarketplaceService.createListing(listingData);
    setCurrentListing(newListing);
    // Reload listings to include new one
    await loadListings();
    return newListing;
  } catch (err: any) {
    console.error('Failed to create listing:', err);
    setError(err.message || 'Failed to create listing');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Update livestock listing
 */
async function updateListing(listingId: number, listingData: Partial<LivestockMarketplaceListing>) {
  setIsLoading(true);
  setError(null);

  try {
    const updatedListing = await LivestockMarketplaceService.updateListing(listingId, listingData);
    setCurrentListing(updatedListing);
    // Reload listings to reflect changes
    await loadListings();
    return updatedListing;
  } catch (err: any) {
    console.error('Failed to update listing:', err);
    setError(err.message || 'Failed to update listing');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Delete livestock listing
 */
async function deleteListing(listingId: number) {
  setIsLoading(true);
  setError(null);

  try {
    await LivestockMarketplaceService.deleteListing(listingId);
    setCurrentListing(null);
    // Reload listings to reflect deletion
    await loadListings();
  } catch (err: any) {
    console.error('Failed to delete listing:', err);
    setError(err.message || 'Failed to delete listing');
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Update filters and reload listings
 */
async function updateFilters(newFilters: LivestockListingFilters) {
  setFilters(newFilters);
  await loadListings(1); // Reset to page 1 when filters change
}

/**
 * Clear all filters
 */
async function clearFilters() {
  setFilters({});
  await loadListings(1);
}

// Export store
export {
  // State
  listings,
  currentListing,
  filters,
  pagination,
  isLoading,
  error,
  // Actions
  loadListings,
  loadListingDetail,
  createListing,
  updateListing,
  deleteListing,
  updateFilters,
  clearFilters,
};
