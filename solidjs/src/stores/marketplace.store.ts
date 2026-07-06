/**
 * Marketplace Store
 * Global state management for marketplace listings
 */

import { createSignal } from 'solid-js';
import { 
  MarketplaceService, 
  type MarketplaceListing, 
  type ListingFilters,
  type ListingsResponse 
} from '../services/marketplace.service';

// Global state
const [listings, setListings] = createSignal<MarketplaceListing[]>([]);
const [currentListing, setCurrentListing] = createSignal<any | null>(null);
const [pagination, setPagination] = createSignal<ListingsResponse['pagination'] | null>(null);
const [filters, setFilters] = createSignal<ListingFilters>({});
const [sortBy, setSortBy] = createSignal('harvest_date');
const [sortOrder, setSortOrder] = createSignal<'asc' | 'desc'>('asc');
const [isLoading, setIsLoading] = createSignal(false);
const [error, setError] = createSignal<string | null>(null);

/**
 * Load marketplace listings
 */
export async function loadListings(
  page: number = 1,
  pageSize: number = 20
): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const response = await MarketplaceService.getListings(
      filters(),
      sortBy(),
      sortOrder(),
      page,
      pageSize
    );
    
    setListings(response.listings);
    setPagination(response.pagination);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to load listings';
    setError(message);
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Load listing detail
 */
export async function loadListingDetail(listingId: string): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    const listing = await MarketplaceService.getListingDetail(listingId);
    setCurrentListing(listing);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to load listing';
    setError(message);
    throw err;
  } finally {
    setIsLoading(false);
  }
}

/**
 * Update filters and reload listings
 */
export async function updateFilters(newFilters: ListingFilters): Promise<void> {
  setFilters(newFilters);
  await loadListings(1); // Reset to page 1 when filters change
}

/**
 * Update sorting and reload listings
 */
export async function updateSort(by: string, order: 'asc' | 'desc'): Promise<void> {
  setSortBy(by);
  setSortOrder(order);
  await loadListings(pagination()?.page || 1);
}

/**
 * Clear filters
 */
export async function clearFilters(): Promise<void> {
  setFilters({});
  await loadListings(1);
}

/**
 * Register buyer interest
 */
export async function registerBuyerInterest(
  listingId: string,
  interestData: any
): Promise<void> {
  setIsLoading(true);
  setError(null);

  try {
    await MarketplaceService.registerBuyerInterest({
      listing_id: listingId,
      ...interestData,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to register interest';
    setError(message);
    throw err;
  } finally {
    setIsLoading(false);
  }
}

// Export signals
export { 
  listings, 
  currentListing, 
  pagination, 
  filters, 
  sortBy, 
  sortOrder, 
  isLoading, 
  error 
};
