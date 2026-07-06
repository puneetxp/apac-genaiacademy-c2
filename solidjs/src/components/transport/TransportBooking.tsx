import { Component, createSignal, createEffect, For, Show } from 'solid-js';
import { createStore } from 'solid-js/store';

interface TransportProvider {
  id: number;
  company_name: string;
  contact_person: string;
  contact_phone: string;
  base_rate_per_km: number;
  minimum_charge: number;
  insurance_available: boolean;
  insurance_rate_percentage: number;
  rating: number;
  total_ratings: number;
  completed_transports: number;
}

interface CostEstimate {
  distance_km: number;
  transport_cost: number;
  insurance_cost: number;
  total_cost: number;
  provider_name: string;
  estimated_travel_hours: number;
}

interface TransportBookingProps {
  transactionId: number;
  pickupAddress: string;
  pickupLatitude?: number;
  pickupLongitude?: number;
  deliveryAddress: string;
  deliveryLatitude?: number;
  deliveryLongitude?: number;
  livestockType: string;
  livestockCount: number;
  animalValue: number;
}

const TransportBooking: Component<TransportBookingProps> = (props) => {
  const [providers, setProviders] = createSignal<TransportProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = createSignal<TransportProvider | null>(null);
  const [costEstimate, setCostEstimate] = createSignal<CostEstimate | null>(null);
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [success, setSuccess] = createSignal(false);

  const [bookingData, setBookingData] = createStore({
    scheduled_pickup_date: '',
    insurance_opted: false,
    special_instructions: ''
  });

  // Load providers on mount
  createEffect(async () => {
    try {
      const response = await fetch(
        `/transport/providers?livestock_type=${props.livestockType}&min_capacity=${props.livestockCount}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setProviders(data);
      }
    } catch (err) {
      console.error('Failed to load providers:', err);
    }
  });

  // Get cost estimate when provider is selected
  createEffect(async () => {
    const provider = selectedProvider();
    if (!provider) return;

    setLoading(true);
    try {
      const response = await fetch('/transport/cost-estimate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          provider_id: provider.id,
          pickup_latitude: props.pickupLatitude,
          pickup_longitude: props.pickupLongitude,
          delivery_latitude: props.deliveryLatitude,
          delivery_longitude: props.deliveryLongitude,
          livestock_type: props.livestockType,
          livestock_count: props.livestockCount,
          animal_value: props.animalValue,
          insurance_opted: bookingData.insurance_opted
        })
      });

      if (response.ok) {
        const estimate = await response.json();
        setCostEstimate(estimate);
      }
    } catch (err) {
      console.error('Failed to get cost estimate:', err);
    } finally {
      setLoading(false);
    }
  });

  const handleBooking = async () => {
    const provider = selectedProvider();
    if (!provider || !bookingData.scheduled_pickup_date) {
      setError('Please select a provider and pickup date');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/transport/bookings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          transaction_id: props.transactionId,
          provider_id: provider.id,
          requester_id: parseInt(localStorage.getItem('user_id') || '0'),
          pickup_address: props.pickupAddress,
          pickup_latitude: props.pickupLatitude,
          pickup_longitude: props.pickupLongitude,
          delivery_address: props.deliveryAddress,
          delivery_latitude: props.deliveryLatitude,
          delivery_longitude: props.deliveryLongitude,
          livestock_type: props.livestockType,
          livestock_count: props.livestockCount,
          animal_value: props.animalValue,
          scheduled_pickup_date: new Date(bookingData.scheduled_pickup_date).toISOString(),
          insurance_opted: bookingData.insurance_opted,
          special_instructions: bookingData.special_instructions
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create booking');
      }

      setSuccess(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="max-w-4xl mx-auto p-6">
      <h2 class="text-2xl font-bold mb-6">Book Transport</h2>

      {success() && (
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          Transport booking created successfully! The provider will contact you soon.
        </div>
      )}

      {error() && (
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error()}
        </div>
      )}

      {/* Transport Details */}
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Transport Details</h3>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="font-medium">Pickup:</span> {props.pickupAddress}
          </div>
          <div>
            <span class="font-medium">Delivery:</span> {props.deliveryAddress}
          </div>
          <div>
            <span class="font-medium">Livestock:</span> {props.livestockCount} {props.livestockType}
          </div>
          <div>
            <span class="font-medium">Value:</span> ₹{props.animalValue.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Provider Selection */}
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Select Transport Provider</h3>
        
        <Show when={providers().length === 0}>
          <p class="text-gray-500">No transport providers available for this route.</p>
        </Show>

        <div class="space-y-4">
          <For each={providers()}>
            {(provider) => (
              <div
                class={`border rounded-lg p-4 cursor-pointer transition ${
                  selectedProvider()?.id === provider.id
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-green-300'
                }`}
                onClick={() => setSelectedProvider(provider)}
              >
                <div class="flex justify-between items-start">
                  <div>
                    <h4 class="font-semibold">{provider.company_name}</h4>
                    <p class="text-sm text-gray-600">{provider.contact_person}</p>
                    <p class="text-sm text-gray-600">{provider.contact_phone}</p>
                  </div>
                  <div class="text-right">
                    <div class="flex items-center space-x-1">
                      <span class="text-yellow-500">★</span>
                      <span class="font-medium">{provider.rating.toFixed(1)}</span>
                      <span class="text-sm text-gray-500">({provider.total_ratings})</span>
                    </div>
                    <p class="text-sm text-gray-600">{provider.completed_transports} trips</p>
                  </div>
                </div>
                <div class="mt-2 flex items-center space-x-4 text-sm">
                  <span>₹{provider.base_rate_per_km}/km</span>
                  <span>Min: ₹{provider.minimum_charge}</span>
                  {provider.insurance_available && (
                    <span class="text-green-600">Insurance Available</span>
                  )}
                </div>
              </div>
            )}
          </For>
        </div>
      </div>

      {/* Cost Estimate */}
      <Show when={costEstimate()}>
        {(estimate) => (
          <div class="bg-white shadow rounded-lg p-6 mb-6">
            <h3 class="text-lg font-semibold mb-4">Cost Estimate</h3>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span>Distance:</span>
                <span class="font-medium">{estimate().distance_km} km</span>
              </div>
              <div class="flex justify-between">
                <span>Estimated Travel Time:</span>
                <span class="font-medium">{estimate().estimated_travel_hours.toFixed(1)} hours</span>
              </div>
              <div class="flex justify-between">
                <span>Transport Cost:</span>
                <span class="font-medium">₹{estimate().transport_cost.toLocaleString()}</span>
              </div>
              {bookingData.insurance_opted && (
                <div class="flex justify-between">
                  <span>Insurance Cost:</span>
                  <span class="font-medium">₹{estimate().insurance_cost.toLocaleString()}</span>
                </div>
              )}
              <div class="flex justify-between text-lg font-bold border-t pt-2">
                <span>Total Cost:</span>
                <span>₹{estimate().total_cost.toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}
      </Show>

      {/* Booking Form */}
      <Show when={selectedProvider()}>
        <div class="bg-white shadow rounded-lg p-6 mb-6">
          <h3 class="text-lg font-semibold mb-4">Booking Details</h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Scheduled Pickup Date *</label>
              <input
                type="datetime-local"
                required
                value={bookingData.scheduled_pickup_date}
                onInput={(e) => setBookingData('scheduled_pickup_date', e.currentTarget.value)}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <Show when={selectedProvider()?.insurance_available}>
              <div>
                <label class="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={bookingData.insurance_opted}
                    onChange={(e) => setBookingData('insurance_opted', e.currentTarget.checked)}
                    class="rounded text-green-600"
                  />
                  <span class="font-medium">
                    Add Insurance ({selectedProvider()?.insurance_rate_percentage}% of animal value)
                  </span>
                </label>
              </div>
            </Show>

            <div>
              <label class="block text-sm font-medium mb-2">Special Instructions</label>
              <textarea
                value={bookingData.special_instructions}
                onInput={(e) => setBookingData('special_instructions', e.currentTarget.value)}
                placeholder="Any special handling requirements..."
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                rows="3"
              />
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => window.history.back()}
            class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleBooking}
            disabled={loading() || !bookingData.scheduled_pickup_date}
            class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading() ? 'Booking...' : 'Confirm Booking'}
          </button>
        </div>
      </Show>
    </div>
  );
};

export default TransportBooking;
