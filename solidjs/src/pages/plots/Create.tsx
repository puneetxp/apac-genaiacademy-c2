import { Component, createSignal, onMount, Show } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { FarmService } from '../../services/farm.service';
import type { Farm } from '../../shared/Interface/Model/Farm';
import apiClient from '../../lib/api-client';

/**
 * Create Plot Page - Full implementation
 */
const PlotCreatePage: Component = () => {
  const navigate = useNavigate();
  const [farms, setFarms] = createSignal<Farm[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [submitting, setSubmitting] = createSignal(false);
  const [error, setError] = createSignal<string>('');
  const [success, setSuccess] = createSignal(false);
  
  // Form data
  const [formData, setFormData] = createSignal({
    farm_id: '',
    plot_name: '',
    plot_area: '',
    soil_type: '',
    irrigation: '',
    sun_exposure: '',
    soil_ph: '',
    water_availability: '',
    notes: ''
  });

  onMount(async () => {
    try {
      const farmsList = await FarmService.getFarms();
      setFarms(farmsList);
    } catch (error) {
      console.error('Failed to load farms:', error);
      setError('Failed to load farms. Please try again.');
    } finally {
      setLoading(false);
    }
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(''); // Clear error on input change
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const data = formData();
      
      // Validation
      if (!data.farm_id) {
        throw new Error('Please select a farm');
      }
      if (!data.plot_name.trim()) {
        throw new Error('Please enter a plot name');
      }
      if (!data.plot_area || parseFloat(data.plot_area) <= 0) {
        throw new Error('Please enter a valid plot area');
      }
      if (!data.soil_type) {
        throw new Error('Please select a soil type');
      }
      if (!data.irrigation) {
        throw new Error('Please select an irrigation type');
      }

      // Prepare request body matching backend schema
      const plotData = {
        name: data.plot_name.trim(),
        area_acres: parseFloat(data.plot_area),
        soil_type: data.soil_type.toLowerCase(),
        irrigation_type: data.irrigation.toLowerCase()
      };

      // Make API call to create plot
      const url = `/farms/${data.farm_id}/plots`;
      await apiClient.post(url, plotData);

      setSuccess(true);
      
      // Redirect to dashboard after short delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);

    } catch (err: any) {
      console.error('Plot creation error:', err);
      setError(err.message || 'Failed to create plot. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div class="min-h-screen bg-gray-50">
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 class="text-2xl font-bold text-gray-900">Create New Plot</h1>
        </div>
      </header>
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-gray-600 mb-6">Add a new plot to your farm</p>
          
          <Show when={success()}>
            <div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
              <p class="text-sm text-green-800">
                Plot created successfully! Redirecting to dashboard...
              </p>
            </div>
          </Show>
          
          <Show when={error()}>
            <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p class="text-sm text-red-800">{error()}</p>
            </div>
          </Show>
          
          <Show when={!loading() && farms().length === 0}>
            <div class="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
              <p class="text-sm text-yellow-800">
                You need to register a farm first before creating plots.
              </p>
            </div>
          </Show>
          
          {/* Form elements for E2E tests */}
          <form onSubmit={handleSubmit} class="space-y-4 max-w-2xl">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Select Farm *</label>
                <select 
                  name="farm_id" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                  disabled={loading() || submitting()}
                  value={formData().farm_id}
                  onChange={(e) => handleInputChange('farm_id', e.currentTarget.value)}
                  required
                >
                  <option value="">Select a farm</option>
                  {farms().map((farm) => (
                    <option value={farm.id}>{farm.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Plot Name *</label>
                <input 
                  type="text" 
                  name="plot_name" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                  placeholder="e.g., North Field"
                  value={formData().plot_name}
                  onInput={(e) => handleInputChange('plot_name', e.currentTarget.value)}
                  disabled={submitting()}
                  required
                />
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Plot Area (acres) *</label>
                <input 
                  type="number" 
                  name="plot_area" 
                  step="0.1"
                  min="0.01"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                  placeholder="e.g., 1.5"
                  value={formData().plot_area}
                  onInput={(e) => handleInputChange('plot_area', e.currentTarget.value)}
                  disabled={submitting()}
                  required
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Soil Type *</label>
                <select 
                  name="soil_type" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                  value={formData().soil_type}
                  onChange={(e) => handleInputChange('soil_type', e.currentTarget.value)}
                  disabled={submitting()}
                  required
                >
                  <option value="">Select soil type</option>
                  <option value="loamy">Loamy</option>
                  <option value="clay">Clay</option>
                  <option value="sandy">Sandy</option>
                  <option value="silty">Silty</option>
                  <option value="peaty">Peaty</option>
                  <option value="chalky">Chalky</option>
                </select>
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Irrigation Type *</label>
                <select 
                  name="irrigation" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                  value={formData().irrigation}
                  onChange={(e) => handleInputChange('irrigation', e.currentTarget.value)}
                  disabled={submitting()}
                  required
                >
                  <option value="">Select irrigation type</option>
                  <option value="drip">Drip Irrigation</option>
                  <option value="sprinkler">Sprinkler</option>
                  <option value="canal">Canal</option>
                  <option value="rain-fed">Rain-fed</option>
                  <option value="borewell">Borewell</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Sun Exposure</label>
                <select 
                  name="sun_exposure" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                  value={formData().sun_exposure}
                  onChange={(e) => handleInputChange('sun_exposure', e.currentTarget.value)}
                  disabled={submitting()}
                >
                  <option value="">Select sun exposure</option>
                  <option value="full">Full Sun (6+ hours)</option>
                  <option value="partial">Partial Sun (3-6 hours)</option>
                  <option value="shade">Shade (less than 3 hours)</option>
                </select>
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Soil pH</label>
                <input 
                  type="number" 
                  name="soil_ph" 
                  step="0.1"
                  min="0"
                  max="14"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                  placeholder="e.g., 6.5"
                  value={formData().soil_ph}
                  onInput={(e) => handleInputChange('soil_ph', e.currentTarget.value)}
                  disabled={submitting()}
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Water Availability</label>
                <select 
                  name="water_availability" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                  value={formData().water_availability}
                  onChange={(e) => handleInputChange('water_availability', e.currentTarget.value)}
                  disabled={submitting()}
                >
                  <option value="">Select water availability</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700">Notes (Optional)</label>
              <textarea 
                name="notes" 
                rows="3"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="Any additional information about this plot..."
                value={formData().notes}
                onInput={(e) => handleInputChange('notes', e.currentTarget.value)}
                disabled={submitting()}
              />
            </div>
            
            <div class="flex gap-2 pt-4">
              <button
                type="submit"
                class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={submitting() || loading() || farms().length === 0}
              >
                {submitting() ? 'Creating...' : 'Create Plot'}
              </button>
              
              <button
                onClick={() => navigate('/dashboard')}
                type="button"
                class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
                disabled={submitting()}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default PlotCreatePage;
