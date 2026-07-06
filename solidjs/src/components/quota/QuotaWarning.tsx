/**
 * QuotaWarning Component
 * Displays warning when quota is low (< 5 requests remaining)
 */

import { Component, Show } from 'solid-js';

interface QuotaWarningProps {
  remainingQuota: number;
  quotaLimit: number;
  onDismiss?: () => void;
}

export const QuotaWarning: Component<QuotaWarningProps> = (props) => {
  const shouldShowWarning = () => props.remainingQuota < 5 && props.remainingQuota > 0;

  return (
    <Show when={shouldShowWarning()}>
      <div class="bg-orange-50 border-l-4 border-orange-400 p-4 mb-4">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg
              class="h-5 w-5 text-orange-400"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-orange-800">Low AI Quota Warning</h3>
            <div class="mt-2 text-sm text-orange-700">
              <p>
                You have only <strong>{props.remainingQuota}</strong> GPS-enhanced AI requests remaining today.
              </p>
              <p class="mt-1">
                After your quota is used, the system will automatically switch to pincode-based recommendations,
                which are still accurate but use regional data instead of precise GPS location.
              </p>
            </div>
            <div class="mt-3">
              <div class="text-xs text-orange-600">
                <p>💡 <strong>Tip:</strong> Your quota resets at midnight IST (Indian Standard Time).</p>
              </div>
            </div>
          </div>
          <Show when={props.onDismiss}>
            <div class="ml-auto pl-3">
              <button
                onClick={props.onDismiss}
                class="inline-flex text-orange-400 hover:text-orange-600 focus:outline-none"
              >
                <span class="sr-only">Dismiss</span>
                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fill-rule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </Show>
        </div>
      </div>
    </Show>
  );
};
