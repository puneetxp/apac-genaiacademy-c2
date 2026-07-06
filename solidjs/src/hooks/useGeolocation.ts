import { createSignal, onCleanup } from 'solid-js';

export interface GeolocationState {
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  error: string | null;
  loading: boolean;
  permissionStatus: 'prompt' | 'granted' | 'denied' | 'unsupported' | null;
}

export interface GeolocationOptions {
  enableHighAccuracy?: boolean;
  timeout?: number;
  maximumAge?: number;
}

/**
 * SolidJS hook for browser geolocation capture with permission handling
 * 
 * Features:
 * - Permission request flow with user-friendly messaging
 * - Success and error state management
 * - Loading indicators during location capture
 * - Automatic cleanup of watchers
 * - Support for both one-time and continuous location tracking
 * 
 * @param options - Geolocation API options
 * @returns Geolocation state and control functions
 */
export function useGeolocation(options: GeolocationOptions = {}) {
  const [state, setState] = createSignal<GeolocationState>({
    latitude: null,
    longitude: null,
    accuracy: null,
    error: null,
    loading: false,
    permissionStatus: null,
  });

  let watchId: number | null = null;

  // Default options
  const defaultOptions: PositionOptions = {
    enableHighAccuracy: options.enableHighAccuracy ?? true,
    timeout: options.timeout ?? 10000, // 10 seconds
    maximumAge: options.maximumAge ?? 0,
  };

  /**
   * Check if geolocation is supported by the browser
   */
  const isSupported = (): boolean => {
    return 'geolocation' in navigator;
  };

  /**
   * Check current permission status (if Permissions API is available)
   */
  const checkPermissionStatus = async (): Promise<void> => {
    if (!isSupported()) {
      setState(prev => ({
        ...prev,
        permissionStatus: 'unsupported',
        error: 'Geolocation is not supported by your browser',
      }));
      return;
    }

    // Check if Permissions API is available
    if ('permissions' in navigator) {
      try {
        const result = await navigator.permissions.query({ name: 'geolocation' });
        setState(prev => ({
          ...prev,
          permissionStatus: result.state as 'prompt' | 'granted' | 'denied',
        }));

        // Listen for permission changes
        result.addEventListener('change', () => {
          setState(prev => ({
            ...prev,
            permissionStatus: result.state as 'prompt' | 'granted' | 'denied',
          }));
        });
      } catch (error) {
        // Permissions API not fully supported, will handle during getCurrentPosition
        console.warn('Permissions API not fully supported:', error);
      }
    }
  };

  /**
   * Success callback for geolocation
   */
  const onSuccess = (position: GeolocationPosition): void => {
    setState({
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      accuracy: position.coords.accuracy,
      error: null,
      loading: false,
      permissionStatus: 'granted',
    });
  };

  /**
   * Error callback for geolocation
   */
  const onError = (error: GeolocationPositionError): void => {
    let errorMessage: string;

    switch (error.code) {
      case error.PERMISSION_DENIED:
        errorMessage = 'Location access denied. Please enable location permissions in your browser settings.';
        setState(prev => ({
          ...prev,
          error: errorMessage,
          loading: false,
          permissionStatus: 'denied',
        }));
        break;
      case error.POSITION_UNAVAILABLE:
        errorMessage = 'Location information unavailable. Please check your device settings.';
        setState(prev => ({
          ...prev,
          error: errorMessage,
          loading: false,
        }));
        break;
      case error.TIMEOUT:
        errorMessage = 'Location request timed out. Please try again.';
        setState(prev => ({
          ...prev,
          error: errorMessage,
          loading: false,
        }));
        break;
      default:
        errorMessage = 'An unknown error occurred while getting your location.';
        setState(prev => ({
          ...prev,
          error: errorMessage,
          loading: false,
        }));
    }
  };

  /**
   * Get current position (one-time)
   */
  const getCurrentPosition = async (): Promise<void> => {
    if (!isSupported()) {
      setState(prev => ({
        ...prev,
        error: 'Geolocation is not supported by your browser',
        permissionStatus: 'unsupported',
      }));
      return;
    }

    setState(prev => ({
      ...prev,
      loading: true,
      error: null,
    }));

    try {
      navigator.geolocation.getCurrentPosition(onSuccess, onError, defaultOptions);
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to access geolocation',
        loading: false,
      }));
    }
  };

  /**
   * Start watching position (continuous updates)
   */
  const watchPosition = (): void => {
    if (!isSupported()) {
      setState(prev => ({
        ...prev,
        error: 'Geolocation is not supported by your browser',
        permissionStatus: 'unsupported',
      }));
      return;
    }

    // Clear existing watch if any
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId);
    }

    setState(prev => ({
      ...prev,
      loading: true,
      error: null,
    }));

    watchId = navigator.geolocation.watchPosition(onSuccess, onError, defaultOptions);
  };

  /**
   * Stop watching position
   */
  const clearWatch = (): void => {
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId);
      watchId = null;
    }
  };

  /**
   * Reset state to initial values
   */
  const reset = (): void => {
    clearWatch();
    setState({
      latitude: null,
      longitude: null,
      accuracy: null,
      error: null,
      loading: false,
      permissionStatus: null,
    });
  };

  /**
   * Manually set coordinates (fallback for manual entry)
   */
  const setManualCoordinates = (latitude: number, longitude: number): void => {
    setState({
      latitude,
      longitude,
      accuracy: null, // No accuracy for manual entry
      error: null,
      loading: false,
      permissionStatus: state().permissionStatus,
    });
  };

  // Check permission status on mount
  checkPermissionStatus();

  // Cleanup on unmount
  onCleanup(() => {
    clearWatch();
  });

  return {
    state,
    getCurrentPosition,
    watchPosition,
    clearWatch,
    reset,
    setManualCoordinates,
    isSupported,
  };
}
