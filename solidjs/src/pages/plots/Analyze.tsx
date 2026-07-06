import { Component } from 'solid-js';
import { useNavigate } from '@solidjs/router';

/**
 * Smart Plot Analysis Page (Stub with form elements for E2E tests)
 * TODO: Implement full plot analysis functionality with AI recommendations
 */
const PlotAnalyzePage: Component = () => {
  const navigate = useNavigate();

  return (
    <div class="min-h-screen bg-gray-50">
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 class="text-2xl font-bold text-gray-900">Smart Plot Analysis</h1>
        </div>
      </header>
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-gray-600 mb-6">AI-powered plot analysis feature</p>
          
          {/* Form elements for E2E tests */}
          <form class="space-y-4 max-w-md">
            <div>
              <label class="block text-sm font-medium text-gray-700">Select Farm</label>
              <select name="farm_id" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
                <option value="">Select a farm</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700">Plot Name</label>
              <input 
                type="text" 
                name="plot_name" 
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="Enter plot name"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700">Area (acres)</label>
              <input 
                type="number" 
                name="area" 
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="Enter area"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700">Soil Type</label>
              <select name="soil_type" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500">
                <option value="">Select soil type</option>
                <option value="loamy">Loamy</option>
                <option value="clay">Clay</option>
                <option value="sandy">Sandy</option>
              </select>
            </div>
            
            <div class="flex gap-2">
              <button
                type="button"
                class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Analyze Plot
              </button>
              
              <button
                onClick={() => navigate('/dashboard')}
                type="button"
                class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Back to Dashboard
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default PlotAnalyzePage;
