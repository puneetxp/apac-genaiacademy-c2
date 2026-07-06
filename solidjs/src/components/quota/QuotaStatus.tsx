/**
 * QuotaStatus Component
 * Displays current AI usage quota status
 */

import { Component, Show, createSignal, onMount } from 'solid-js';
import { AIQuotaService, QuotaStatus as QuotaStatusType } from '../../services/ai-quota.service';

interface QuotaStatusProps {
  userId: number; // Integer user ID from users.id
  compact?: boolean;
  showDetails?: boolean;
}

export const QuotaStatus: Component<QuotaStatusProps> = (props) => {
  const [quotaStatus, setQuotaStatus] = createSignal<QuotaStatusType | null>(null);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);

  const loadQuotaStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const status = await AIQuotaService.getQuotaStatus(props.userId);
      setQuotaStatus(status);
    } catch (err: any) {
      console.error('Failed to load quota status:', err);
      setError(err.message || 'Failed to load quota status');
    } finally {
      setLoading(false);
    }
  };

  onMount(() => {
    loadQuotaStatus();
  });

  const getProgressPercentage = () => {
    const status = quotaStatus();
    if (!status) return 0;
    return (status.gps_enhanced_requests / status.quota_limit) * 100;
  };

  const getProgressColor = () => {
    const percentage = getProgressPercentage();
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 75) return 'bg-orange-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const formatResetTime = (resetTime: string) => {
    const date = new Date(resetTime);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  return (
    <div class={props.compact ? 'p-3' : 'p-4 bg-white rounded-lg shadow'}>
      <Show when={loading()}>
        <div class="flex items-center justify-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        </div>
      </Show>

      <Show when={error()}>
        <div class="bg-red-50 border border-red-200 rounded-md p-3">
          <p class="text-sm text-red-800">{error()}</p>
          <button
            onClick={loadQuotaStatus}
            class="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Retry
          </button>
        </div>
      </Show>

      <Show when={!loading() && !error() && quotaStatus()}>
        {(status) => (
          <div>
            <div class="flex items-center justify-between mb-2">
              <h3 class={props.compact ? 'text-sm font-medium text-gray-700' : 'text-base font-semibold text-gray-900'}>
                AI Usage Today
              </h3>
              <button
                onClick={loadQuotaStatus}
                class="text-xs text-gray-500 hover:text-gray-700"
                title="Refresh"
              >
                ↻
              </button>
            </div>

            {/* Progress Bar */}
            <div class="mb-3">
              <div class="flex items-center justify-between mb-1">
                <span class="text-sm text-gray-600">
                  {status().remaining_quota} of {status().quota_limit} remaining
                </span>
                <span class="text-xs text-gray-500">
                  {status().gps_enhanced_requests} used
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class={`${getProgressColor()} h-2 rounded-full transition-all duration-300`}
                  style={{ width: `${getProgressPercentage()}%` }}
                ></div>
              </div>
            </div>

            {/* Status Message */}
            <Show when={status().quota_exceeded}>
              <div class="bg-red-50 border border-red-200 rounded-md p-2 mb-3">
                <p class="text-xs text-red-800">
                  Daily quota exceeded. Using pincode-based recommendations.
                </p>
              </div>
            </Show>

            <Show when={!status().quota_exceeded && status().remaining_quota < 5}>
              <div class="bg-orange-50 border border-orange-200 rounded-md p-2 mb-3">
                <p class="text-xs text-orange-800">
                  Low quota: {status().remaining_quota} GPS-enhanced requests remaining
                </p>
              </div>
            </Show>

            {/* Details */}
            <Show when={props.showDetails !== false}>
              <div class="space-y-1 text-xs text-gray-600">
                <div class="flex justify-between">
                  <span>GPS-enhanced requests:</span>
                  <span class="font-medium">{status().gps_enhanced_requests}</span>
                </div>
                <div class="flex justify-between">
                  <span>Pincode-based requests:</span>
                  <span class="font-medium">{status().pincode_requests}</span>
                </div>
                <div class="flex justify-between">
                  <span>Resets in:</span>
                  <span class="font-medium">{formatResetTime(status().next_reset)}</span>
                </div>
              </div>
            </Show>
          </div>
        )}
      </Show>
    </div>
  );
};
