# API Client Documentation

## Overview

The API Client is a comprehensive fetch wrapper that provides:
- **JWT Authentication**: Automatic token injection and refresh
- **Request/Response Interceptors**: Customize request/response handling
- **Error Handling**: Consistent error formatting and handling
- **Retry Logic**: Automatic retry on network failures and 5xx errors
- **Request Caching**: Intelligent caching for GET requests
- **Request Deduplication**: Prevents duplicate concurrent requests
- **Timeout Management**: Configurable request timeouts
- **httpx Compatibility**: Works seamlessly with FastAPI/httpx backend

## Installation

The API client is located at `src/lib/api-client.ts` and is automatically imported by all service files.

```typescript
import apiClient from '../lib/api-client';
```

## Configuration

The default API client instance is configured with:

```typescript
const apiClient = new ApiClient({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,           // 30 seconds
  retryAttempts: 3,         // Retry failed requests 3 times
  retryDelay: 1000,         // 1 second delay between retries
  cacheEnabled: true,       // Enable request caching
  cacheTTL: 300000,         // 5 minutes default cache TTL
});
```

## Basic Usage

### GET Request

```typescript
// Simple GET request
const response = await apiClient.get<Farm[]>('/farms');
const farms = response.data;

// GET with query parameters
const response = await apiClient.get<Farm>('/farms/123', {
  params: { include: 'plots' }
});

// GET with caching
const response = await apiClient.get<Farm[]>('/farms', {
  cache: true,
  cacheTTL: 60000, // Cache for 1 minute
});
```

### POST Request

```typescript
// POST with body
const response = await apiClient.post<Farm>('/farms', {
  name: 'My Farm',
  state: 'Punjab',
  district: 'Ludhiana',
  total_area: 10,
});

// POST without authentication
const response = await apiClient.post('/auth/signin', credentials, {
  requiresAuth: false,
});
```

### PUT Request

```typescript
const response = await apiClient.put<Farm>(`/farms/${id}`, {
  name: 'Updated Farm Name',
});
```

### DELETE Request

```typescript
await apiClient.delete(`/farms/${id}`);
```

## Authentication

### Automatic Token Injection

The API client automatically injects JWT tokens from localStorage:

```typescript
// Token is automatically added to Authorization header
const response = await apiClient.get('/farms');
// Request includes: Authorization: Bearer <token>
```

### Disable Authentication

For public endpoints:

```typescript
const response = await apiClient.get('/marketplace/listings', {
  requiresAuth: false,
});
```

### Automatic Token Refresh

When a 401 response is received, the client automatically:
1. Attempts to refresh the token using the refresh token
2. Retries the original request with the new token
3. If refresh fails, clears tokens and throws error

```typescript
// This happens automatically - no code needed
const response = await apiClient.get('/farms');
// If token expired:
// 1. Receives 401
// 2. Calls /auth/refresh-token
// 3. Stores new tokens
// 4. Retries GET /farms
// 5. Returns successful response
```

## Request Caching

### Enable Caching

```typescript
// Cache for default TTL (5 minutes)
const response = await apiClient.get('/farms', {
  cache: true,
});

// Cache with custom TTL
const response = await apiClient.get('/farms', {
  cache: true,
  cacheTTL: 120000, // 2 minutes
});
```

### Clear Cache

```typescript
// Clear all cache
apiClient.clearCache();

// Clear cache by pattern
apiClient.clearCacheByPattern(new RegExp('/farms'));

// Clear cache after mutation
await apiClient.post('/farms', farmData);
apiClient.clearCacheByPattern(new RegExp('/farms'));
```

### Request Deduplication

Concurrent identical GET requests are automatically deduplicated:

```typescript
// These three requests will only make ONE network call
const [farms1, farms2, farms3] = await Promise.all([
  apiClient.get('/farms'),
  apiClient.get('/farms'),
  apiClient.get('/farms'),
]);
// All three receive the same response
```

## Error Handling

### Error Structure

```typescript
interface ApiError {
  message: string;
  status?: number;
  statusText?: string;
  detail?: string;
  errors?: any;
}
```

### Handling Errors

```typescript
try {
  const response = await apiClient.get('/farms');
  const farms = response.data;
} catch (error: any) {
  console.error('API Error:', error.message);
  console.error('Status:', error.status);
  console.error('Details:', error.detail);
}
```

### Automatic Retry

The client automatically retries on:
- Network errors (Failed to fetch)
- 5xx server errors
- Timeout errors

```typescript
// This will retry up to 3 times with 1 second delay
const response = await apiClient.get('/farms');

// Disable retry for specific request
const response = await apiClient.get('/farms', {
  retry: false,
});
```

## Timeout Management

### Default Timeout

All requests have a 30-second timeout by default.

### Custom Timeout

```typescript
// 15 second timeout for AI generation
const response = await apiClient.post('/crops/annual-strategy', data, {
  timeout: 15000,
});
```

### Timeout Error

```typescript
try {
  const response = await apiClient.get('/slow-endpoint');
} catch (error: any) {
  if (error.status === 408) {
    console.error('Request timeout');
  }
}
```

## Interceptors

### Request Interceptors

Add custom logic before requests are sent:

```typescript
apiClient.addRequestInterceptor((config, url) => {
  // Add custom header
  config.headers = {
    ...config.headers,
    'X-Custom-Header': 'value',
  };
  return config;
});

// Async interceptor
apiClient.addRequestInterceptor(async (config, url) => {
  // Fetch something before request
  const data = await fetchSomething();
  config.headers['X-Data'] = data;
  return config;
});
```

### Response Interceptors

Add custom logic after responses are received:

```typescript
apiClient.addResponseInterceptor((response) => {
  // Log all responses
  console.log('Response:', response.status, response.url);
  return response;
});

// Async interceptor
apiClient.addResponseInterceptor(async (response) => {
  // Process response
  if (response.status === 200) {
    await trackSuccess();
  }
  return response;
});
```

### Error Interceptors

Add custom error handling:

```typescript
apiClient.addErrorInterceptor((error) => {
  // Log errors to monitoring service
  logToMonitoring(error);
  throw error;
});
```

## Service Integration Examples

### Farm Service

```typescript
export class FarmService {
  static async createFarm(data: FarmCreate): Promise<Farm> {
    const response = await apiClient.post<Farm>('/farms', data);
    return response.data;
  }

  static async getFarms(): Promise<Farm[]> {
    const response = await apiClient.get<Farm[]>('/farms', {
      cache: true,
      cacheTTL: 60000,
    });
    return response.data;
  }

  static async updateFarm(id: number, data: FarmUpdate): Promise<Farm> {
    const response = await apiClient.put<Farm>(`/farms/${id}`, data);
    apiClient.clearCacheByPattern(new RegExp('/farms'));
    return response.data;
  }
}
```

### Strategy Service

```typescript
export class StrategyService {
  static async generateStrategy(request: StrategyRequest): Promise<AnnualStrategy> {
    const response = await apiClient.post<AnnualStrategy>(
      '/crops/annual-strategy',
      request,
      {
        cache: false,
        timeout: 15000, // AI generation takes longer
      }
    );
    return response.data;
  }

  static async getFarmStrategies(farmId: number): Promise<SavedStrategy[]> {
    const response = await apiClient.get<SavedStrategy[]>(
      `/crops/annual-strategy/farm/${farmId}`,
      {
        cache: true,
        cacheTTL: 120000,
      }
    );
    return response.data;
  }
}
```

### Marketplace Service

```typescript
export class MarketplaceService {
  static async getListings(filters: ListingFilters): Promise<ListingsResponse> {
    const response = await apiClient.get<ListingsResponse>(
      '/marketplace/listings',
      {
        params: filters,
        requiresAuth: false, // Public endpoint
        cache: true,
        cacheTTL: 60000,
      }
    );
    return response.data;
  }

  static async registerBuyerInterest(request: BuyerInterestRequest): Promise<any> {
    const response = await apiClient.post('/marketplace/buyer-interest', request);
    apiClient.clearCacheByPattern(new RegExp(`/marketplace/listings/${request.listing_id}`));
    return response.data;
  }
}
```

## Advanced Features

### Custom API Client Instance

Create a custom instance with different configuration:

```typescript
import { ApiClient } from '../lib/api-client';

const customClient = new ApiClient({
  baseURL: 'https://api.example.com',
  timeout: 60000,
  retryAttempts: 5,
  cacheEnabled: false,
});
```

### Response Structure

All successful responses include:

```typescript
interface ApiResponse<T> {
  data: T;              // Response body
  status: number;       // HTTP status code
  statusText: string;   // HTTP status text
  headers: Headers;     // Response headers
}
```

### Query Parameters

```typescript
// Automatic query parameter encoding
const response = await apiClient.get('/marketplace/listings', {
  params: {
    crop_type: 'wheat',
    state: 'Punjab',
    page: 1,
    page_size: 20,
  },
});
// Calls: /marketplace/listings?crop_type=wheat&state=Punjab&page=1&page_size=20
```

## Best Practices

### 1. Cache Frequently Accessed Data

```typescript
// Good: Cache farm list
const farms = await apiClient.get('/farms', {
  cache: true,
  cacheTTL: 60000,
});

// Bad: Don't cache mutations
const farm = await apiClient.post('/farms', data, {
  cache: true, // ❌ Don't do this
});
```

### 2. Clear Cache After Mutations

```typescript
// Create farm
await apiClient.post('/farms', data);

// Clear farm cache so next GET fetches fresh data
apiClient.clearCacheByPattern(new RegExp('/farms'));
```

### 3. Use Appropriate Timeouts

```typescript
// Short timeout for simple queries
const farms = await apiClient.get('/farms', {
  timeout: 5000,
});

// Longer timeout for AI generation
const strategy = await apiClient.post('/crops/annual-strategy', data, {
  timeout: 15000,
});
```

### 4. Handle Errors Gracefully

```typescript
try {
  const response = await apiClient.get('/farms');
  return response.data;
} catch (error: any) {
  if (error.status === 404) {
    return []; // Return empty array for not found
  }
  throw error; // Re-throw other errors
}
```

### 5. Disable Auth for Public Endpoints

```typescript
// Public marketplace listings
const listings = await apiClient.get('/marketplace/listings', {
  requiresAuth: false,
});

// Auth required for user farms
const farms = await apiClient.get('/farms');
// requiresAuth defaults to true
```

## Migration from Fetch

### Before (Raw Fetch)

```typescript
const response = await fetch(`${API_BASE}/farms`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
});

if (!response.ok) {
  const error = await response.json();
  throw new Error(error.detail || 'Failed to fetch farms');
}

return response.json();
```

### After (API Client)

```typescript
const response = await apiClient.get<Farm[]>('/farms');
return response.data;
```

Benefits:
- ✅ Automatic token injection
- ✅ Automatic error handling
- ✅ Automatic retry on failure
- ✅ Request caching
- ✅ Type safety
- ✅ Less boilerplate code

## Troubleshooting

### Token Not Being Sent

Ensure token is stored in localStorage:

```typescript
localStorage.setItem('access_token', token);
```

### Cache Not Working

Ensure cache is enabled and method is GET:

```typescript
// ✅ Correct
const response = await apiClient.get('/farms', {
  cache: true,
});

// ❌ Wrong - POST requests are never cached
const response = await apiClient.post('/farms', data, {
  cache: true,
});
```

### Timeout Errors

Increase timeout for slow endpoints:

```typescript
const response = await apiClient.get('/slow-endpoint', {
  timeout: 60000, // 60 seconds
});
```

### CORS Errors

Ensure backend allows the origin and includes proper CORS headers.

## Performance Tips

1. **Use caching for frequently accessed data**
   - Farm lists, marketplace listings, strategies

2. **Clear cache after mutations**
   - After POST, PUT, DELETE operations

3. **Use request deduplication**
   - Multiple components fetching same data

4. **Set appropriate cache TTLs**
   - Short TTL (1 min) for frequently changing data
   - Long TTL (5 min) for stable data

5. **Disable retry for non-idempotent operations**
   - Payment processing, order creation

## Security Considerations

1. **Tokens are stored in localStorage**
   - Consider using httpOnly cookies for production

2. **Automatic token refresh**
   - Refresh tokens should have short expiry

3. **HTTPS only in production**
   - Never send tokens over HTTP

4. **Clear tokens on logout**
   - Call `apiClient.clearAuthTokens()` or use AuthService

## Summary

The API Client provides a robust, production-ready HTTP client with:
- ✅ Automatic authentication
- ✅ Intelligent caching
- ✅ Error handling and retry logic
- ✅ Request/response interceptors
- ✅ TypeScript support
- ✅ httpx/FastAPI compatibility

All services have been updated to use the API client, providing consistent error handling, authentication, and caching across the entire application.
