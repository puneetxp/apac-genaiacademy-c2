/**
 * QuotaMonitoring Page (Admin)
 * Admin dashboard for monitoring AI quota usage across all users
 */

import { Component, createSignal, onMount, Show, For } from 'solid-js';
import { AIQuotaService, QuotaStatistics } from '../../services/ai-quota.service';

interface DateRange {
  start_date: string;
  end_date: string;
}

export const QuotaMonitoring: Component = () => {
  const [statistics, setStatistics] = createSignal<QuotaStatistics | null>(null);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);
  const [resetting, setResetting] = createSignal(false);
  const [resetSuccess, setResetSuccess] = createSignal<string | null>(null);

  // Date range for statistics
  const [dateRange, setDateRange] = createSignal<DateRange>({
    start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });

  const loadStatistics = async () => {
    try {
      setLoading(true);
      setError(null);
      const range = dateRange();
      const stats = await AIQuotaService.getStatistics(range.start_date, range.end_date);
      setStatistics(stats);
    } catch (err: any) {
      console.error('Failed to load statistics:', err);
      setError(err.message || 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  const handleResetQuota = async () => {
    if (!confirm('Are you sure you want to reset daily quota for all users? This action cannot be undone.')) {
      return;
    }

    try {
      setResetting(true);
      setResetSuccess(null);
      const result = await AIQuotaService.resetDailyQuota();
      setResetSuccess(`Successfully reset quota for ${result.users_reset} users at ${new Date(result.reset_time).toLocaleString('en-IN')}`);
      // Reload statistics after reset
      await loadStatistics();
    } catch (err: any) {
      console.error('Failed to reset quota:', err);
      setError(err.message || 'Failed to reset quota');
    } finally {
      setResetting(false);
    }
  };

  const handleDateRangeChange = (field: 'start_date' | 'end_date', value: string) => {
    setDateRange(prev => ({ ...prev, [field]: value }));
  };

  const handleApplyDateRange = () => {
    loadStatistics();
  };

  onMount(() => {
    loadStatistics();
  });

  return (
    <div class="container mx-auto px-4 py-6 max-w-7xl">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">AI Quota Monitoring</h1>
        <p class="text-gray-600">
          Monitor and manage AI usage quotas across all users
        </p>
      </div>

      {/* Success Message */}
      <Show when={resetSuccess()}>
        <div class="mb-4 bg-green-50 border border-green-200 rounded-md p-4">
          <div class="flex">
            <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <div class="ml-3">
              <p class="text-sm text-green-800">{resetSuccess()}</p>
            </div>
            <button
              onClick={() => setResetSuccess(null)}
              class="ml-auto text-green-400 hover:text-green-600"
            >
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </Show>

      {/* Error Message */}
      <Show when={error()}>
        <div class="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
          <p class="text-sm text-red-800">{error()}</p>
          <button
            onClick={loadStatistics}
            class="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Retry
          </button>
        </div>
      </Show>

      {/* Date Range Filter */}
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <h3 class="text-base font-semibold text-gray-900 mb-4">Date Range</h3>
        <div class="flex flex-wrap items-end gap-4">
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              type="date"
              value={dateRange().start_date}
              onChange={(e) => handleDateRangeChange('start_date', e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={dateRange().end_date}
              onChange={(e) => handleDateRangeChange('end_date', e.currentTarget.value)}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <button
            onClick={handleApplyDateRange}
            disabled={loading()}
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Apply
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <Show when={!loading() && statistics()}>
        {(stats) => (
          <>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-blue-100 rounded-md p-3">
                    <svg class="h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500">Total Users</p>
                    <p class="text-2xl font-bold text-gray-900">{stats().total_users}</p>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-green-100 rounded-md p-3">
                    <svg class="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500">GPS Requests</p>
                    <p class="text-2xl font-bold text-gray-900">{stats().total_gps_requests}</p>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-purple-100 rounded-md p-3">
                    <svg class="h-6 w-6 text-purple-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500">Pincode Requests</p>
                    <p class="text-2xl font-bold text-gray-900">{stats().total_pincode_requests}</p>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-orange-100 rounded-md p-3">
                    <svg class="h-6 w-6 text-orange-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-500">Avg per User</p>
                    <p class="text-2xl font-bold text-gray-900">{stats().average_requests_per_user.toFixed(1)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Admin Actions */}
            <div class="bg-white rounded-lg shadow p-6 mb-6">
              <h3 class="text-base font-semibold text-gray-900 mb-4">Admin Actions</h3>
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-700 mb-1">
                    <strong>Reset Daily Quota</strong>
                  </p>
                  <p class="text-xs text-gray-500">
                    Manually reset GPS-enhanced quota for all users. This is normally done automatically at midnight IST.
                  </p>
                </div>
                <button
                  onClick={handleResetQuota}
                  disabled={resetting()}
                  class="ml-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
                >
                  <Show when={resetting()}>
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </Show>
                  {resetting() ? 'Resetting...' : 'Reset Quota'}
                </button>
              </div>
            </div>

            {/* Usage Breakdown */}
            <div class="bg-white rounded-lg shadow p-6">
              <h3 class="text-base font-semibold text-gray-900 mb-4">Usage Breakdown</h3>
              <div class="space-y-4">
                <div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-600">GPS-Enhanced Requests</span>
                    <span class="font-medium text-gray-900">
                      {stats().total_gps_requests} ({((stats().total_gps_requests / (stats().total_gps_requests + stats().total_pincode_requests)) * 100).toFixed(1)}%)
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-green-500 h-2 rounded-full"
                      style={{ width: `${(stats().total_gps_requests / (stats().total_gps_requests + stats().total_pincode_requests)) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-600">Pincode-Based Requests</span>
                    <span class="font-medium text-gray-900">
                      {stats().total_pincode_requests} ({((stats().total_pincode_requests / (stats().total_gps_requests + stats().total_pincode_requests)) * 100).toFixed(1)}%)
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-purple-500 h-2 rounded-full"
                      style={{ width: `${(stats().total_pincode_requests / (stats().total_gps_requests + stats().total_pincode_requests)) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </Show>

      {/* Loading State */}
      <Show when={loading()}>
        <div class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        </div>
      </Show>
    </div>
  );
};
