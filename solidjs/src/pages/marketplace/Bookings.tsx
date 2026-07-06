/**
 * Bookings List Page
 * Displays list of advance bookings for farmers and buyers
 */

import { Component, createSignal, onMount, Show, For } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { AdvanceBookingService, AdvanceBooking } from '../../services/advance-booking.service';

export const Bookings: Component = () => {
  const navigate = useNavigate();
  
  const [role, setRole] = createSignal<'buyer' | 'farmer'>('buyer');
  const [statusFilter, setStatusFilter] = createSignal<string>('');
  const [bookings, setBookings] = createSignal<AdvanceBooking[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal('');

  onMount(async () => {
    await loadBookings();
  });

  const loadBookings = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await AdvanceBookingService.listBookings(
        role(),
        statusFilter() || undefined
      );
      setBookings(response.bookings);
    } catch (err: any) {
      setError(err.message || 'Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (newRole: 'buyer' | 'farmer') => {
    setRole(newRole);
    await loadBookings();
  };

  const handleStatusFilterChange = async (status: string) => {
    setStatusFilter(status);
    await loadBookings();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      case 'quality_check':
        return 'bg-purple-100 text-purple-800';
      case 'delivered':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-6">My Bookings</h1>

      {/* Role Selector */}
      <div class="bg-white rounded-lg shadow-md p-4 mb-6">
        <div class="flex space-x-4">
          <button
            onClick={() => handleRoleChange('buyer')}
            class={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
              role() === 'buyer'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            As Buyer
          </button>
          <button
            onClick={() => handleRoleChange('farmer')}
            class={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
              role() === 'farmer'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            As Farmer
          </button>
        </div>
      </div>

      {/* Filters */}
      <div class="bg-white rounded-lg shadow-md p-4 mb-6">
        <div class="flex items-center space-x-4">
          <label class="text-sm font-medium text-gray-700">Filter by Status:</label>
          <select
            value={statusFilter()}
            onChange={(e) => handleStatusFilterChange(e.currentTarget.value)}
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="quality_check">Quality Check</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Loading State */}
      <Show when={loading()}>
        <div class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
          <p class="mt-4 text-gray-600">Loading bookings...</p>
        </div>
      </Show>

      {/* Error State */}
      <Show when={error()}>
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error()}
        </div>
      </Show>

      {/* Bookings List */}
      <Show when={!loading() && !error()}>
        <Show
          when={bookings().length > 0}
          fallback={
            <div class="bg-white rounded-lg shadow-md p-12 text-center">
              <p class="text-gray-500 text-lg">No bookings found</p>
              <p class="text-gray-400 mt-2">
                {role() === 'buyer'
                  ? 'Browse marketplace listings to create advance bookings'
                  : 'Your crops will appear here when buyers create bookings'}
              </p>
            </div>
          }
        >
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <For each={bookings()}>
              {(booking) => (
                <div
                  class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => navigate(`/marketplace/bookings/${booking.id}`)}
                >
                  {/* Status Badge */}
                  <div class="flex items-center justify-between mb-4">
                    <span class="text-sm text-gray-500">Booking #{booking.id}</span>
                    <span
                      class={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                        booking.status
                      )}`}
                    >
                      {booking.status.toUpperCase()}
                    </span>
                  </div>

                  {/* Booking Details */}
                  <div class="space-y-3">
                    <div>
                      <p class="text-sm text-gray-600">Quantity</p>
                      <p class="font-medium">{booking.quantity_booked} kg</p>
                    </div>

                    <div>
                      <p class="text-sm text-gray-600">Total Amount</p>
                      <p class="font-medium text-lg text-green-600">₹{booking.total_amount}</p>
                    </div>

                    <div>
                      <p class="text-sm text-gray-600">Advance Payment</p>
                      <p class="font-medium">
                        ₹{booking.advance_payment_amount} ({booking.advance_payment_percent}%)
                      </p>
                    </div>

                    <div>
                      <p class="text-sm text-gray-600">Expected Delivery</p>
                      <p class="font-medium">
                        {new Date(booking.expected_delivery_date).toLocaleDateString()}
                      </p>
                    </div>

                    <div>
                      <p class="text-sm text-gray-600">Booking Date</p>
                      <p class="text-sm">
                        {new Date(booking.booking_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {/* View Details Button */}
                  <button
                    class="w-full mt-4 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 font-medium"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/marketplace/bookings/${booking.id}`);
                    }}
                  >
                    View Details
                  </button>
                </div>
              )}
            </For>
          </div>
        </Show>
      </Show>
    </div>
  );
};

export default Bookings;
