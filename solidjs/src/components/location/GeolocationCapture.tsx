import { Component, Show, createSignal } from 'solid-js';
import { useGeolocation } from '../../hooks/useGeolocation';

interface GeolocationCaptureProps {
  onLocationCapture?: (latitude: number, longitude: number, accuracy: number | null) => void;
  showManualEntry?: boolean;
  enableHighAccuracy?: boolean;
}

/**
 * Geolocation capture component with permission flow and manual fallback
 * 
 * Features:
 * - User-friendly permission request messaging
 * - Loading indicators during capture
 * - Error handling with helpful messages
 * - Manual lat/long entry fallback
 * - Mobile-optimized UI
 */
export const GeolocationCapture: Component<GeolocationCaptureProps> = (props) => {
  const {
    state,
    getCurrentPosition,
    reset,
    setManualCoordinates,
    isSupported,
  } = useGeolocation({
    enableHighAccuracy: props.enableHighAccuracy ?? true,
    timeout: 10000,
    maximumAge: 0,
  });

  const [showManualEntry, setShowManualEntry] = createSignal(false);
  const [manualLat, setManualLat] = createSignal('');
  const [manualLng, setManualLng] = createSignal('');
  const [manualError, setManualError] = createSignal('');

  /**
   * Handle location capture button click
   */
  const handleCaptureLocation = async () => {
    await getCurrentPosition();
  };

  /**
   * Handle manual coordinate submission
   */
  const handleManualSubmit = () => {
    const lat = parseFloat(manualLat());
    const lng = parseFloat(manualLng());

    // Validate coordinates
    if (isNaN(lat) || isNaN(lng)) {
      setManualError('Please enter valid numbers for latitude and longitude');
      return;
    }

    if (lat < -90 || lat > 90) {
      setManualError('Latitude must be between -90 and 90');
      return;
    }

    if (lng < -180 || lng > 180) {
      setManualError('Longitude must be between -180 and 180');
      return;
    }

    setManualError('');
    setManualCoordinates(lat, lng);
    setShowManualEntry(false);

    // Notify parent component
    if (props.onLocationCapture) {
      props.onLocationCapture(lat, lng, null);
    }
  };

  /**
   * Handle successful location capture
   */
  const handleLocationSuccess = () => {
    const currentState = state();
    if (currentState.latitude && currentState.longitude && props.onLocationCapture) {
      props.onLocationCapture(
        currentState.latitude,
        currentState.longitude,
        currentState.accuracy
      );
    }
  };

  // Call success handler when location is captured
  const currentState = state();
  if (currentState.latitude && currentState.longitude && !currentState.loading) {
    handleLocationSuccess();
  }

  return (
    <div class="geolocation-capture bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div class="mb-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">
          Capture Location (Optional)
        </h3>
        <p class="text-sm text-gray-600">
          GPS coordinates enhance AI recommendations but are optional. You can also enter coordinates manually.
        </p>
      </div>

      {/* Unsupported Browser */}
      <Show when={!isSupported()}>
        <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <div>
              <h4 class="text-sm font-medium text-red-800 mb-1">Geolocation Not Supported</h4>
              <p class="text-sm text-red-700">
                Your browser doesn't support geolocation. Please enter coordinates manually or use a modern browser.
              </p>
            </div>
          </div>
        </div>
      </Show>

      {/* Permission Denied */}
      <Show when={state().permissionStatus === 'denied'}>
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <div>
              <h4 class="text-sm font-medium text-yellow-800 mb-1">Location Access Denied</h4>
              <p class="text-sm text-yellow-700">
                Please enable location permissions in your browser settings to use GPS capture.
              </p>
            </div>
          </div>
        </div>
      </Show>

      {/* Error Message */}
      <Show when={state().error}>
        <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <div>
              <h4 class="text-sm font-medium text-red-800 mb-1">Error</h4>
              <p class="text-sm text-red-700">{state().error}</p>
            </div>
          </div>
        </div>
      </Show>

      {/* Success Message */}
      <Show when={state().latitude && state().longitude && !state().loading}>
        <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <div class="flex-1">
              <h4 class="text-sm font-medium text-green-800 mb-2">Location Captured Successfully</h4>
              <div class="text-sm text-green-700 space-y-1">
                <p><span class="font-medium">Latitude:</span> {state().latitude?.toFixed(6)}</p>
                <p><span class="font-medium">Longitude:</span> {state().longitude?.toFixed(6)}</p>
                <Show when={state().accuracy}>
                  <p><span class="font-medium">Accuracy:</span> ±{state().accuracy?.toFixed(0)}m</p>
                </Show>
              </div>
            </div>
          </div>
        </div>
      </Show>

      {/* Capture Button */}
      <Show when={!showManualEntry()}>
        <div class="space-y-3">
          <button
            onClick={handleCaptureLocation}
            disabled={state().loading || !isSupported()}
            class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center"
          >
            <Show when={state().loading}>
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Capturing Location...
            </Show>
            <Show when={!state().loading}>
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {state().latitude ? 'Recapture Location' : 'Capture My Location'}
            </Show>
          </button>

          <Show when={props.showManualEntry !== false}>
            <button
              onClick={() => setShowManualEntry(true)}
              class="w-full bg-white hover:bg-gray-50 text-gray-700 font-medium py-3 px-4 rounded-lg border border-gray-300 transition-colors duration-200"
            >
              Enter Coordinates Manually
            </button>
          </Show>

          <Show when={state().latitude && state().longitude}>
            <button
              onClick={reset}
              class="w-full bg-white hover:bg-gray-50 text-red-600 font-medium py-2 px-4 rounded-lg border border-red-300 transition-colors duration-200 text-sm"
            >
              Clear Location
            </button>
          </Show>
        </div>
      </Show>

      {/* Manual Entry Form */}
      <Show when={showManualEntry()}>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Latitude
            </label>
            <input
              type="number"
              step="0.000001"
              placeholder="e.g., 28.6139"
              value={manualLat()}
              onInput={(e) => setManualLat(e.currentTarget.value)}
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <p class="text-xs text-gray-500 mt-1">Range: -90 to 90</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Longitude
            </label>
            <input
              type="number"
              step="0.000001"
              placeholder="e.g., 77.2090"
              value={manualLng()}
              onInput={(e) => setManualLng(e.currentTarget.value)}
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <p class="text-xs text-gray-500 mt-1">Range: -180 to 180</p>
          </div>

          <Show when={manualError()}>
            <div class="bg-red-50 border border-red-200 rounded-lg p-3">
              <p class="text-sm text-red-700">{manualError()}</p>
            </div>
          </Show>

          <div class="flex space-x-3">
            <button
              onClick={handleManualSubmit}
              class="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Set Coordinates
            </button>
            <button
              onClick={() => {
                setShowManualEntry(false);
                setManualError('');
                setManualLat('');
                setManualLng('');
              }}
              class="flex-1 bg-white hover:bg-gray-50 text-gray-700 font-medium py-2 px-4 rounded-lg border border-gray-300 transition-colors duration-200"
            >
              Cancel
            </button>
          </div>
        </div>
      </Show>

      {/* Help Text */}
      <div class="mt-4 pt-4 border-t border-gray-200">
        <p class="text-xs text-gray-500">
          <strong>Note:</strong> GPS coordinates are optional but provide more accurate AI recommendations. 
          The system works fully with pincode-based location when GPS is unavailable.
        </p>
      </div>
    </div>
  );
};
