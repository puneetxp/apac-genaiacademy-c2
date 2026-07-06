import { Component, createSignal, Show } from 'solid-js';
import { createStore } from 'solid-js/store';

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

interface SupplyRequestFormProps {
  onSubmit: (data: SupplyRequestFormData) => Promise<void>;
  onCancel?: () => void;
}

const SupplyRequestForm: Component<SupplyRequestFormProps> = (props) => {
  const [formData, setFormData] = createStore<SupplyRequestFormData>({
    crop_type: '',
    quantity_needed: 0,
    quality_requirements: '',
    delivery_date_start: '',
    delivery_date_end: '',
    max_price_per_unit: null,
    recurring: false,
    recurrence_pattern: '',
    is_emergency: false,
    delivery_address: '',
    delivery_pincode: '',
    delivery_state: '',
    delivery_district: '',
    notes: ''
  });

  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  const cropTypes = [
    'Wheat', 'Rice', 'Maize', 'Barley', 'Sorghum',
    'Tomato', 'Potato', 'Onion', 'Cabbage', 'Cauliflower',
    'Cotton', 'Sugarcane', 'Soybean', 'Groundnut', 'Mustard'
  ];

  const qualityGrades = ['Grade A', 'Grade B', 'Grade C', 'Organic', 'Standard'];

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!formData.crop_type) {
      setError('Please select a crop type');
      return;
    }
    if (formData.quantity_needed <= 0) {
      setError('Quantity must be greater than 0');
      return;
    }
    if (!formData.delivery_date_start || !formData.delivery_date_end) {
      setError('Please specify delivery window');
      return;
    }

    setLoading(true);
    try {
      await props.onSubmit(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold text-gray-800 mb-6">
        Post Supply Request
      </h2>

      <Show when={error()}>
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error()}
        </div>
      </Show>

      <form onSubmit={handleSubmit} class="space-y-6">
        {/* Crop Type */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Crop Type *
          </label>
          <select
            value={formData.crop_type}
            onChange={(e) => setFormData('crop_type', e.currentTarget.value)}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          >
            <option value="">Select crop type</option>
            {cropTypes.map((crop) => (
              <option value={crop}>{crop}</option>
            ))}
          </select>
        </div>

        {/* Quantity */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Quantity Needed (kg) *
          </label>
          <input
            type="number"
            value={formData.quantity_needed}
            onInput={(e) => setFormData('quantity_needed', parseFloat(e.currentTarget.value))}
            min="0"
            step="0.01"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
        </div>

        {/* Quality Requirements */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Quality Requirements
          </label>
          <select
            value={formData.quality_requirements}
            onChange={(e) => setFormData('quality_requirements', e.currentTarget.value)}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="">Select quality grade</option>
            {qualityGrades.map((grade) => (
              <option value={grade}>{grade}</option>
            ))}
          </select>
        </div>

        {/* Delivery Window */}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Delivery Start Date *
            </label>
            <input
              type="date"
              value={formData.delivery_date_start}
              onInput={(e) => setFormData('delivery_date_start', e.currentTarget.value)}
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Delivery End Date *
            </label>
            <input
              type="date"
              value={formData.delivery_date_end}
              onInput={(e) => setFormData('delivery_date_end', e.currentTarget.value)}
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              required
            />
          </div>
        </div>

        {/* Max Price */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Maximum Price per kg (₹)
          </label>
          <input
            type="number"
            value={formData.max_price_per_unit || ''}
            onInput={(e) => setFormData('max_price_per_unit', e.currentTarget.value ? parseFloat(e.currentTarget.value) : null)}
            min="0"
            step="0.01"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            placeholder="Optional"
          />
        </div>

        {/* Delivery Location */}
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-800">Delivery Location</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Pincode
              </label>
              <input
                type="text"
                value={formData.delivery_pincode}
                onInput={(e) => setFormData('delivery_pincode', e.currentTarget.value)}
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="e.g., 122003"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                State
              </label>
              <input
                type="text"
                value={formData.delivery_state}
                onInput={(e) => setFormData('delivery_state', e.currentTarget.value)}
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="e.g., Haryana"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              District
            </label>
            <input
              type="text"
              value={formData.delivery_district}
              onInput={(e) => setFormData('delivery_district', e.currentTarget.value)}
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="e.g., Gurgaon"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Full Address
            </label>
            <textarea
              value={formData.delivery_address}
              onInput={(e) => setFormData('delivery_address', e.currentTarget.value)}
              rows={3}
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Complete delivery address"
            />
          </div>
        </div>

        {/* Recurring & Emergency */}
        <div class="space-y-3">
          <label class="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.is_emergency}
              onChange={(e) => setFormData('is_emergency', e.currentTarget.checked)}
              class="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span class="text-sm font-medium text-gray-700">
              🚨 Emergency Request (Urgent)
            </span>
          </label>

          <label class="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.recurring}
              onChange={(e) => setFormData('recurring', e.currentTarget.checked)}
              class="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <span class="text-sm font-medium text-gray-700">
              Recurring Request (Regular Supply)
            </span>
          </label>

          <Show when={formData.recurring}>
            <div class="ml-8">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Recurrence Pattern
              </label>
              <select
                value={formData.recurrence_pattern}
                onChange={(e) => setFormData('recurrence_pattern', e.currentTarget.value)}
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select pattern</option>
                <option value="weekly">Weekly</option>
                <option value="biweekly">Bi-weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          </Show>
        </div>

        {/* Notes */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Additional Notes
          </label>
          <textarea
            value={formData.notes}
            onInput={(e) => setFormData('notes', e.currentTarget.value)}
            rows={3}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            placeholder="Any special requirements or instructions..."
          />
        </div>

        {/* Submit Buttons */}
        <div class="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={loading()}
            class="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading() ? 'Submitting...' : 'Find Suppliers'}
          </button>
          
          <Show when={props.onCancel}>
            <button
              type="button"
              onClick={props.onCancel}
              class="px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </Show>
        </div>
      </form>
    </div>
  );
};

export default SupplyRequestForm;
