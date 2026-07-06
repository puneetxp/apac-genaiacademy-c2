import { Component, createSignal, Show, onMount } from 'solid-js';
import { notificationService } from '../../services/notification.service';

interface NotificationPermissionPromptProps {
  onPermissionGranted?: () => void;
  onPermissionDenied?: () => void;
  autoShow?: boolean;
}

const NotificationPermissionPrompt: Component<NotificationPermissionPromptProps> = (props) => {
  const [showPrompt, setShowPrompt] = createSignal(false);
  const [isLoading, setIsLoading] = createSignal(false);
  const [permissionState, setPermissionState] = createSignal(notificationService.getPermissionState());

  // VAPID public key - should be fetched from backend or environment variable
  const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || '';

  onMount(() => {
    // Check if we should show the prompt
    const state = notificationService.getPermissionState();
    setPermissionState(state);

    // Auto-show if enabled and permission is in prompt state
    if (props.autoShow && state.prompt && state.supported) {
      // Delay showing to avoid immediate popup
      setTimeout(() => {
        setShowPrompt(true);
      }, 2000);
    }
  });

  const handleEnableNotifications = async () => {
    setIsLoading(true);

    try {
      const success = await notificationService.setupNotifications(VAPID_PUBLIC_KEY);

      if (success) {
        setShowPrompt(false);
        setPermissionState(notificationService.getPermissionState());
        props.onPermissionGranted?.();

        // Show success notification
        await notificationService.showLocalNotification({
          title: 'Notifications Enabled!',
          body: 'You will now receive important updates about your crops and marketplace activity.',
          type: 'general',
          url: '/',
        });
      } else {
        props.onPermissionDenied?.();
      }
    } catch (error) {
      console.error('Failed to enable notifications:', error);
      props.onPermissionDenied?.();
    } finally {
      setIsLoading(false);
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    // Store dismissal in localStorage to avoid showing again too soon
    localStorage.setItem('notification-prompt-dismissed', Date.now().toString());
  };

  const handleManualShow = () => {
    const state = notificationService.getPermissionState();
    setPermissionState(state);

    if (state.supported && !state.denied) {
      setShowPrompt(true);
    }
  };

  return (
    <>
      {/* Manual trigger button (can be placed in settings) */}
      <Show when={!showPrompt() && permissionState().supported && !permissionState().granted}>
        <button
          onClick={handleManualShow}
          class="text-sm text-blue-600 hover:text-blue-700 underline"
        >
          Enable Notifications
        </button>
      </Show>

      {/* Permission prompt modal */}
      <Show when={showPrompt()}>
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            {/* Icon */}
            <div class="flex justify-center mb-4">
              <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <svg
                  class="w-8 h-8 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
              </div>
            </div>

            {/* Title */}
            <h3 class="text-xl font-semibold text-gray-900 text-center mb-2">
              Stay Updated with Notifications
            </h3>

            {/* Description */}
            <p class="text-gray-600 text-center mb-6">
              Get timely alerts about:
            </p>

            {/* Benefits list */}
            <ul class="space-y-3 mb-6">
              <li class="flex items-start">
                <svg
                  class="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clip-rule="evenodd"
                  />
                </svg>
                <span class="text-gray-700">Buyer interest in your crops</span>
              </li>
              <li class="flex items-start">
                <svg
                  class="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clip-rule="evenodd"
                  />
                </svg>
                <span class="text-gray-700">Crop strategy implementation reminders</span>
              </li>
              <li class="flex items-start">
                <svg
                  class="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clip-rule="evenodd"
                  />
                </svg>
                <span class="text-gray-700">Weather alerts and harvest reminders</span>
              </li>
              <li class="flex items-start">
                <svg
                  class="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clip-rule="evenodd"
                  />
                </svg>
                <span class="text-gray-700">Important marketplace updates</span>
              </li>
            </ul>

            {/* Action buttons */}
            <div class="flex gap-3">
              <button
                onClick={handleDismiss}
                disabled={isLoading()}
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Not Now
              </button>
              <button
                onClick={handleEnableNotifications}
                disabled={isLoading()}
                class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center"
              >
                <Show when={isLoading()} fallback="Enable">
                  <svg
                    class="animate-spin h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    />
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                </Show>
              </button>
            </div>

            {/* Privacy note */}
            <p class="text-xs text-gray-500 text-center mt-4">
              You can change notification preferences anytime in settings
            </p>
          </div>
        </div>
      </Show>

      {/* Not supported message */}
      <Show when={!permissionState().supported}>
        <div class="text-sm text-gray-500 text-center p-4 bg-gray-50 rounded-lg">
          Push notifications are not supported in your browser
        </div>
      </Show>

      {/* Permission denied message */}
      <Show when={permissionState().denied}>
        <div class="text-sm text-amber-700 bg-amber-50 p-4 rounded-lg">
          <p class="font-medium mb-1">Notifications Blocked</p>
          <p class="text-xs">
            To enable notifications, please update your browser settings and allow notifications for
            this site.
          </p>
        </div>
      </Show>
    </>
  );
};

export default NotificationPermissionPrompt;
