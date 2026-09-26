import { Component, createSignal } from 'solid-js';
import { GeolocationCapture } from '../../components/location/GeolocationCapture';

/**
 * Test page for geolocation capture functionality
 * 
 * This page demonstrates:
 * - Browser geolocation capture
 * - Permission handling
 * - Manual coordinate entry
 * - Mobile-optimized UI
 */
const GeolocationTest: Component = () => {
  const [capturedLocation, setCapturedLocation] = createSignal<{
    latitude: number;
    longitude: number;
    accuracy: number | null;
  } | null>(null);

  const handleLocationCapture = (latitude: number, longitude: number, accuracy: number | null) => {
    setCapturedLocation({ latitude, longitude, accuracy });
    console.log('Location captured:', { latitude, longitude, accuracy });
  };

  return (
    <div class="min-h-screen bg-gray-50 py-8 px-4">
      <div class="max-w-2xl mx-auto">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            Geolocation Test
          </h1>
          <p class="text-gray-600">
            Test browser geolocation capture with permission handling and manual fallback.
          </p>
        </div>

        <div class="mb-6">
          <GeolocationCapture
            onLocationCapture={handleLocationCapture}
            showManualEntry={true}
            enableHighAccuracy={true}
          />
        </div>

        {capturedLocation() && (
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h2 class="text-lg font-semibold text-blue-900 mb-4">
              Captured Location Data
            </h2>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="font-medium text-blue-800">Latitude:</span>
                <span class="text-blue-900">{capturedLocation()!.latitude.toFixed(6)}</span>
              </div>
              <div class="flex justify-between">
                <span class="font-medium text-blue-800">Longitude:</span>
                <span class="text-blue-900">{capturedLocation()!.longitude.toFixed(6)}</span>
              </div>
              {capturedLocation()!.accuracy && (
                <div class="flex justify-between">
                  <span class="font-medium text-blue-800">Accuracy:</span>
                  <span class="text-blue-900">±{(capturedLocation()!.accuracy ?? 0).toFixed(0)}m</span>
                </div>
              )}
            </div>
          </div>
        )}

        <div class="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Testing Instructions
          </h2>
          <div class="space-y-4 text-sm text-gray-700">
            <div>
              <h3 class="font-medium text-gray-900 mb-2">Desktop Testing:</h3>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li>Click "Capture My Location" to request browser permission</li>
                <li>Allow or deny permission to test different flows</li>
                <li>Try manual entry if permission is denied</li>
                <li>Test with browser location services disabled</li>
              </ul>
            </div>
            <div>
              <h3 class="font-medium text-gray-900 mb-2">Mobile Testing (Android/iOS):</h3>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li>Open this page on your mobile device</li>
                <li>Test with location services enabled/disabled</li>
                <li>Test with app permissions granted/denied</li>
                <li>Verify manual entry works on mobile keyboard</li>
                <li>Check loading indicators and error messages</li>
              </ul>
            </div>
            <div>
              <h3 class="font-medium text-gray-900 mb-2">Expected Behavior:</h3>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li>Permission prompt appears on first click</li>
                <li>Loading indicator shows during capture</li>
                <li>Success message displays with coordinates</li>
                <li>Error messages are user-friendly</li>
                <li>Manual entry validates coordinate ranges</li>
                <li>Clear button resets the state</li>
              </ul>
            </div>
          </div>
        </div>

        <div class="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <div>
              <h4 class="text-sm font-medium text-yellow-800 mb-1">Testing Note</h4>
              <p class="text-sm text-yellow-700">
                For mobile testing, you may need to access this page via HTTPS or localhost. 
                Some browsers restrict geolocation on insecure connections.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeolocationTest;
