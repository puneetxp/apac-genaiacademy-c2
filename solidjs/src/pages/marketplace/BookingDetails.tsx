/**
 * Booking Details Page
 * Displays advance booking details with quality verification workflow
 */

import { Component, createSignal, onMount, Show, For } from 'solid-js';
import { useParams, useNavigate } from '@solidjs/router';
import { AdvanceBookingService, AdvanceBooking, QualityVerification, PaymentMilestone } from '../../services/advance-booking.service';
import { QualityVerificationForm } from '../../components/marketplace/QualityVerificationForm';
import { QualityHistory } from '../../components/marketplace/QualityHistory';
import { QualityDispute, DisputeData } from '../../components/marketplace/QualityDispute';

export const BookingDetails: Component = () => {
  const params = useParams();
  const navigate = useNavigate();
  
  const [booking, setBooking] = createSignal<AdvanceBooking | null>(null);
  const [listing, setListing] = createSignal<any>(null);
  const [paymentMilestones, setPaymentMilestones] = createSignal<PaymentMilestone[]>([]);
  const [qualityVerifications, setQualityVerifications] = createSignal<QualityVerification[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal('');
  const [showVerificationForm, setShowVerificationForm] = createSignal(false);
  const [showDisputeForm, setShowDisputeForm] = createSignal(false);
  const [selectedVerificationId, setSelectedVerificationId] = createSignal<number | null>(null);

  onMount(async () => {
    await loadBookingDetails();
  });

  const loadBookingDetails = async () => {
    setLoading(true);
    setError('');

    try {
      const bookingId = parseInt(params.id ?? "");
      const response = await AdvanceBookingService.getBookingDetails(bookingId);
      
      setBooking(response.booking);
      setListing(response.listing);
      setPaymentMilestones(response.payment_milestones);
      setQualityVerifications(response.quality_verifications);
    } catch (err: any) {
      setError(err.message || 'Failed to load booking details');
    } finally {
      setLoading(false);
    }
  };

  const handleVerificationSuccess = async () => {
    setShowVerificationForm(false);
    await loadBookingDetails();
  };

  const handleDisputeSubmit = async (dispute: DisputeData) => {
    try {
      await AdvanceBookingService.raiseDispute(parseInt(params.id ?? ""), {
        dispute_reason: dispute.dispute_reason,
        details: [dispute.evidence_description, dispute.requested_resolution && `Requested resolution: ${dispute.requested_resolution}`]
          .filter(Boolean).join('\n'),
        photos: dispute.evidence_photos,
      });
      setShowDisputeForm(false);
      await loadBookingDetails();
      alert('Dispute submitted successfully. Our team will review it within 24-48 hours.');
    } catch (err: any) {
      console.error('Failed to submit dispute:', err);
      alert(err?.message || 'Failed to submit dispute. Please try again.');
    }
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

  const getMilestoneStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'due':
        return 'bg-yellow-100 text-yellow-800';
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div class="container mx-auto px-4 py-8">
      <Show when={loading()}>
        <div class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
          <p class="mt-4 text-gray-600">Loading booking details...</p>
        </div>
      </Show>

      <Show when={error()}>
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error()}
        </div>
      </Show>

      <Show when={!loading() && booking()}>
        <div class="space-y-6">
          {/* Header */}
          <div class="flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate('/marketplace/bookings')}
                class="text-green-600 hover:text-green-700 mb-2 flex items-center"
              >
                ← Back to Bookings
              </button>
              <h1 class="text-3xl font-bold">Booking #{booking()?.id}</h1>
            </div>
            <span class={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(booking()?.status || '')}`}>
              {booking()?.status.toUpperCase()}
            </span>
          </div>

          {/* Booking Summary */}
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-bold mb-4">Booking Summary</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-600">Crop</p>
                <p class="font-medium">{listing()?.crop_type} - {listing()?.crop_variety}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Location</p>
                <p class="font-medium">{listing()?.location_district}, {listing()?.location_state}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Quantity Booked</p>
                <p class="font-medium">{booking()?.quantity_booked} kg</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Price per Unit</p>
                <p class="font-medium">₹{booking()?.price_per_unit}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Total Amount</p>
                <p class="font-medium text-lg">₹{booking()?.total_amount}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Expected Delivery</p>
                <p class="font-medium">
                  {booking()?.expected_delivery_date ? new Date(booking()!.expected_delivery_date).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Quality Standards */}
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-bold mb-4">Quality Standards</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p class="text-sm text-gray-600">Grade</p>
                <p class="font-medium">{booking()?.quality_standards.grade}</p>
              </div>
              <Show when={booking()?.quality_standards.size}>
                <div>
                  <p class="text-sm text-gray-600">Size</p>
                  <p class="font-medium">{booking()?.quality_standards.size}</p>
                </div>
              </Show>
              <Show when={booking()?.quality_standards.moisture_content}>
                <div>
                  <p class="text-sm text-gray-600">Max Moisture</p>
                  <p class="font-medium">{booking()?.quality_standards.moisture_content}%</p>
                </div>
              </Show>
              <div>
                <p class="text-sm text-gray-600">Organic</p>
                <p class="font-medium">
                  {booking()?.quality_standards.organic_certified ? 'Required' : 'Not Required'}
                </p>
              </div>
            </div>
          </div>

          {/* Payment Milestones */}
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-bold mb-4">Payment Schedule</h2>
            <div class="space-y-3">
              <For each={paymentMilestones()}>
                {(milestone) => (
                  <div class="flex items-center justify-between border-b border-gray-200 pb-3">
                    <div class="flex-1">
                      <p class="font-medium capitalize">{milestone.milestone_type.replaceAll('_', ' ')}</p>
                      <p class="text-sm text-gray-600">
                        Due: {new Date(milestone.due_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div class="text-right">
                      <p class="font-medium">₹{milestone.amount}</p>
                      <span class={`px-3 py-1 rounded-full text-xs font-medium ${getMilestoneStatusColor(milestone.status)}`}>
                        {milestone.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                )}
              </For>
            </div>
          </div>

          {/* Quality Verification Section */}
          <Show when={!showVerificationForm() && !showDisputeForm()}>
            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-bold">Quality Verification</h2>
                <button
                  onClick={() => setShowVerificationForm(true)}
                  class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                >
                  Submit Verification
                </button>
              </div>

              <Show
                when={qualityVerifications().length > 0}
                fallback={
                  <p class="text-gray-500 text-center py-4">
                    No quality verifications submitted yet
                  </p>
                }
              >
                <QualityHistory verifications={qualityVerifications()} />
                
                {/* Dispute Button */}
                <Show when={qualityVerifications().length > 0}>
                  <div class="mt-4 text-center">
                    <button
                      onClick={() => {
                        setSelectedVerificationId(qualityVerifications()[0].id);
                        setShowDisputeForm(true);
                      }}
                      class="text-red-600 hover:text-red-700 font-medium"
                    >
                      Dispute Latest Verification
                    </button>
                  </div>
                </Show>
              </Show>
            </div>
          </Show>

          {/* Quality Verification Form */}
          <Show when={showVerificationForm()}>
            <QualityVerificationForm
              bookingId={booking()!.id}
              qualityStandards={booking()!.quality_standards}
              onSuccess={handleVerificationSuccess}
              onCancel={() => setShowVerificationForm(false)}
            />
          </Show>

          {/* Quality Dispute Form */}
          <Show when={showDisputeForm()}>
            <QualityDispute
              bookingId={booking()!.id}
              verificationId={selectedVerificationId()!}
              onSubmit={handleDisputeSubmit}
              onCancel={() => setShowDisputeForm(false)}
            />
          </Show>
        </div>
      </Show>
    </div>
  );
};

export default BookingDetails;
