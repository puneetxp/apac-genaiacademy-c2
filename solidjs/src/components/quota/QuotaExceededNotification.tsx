/**
 * QuotaExceededNotification Component
 * Displays notification when quota is exceeded with fallback explanation
 */

import { Component, Show } from 'solid-js';

interface QuotaExceededNotificationProps {
  quotaExceeded: boolean;
  nextResetTime: string;
  onDismiss?: () => void;
}

export const QuotaExceededNotification: Component<QuotaExceededNotificationProps> = (props) => {
  const formatResetTime = (resetTime: string) => {
    const date = new Date(resetTime);
    return date.toLocaleString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
      timeZone: 'Asia/Kolkata'
    });
  };

  const getTimeUntilReset = (resetTime: string) => {
    const date = new Date(resetTime);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours} hour${hours > 1 ? 's' : ''} and ${minutes} minute${minutes > 1 ? 's' : ''}`;
    }
    return `${minutes} minute${minutes > 1 ? 's' : ''}`;
  };

  return (
    <Show when={props.quotaExceeded}>
      <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg
              class="h-6 w-6 text-red-400"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-red-800">Daily AI Quota Exceeded</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>
                You've used all <strong>20 GPS-enhanced AI requests</strong> for today.
              </p>
              <p class="mt-2">
                <strong>Don't worry!</strong> You can still use the platform with pincode-based recommendations:
              </p>
              <ul class="mt-2 ml-4 list-disc space-y-1">
                <li>Recommendations based on your pincode, state, and district</li>
                <li>Regional crop analysis and market intelligence</li>
                <li>Seasonal guidance and weather patterns</li>
                <li>All marketplace features remain available</li>
              </ul>
            </div>
            <div class="mt-4 bg-red-100 rounded-md p-3">
              <div class="flex items-center">
                <svg
                  class="h-5 w-5 text-red-600 mr-2"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                    clip-rule="evenodd"
                  />
                </svg>
                <div class="text-sm text-red-800">
                  <p>
                    <strong>Quota resets in:</strong> {getTimeUntilReset(props.nextResetTime)}
                  </p>
                  <p class="text-xs mt-1">
                    Next reset at {formatResetTime(props.nextResetTime)} IST
                  </p>
                </div>
              </div>
            </div>
            <div class="mt-3">
              <div class="text-xs text-red-600">
                <p>
                  💡 <strong>Why the limit?</strong> GPS-enhanced AI recommendations use advanced analysis
                  and cost more to provide. The 20-request daily limit helps us keep the service affordable
                  while ensuring quality recommendations for all farmers.
                </p>
              </div>
            </div>
          </div>
          <Show when={props.onDismiss}>
            <div class="ml-auto pl-3">
              <button
                onClick={props.onDismiss}
                class="inline-flex text-red-400 hover:text-red-600 focus:outline-none"
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
