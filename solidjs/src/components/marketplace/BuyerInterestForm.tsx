/**
 * Buyer Interest Form Component
 * Form for buyers to express interest in a listing
 */

import { Component, createSignal, Show } from 'solid-js';

interface BuyerInterestFormProps {
  listingId: string;
  cropType: string;
  onSubmit: (data: any) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const BuyerInterestForm: Component<BuyerInterestFormProps> = (props) => {
  const [formData, setFormData] = createSignal({
    interest_type: 'inquiry',
    quantity_interested: '',
    preferred_price: '',
    buyer_phone: '',
    buyer_email: '',
    buyer_company: '',
    quality_requirements: '',
    delivery_requirements: '',
    payment_terms: '',
    message: '',
  });

  const [validationErrors, setValidationErrors] = createSignal<Record<string, string>>({});

  const updateField = (field: string, value: string) => {
    setFormData({ ...formData(), [field]: value });
    setValidationErrors({ ...validationErrors(), [field]: '' });
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    const data = formData();

    if (!data.buyer_phone && !data.buyer_email) {
      errors.contact = 'Please provide either phone number or email';
    }

    if (data.buyer_phone && !/^[6-9]\d{9}$/.test(data.buyer_phone)) {
      errors.buyer_phone = 'Please enter a valid 10-digit phone number';
    }

    if (data.buyer_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.buyer_email)) {
      errors.buyer_email = 'Please enter a valid email address';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: Event) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const data = formData();
    props.onSubmit({
      interest_type: data.interest_type,
      quantity_interested: data.quantity_interested ? parseFloat(data.quantity_interested) : undefined,
      preferred_price: data.preferred_price ? parseFloat(data.preferred_price) : undefined,
      buyer_phone: data.buyer_phone || undefined,
      buyer_email: data.buyer_email || undefined,
      buyer_company: data.buyer_company || undefined,
      quality_requirements: data.quality_requirements || undefined,
      delivery_requirements: data.delivery_requirements || undefined,
      payment_terms: data.payment_terms || undefined,
      message: data.message || undefined,
    });
  };

  return (
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h2 class="text-2xl font-bold text-gray-800 mb-2">
            Express Interest
          </h2>
          <p class="text-gray-600 mb-6">
            Fill out this form to contact the farmer about {props.cropType}
          </p>

          <form onSubmit={handleSubmit} class="space-y-4">
            {/* Interest Type */}
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Type of Interest *
              </label>
              <select
                value={formData().interest_type}
                onChange={(e) => updateField('interest_type', e.currentTarget.value)}
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                required
              >
                <option value="inquiry">General Inquiry</option>
                <option value="booking_intent">Booking Intent</option>
                <option value="firm_order">Firm Order</option>
              </select>
            </div>

            {/* Contact Information */}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <input
                  type="tel"
                  value={formData().buyer_phone}
                  onInput={(e) => updateField('buyer_phone', e.currentTarget.value)}
                  placeholder="10-digit mobile number"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
                <Show when={validationErrors().buyer_phone}>
                  <p class="mt-1 text-sm text-red-600">{validationErrors().buyer_phone}</p>
                </Show>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={formData().buyer_email}
                  onInput={(e) => updateField('buyer_email', e.currentTarget.value)}
                  placeholder="your@email.com"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
                <Show when={validationErrors().buyer_email}>
                  <p class="mt-1 text-sm text-red-600">{validationErrors().buyer_email}</p>
                </Show>
              </div>
            </div>

            <Show when={validationErrors().contact}>
              <p class="text-sm text-red-600">{validationErrors().contact}</p>
            </Show>

            {/* Company Name */}
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Company Name (Optional)
              </label>
              <input
                type="text"
                value={formData().buyer_company}
                onInput={(e) => updateField('buyer_company', e.currentTarget.value)}
                placeholder="Your company name"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Quantity and Price */}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Quantity Interested (quintals)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={formData().quantity_interested}
                  onInput={(e) => updateField('quantity_interested', e.currentTarget.value)}
                  placeholder="e.g., 50"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Preferred Price (₹ per quintal)
                </label>
                <input
                  type="number"
                  step="100"
                  value={formData().preferred_price}
                  onInput={(e) => updateField('preferred_price', e.currentTarget.value)}
                  placeholder="e.g., 2000"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>

            {/* Quality Requirements */}
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Quality Requirements (Optional)
              </label>
              <textarea
                value={formData().quality_requirements}
                onInput={(e) => updateField('quality_requirements', e.currentTarget.value)}
                placeholder="Specify any quality requirements..."
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Delivery Requirements */}
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Delivery Requirements (Optional)
              </label>
              <textarea
                value={formData().delivery_requirements}
                onInput={(e) => updateField('delivery_requirements', e.currentTarget.value)}
                placeholder="Specify delivery location and requirements..."
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Payment Terms */}
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Payment Terms (Optional)
              </label>
              <input
                type="text"
                value={formData().payment_terms}
                onInput={(e) => updateField('payment_terms', e.currentTarget.value)}
                placeholder="e.g., Advance payment, Cash on delivery"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Message */}
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Additional Message (Optional)
              </label>
              <textarea
                value={formData().message}
                onInput={(e) => updateField('message', e.currentTarget.value)}
                placeholder="Any additional information for the farmer..."
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Buttons */}
            <div class="flex gap-3 pt-4">
              <button
                type="button"
                onClick={props.onCancel}
                class="flex-1 py-3 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-md transition-colors"
                disabled={props.isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={props.isLoading}
                class="flex-1 py-3 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
              >
                {props.isLoading ? 'Submitting...' : 'Submit Interest'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default BuyerInterestForm;
