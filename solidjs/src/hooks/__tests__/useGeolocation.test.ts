import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@solidjs/testing-library';
import { useGeolocation } from '../useGeolocation';

describe('useGeolocation', () => {
  let mockGeolocation: any;
  let mockPermissions: any;

  beforeEach(() => {
    // Mock geolocation API
    mockGeolocation = {
      getCurrentPosition: vi.fn(),
      watchPosition: vi.fn(),
      clearWatch: vi.fn(),
    };

    // Mock permissions API
    mockPermissions = {
      query: vi.fn(),
    };

    Object.defineProperty(global.navigator, 'geolocation', {
      value: mockGeolocation,
      writable: true,
      configurable: true,
    });

    Object.defineProperty(global.navigator, 'permissions', {
      value: mockPermissions,
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('isSupported', () => {
    it('should return true when geolocation is supported', () => {
      const { result } = renderHook(() => useGeolocation());
      expect(result.isSupported()).toBe(true);
    });

    it('should return false when geolocation is not supported', () => {
      // @ts-ignore
      delete global.navigator.geolocation;
      const { result } = renderHook(() => useGeolocation());
      expect(result.isSupported()).toBe(false);
    });
  });

  describe('getCurrentPosition', () => {
    it('should set loading state when requesting position', async () => {
      const { result } = renderHook(() => useGeolocation());
      
      result.getCurrentPosition();
      
      await waitFor(() => {
        expect(result.state().loading).toBe(true);
      });
    });

    it('should capture location successfully', async () => {
      const mockPosition = {
        coords: {
          latitude: 28.6139,
          longitude: 77.2090,
          accuracy: 10,
        },
      };

      mockGeolocation.getCurrentPosition.mockImplementation((success: any) => {
        success(mockPosition);
      });

      const { result } = renderHook(() => useGeolocation());
      
      await result.getCurrentPosition();
      
      await waitFor(() => {
        expect(result.state().latitude).toBe(28.6139);
        expect(result.state().longitude).toBe(77.2090);
        expect(result.state().accuracy).toBe(10);
        expect(result.state().loading).toBe(false);
        expect(result.state().error).toBe(null);
        expect(result.state().permissionStatus).toBe('granted');
      });
    });

    it('should handle permission denied error', async () => {
      const mockError = {
        code: 1, // PERMISSION_DENIED
        message: 'User denied geolocation',
        PERMISSION_DENIED: 1,
        POSITION_UNAVAILABLE: 2,
        TIMEOUT: 3,
      };

      mockGeolocation.getCurrentPosition.mockImplementation((_: any, error: any) => {
        error(mockError);
      });

      const { result } = renderHook(() => useGeolocation());
      
      await result.getCurrentPosition();
      
      await waitFor(() => {
        expect(result.state().error).toContain('Location access denied');
        expect(result.state().loading).toBe(false);
        expect(result.state().permissionStatus).toBe('denied');
      });
    });

    it('should handle position unavailable error', async () => {
      const mockError = {
        code: 2, // POSITION_UNAVAILABLE
        message: 'Position unavailable',
        PERMISSION_DENIED: 1,
        POSITION_UNAVAILABLE: 2,
        TIMEOUT: 3,
      };

      mockGeolocation.getCurrentPosition.mockImplementation((_: any, error: any) => {
        error(mockError);
      });

      const { result } = renderHook(() => useGeolocation());
      
      await result.getCurrentPosition();
      
      await waitFor(() => {
        expect(result.state().error).toContain('Location information unavailable');
        expect(result.state().loading).toBe(false);
      });
    });

    it('should handle timeout error', async () => {
      const mockError = {
        code: 3, // TIMEOUT
        message: 'Timeout',
        PERMISSION_DENIED: 1,
        POSITION_UNAVAILABLE: 2,
        TIMEOUT: 3,
      };

      mockGeolocation.getCurrentPosition.mockImplementation((_: any, error: any) => {
        error(mockError);
      });

      const { result } = renderHook(() => useGeolocation());
      
      await result.getCurrentPosition();
      
      await waitFor(() => {
        expect(result.state().error).toContain('Location request timed out');
        expect(result.state().loading).toBe(false);
      });
    });

    it('should handle unsupported browser', async () => {
      // @ts-ignore
      delete global.navigator.geolocation;

      const { result } = renderHook(() => useGeolocation());
      
      await result.getCurrentPosition();
      
      await waitFor(() => {
        expect(result.state().error).toContain('Geolocation is not supported');
        expect(result.state().permissionStatus).toBe('unsupported');
      });
    });
  });

  describe('watchPosition', () => {
    it('should start watching position', () => {
      const watchId = 123;
      mockGeolocation.watchPosition.mockReturnValue(watchId);

      const { result } = renderHook(() => useGeolocation());
      
      result.watchPosition();
      
      expect(mockGeolocation.watchPosition).toHaveBeenCalled();
    });

    it('should clear existing watch before starting new one', () => {
      const watchId1 = 123;
      const watchId2 = 456;
      mockGeolocation.watchPosition
        .mockReturnValueOnce(watchId1)
        .mockReturnValueOnce(watchId2);

      const { result } = renderHook(() => useGeolocation());
      
      result.watchPosition();
      result.watchPosition();
      
      expect(mockGeolocation.clearWatch).toHaveBeenCalledWith(watchId1);
      expect(mockGeolocation.watchPosition).toHaveBeenCalledTimes(2);
    });
  });

  describe('clearWatch', () => {
    it('should clear watch when called', () => {
      const watchId = 123;
      mockGeolocation.watchPosition.mockReturnValue(watchId);

      const { result } = renderHook(() => useGeolocation());
      
      result.watchPosition();
      result.clearWatch();
      
      expect(mockGeolocation.clearWatch).toHaveBeenCalledWith(watchId);
    });

    it('should not throw error when no watch is active', () => {
      const { result } = renderHook(() => useGeolocation());
      
      expect(() => result.clearWatch()).not.toThrow();
    });
  });

  describe('reset', () => {
    it('should reset state to initial values', async () => {
      const mockPosition = {
        coords: {
          latitude: 28.6139,
          longitude: 77.2090,
          accuracy: 10,
        },
      };

      mockGeolocation.getCurrentPosition.mockImplementation((success: any) => {
        success(mockPosition);
      });

      const { result } = renderHook(() => useGeolocation());
      
      await result.getCurrentPosition();
      
      await waitFor(() => {
        expect(result.state().latitude).toBe(28.6139);
      });

      result.reset();
      
      await waitFor(() => {
        expect(result.state().latitude).toBe(null);
        expect(result.state().longitude).toBe(null);
        expect(result.state().accuracy).toBe(null);
        expect(result.state().error).toBe(null);
        expect(result.state().loading).toBe(false);
      });
    });
  });

  describe('setManualCoordinates', () => {
    it('should set coordinates manually', () => {
      const { result } = renderHook(() => useGeolocation());
      
      result.setManualCoordinates(28.6139, 77.2090);
      
      expect(result.state().latitude).toBe(28.6139);
      expect(result.state().longitude).toBe(77.2090);
      expect(result.state().accuracy).toBe(null);
      expect(result.state().error).toBe(null);
      expect(result.state().loading).toBe(false);
    });

    it('should preserve permission status when setting manual coordinates', async () => {
      const mockPermissionResult = {
        state: 'granted',
        addEventListener: vi.fn(),
      };

      mockPermissions.query.mockResolvedValue(mockPermissionResult);

      const { result } = renderHook(() => useGeolocation());
      
      await waitFor(() => {
        expect(result.state().permissionStatus).toBe('granted');
      });

      result.setManualCoordinates(28.6139, 77.2090);
      
      expect(result.state().permissionStatus).toBe('granted');
    });
  });

  describe('options', () => {
    it('should use custom options', async () => {
      const customOptions = {
        enableHighAccuracy: false,
        timeout: 5000,
        maximumAge: 1000,
      };

      mockGeolocation.getCurrentPosition.mockImplementation((success: any) => {
        success({
          coords: {
            latitude: 28.6139,
            longitude: 77.2090,
            accuracy: 10,
          },
        });
      });

      const { result } = renderHook(() => useGeolocation(customOptions));
      
      await result.getCurrentPosition();
      
      expect(mockGeolocation.getCurrentPosition).toHaveBeenCalledWith(
        expect.any(Function),
        expect.any(Function),
        expect.objectContaining({
          enableHighAccuracy: false,
          timeout: 5000,
          maximumAge: 1000,
        })
      );
    });

    it('should use default options when not provided', async () => {
      mockGeolocation.getCurrentPosition.mockImplementation((success: any) => {
        success({
          coords: {
            latitude: 28.6139,
            longitude: 77.2090,
            accuracy: 10,
          },
        });
      });

      const { result } = renderHook(() => useGeolocation());
      
      await result.getCurrentPosition();
      
      expect(mockGeolocation.getCurrentPosition).toHaveBeenCalledWith(
        expect.any(Function),
        expect.any(Function),
        expect.objectContaining({
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        })
      );
    });
  });

  describe('cleanup', () => {
    it('should clear watch on unmount', () => {
      const watchId = 123;
      mockGeolocation.watchPosition.mockReturnValue(watchId);

      // @solidjs/testing-library's renderHook returns `cleanup` (disposes the hook's owner)
      const { result, cleanup: unmount } = renderHook(() => useGeolocation());
      
      result.watchPosition();
      unmount();
      
      expect(mockGeolocation.clearWatch).toHaveBeenCalledWith(watchId);
    });
  });
});
