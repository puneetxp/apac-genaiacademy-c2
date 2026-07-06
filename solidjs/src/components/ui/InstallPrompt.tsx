import { Component, createSignal, onMount, Show } from 'solid-js';
import { FiDownload, FiX } from 'solid-icons/fi';

/**
 * Install Prompt Component
 * Shows a custom "Add to Home Screen" prompt for PWA installation
 */
const InstallPrompt: Component = () => {
  const [showPrompt, setShowPrompt] = createSignal(false);
  const [deferredPrompt, setDeferredPrompt] = createSignal<any>(null);

  onMount(() => {
    // Check if user has already dismissed the prompt
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    const installed = localStorage.getItem('pwa-installed');

    if (dismissed || installed) {
      return;
    }

    // Listen for the beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
      // Prevent the default browser prompt
      e.preventDefault();
      
      // Store the event for later use
      setDeferredPrompt(e);
      
      // Show our custom prompt after a short delay
      setTimeout(() => {
        setShowPrompt(true);
      }, 3000); // Show after 3 seconds
    });

    // Listen for app installed event
    window.addEventListener('appinstalled', () => {
      console.log('[PWA] App installed successfully');
      localStorage.setItem('pwa-installed', 'true');
      setShowPrompt(false);
      setDeferredPrompt(null);
    });
  });

  const handleInstall = async () => {
    const prompt = deferredPrompt();
    
    if (!prompt) {
      return;
    }

    // Show the browser's install prompt
    prompt.prompt();

    // Wait for the user's response
    const { outcome } = await prompt.userChoice;
    
    console.log(`[PWA] User response: ${outcome}`);

    if (outcome === 'accepted') {
      console.log('[PWA] User accepted the install prompt');
      localStorage.setItem('pwa-installed', 'true');
    } else {
      console.log('[PWA] User dismissed the install prompt');
    }

    // Clear the deferred prompt
    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-install-dismissed', 'true');
    
    // Allow showing again after 7 days
    setTimeout(() => {
      localStorage.removeItem('pwa-install-dismissed');
    }, 7 * 24 * 60 * 60 * 1000);
  };

  return (
    <Show when={showPrompt()}>
      <div class="fixed bottom-20 left-4 right-4 z-50 animate-slide-up">
        <div class="bg-white rounded-lg shadow-2xl border border-gray-200 p-4">
          <div class="flex items-start gap-3">
            {/* Icon */}
            <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <FiDownload class="w-6 h-6 text-green-600" />
            </div>

            {/* Content */}
            <div class="flex-1 min-w-0">
              <h3 class="text-base font-semibold text-gray-900 mb-1">
                Install CropSense AI
              </h3>
              <p class="text-sm text-gray-600 mb-3">
                Add to your home screen for quick access and offline use
              </p>

              {/* Actions */}
              <div class="flex gap-2">
                <button
                  onClick={handleInstall}
                  class="flex-1 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 active:bg-green-800 transition-colors"
                >
                  Install
                </button>
                <button
                  onClick={handleDismiss}
                  class="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 active:bg-gray-300 transition-colors"
                >
                  Not Now
                </button>
              </div>
            </div>

            {/* Close button */}
            <button
              onClick={handleDismiss}
              class="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close"
            >
              <FiX class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </Show>
  );
};

export default InstallPrompt;
