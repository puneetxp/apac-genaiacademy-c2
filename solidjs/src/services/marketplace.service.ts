/**
 * Marketplace Service
 * API integration for marketplace listings and buyer interests
 */

import apiClient from '../lib/api-client';
import { buildUrl } from '~/config/api-registry';

// Types
export interface MarketplaceListing {
  id: string;
  title: string;
  description: string;
  crop_type: string;
  crop_variety: string;
  estimated_quantity: number;
  quantity_unit: string;
  quality_grade: string;
  quality_confidence?: number;
  expected_harvest_date: string;
  harvest_window: {
    start: string | null;
    end: string | null;
  };
  asking_price_per_unit?: number;
  price_negotiable: boolean;
  location: {
    state: string;
    district: string;
    block?: string;
  };
  contact: {
    enabled: boolean;
    phone?: string;
    email?: string;
  };
  market_intelligence: {
    demand_score?: number;
    price_trend?: string;
    yoy_growth?: number;
  };
  status: string;
  view_count: number;
  interest_count: number;
  listed_at: string;
}

export interface ListingFilters {
  crop_type?: string;
  state?: string;
  district?: string;
  min_quantity?: number;
  max_quantity?: number;
  harvest_from?: string;
  harvest_to?: string;
  quality_grade?: string;
  min_price?: number;
  max_price?: number;
}

export interface ListingsResponse {
  success: boolean;
  listings: MarketplaceListing[];
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters_applied: ListingFilters;
  sort: {
    by: string;
    order: string;
  };
}

export interface BuyerInterestRequest {
  listing_id: string;
  interest_type?: string;
  quantity_interested?: number;
  preferred_price?: number;
  buyer_phone?: string;
  buyer_email?: string;
  buyer_company?: string;
  quality_requirements?: string;
  delivery_requirements?: string;
  payment_terms?: string;
  message?: string;
}

export class MarketplaceService {
  /**
   * Get marketplace listings with filters and pagination
   */
  static async getListings(
    filters: ListingFilters = {},
    sortBy: string = 'harvest_date',
    sortOrder: string = 'asc',
    page: number = 1,
    pageSize: number = 20
  ): Promise<ListingsResponse> {
    const params: Record<string, string | number | boolean> = {
      sort_by: sortBy,
      sort_order: sortOrder,
      page,
      page_size: pageSize,
    };

    // Add filters
    if (filters.crop_type) params.crop_type = filters.crop_type;
    if (filters.state) params.state = filters.state;
    if (filters.district) params.district = filters.district;
    if (filters.min_quantity) params.min_quantity = filters.min_quantity;
    if (filters.max_quantity) params.max_quantity = filters.max_quantity;
    if (filters.harvest_from) params.harvest_from = filters.harvest_from;
    if (filters.harvest_to) params.harvest_to = filters.harvest_to;
    if (filters.quality_grade) params.quality_grade = filters.quality_grade;
    if (filters.min_price) params.min_price = filters.min_price;
    if (filters.max_price) params.max_price = filters.max_price;

    const url = buildUrl('marketplace', 'listings');
    const response = await apiClient.get<ListingsResponse>(
      url,
      {
        params,
        requiresAuth: false, // Public listings
        cache: true,
        cacheTTL: 60000, // 1 minute cache
      }
    );

    return response.data;
  }

  /**
   * Get listing detail
   */
  static async getListingDetail(listingId: string): Promise<any> {
    const url = buildUrl('marketplace', 'getListing', { id: listingId });
    const response = await apiClient.get(
      url,
      {
        requiresAuth: false,
        cache: true,
        cacheTTL: 120000, // 2 minutes cache
      }
    );

    return response.data.listing;
  }

  /**
   * Register buyer interest
   */
  static async registerBuyerInterest(request: BuyerInterestRequest): Promise<any> {
    // Buyer interest endpoint not in registry, use direct URL
    const response = await apiClient.post(
      '/api/v1/marketplace/buyer-interest',
      request
    );
    // Clear listing cache after interest registration
    apiClient.clearCacheByPattern(new RegExp(`/marketplace/listings/${request.listing_id}`));
    return response.data;
  }

  /**
   * Create marketplace listing for a crop
   */
  static async createListing(cropId: string, yieldPrediction?: any): Promise<any> {
    const url = buildUrl('marketplace', 'createListing');
    const response = await apiClient.post(
      url,
      {
        crop_id: cropId,
        yield_prediction: yieldPrediction,
      }
    );
    // Clear listings cache after create
    apiClient.clearCacheByPattern(new RegExp(`/marketplace/listings`));
    return response.data;
  }
}
