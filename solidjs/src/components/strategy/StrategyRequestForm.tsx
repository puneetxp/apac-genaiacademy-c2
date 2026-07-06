/**
 * Strategy Request Form Component
 * Form to request annual crop strategy generation
 */

import { Component, createSignal, Show } from 'solid-js';
import { LoadingSpinner } from '../ui/LoadingSpinner';

interface StrategyRequestFormProps {
  farmId: number;
  farmName: string;
  onSubmit: (
    previousCrops?: string,
    budgetPerAcre?: number,
    preferredCrop?: string,
    customMessage?: string
  ) => void;
  onCancel?: () => void;
  isLoading: boolean;
}

const StrategyRequestForm: Component<StrategyRequestFormProps> = (props) => {
  const [previousCrops, setPreviousCrops] = createSignal('');
  const [budgetPerAcre, setBudgetPerAcre] = createSignal<number | undefined>(undefined);
  const [customMessage, setCustomMessage] = createSignal('');

  const handleSubmit = (e: Event) => {
    e.preventDefault();
    props.onSubmit(
      previousCrops() || undefined,
      budgetPerAcre(),
      undefined,
      customMessage() || undefined
    );
  };

  return (
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold text-gray-800 mb-2">
        Generate Annual Crop Strategy
      </h2>
      <p class="text-gray-600 mb-6">
        Get AI-powered recommendations for Kharif, Rabi, and Zaid seasons for {props.farmName}
      </p>

      <form onSubmit={handleSubmit} class="space-y-6">
        {/* Previous Crops */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Previous Crops (Optional)
          </label>
          <input
            type="text"
            value={previousCrops()}
            onInput={(e) => setPreviousCrops(e.currentTarget.value)}
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="e.g., Wheat, Rice (last 2 seasons)"
          />
          <p class="mt-1 text-sm text-gray-500">
            Enter crops grown in the last 1-2 seasons for better recommendations
          </p>
        </div>

        {/* Budget Per Acre */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Investment Capacity per Acre (₹) (Optional)
          </label>
          <input
            type="number"
            step="1000"
            min="0"
            value={budgetPerAcre() || ''}
            onInput={(e) => setBudgetPerAcre(parseFloat(e.currentTarget.value) || undefined)}
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="e.g., 50000"
          />
          <p class="mt-1 text-sm text-gray-500">
            Your budget per acre helps us recommend crops within your investment capacity
          </p>
        </div>

        {/* Info Box */}
        <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
          <h3 class="text-sm font-semibold text-blue-900 mb-2">
            What you'll get:
          </h3>
          <ul class="text-sm text-blue-800 space-y-1">
            <li>• Kharif season crop recommendations (June-October)</li>
            <li>• Rabi season crop recommendations (November-April)</li>
            <li>• Zaid season options (May-June)</li>
            <li>• Expected yields and profit estimates</li>
            <li>• Month-by-month action plan</li>
            <li>• Alternative crop options</li>
            <li>• Risk assessment and mitigation strategies</li>
          </ul>
        </div>

        {/* Custom Message for AI */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Custom Message to AI (Optional)
          </label>
          <textarea
            value={customMessage()}
            onInput={(e) => setCustomMessage(e.currentTarget.value)}
            rows={4}
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Share specific challenges, crop preferences, or market commitments you want the AI to consider."
          />
          <p class="mt-1 text-sm text-gray-500">
            This note is passed directly to the AI so it can personalize the strategy for your situation.
          </p>
        </div>

        {/* Buttons */}
        <div class="flex gap-3">
          <Show when={props.onCancel}>
            <button
              type="button"
              onClick={props.onCancel}
              class="flex-1 py-3 px-4 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-700 font-medium rounded-md transition-colors"
              disabled={props.isLoading}
            >
              Cancel
            </button>
          </Show>
          <button
            type="submit"
            disabled={props.isLoading}
            class="flex-1 py-3 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors flex items-center justify-center gap-2"
          >
            <Show when={props.isLoading}>
              <LoadingSpinner size="sm" color="white" />
            </Show>
            {props.isLoading ? 'Generating Strategy...' : 'Generate Strategy'}
          </button>
        </div>

        {/* Loading Progress */}
        <Show when={props.isLoading}>
          <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
              <div class="flex-1">
                <p class="text-sm font-medium text-yellow-900 mb-1">
                  Analyzing your farm profile...
                </p>
                <p class="text-xs text-yellow-800">
                  This may take up to 10 seconds. Our AI is analyzing regional patterns, soil conditions, and market trends to create your personalized strategy.
                </p>
              </div>
            </div>
          </div>
        </Show>
      </form>
    </div>
  );
};

export default StrategyRequestForm;
