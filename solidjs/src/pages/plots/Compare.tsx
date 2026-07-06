import { Component } from 'solid-js';
import { useNavigate } from '@solidjs/router';

/**
 * Compare Plots Page (Stub with form elements for E2E tests)
 * TODO: Implement full plot comparison functionality with AI recommendations
 */
const PlotComparePage: Component = () => {
  const navigate = useNavigate();

  return (
    <div class="min-h-screen bg-gray-50">
      <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 class="text-2xl font-bold text-gray-900">Compare Plots</h1>
        </div>
      </header>
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-gray-600 mb-6">Select plots to compare with AI insights</p>
          
          {/* Form elements for E2E tests */}
          <form class="space-y-4 max-w-md">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Select Plots to Compare</label>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input 
                    type="checkbox" 
                    value="plot-1" 
                    class="rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Plot 1</span>
                </label>
                <label class="flex items-center">
                  <input 
                    type="checkbox" 
                    value="plot-2" 
                    class="rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Plot 2</span>
                </label>
                <label class="flex items-center">
                  <input 
                    type="checkbox" 
                    value="plot-3" 
                    class="rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Plot 3</span>
                </label>
              </div>
            </div>
            
            <div class="flex gap-2">
              <button
                type="button"
                class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Compare Plots
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

export default PlotComparePage;
