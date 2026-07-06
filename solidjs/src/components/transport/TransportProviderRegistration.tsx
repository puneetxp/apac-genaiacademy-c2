import { Component, createSignal, For } from 'solid-js';
import { createStore } from 'solid-js/store';

interface TransportProviderFormData {
  company_name: string;
  contact_person: string;
  contact_phone: string;
  contact_email: string;
  service_areas: string[];
  vehicle_types: string[];
  livestock_specialization: string[];
  base_rate_per_km: number;
  minimum_charge: number;
  max_capacity_animals: number;
  insurance_available: boolean;
  insurance_rate_percentage: number;
  license_number: string;
}

const TransportProviderRegistration: Component = () => {
  const [formData, setFormData] = createStore<TransportProviderFormData>({
    company_name: '',
    contact_person: '',
    contact_phone: '',
    contact_email: '',
    service_areas: [],
    vehicle_types: [],
    livestock_specialization: [],
    base_rate_per_km: 0,
    minimum_charge: 0,
    max_capacity_animals: 0,
    insurance_available: false,
    insurance_rate_percentage: 0,
    license_number: ''
  });

  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [success, setSuccess] = createSignal(false);

  const vehicleTypeOptions = [
    { value: 'truck', label: 'Truck' },
    { value: 'tempo', label: 'Tempo' },
    { value: 'mini_truck', label: 'Mini Truck' },
    { value: 'specialized_livestock', label: 'Specialized Livestock Vehicle' }
  ];

  const livestockOptions = [
    { value: 'cattle', label: 'Cattle' },
    { value: 'buffalo', label: 'Buffalo' },
    { value: 'goat', label: 'Goat' },
    { value: 'sheep', label: 'Sheep' },
    { value: 'poultry', label: 'Poultry' }
  ];

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/transport/providers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...formData,
          user_id: parseInt(localStorage.getItem('user_id') || '0')
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to register provider');
      }

      setSuccess(true);
      setTimeout(() => {
        window.location.href = '/transport/dashboard';
      }, 2000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleVehicleType = (type: string) => {
    const current = formData.vehicle_types;
    if (current.includes(type)) {
      setFormData('vehicle_types', current.filter(t => t !== type));
    } else {
      setFormData('vehicle_types', [...current, type]);
    }
  };

  const toggleLivestockType = (type: string) => {
    const current = formData.livestock_specialization;
    if (current.includes(type)) {
      setFormData('livestock_specialization', current.filter(t => t !== type));
    } else {
      setFormData('livestock_specialization', [...current, type]);
    }
  };

  return (
    <div class="max-w-4xl mx-auto p-6">
      <h1 class="text-3xl font-bold mb-6">Register as Transport Provider</h1>

      {success() && (
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          Registration successful! Redirecting to dashboard...
        </div>
      )}

      {error() && (
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error()}
        </div>
      )}

      <form onSubmit={handleSubmit} class="space-y-6">
        {/* Company Information */}
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-xl font-semibold mb-4">Company Information</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-2">Company Name *</label>
              <input
                type="text"
                required
                value={formData.company_name}
                onInput={(e) => setFormData('company_name', e.currentTarget.value)}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Contact Person *</label>
              <input
                type="text"
                required
                value={formData.contact_person}
                onInput={(e) => setFormData('contact_person', e.currentTarget.value)}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Contact Phone *</label>
              <input
                type="tel"
                required
                value={formData.contact_phone}
                onInput={(e) => setFormData('contact_phone', e.currentTarget.value)}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Contact Email</label>
              <input
                type="email"
                value={formData.contact_email}
                onInput={(e) => setFormData('contact_email', e.currentTarget.value)}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">License Number</label>
              <input
                type="text"
                value={formData.license_number}
                onInput={(e) => setFormData('license_number', e.currentTarget.value)}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>
        </div>

        {/* Service Details */}
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-xl font-semibold mb-4">Service Details</h2>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Vehicle Types *</label>
              <div class="grid grid-cols-2 gap-2">
                <For each={vehicleTypeOptions}>
                  {(option) => (
                    <label class="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.vehicle_types.includes(option.value)}
                        onChange={() => toggleVehicleType(option.value)}
                        class="rounded text-green-600"
                      />
                      <span>{option.label}</span>
                    </label>
                  )}
                </For>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Livestock Specialization</label>
              <div class="grid grid-cols-2 gap-2">
                <For each={livestockOptions}>
                  {(option) => (
                    <label class="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.livestock_specialization.includes(option.value)}
                        onChange={() => toggleLivestockType(option.value)}
                        class="rounded text-green-600"
                      />
                      <span>{option.label}</span>
                    </label>
                  )}
                </For>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Service Areas (comma-separated) *</label>
              <textarea
                required
                placeholder="e.g., Maharashtra, Gujarat, Rajasthan"
                value={formData.service_areas.join(', ')}
                onInput={(e) => setFormData('service_areas', e.currentTarget.value.split(',').map(s => s.trim()))}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                rows="3"
              />
            </div>
          </div>
        </div>

        {/* Pricing */}
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-xl font-semibold mb-4">Pricing</h2>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium mb-2">Base Rate per KM (₹) *</label>
              <input
                type="number"
                required
                min="0"
                step="0.01"
                value={formData.base_rate_per_km}
                onInput={(e) => setFormData('base_rate_per_km', parseFloat(e.currentTarget.value))}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Minimum Charge (₹) *</label>
              <input
                type="number"
                required
                min="0"
                step="0.01"
                value={formData.minimum_charge}
                onInput={(e) => setFormData('minimum_charge', parseFloat(e.currentTarget.value))}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Max Capacity (Animals) *</label>
              <input
                type="number"
                required
                min="1"
                value={formData.max_capacity_animals}
                onInput={(e) => setFormData('max_capacity_animals', parseInt(e.currentTarget.value))}
                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>

          <div class="mt-4">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.insurance_available}
                onChange={(e) => setFormData('insurance_available', e.currentTarget.checked)}
                class="rounded text-green-600"
              />
              <span class="font-medium">Offer Insurance</span>
            </label>

            {formData.insurance_available && (
              <div class="mt-2">
                <label class="block text-sm font-medium mb-2">Insurance Rate (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.insurance_rate_percentage}
                  onInput={(e) => setFormData('insurance_rate_percentage', parseFloat(e.currentTarget.value))}
                  class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                />
              </div>
            )}
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
            type="submit"
            disabled={loading()}
            class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading() ? 'Registering...' : 'Register Provider'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TransportProviderRegistration;
