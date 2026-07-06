/**
 * QuotaHistory Page
 * Displays user's AI usage history and quota status
 */

import { Component, createSignal, onMount, Show, For } from 'solid-js';
import { AIQuotaService, QuotaStatus } from '../../services/ai-quota.service';
import { user } from '../../stores/auth.store';
import { QuotaStatus as QuotaStatusComponent } from '../../components/quota/QuotaStatus';
import { QuotaWarning } from '../../components/quota/QuotaWarning';
import { QuotaExceededNotification } from '../../components/quota/QuotaExceededNotification';

interface UsageHistoryEntry {
  date: string;
  gps_enhanced_requests: number;
  pincode_requests: number;
  total_requests: number;
}

export const QuotaHistory: Component = () => {
  const [quotaStatus, setQuotaStatus] = createSignal<QuotaStatus | null>(null);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);
  const [showWarning, setShowWarning] = createSignal(true);
  const [showExceededNotification, setShowExceededNotification] = createSignal(true);

  // Mock history data - in production, this would come from an API endpoint
  const [usageHistory] = createSignal<UsageHistoryEntry[]>([
    { date: '2026-02-28', gps_enhanced_requests: 15, pincode_requests: 42, total_requests: 57 },
    { date: '2026-02-27', gps_enhanced_requests: 18, pincode_requests: 35, total_requests: 53 },
    { date: '2026-02-26', gps_enhanced_requests: 12, pincode_requests: 28, total_requests: 40 },
    { date: '2026-02-25', gps_enhanced_requests: 20, pincode_requests: 45, total_requests: 65 },
    { date: '2026-02-24', gps_enhanced_requests: 8, pincode_requests: 22, total_requests: 30 },
  ]);

  const loadQuotaStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      // Get user ID from auth context
      const currentUser = user();
      if (!currentUser?.id) {
        setError('User not authenticated');
        return;
      }
      const status = await AIQuotaService.getQuotaStatus(currentUser.id);
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

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const getTotalUsage = () => {
    return usageHistory().reduce((sum, entry) => sum + entry.total_requests, 0);
  };

  const getAverageUsage = () => {
    const history = usageHistory();
    if (history.length === 0) return 0;
    return Math.round(getTotalUsage() / history.length);
  };

  return (
    <div class="container mx-auto px-4 py-6 max-w-6xl">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">AI Usage & Quota</h1>
        <p class="text-gray-600">
          Track your AI-powered recommendation usage and manage your daily quota
        </p>
      </div>

      {/* Notifications */}
      <Show when={quotaStatus()}>
        {(status) => (
          <>
            <Show when={showExceededNotification()}>
              <QuotaExceededNotification
                quotaExceeded={status().quota_exceeded}
                nextResetTime={status().next_reset}
                onDismiss={() => setShowExceededNotification(false)}
              />
            </Show>
            <Show when={showWarning()}>
              <QuotaWarning
                remainingQuota={status().remaining_quota}
                quotaLimit={status().quota_limit}
                onDismiss={() => setShowWarning(false)}
              />
            </Show>
          </>
        )}
      </Show>

      {/* Current Status */}
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div class="lg:col-span-2">
          <Show when={quotaStatus()}>
            {(status) => (
              <QuotaStatusComponent
                userId={status().user_id}
                showDetails={true}
              />
            )}
          </Show>
        </div>

        {/* Summary Stats */}
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-base font-semibold text-gray-900 mb-4">Usage Summary</h3>
          <div class="space-y-3">
            <div>
              <p class="text-xs text-gray-500">Total Requests (Last 5 days)</p>
              <p class="text-2xl font-bold text-gray-900">{getTotalUsage()}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Average per Day</p>
              <p class="text-xl font-semibold text-gray-700">{getAverageUsage()}</p>
            </div>
            <Show when={quotaStatus()}>
              {(status) => (
                <div>
                  <p class="text-xs text-gray-500">Today's Usage</p>
                  <p class="text-xl font-semibold text-gray-700">
                    {status().gps_enhanced_requests + status().pincode_requests}
                  </p>
                </div>
              )}
            </Show>
          </div>
        </div>
      </div>

      {/* Usage History Table */}
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
          <h3 class="text-lg font-medium text-gray-900">Usage History</h3>
          <p class="mt-1 text-sm text-gray-500">Your AI request history for the last 5 days</p>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  GPS-Enhanced
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pincode-Based
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <For each={usageHistory()}>
                {(entry) => (
                  <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatDate(entry.date)}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {entry.gps_enhanced_requests}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {entry.pincode_requests}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {entry.total_requests}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <Show
                        when={entry.gps_enhanced_requests >= 20}
                        fallback={
                          <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            Normal
                          </span>
                        }
                      >
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-orange-100 text-orange-800">
                          Quota Reached
                        </span>
                      </Show>
                    </td>
                  </tr>
                )}
              </For>
            </tbody>
          </table>
        </div>
      </div>

      {/* Information Panel */}
      <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-blue-900 mb-2">About AI Usage Quota</h4>
        <div class="text-sm text-blue-800 space-y-2">
          <p>
            <strong>GPS-Enhanced Requests:</strong> Use precise GPS coordinates for microclimate analysis
            and highly accurate recommendations. Limited to 20 per day to control costs.
          </p>
          <p>
            <strong>Pincode-Based Requests:</strong> Use regional data based on your pincode, state, and district.
            Unlimited usage with good accuracy for most farming decisions.
          </p>
          <p>
            <strong>Quota Reset:</strong> Your GPS-enhanced quota resets daily at midnight IST (Indian Standard Time).
          </p>
        </div>
      </div>
    </div>
  );
};
