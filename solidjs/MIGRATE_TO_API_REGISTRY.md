# Migration Guide: Using API Registry

## Step-by-Step Migration

### Step 1: Import the Helper

```typescript
import { buildUrl } from '@/config/api-registry';
```

### Step 2: Replace Hardcoded URLs

#### Example: Crop Service

**Before**:
```typescript
// src/services/crop.service.ts
export const cropService = {
  async getMyStrategies() {
    // ❌ Hardcoded and WRONG endpoint
    return apiClient.get('/api/v1/crops/my-strategies');
  }
};
```

**After**:
```typescript
// src/services/crop.service.ts
import { buildUrl } from '@/config/api-registry';

export const cropService = {
  async getMyStrategies() {
    // ✅ Correct endpoint from registry
    const url = buildUrl('crops', 'myStrategies');
    return apiClient.get(url);
  }
};
```

### Step 3: Handle Path Parameters

**Before**:
```typescript
async getStrategy(id: string) {
  return apiClient.get(`/api/v1/annual-strategy/${id}`);
}
```

**After**:
```typescript
async getStrategy(id: string) {
  const url = buildUrl('crops', 'getStrategy', { id });
  return apiClient.get(url);
}
```

## Common Patterns

### Pattern 1: Simple GET Request
```typescript
import { buildUrl } from '@/config/api-registry';

// List all farms
const url = buildUrl('farms', 'list');
const farms = await apiClient.get(url);
```

### Pattern 2: GET with ID Parameter
```typescript
// Get specific farm
const url = buildUrl('farms', 'get', { id: farmId });
const farm = await apiClient.get(url);
```

### Pattern 3: POST Request
```typescript
// Create new listing
const url = buildUrl('marketplace', 'createListing');
const listing = await apiClient.post(url, data);
```

### Pattern 4: Multiple Parameters
```typescript
// Lookup pincode
const url = buildUrl('address', 'lookupPincode', { pincode: '110001' });
const address = await apiClient.get(url);
```

## Files to Update

Priority order for migration:

1. **High Priority** (Broken endpoints):
   - `src/services/crop.service.ts` - Fix my-strategies endpoint
   - `src/services/annual-strategy.service.ts` - Fix strategy endpoints
   
2. **Medium Priority** (Frequently used):
   - `src/services/auth.service.ts`
   - `src/services/farm.service.ts`
   - `src/services/marketplace.service.ts`
   
3. **Low Priority** (Less critical):
   - All other service files
   - Component-level API calls

## Testing After Migration

1. **Check Network Tab**: Verify correct URLs are being called
2. **Test User Flows**: 
   - Login/Signup
   - View crop strategies
   - Create marketplace listings
3. **Check Console**: No 404 errors

## Quick Reference: Common Endpoint Mappings

| Old (Wrong) | New (Correct) | Registry Call |
|------------|---------------|---------------|
| `/api/v1/crops/my-strategies` | `/api/v1/annual-strategy/list` | `buildUrl('crops', 'myStrategies')` |
| `/api/v1/crops/strategy/{id}` | `/api/v1/annual-strategy/{id}` | `buildUrl('crops', 'getStrategy', {id})` |
| `/api/v1/crops/save` | `/api/v1/annual-strategy/save` | `buildUrl('crops', 'saveStrategy')` |
| `/api/v1/auth/login` | `/api/v1/auth/login` | `buildUrl('auth', 'login')` |
| `/api/v1/farms` | `/api/v1/farms` | `buildUrl('farms', 'list')` |

## Benefits of Migration

✅ **No more 404 errors** - Endpoints are guaranteed to match backend
✅ **Type safety** - TypeScript catches typos at compile time
✅ **Easy refactoring** - Change baseUrl in one place
✅ **Self-documenting** - See all available endpoints in registry
✅ **IDE support** - Auto-completion for categories and endpoint names

## Need Help?

See `API_REGISTRY_USAGE.md` for detailed examples and patterns.
