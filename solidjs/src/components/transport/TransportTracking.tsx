import { Component, createSignal, createEffect, For, Show } from 'solid-js';

interface TrackingUpdate {
  status: string;
  timestamp: string;
  message: string;
}

interface TransportBooking {
  id: number;
  provider_id: number;
  pickup_address: string;
  delivery_address: string;
  distance_km: number;
  livestock_type: string;
  livestock_count: number;
  transport_cost: number;
  insurance_opted: boolean;
  insurance_cost: number;
  total_cost: number;
  scheduled_pickup_date: string;
  estimated_delivery_date: string;
  actual_pickup_date: string | null;
  actual_delivery_date: string | null;
  status: string;
  tracking_updates: string;
  special_instructions: string;
  rating: number | null;
  review: string | null;
}

interface TransportTrackingProps {
  bookingId: number;
}

const TransportTracking: Component<TransportTrackingProps> = (props) => {
  const [booking, setBooking] = createSignal<TransportBooking | null>(null);
  const [trackingUpdates, setTrackingUpdates] = createSignal<TrackingUpdate[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [showRatingForm, setShowRatingForm] = createSignal(false);
  const [rating, setRating] = createSignal(0);
  const [review, setReview] = createSignal('');

  const loadBooking = async () => {
    try {
      const response = await fetch(`/transport/bookings/${props.bookingId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setBooking(data);
        
        if (data.tracking_updates) {
          const updates = JSON.parse(data.tracking_updates);
          setTrackingUpdates(updates.reverse()); // Show latest first
        }
      }
    } catch (err) {
      console.error('Failed to load booking:', err);
    } finally {
      setLoading(false);
    }
  };

  createEffect(() => {
    loadBooking();
    // Refresh every 30 seconds
    const interval = setInterval(loadBooking, 30000);
    return () => clearInterval(interval);
  });

  const submitRating = async () => {
    try {
      const response = await fetch(`/transport/bookings/${props.bookingId}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          rating: rating(),
          review: review()
        })
      });

      if (response.ok) {
        await loadBooking();
        setShowRatingForm(false);
      }
    } catch (err) {
      console.error('Failed to submit rating:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'in_transit': return 'bg-purple-100 text-purple-800';
      case 'delivered': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    return status.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div class="max-w-4xl mx-auto p-6">
      <Show when={loading()}>
        <div class="text-center py-8">Loading...</div>
      </Show>

      <Show when={!loading() && booking()}>
        {(b) => (
          <>
            <div class="flex justify-between items-start mb-6">
              <div>
                <h1 class="text-3xl font-bold">Transport Tracking</h1>
                <p class="text-gray-600">Booking #{b().id}</p>
              </div>
              <div class={`px-4 py-2 rounded-full font-semibold ${getStatusColor(b().status)}`}>
                {getStatusLabel(b().status)}
              </div>
            </div>

            {/* Transport Details */}
            <div class="bg-white shadow rounded-lg p-6 mb-6">
              <h2 class="text-xl font-semibold mb-4">Transport Details</h2>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p class="text-sm text-gray-600">Pickup Location</p>
                  <p class="font-medium">{b().pickup_address}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Delivery Location</p>
                  <p class="font-medium">{b().delivery_address}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Distance</p>
                  <p class="font-medium">{b().distance_km} km</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Livestock</p>
                  <p class="font-medium">{b().livestock_count} {b().livestock_type}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Scheduled Pickup</p>
                  <p class="font-medium">{new Date(b().scheduled_pickup_date).toLocaleString()}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Estimated Delivery</p>
                  <p class="font-medium">{new Date(b().estimated_delivery_date).toLocaleString()}</p>
                </div>
                {b().actual_pickup_date && (
                  <div>
                    <p class="text-sm text-gray-600">Actual Pickup</p>
                    <p class="font-medium">{new Date(b().actual_pickup_date).toLocaleString()}</p>
                  </div>
                )}
                {b().actual_delivery_date && (
                  <div>
                    <p class="text-sm text-gray-600">Actual Delivery</p>
                    <p class="font-medium">{new Date(b().actual_delivery_date).toLocaleString()}</p>
                  </div>
                )}
              </div>

              {b().special_instructions && (
                <div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                  <p class="text-sm font-medium text-yellow-800">Special Instructions:</p>
                  <p class="text-sm text-yellow-700">{b().special_instructions}</p>
                </div>
              )}
            </div>

            {/* Cost Breakdown */}
            <div class="bg-white shadow rounded-lg p-6 mb-6">
              <h2 class="text-xl font-semibold mb-4">Cost Breakdown</h2>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span>Transport Cost:</span>
                  <span class="font-medium">₹{b().transport_cost.toLocaleString()}</span>
                </div>
                {b().insurance_opted && (
                  <div class="flex justify-between">
                    <span>Insurance Cost:</span>
                    <span class="font-medium">₹{b().insurance_cost?.toLocaleString()}</span>
                  </div>
                )}
                <div class="flex justify-between text-lg font-bold border-t pt-2">
                  <span>Total Cost:</span>
                  <span>₹{b().total_cost.toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* Tracking Timeline */}
            <div class="bg-white shadow rounded-lg p-6 mb-6">
              <h2 class="text-xl font-semibold mb-4">Tracking Timeline</h2>
              <div class="space-y-4">
                <For each={trackingUpdates()}>
                  {(update, index) => (
                    <div class="flex">
                      <div class="flex flex-col items-center mr-4">
                        <div class={`w-3 h-3 rounded-full ${index() === 0 ? 'bg-green-500' : 'bg-gray-300'}`} />
                        {index() < trackingUpdates().length - 1 && (
                          <div class="w-0.5 h-full bg-gray-300 my-1" />
                        )}
                      </div>
                      <div class="flex-1 pb-4">
                        <div class="flex justify-between items-start">
                          <div>
                            <p class="font-medium">{getStatusLabel(update.status)}</p>
                            <p class="text-sm text-gray-600">{update.message}</p>
                          </div>
                          <p class="text-sm text-gray-500">
                            {new Date(update.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </For>
              </div>
            </div>

            {/* Rating and Review */}
            <Show when={b().status === 'delivered' && !b().rating}>
              <div class="bg-white shadow rounded-lg p-6">
                <h2 class="text-xl font-semibold mb-4">Rate This Transport</h2>
                
                <Show when={!showRatingForm()}>
                  <button
                    onClick={() => setShowRatingForm(true)}
                    class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Add Rating & Review
                  </button>
                </Show>

                <Show when={showRatingForm()}>
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium mb-2">Rating</label>
                      <div class="flex space-x-2">
                        <For each={[1, 2, 3, 4, 5]}>
                          {(star) => (
                            <button
                              onClick={() => setRating(star)}
                              class={`text-3xl ${star <= rating() ? 'text-yellow-500' : 'text-gray-300'}`}
                            >
                              ★
                            </button>
                          )}
                        </For>
                      </div>
                    </div>

                    <div>
                      <label class="block text-sm font-medium mb-2">Review (Optional)</label>
                      <textarea
                        value={review()}
                        onInput={(e) => setReview(e.currentTarget.value)}
                        placeholder="Share your experience..."
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                        rows="4"
                      />
                    </div>

                    <div class="flex space-x-4">
                      <button
                        onClick={() => setShowRatingForm(false)}
                        class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={submitRating}
                        disabled={rating() === 0}
                        class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                      >
                        Submit Rating
                      </button>
                    </div>
                  </div>
                </Show>
              </div>
            </Show>

            {/* Existing Rating */}
            <Show when={b().rating}>
              <div class="bg-white shadow rounded-lg p-6">
                <h2 class="text-xl font-semibold mb-4">Your Rating</h2>
                <div class="flex items-center space-x-2 mb-2">
                  <For each={[1, 2, 3, 4, 5]}>
                    {(star) => (
                      <span class={`text-2xl ${star <= (b().rating || 0) ? 'text-yellow-500' : 'text-gray-300'}`}>
                        ★
                      </span>
                    )}
                  </For>
                </div>
                {b().review && (
                  <p class="text-gray-700">{b().review}</p>
                )}
              </div>
            </Show>
          </>
        )}
      </Show>
    </div>
  );
};

export default TransportTracking;
