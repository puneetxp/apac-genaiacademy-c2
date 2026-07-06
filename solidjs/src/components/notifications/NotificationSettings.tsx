import { Component, createSignal, onMount, Show } from 'solid-js';
import { notificationService } from '../../services/notification.service';

const NotificationSettings: Component = () => {
  const [permissionState, setPermissionState] = createSignal(notificationService.getPermissionState());
  const [isSubscribed, setIsSubscribed] = createSignal(false);
  const [isLoading, setIsLoading] = createSignal(false);

  const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || '';

  onMount(async () => {
    // Check current subscription status
    const subscription = await notificationService.getPushSubscription();
    setIsSubscribed(!!subscription);
    setPermissionState(notificationService.getPermissionState());
  });

  const handleEnableNotifications = async () => {
    setIsLoading(true);

    try {
      const success = await notificationService.setupNotifications(VAPID_PUBLIC_KEY);

      if (success) {
        setIsSubscribed(true);
        setPermissionState(notificationService.getPermissionState());

        // Show confirmation
        await notificationService.showLocalNotification({
          title: 'Notifications Enabled',
          body: 'You will now receive important updates',
          type: 'general',
        });
      }
    } catch (error) {
      console.error('Failed to enable notifications:', error);
      alert('Failed to enable notifications. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisableNotifications = async () => {
    setIsLoading(true);

    try {
      const success = await notificationService.disableNotifications();

      if (success) {
        setIsSubscribed(false);
        setPermissionState(notificationService.getPermissionState());
      }
    } catch (error) {
      console.error('Failed to disable notifications:', error);
      alert('Failed to disable notifications. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestNotification = async () => {
    try {
      await notificationService.showLocalNotification({
        title: 'Test Notification',
        body: 'This is a test notification from CropSense AI',
        type: 'general',
        url: '/',
        actions: [
          { action: 'view', title: 'View' },
          { action: 'dismiss', title: 'Dismiss' },
        ],
      });
    } catch (error) {
      console.error('Failed to show test notification:', error);
      alert('Failed to show test notification. Please check permissions.');
    }
  };

  return (
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Notification Settings</h2>

      {/* Browser support check */}
      <Show
        when={permissionState().supported}
        fallback={
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p class="text-gray-700">
              Push notifications are not supported in your browser. Please use a modern browser like
              Chrome, Firefox, or Safari.
            </p>
          </div>
        }
      >
        {/* Current status */}
        <div class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">Notification Status</span>
            <Show
              when={permissionState().granted && isSubscribed()}
              fallback={
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Disabled
                </span>
              }
            >
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Enabled
              </span>
            </Show>
          </div>

          <Show when={permissionState().denied}>
            <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
              <p class="text-sm text-amber-800">
                <strong>Notifications Blocked:</strong> You have blocked notifications for this site.
                To enable them, please update your browser settings.
              </p>
            </div>
          </Show>
        </div>

        {/* Notification types */}
        <div class="mb-6">
          <h3 class="text-sm font-medium text-gray-700 mb-3">You will receive notifications for:</h3>
          <ul class="space-y-2">
            <li class="flex items-center text-sm text-gray-600">
              <svg
                class="w-5 h-5 text-green-600 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd"
                />
              </svg>
              Buyer interest in your marketplace listings
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg
                class="w-5 h-5 text-green-600 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd"
                />
              </svg>
              Crop strategy implementation reminders
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg
                class="w-5 h-5 text-green-600 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd"
                />
              </svg>
              Weather alerts and warnings
            </li>
            <li class="flex items-center text-sm text-gray-600">
              <svg
                class="w-5 h-5 text-green-600 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd"
                />
              </svg>
              Harvest timing reminders
            </li>
          </ul>
        </div>

        {/* Action buttons */}
        <div class="space-y-3">
          <Show
            when={permissionState().granted && isSubscribed()}
            fallback={
              <Show when={!permissionState().denied}>
                <button
                  onClick={handleEnableNotifications}
                  disabled={isLoading()}
                  class="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <Show when={isLoading()} fallback="Enable Notifications">
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
              </Show>
            }
          >
            <button
              onClick={handleTestNotification}
              class="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Send Test Notification
            </button>

            <button
              onClick={handleDisableNotifications}
              disabled={isLoading()}
              class="w-full px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Disable Notifications
            </button>
          </Show>
        </div>

        {/* Privacy note */}
        <div class="mt-6 pt-6 border-t border-gray-200">
          <p class="text-xs text-gray-500">
            <strong>Privacy:</strong> We only send notifications for important updates related to your
            farming activities. You can disable notifications at any time.
          </p>
        </div>
      </Show>
    </div>
  );
};

export default NotificationSettings;
