import { Component, createSignal, Show, onMount } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import SupplyRequestForm from '../../components/marketplace/SupplyRequestForm';
import SupplyMatches from '../../components/marketplace/SupplyMatches';

interface SupplyRequestFormData {
  crop_type: string;
  quantity_needed: number;
  quality_requirements: string;
  delivery_date_start: string;
  delivery_date_end: string;
  max_price_per_unit: number | null;
  recurring: boolean;
  recurrence_pattern: string;
  is_emergency: boolean;
  delivery_address: string;
  delivery_pincode: string;
  delivery_state: string;
  delivery_district: string;
  notes: string;
}

interface SupplyRequestResponse {
  request_id: number;
  initial_matches: {
    single_farmer_matches: any[];
    aggregated_options: any[];
  };
  status: string;
}

const BuyerDashboard: Component = () => {
  const navigate = useNavigate();
  const [step, setStep] = createSignal<'form' | 'matches'>('form');
  const [requestId, setRequestId] = createSignal<number | null>(null);
  const [matches, setMatches] = createSignal<any>(null);
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [success, setSuccess] = createSignal<string | null>(null);

  // Get buyer ID from auth context (mock for now)
  const buyerId = 1; // TODO: Get from auth context

  const handleSubmitRequest = async (formData: SupplyRequestFormData) => {
    setError(null);
    setLoading(true);

    try {
      const requestData = {
        ...formData,
        buyer_id: buyerId,
        delivery_date_start: new Date(formData.delivery_date_start).toISOString(),
        delivery_date_end: new Date(formData.delivery_date_end).toISOString()
      };

      const response = await fetch('/supply-requests/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create supply request');
      }

      const result: SupplyRequestResponse = await response.json();
      
      setRequestId(result.request_id);
      setMatches(result.initial_matches);
      setStep('matches');
      
      if (result.initial_matches.single_farmer_matches.length === 0 && 
          result.initial_matches.aggregated_options.length === 0) {
        setError('No matches found. Try adjusting your requirements.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit request');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptSingle = async (matchId: number) => {
    if (!requestId()) return;

    try {
      const response = await fetch(`/supply-requests/${requestId()}/accept-match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ match_id: matchId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to accept match');
      }

      const result = await response.json();
      setSuccess(`Successfully created ${result.booking_ids.length} booking(s)!`);
      
      // Navigate to bookings page after 2 seconds
      setTimeout(() => {
        navigate('/marketplace/bookings');
      }, 2000);
    } catch (err) {
      throw err; // Re-throw to be handled by SupplyMatches component
    }
  };

  const handleAcceptAggregated = async (groupId: string) => {
    if (!requestId()) return;

    try {
      const response = await fetch(`/supply-requests/${requestId()}/accept-match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ aggregation_group_id: groupId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to accept match');
      }

      const result = await response.json();
      setSuccess(`Successfully created ${result.booking_ids.length} booking(s)!`);
      
      // Navigate to bookings page after 2 seconds
      setTimeout(() => {
        navigate('/marketplace/bookings');
      }, 2000);
    } catch (err) {
      throw err; // Re-throw to be handled by SupplyMatches component
    }
  };

  const handleRefreshMatches = async () => {
    if (!requestId()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/supply-requests/${requestId()}/refresh-matches`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to refresh matches');
      }

      const result = await response.json();
      setMatches(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh matches');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToForm = () => {
    setStep('form');
    setRequestId(null);
    setMatches(null);
    setError(null);
    setSuccess(null);
  };

  return (
    <div class="min-h-screen bg-gray-50 py-8">
      <div class="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            Buyer Dashboard
          </h1>
          <p class="text-gray-600">
            Post your supply requirements and get AI-matched with farmers
          </p>
        </div>

        {/* Success Message */}
        <Show when={success()}>
          <div class="bg-green-50 border border-green-200 text-green-700 px-6 py-4 rounded-lg mb-6">
            <div class="flex items-center gap-3">
              <span class="text-2xl">✅</span>
              <div>
                <p class="font-medium">{success()}</p>
                <p class="text-sm">Redirecting to bookings page...</p>
              </div>
            </div>
          </div>
        </Show>

        {/* Step Indicator */}
        <div class="mb-8">
          <div class="flex items-center justify-center gap-4">
            <div class={`flex items-center gap-2 ${step() === 'form' ? 'text-green-600' : 'text-gray-400'}`}>
              <div class={`w-8 h-8 rounded-full flex items-center justify-center ${step() === 'form' ? 'bg-green-600 text-white' : 'bg-gray-300'}`}>
                1
              </div>
              <span class="font-medium">Post Request</span>
            </div>
            
            <div class="w-16 h-1 bg-gray-300" />
            
            <div class={`flex items-center gap-2 ${step() === 'matches' ? 'text-green-600' : 'text-gray-400'}`}>
              <div class={`w-8 h-8 rounded-full flex items-center justify-center ${step() === 'matches' ? 'bg-green-600 text-white' : 'bg-gray-300'}`}>
                2
              </div>
              <span class="font-medium">Review Matches</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <Show when={step() === 'form'}>
          <SupplyRequestForm
            onSubmit={handleSubmitRequest}
          />
        </Show>

        <Show when={step() === 'matches' && matches()}>
          <div class="space-y-6">
            {/* Header with actions */}
            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex justify-between items-center">
                <div>
                  <h2 class="text-2xl font-bold text-gray-800 mb-2">
                    AI-Matched Suppliers
                  </h2>
                  <p class="text-gray-600">
                    Request ID: #{requestId()}
                  </p>
                </div>
                <div class="flex gap-3">
                  <button
                    onClick={handleRefreshMatches}
                    disabled={loading()}
                    class="px-4 py-2 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
                  >
                    {loading() ? 'Refreshing...' : '🔄 Refresh Matches'}
                  </button>
                  <button
                    onClick={handleBackToForm}
                    class="px-4 py-2 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    ← New Request
                  </button>
                </div>
              </div>
            </div>

            {/* Matches */}
            <SupplyMatches
              singleMatches={matches()?.single_farmer_matches || []}
              aggregatedOptions={matches()?.aggregated_options || []}
              onAcceptSingle={handleAcceptSingle}
              onAcceptAggregated={handleAcceptAggregated}
            />
          </div>
        </Show>
      </div>
    </div>
  );
};

export default BuyerDashboard;
