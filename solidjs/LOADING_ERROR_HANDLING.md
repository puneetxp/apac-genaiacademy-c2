# Loading States and Error Handling Implementation

## Overview

This document describes the comprehensive loading states and error handling system implemented for the Rural Farming Platform frontend. The system provides user-friendly feedback for all async operations, including loading spinners, skeleton screens, toast notifications, and retry functionality.

## Components Implemented

### 1. Toast Notification System (`components/ui/Toast.tsx`)

**Purpose:** Display temporary success, error, warning, and info messages to users.

**Features:**
- 4 toast types: success, error, warning, info
- Auto-dismiss after configurable duration (default: 5 seconds)
- Manual dismiss with close button
- Animated slide-in/slide-out transitions
- Stacked display for multiple toasts
- Icon indicators for each toast type

**Usage:**
```typescript
import { showToast } from '../components/ui/Toast';

// Success message
showToast('success', 'Farm registered successfully');

// Error message
showToast('error', 'Failed to load data');

// Warning message
showToast('warning', 'Your session will expire soon');

// Info message
showToast('info', 'Processing your request...');

// Custom duration (in milliseconds)
showToast('success', 'Saved!', 3000);
```

**Integration:**
- Added `<ToastContainer />` to `App.tsx` root component
- Toasts appear in top-right corner of screen
- Z-index: 50 (above most content)

### 2. Loading Spinner (`components/ui/LoadingSpinner.tsx`)

**Purpose:** Display animated loading indicator during async operations.

**Features:**
- 4 sizes: sm, md, lg, xl
- 3 color variants: primary (green), white, gray
- Optional loading text
- Full-screen overlay mode
- Smooth spin animation

**Usage:**
```typescript
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

// Inline spinner
<LoadingSpinner size="md" color="primary" />

// With text
<LoadingSpinner size="lg" text="Loading data..." />

// Full-screen overlay
<LoadingSpinner size="xl" text="Processing..." fullScreen={true} />

// In button
<button disabled={loading()}>
  <Show when={loading()}>
    <LoadingSpinner size="sm" color="white" />
  </Show>
  {loading() ? 'Saving...' : 'Save'}
</button>
```

### 3. Skeleton Screens (`components/ui/SkeletonScreen.tsx`)

**Purpose:** Display placeholder content while data is loading for better perceived performance.

**Components:**
- `Skeleton` - Base skeleton component with customizable dimensions
- `SkeletonCard` - Card-shaped skeleton for content cards
- `SkeletonList` - List of skeleton items (configurable count)
- `SkeletonTable` - Table skeleton with rows and columns
- `SkeletonForm` - Form skeleton with input fields
- `SkeletonDashboard` - Complete dashboard skeleton layout

**Usage:**
```typescript
import { SkeletonCard, SkeletonList, SkeletonDashboard } from '../components/ui/SkeletonScreen';

// Card skeleton
<Show when={loading()} fallback={<ActualCard />}>
  <SkeletonCard />
</Show>

// List skeleton (3 items by default)
<SkeletonList count={5} />

// Dashboard skeleton
<Show when={loading()} fallback={<Dashboard />}>
  <SkeletonDashboard />
</Show>

// Custom skeleton
<Skeleton width="200px" height="24px" rounded="md" />
```

### 4. Error Display (`components/ui/ErrorDisplay.tsx`)

**Purpose:** Show user-friendly error messages with retry functionality.

**Features:**
- User-friendly error messages for common HTTP status codes
- Retry button for failed operations
- Full-screen or inline display modes
- Error icon and visual hierarchy
- Status code display for debugging
- Detailed error information when available

**Status Code Handling:**
- 401: "Your session has expired. Please sign in again."
- 403: "You do not have permission to access this resource."
- 404: "The requested resource was not found."
- 408: "The request took too long. Please check your connection and try again."
- 5xx: "Our servers are experiencing issues. Please try again later."

**Usage:**
```typescript
import { ErrorDisplay, InlineError } from '../components/ui/ErrorDisplay';

// Full error display with retry
<ErrorDisplay
  error={error()}
  onRetry={handleRetry}
  title="Failed to load data"
/>

// Full-screen error
<ErrorDisplay
  error={error()}
  onRetry={handleRetry}
  fullScreen={true}
/>

// Inline error for form fields
<InlineError message={fieldError()} />
```

### 5. Async Utilities (`utils/useAsync.ts`)

**Purpose:** Simplify async operation management with built-in loading, error, and success states.

**Hooks:**

#### `useAsync` - Manual execution
```typescript
import { useAsync } from '../utils/useAsync';

const { data, loading, error, execute, reset } = useAsync(
  async () => await fetchData(),
  {
    showSuccessToast: true,
    successMessage: 'Data loaded successfully',
    showErrorToast: true,
    onSuccess: (data) => console.log('Success:', data),
    onError: (error) => console.error('Error:', error),
  }
);

// Execute manually
await execute();
```

#### `useAsyncEffect` - Auto-execute on mount
```typescript
import { useAsyncEffect } from '../utils/useAsync';

const { data, loading, error } = useAsyncEffect(
  async () => await fetchData(),
  { showErrorToast: true }
);
```

#### `useAsyncSubmit` - Form submission
```typescript
import { useAsyncSubmit } from '../utils/useAsync';

const { submitting, error, success, submit, reset } = useAsyncSubmit(
  async (formData) => await saveData(formData),
  {
    showSuccessToast: true,
    successMessage: 'Saved successfully',
  }
);

// In form handler
const handleSubmit = async (e) => {
  e.preventDefault();
  await submit(formData);
};
```

## Enhanced Components

### Authentication Components

**SignInForm.tsx:**
- Loading spinner in submit button
- Toast notifications for success/error
- Enhanced error display with icon
- Disabled state during loading

**SignUpForm.tsx:**
- Similar enhancements as SignInForm
- Field-level error display
- Loading state management

### Strategy Components

**StrategyRequestForm.tsx:**
- Loading spinner in submit button
- Progress indicator during AI generation
- Informative loading message (up to 10 seconds)
- Disabled form during submission

**StrategyResults.tsx:**
- Skeleton screens while loading strategy data
- Error display with retry for failed loads
- Loading states for individual sections

### Marketplace Components

**ListingGrid.tsx:**
- Skeleton cards (6 cards) during initial load
- Empty state with helpful message
- Smooth transition from loading to content

**ListingDetail.tsx:**
- Full skeleton screen for listing details
- Error display with retry button
- Loading states for buyer interest submission

### Dashboard

**Dashboard.tsx:**
- Complete dashboard skeleton during load
- Error display with retry functionality
- Refresh button with loading feedback
- Toast notification on refresh

## Best Practices

### 1. Loading States

**Always show loading feedback for operations > 200ms:**
```typescript
const [loading, setLoading] = createSignal(false);

const handleAction = async () => {
  setLoading(true);
  try {
    await performAction();
  } finally {
    setLoading(false);
  }
};
```

**Use skeleton screens for initial page loads:**
```typescript
<Show when={!loading()} fallback={<SkeletonDashboard />}>
  <Dashboard data={data()} />
</Show>
```

**Use spinners for button actions:**
```typescript
<button disabled={loading()}>
  <Show when={loading()}>
    <LoadingSpinner size="sm" color="white" />
  </Show>
  {loading() ? 'Saving...' : 'Save'}
</button>
```

### 2. Error Handling

**Always catch and display errors:**
```typescript
try {
  await riskyOperation();
  showToast('success', 'Operation completed');
} catch (error) {
  showToast('error', error.message);
  setError(error);
}
```

**Provide retry functionality for recoverable errors:**
```typescript
<ErrorDisplay
  error={error()}
  onRetry={() => {
    setError(null);
    execute();
  }}
/>
```

**Use inline errors for form validation:**
```typescript
<input
  type="email"
  value={email()}
  onInput={(e) => setEmail(e.currentTarget.value)}
/>
<InlineError message={emailError()} />
```

### 3. User Feedback

**Show success feedback for important actions:**
```typescript
await saveData();
showToast('success', 'Changes saved successfully');
```

**Provide context in loading messages:**
```typescript
<LoadingSpinner 
  text="Analyzing your farm profile..." 
  size="lg" 
/>
```

**Use appropriate toast types:**
- `success` - Completed actions (saved, deleted, created)
- `error` - Failed operations (network errors, validation errors)
- `warning` - Important notices (session expiring, quota limits)
- `info` - Informational messages (processing, redirecting)

### 4. Performance

**Use skeleton screens for perceived performance:**
- Shows content structure immediately
- Reduces perceived loading time
- Better UX than blank screens or spinners

**Implement optimistic updates where appropriate:**
```typescript
// Update UI immediately
setData(newData);
showToast('success', 'Updated');

// Sync with server in background
try {
  await syncWithServer(newData);
} catch (error) {
  // Revert on error
  setData(oldData);
  showToast('error', 'Failed to sync');
}
```

## API Client Integration

The API client (`lib/api-client.ts`) already includes:
- Automatic retry logic (3 attempts with exponential backoff)
- Request timeout handling (30 seconds default)
- Token refresh on 401 errors
- Request/response interceptors
- Caching for GET requests
- Request deduplication

**Error handling is automatic:**
```typescript
try {
  const response = await apiClient.get('/farms');
  // Success - response.data contains the data
} catch (error) {
  // Error - error contains ApiError with message, status, detail
  showToast('error', error.message);
}
```

## Testing Checklist

- [ ] All async operations show loading state
- [ ] All errors display user-friendly messages
- [ ] Retry buttons work for failed operations
- [ ] Toast notifications appear for important actions
- [ ] Skeleton screens display during initial loads
- [ ] Loading spinners appear in buttons during submission
- [ ] Form fields show inline validation errors
- [ ] Network errors are handled gracefully
- [ ] Timeout errors show appropriate messages
- [ ] 401 errors redirect to sign-in
- [ ] Success messages confirm completed actions

## Future Enhancements

1. **Progress Bars** - For long-running operations (file uploads, batch processing)
2. **Offline Indicators** - Show when app is offline with queued actions
3. **Undo/Redo** - For destructive actions with toast action buttons
4. **Loading Priorities** - Critical content loads first, secondary content lazy loads
5. **Error Boundaries** - Catch and display React/SolidJS errors gracefully
6. **Analytics** - Track error rates and loading times for optimization

## Summary

The loading states and error handling system provides:
- ✅ Comprehensive user feedback for all async operations
- ✅ User-friendly error messages with retry functionality
- ✅ Skeleton screens for better perceived performance
- ✅ Toast notifications for success/error feedback
- ✅ Loading spinners for buttons and full-screen operations
- ✅ Consistent UX patterns across the application
- ✅ Easy-to-use utilities for developers

All components are fully integrated and ready for use throughout the application.
