/**
 * Marketplace Listing Detail Page
 * View detailed information about a specific listing
 */

import { Component, createSignal, onMount, Show, lazy, Suspense } from 'solid-js';
import { useParams, useNavigate } from '@solidjs/router';
import {
  currentListing,
  isLoading,
  error,
  loadListingDetail,
  registerBuyerInterest,
} from '../../stores/marketplace.store';

// Lazy load marketplace detail components
const ListingDetail = lazy(() => import('../../components/marketplace/ListingDetail'));
const BuyerInterestForm = lazy(() => import('../../components/marketplace/BuyerInterestForm'));

const ListingDetailPage: Component = () => {
  const params = useParams();
  const navigate = useNavigate();
  const [showInterestForm, setShowInterestForm] = createSignal(false);
  const [interestSubmitted, setInterestSubmitted] = createSignal(false);
  const [submitError, setSubmitError] = createSignal<string | null>(null);

  onMount(async () => {
    const listingId = params.id;
    
    if (!listingId) {
      navigate('/marketplace');
      return;
    }

    try {
      await loadListingDetail(listingId);
    } catch (err) {
      console.error('Failed to load listing:', err);
    }
  });

  const handleContactFarmer = () => {
    setShowInterestForm(true);
  };

  const handleSubmitInterest = async (interestData: any) => {
    const listingId = params.id;
    
    if (!listingId) return;

    setSubmitError(null);

    try {
      await registerBuyerInterest(listingId, interestData);
      setInterestSubmitted(true);
      setShowInterestForm(false);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to submit interest');
    }
  };

  const handleCancelInterest = () => {
    setShowInterestForm(false);
    setSubmitError(null);
  };

  return (
    <div class="min-h-screen bg-gray-50">
      {/* Header */}
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Listing Details</h1>
          <button
            onClick={() => navigate('/marketplace')}
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
          >
            Back to Marketplace
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Show when={isLoading()}>
          <div class="text-center py-12">
            <p class="text-gray-600">Loading listing details...</p>
          </div>
        </Show>

        <Show when={error()}>
          <div class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error()}
          </div>
        </Show>

        <Show when={interestSubmitted()}>
          <div class="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-md">
            <h3 class="font-semibold mb-1">Interest Submitted Successfully!</h3>
            <p class="text-sm">
              The farmer will receive your contact information and will reach out to you soon.
            </p>
          </div>
        </Show>

        <Show when={submitError()}>
          <div class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {submitError()}
          </div>
        </Show>

        <Show when={!isLoading() && currentListing()}>
          <Suspense fallback={<div class="bg-white rounded-lg shadow-md p-6 animate-pulse h-96" />}>
            <ListingDetail
              listing={currentListing()!}
              onContactFarmer={handleContactFarmer}
            />
          </Suspense>
        </Show>

        {/* Buyer Interest Form Modal */}
        <Show when={showInterestForm() && currentListing()}>
          <Suspense fallback={<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-6 animate-pulse h-96 w-full max-w-md" />
          </div>}>
            <BuyerInterestForm
              listingId={params.id!}
              cropType={currentListing()!.crop_type}
              onSubmit={handleSubmitInterest}
              onCancel={handleCancelInterest}
              isLoading={isLoading()}
            />
          </Suspense>
        </Show>
      </main>
    </div>
  );
};

export default ListingDetailPage;
