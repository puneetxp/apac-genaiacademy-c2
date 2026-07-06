/**
 * API Client
 * Comprehensive fetch wrapper with authentication, error handling, retry logic, and caching
 * Compatible with FastAPI/httpx backend
 */

// Types
export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
  cacheEnabled?: boolean;
  cacheTTL?: number;
}

export interface RequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  params?: Record<string, string | number | boolean>;
  timeout?: number;
  retry?: boolean;
  cache?: boolean;
  cacheTTL?: number;
  requiresAuth?: boolean;
}

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Headers;
}

export interface ApiError {
  message: string;
  status?: number;
  statusText?: string;
  detail?: string;
  errors?: any;
}

interface CacheEntry {
  data: any;
  timestamp: number;
  ttl: number;
}

// Request/Response Interceptors
type RequestInterceptor = (config: RequestConfig, url: string) => Promise<RequestConfig> | RequestConfig;
type ResponseInterceptor = (response: Response) => Promise<Response> | Response;
type ErrorInterceptor = (error: ApiError) => Promise<never> | never;

/**
 * API Client Class
 * Provides comprehensive HTTP client with interceptors, retry logic, and caching
 */
export class ApiClient {
  private config: Required<ApiClientConfig>;
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private errorInterceptors: ErrorInterceptor[] = [];
  private cache: Map<string, CacheEntry> = new Map();
  private pendingRequests: Map<string, Promise<any>> = new Map();

  constructor(config: ApiClientConfig) {
    this.config = {
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      retryAttempts: config.retryAttempts || 3,
      retryDelay: config.retryDelay || 1000,
      cacheEnabled: config.cacheEnabled !== false,
      cacheTTL: config.cacheTTL || 300000, // 5 minutes default
    };

    // Setup default interceptors
    this.setupDefaultInterceptors();
  }

  /**
   * Setup default request/response interceptors
   */
  private setupDefaultInterceptors(): void {
    // Request interceptor: Add JWT token
    this.addRequestInterceptor(async (config, url) => {
      if (config.requiresAuth !== false) {
        const token = this.getAuthToken();
        if (token) {
          config.headers = {
            ...config.headers,
            'Authorization': `Bearer ${token}`,
          };
        }
      }
      return config;
    });

    // Request interceptor: Add default headers
    this.addRequestInterceptor((config) => {
      config.headers = {
        'Content-Type': 'application/json',
        ...config.headers,
      };
      return config;
    });

    // Response interceptor: Handle token refresh
    this.addResponseInterceptor(async (response) => {
      if (response.status === 401) {
        // Token expired, try to refresh
        const refreshed = await this.refreshAuthToken();
        if (refreshed) {
          // Retry the original request with new token
          throw new Error('TOKEN_REFRESHED');
        }
      }
      return response;
    });

    // Error interceptor: Format errors
    this.addErrorInterceptor((error) => {
      console.error('API Error:', error);
      throw error;
    });
  }

  /**
   * Add request interceptor
   */
  addRequestInterceptor(interceptor: RequestInterceptor): void {
    this.requestInterceptors.push(interceptor);
  }

  /**
   * Add response interceptor
   */
  addResponseInterceptor(interceptor: ResponseInterceptor): void {
    this.responseInterceptors.push(interceptor);
  }

  /**
   * Add error interceptor
   */
  addErrorInterceptor(interceptor: ErrorInterceptor): void {
    this.errorInterceptors.push(interceptor);
  }

  /**
   * Get auth token from localStorage
   */
  private getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Refresh auth token
   */
  private async refreshAuthToken(): Promise<boolean> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      const username = localStorage.getItem('username');

      if (!refreshToken || !username) {
        return false;
      }

      // Use baseURL which already includes /api/v1
      const response = await fetch(`${this.config.baseURL}/auth/refresh-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, refresh_token: refreshToken }),
      });

      if (!response.ok) {
        // Refresh failed, clear tokens
        this.clearAuthTokens();
        return false;
      }

      const tokens = await response.json();
      this.storeAuthTokens(tokens, username);
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearAuthTokens();
      return false;
    }
  }

  /**
   * Store auth tokens
   */
  private storeAuthTokens(tokens: any, username: string): void {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('id_token', tokens.id_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    localStorage.setItem('username', username);
    localStorage.setItem('token_expires_at', String(Date.now() + tokens.expires_in * 1000));
  }

  /**
   * Clear auth tokens
   */
  private clearAuthTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    localStorage.removeItem('token_expires_at');
  }

  /**
   * Build full URL with query parameters
   */
  private buildURL(endpoint: string, params?: Record<string, string | number | boolean>): string {
    // Ensure endpoint doesn't start with / if baseURL ends with /
    // and vice versa to avoid double slashes or missing slashes
    let fullPath = this.config.baseURL;
    if (!fullPath.endsWith('/') && !endpoint.startsWith('/')) {
      fullPath += '/';
    } else if (fullPath.endsWith('/') && endpoint.startsWith('/')) {
      endpoint = endpoint.slice(1);
    }
    fullPath += endpoint;
    
    console.log('🔍 buildURL - endpoint:', endpoint);
    console.log('🔍 buildURL - baseURL:', this.config.baseURL);
    console.log('🔍 buildURL - fullPath:', fullPath);
    
    const url = new URL(fullPath);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    const finalUrl = url.toString();
    console.log('🔍 buildURL - finalUrl:', finalUrl);
    return finalUrl;
  }

  /**
   * Generate cache key
   */
  private getCacheKey(url: string, config: RequestConfig): string {
    const method = config.method || 'GET';
    const body = config.body ? JSON.stringify(config.body) : '';
    return `${method}:${url}:${body}`;
  }

  /**
   * Get cached response
   */
  private getCachedResponse(key: string): any | null {
    if (!this.config.cacheEnabled) return null;

    const entry = this.cache.get(key);
    if (!entry) return null;

    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  /**
   * Set cached response
   */
  private setCachedResponse(key: string, data: any, ttl: number): void {
    if (!this.config.cacheEnabled) return;

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Clear cache by pattern
   */
  clearCacheByPattern(pattern: RegExp): void {
    for (const key of this.cache.keys()) {
      if (pattern.test(key)) {
        this.cache.delete(key);
      }
    }
  }

  /**
   * Execute request with retry logic
   */
  private async executeWithRetry<T>(
    url: string,
    config: RequestConfig,
    attempt: number = 1
  ): Promise<ApiResponse<T>> {
    try {
      // Apply request interceptors
      let processedConfig = config;
      for (const interceptor of this.requestInterceptors) {
        processedConfig = await interceptor(processedConfig, url);
      }

      // Create abort controller for timeout
      const controller = new AbortController();
      const timeout = processedConfig.timeout || this.config.timeout;
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      // Make request
      console.log(`🌐 Making ${processedConfig.method || 'GET'} request to:`, url);
      const response = await fetch(url, {
        method: processedConfig.method || 'GET',
        headers: processedConfig.headers,
        body: processedConfig.body ? JSON.stringify(processedConfig.body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Apply response interceptors
      let processedResponse = response;
      for (const interceptor of this.responseInterceptors) {
        processedResponse = await interceptor(processedResponse);
      }

      // Handle non-OK responses
      if (!processedResponse.ok) {
        const errorData = await this.parseErrorResponse(processedResponse);
        const error: ApiError = {
          message: errorData.detail || errorData.message || processedResponse.statusText,
          status: processedResponse.status,
          statusText: processedResponse.statusText,
          detail: errorData.detail,
          errors: errorData.errors,
        };

        // Apply error interceptors
        for (const interceptor of this.errorInterceptors) {
          await interceptor(error);
        }

        throw error;
      }

      // Parse response
      const data = await this.parseResponse<T>(processedResponse);

      return {
        data,
        status: processedResponse.status,
        statusText: processedResponse.statusText,
        headers: processedResponse.headers,
      };
    } catch (error: any) {
      // Handle token refresh retry
      if (error.message === 'TOKEN_REFRESHED' && attempt === 1) {
        return this.executeWithRetry<T>(url, config, attempt + 1);
      }

      // Handle timeout
      if (error.name === 'AbortError') {
        const timeoutError: ApiError = {
          message: 'Request timeout',
          status: 408,
          statusText: 'Request Timeout',
        };
        throw timeoutError;
      }

      // Retry on network errors
      const shouldRetry = config.retry !== false && 
                         attempt < this.config.retryAttempts &&
                         this.isRetryableError(error);

      if (shouldRetry) {
        const delay = this.config.retryDelay * attempt;
        await this.sleep(delay);
        return this.executeWithRetry<T>(url, config, attempt + 1);
      }

      throw error;
    }
  }

  /**
   * Check if error is retryable
   */
  private isRetryableError(error: any): boolean {
    // Retry on network errors and 5xx server errors
    return (
      !error.status ||
      error.status >= 500 ||
      error.message === 'Failed to fetch' ||
      error.message === 'Network request failed'
    );
  }

  /**
   * Parse response body
   */
  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    
    if (contentType?.includes('application/json')) {
      return response.json();
    }
    
    if (contentType?.includes('text/')) {
      return response.text() as any;
    }
    
    return response.blob() as any;
  }

  /**
   * Parse error response
   */
  private async parseErrorResponse(response: Response): Promise<any> {
    try {
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        return await response.json();
      }
      return { message: await response.text() };
    } catch {
      return { message: response.statusText };
    }
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Make HTTP request
   */
  async request<T = any>(endpoint: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    const url = this.buildURL(endpoint, config.params);
    const method = config.method || 'GET';
    const cacheKey = this.getCacheKey(url, config);

    // Check cache for GET requests
    if (method === 'GET' && config.cache !== false) {
      const cached = this.getCachedResponse(cacheKey);
      if (cached) {
        return {
          data: cached,
          status: 200,
          statusText: 'OK (Cached)',
          headers: new Headers(),
        };
      }

      // Deduplicate concurrent requests
      const pending = this.pendingRequests.get(cacheKey);
      if (pending) {
        return pending;
      }
    }

    // Execute request
    const requestPromise = this.executeWithRetry<T>(url, config);

    // Store pending request for deduplication
    if (method === 'GET') {
      this.pendingRequests.set(cacheKey, requestPromise);
      requestPromise.finally(() => {
        this.pendingRequests.delete(cacheKey);
      });
    }

    const response = await requestPromise;

    // Cache successful GET responses
    if (method === 'GET' && config.cache !== false && response.status === 200) {
      const ttl = config.cacheTTL || this.config.cacheTTL;
      this.setCachedResponse(cacheKey, response.data, ttl);
    }

    return response;
  }

  /**
   * GET request
   */
  async get<T = any>(endpoint: string, config: Omit<RequestConfig, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T = any>(endpoint: string, body?: any, config: Omit<RequestConfig, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'POST', body });
  }

  /**
   * PUT request
   */
  async put<T = any>(endpoint: string, body?: any, config: Omit<RequestConfig, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'PUT', body });
  }

  /**
   * PATCH request
   */
  async patch<T = any>(endpoint: string, body?: any, config: Omit<RequestConfig, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'PATCH', body });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(endpoint: string, config: Omit<RequestConfig, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }
}

// Create default API client instance
function deriveBaseURL(): string {
  // Try to get VITE_API_URL from import.meta.env
  const envBaseURL = (import.meta as any)?.env?.VITE_API_URL;
  
  console.log('🔍 Environment check:', {
    'import.meta.env': (import.meta as any)?.env,
    'VITE_API_URL': envBaseURL,
    'window.location.origin': typeof window !== 'undefined' ? window.location?.origin : 'N/A'
  });
  
  if (envBaseURL && typeof envBaseURL === 'string') {
    // VITE_API_URL should be http://localhost:8000, append /api/v1
    const baseUrl = envBaseURL.trim().replace(/\/$/, '');
    const fullUrl = `${baseUrl}/api/v1`;
    console.log('✅ Using VITE_API_URL:', fullUrl);
    return fullUrl;
  }

  // Fallback: Use backend port 8000 explicitly
  console.warn('⚠️ VITE_API_URL not found, using fallback: http://localhost:8000/api/v1');
  return 'http://localhost:8000/api/v1';
}

const baseURL = deriveBaseURL();
console.log('🔧 API Client baseURL:', baseURL);

const apiClient = new ApiClient({
  baseURL,
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
  cacheEnabled: true,
  cacheTTL: 300000, // 5 minutes
});

export default apiClient;
