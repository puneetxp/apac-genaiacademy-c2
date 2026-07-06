import { Component, createSignal, onMount, onCleanup, Show } from 'solid-js';
import { FiWifiOff, FiWifi } from 'solid-icons/fi';

/**
 * Offline Indicator Component
 * Shows connection status and queued actions
 */
const OfflineIndicator: Component = () => {
  const [isOnline, setIsOnline] = createSignal(navigator.onLine);
  const [showReconnected, setShowReconnected] = createSignal(false);
  const [queuedActions, setQueuedActions] = createSignal(0);

  onMount(() => {
    // Listen for online/offline events
    const handleOnline = () => {
      setIsOnline(true);
      setShowReconnected(true);
      
      // Check for queued actions
      checkQueuedActions();
      
      // Hide reconnected message after 3 seconds
      setTimeout(() => {
        setShowReconnected(false);
      }, 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowReconnected(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check initial queued actions
    checkQueuedActions();

    // Cleanup
    onCleanup(() => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    });
  });

  const checkQueuedActions = () => {
    try {
      const queue = localStorage.getItem('offline-queue');
      if (queue) {
        const actions = JSON.parse(queue);
        setQueuedActions(actions.length);
      } else {
        setQueuedActions(0);
      }
    } catch (error) {
      console.error('[Offline] Error checking queued actions:', error);
      setQueuedActions(0);
    }
  };

  return (
    <>
      {/* Offline Banner */}
      <Show when={!isOnline()}>
        <div class="fixed top-0 left-0 right-0 z-50 bg-yellow-500 text-white px-4 py-2 shadow-lg">
          <div class="flex items-center justify-center gap-2 text-sm font-medium">
            <FiWifiOff class="w-4 h-4" />
            <span>You're offline</span>
            <Show when={queuedActions() > 0}>
              <span class="ml-2 px-2 py-0.5 bg-yellow-600 rounded-full text-xs">
                {queuedActions()} queued
              </span>
            </Show>
          </div>
        </div>
      </Show>

      {/* Reconnected Banner */}
      <Show when={showReconnected()}>
        <div class="fixed top-0 left-0 right-0 z-50 bg-green-500 text-white px-4 py-2 shadow-lg animate-slide-down">
          <div class="flex items-center justify-center gap-2 text-sm font-medium">
            <FiWifi class="w-4 h-4" />
            <span>Back online</span>
            <Show when={queuedActions() > 0}>
              <span class="ml-2 text-xs">Syncing {queuedActions()} actions...</span>
            </Show>
          </div>
        </div>
      </Show>
    </>
  );
};

export default OfflineIndicator;
