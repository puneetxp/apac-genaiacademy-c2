# Offline Support Implementation

## Overview

This document describes the offline support features implemented for the CropSense AI PWA, enabling farmers to use the app even with intermittent connectivity.

## Features Implemented

### 1. Service Worker with Enhanced Caching

**Location:** `public/sw.js`

**Caching Strategies:**
- **Static Assets:** Cache-first strategy with background updates
- **API Requests:** Network-first with cache fallback
- **Navigation:** Offline fallback to cached index.html

**Cache Management:**
- Cache version: `farming-platform-v1.1`
- Automatic cleanup of old caches on activation
- Selective caching of successful responses only

### 2. Install Prompt Component

**Location:** `src/components/ui/InstallPrompt.tsx`

**Features:**
- Custom "Add to Home Screen" prompt
- Appears 3 seconds after page load
- Dismissible with 7-day cooldown
- Tracks installation status in localStorage
- Responsive design with green theme

**User Experience:**
- Shows app icon and benefits
- "Install" and "Not Now" buttons
- Auto-dismisses after user action
- Prevents repeated prompts

### 3. Offline Indicator

**Location:** `src/components/ui/OfflineIndicator.tsx`

**Features:**
- Real-time connection status monitoring
- Shows offline banner when disconnected
- Displays "Back online" message when reconnected
- Shows count of queued actions
- Auto-dismisses reconnection message after 3 seconds

**Visual Design:**
- Yellow banner for offline state
- Green banner for reconnection
- Icon indicators (WiFi off/on)
- Queue count badge

### 4. Offline Queue System

**Location:** `src/utils/offlineQueue.ts`

**Features:**
- Queues API requests made while offline
- Automatic sync when connection restored
- Retry logic with max 3 attempts
- localStorage-based persistence
- Background sync support

**API:**
```typescript
// Queue an action
queueAction(method, url, body, headers)

// Get queue size
getQueueSize()

// Process queue manually
processQueue()

// Clear queue
clearQueue()

// Initialize (call on app start)
initOfflineQueue()
```

### 5. App Update Notification

**Location:** `src/utils/initServiceWorker.ts`

**Features:**
- Detects new service worker versions
- Shows update notification banner
- "Update Now" button triggers immediate update
- Dismissible with auto-dismiss after 30 seconds
- Smooth reload after update

**Update Flow:**
1. New service worker detected
2. Banner appears at top of screen
3. User clicks "Update Now"
4. Service worker skips waiting
5. Page reloads with new version

### 6. Background Sync

**Service Worker Feature:**
- Registers `sync-offline-queue` tag
- Automatically syncs when connection restored
- Communicates with app via postMessage
- Fallback for browsers without sync API

## PWA Manifest Configuration

**Location:** `public/manifest.json`

**Key Features:**
- App name: "CropSense AI - Farming Platform"
- Standalone display mode
- Portrait orientation
- Green theme color (#22c55e)
- Multiple icon sizes (72px to 512px)
- App shortcuts for quick access
- Categories: agriculture, business, productivity

## Icon Generation

**Tool:** `public/generate-icons.html`

**Features:**
- Browser-based icon generator
- Generates all required sizes (72, 96, 128, 144, 152, 192, 384, 512)
- Green gradient background
- Simple leaf/crop icon design
- "CS" text overlay for larger icons
- Badge icon (72x72) for notifications
- Download individual or all icons

**Usage:**
1. Open `generate-icons.html` in browser
2. Click "Generate All Icons"
3. Click "Download All Icons"
4. Place icons in `public/` directory

## CSS Animations

**Location:** `src/assets/styles/index.css`

**Animations Added:**
- `slideUp`: Bottom-to-top entrance (install prompt)
- `slideDown`: Top-to-bottom entrance (update banner, offline indicator)
- `fadeIn`: Smooth fade in
- `fadeOut`: Smooth fade out

**Safe Area Support:**
- `pb-safe-bottom`: Bottom padding for notched devices
- `pt-safe-top`: Top padding for status bar
- `pl-safe-left`: Left padding for curved edges
- `pr-safe-right`: Right padding for curved edges

## Integration

### App.tsx Changes

```typescript
import InstallPrompt from './components/ui/InstallPrompt';
import OfflineIndicator from './components/ui/OfflineIndicator';
import { initServiceWorker } from './utils/initServiceWorker';

// In component:
<OfflineIndicator />
<InstallPrompt />

// In onMount:
initServiceWorker().catch((error) => {
  console.error('Failed to initialize service worker:', error);
});
```

### Service Worker Initialization

```typescript
import { initOfflineQueue } from './utils/offlineQueue';

// Initialize offline queue on app start
initOfflineQueue();

// Service worker handles:
// - Push notifications
// - Offline caching
// - Background sync
// - App updates
```

## Testing Offline Functionality

### Manual Testing

1. **Install Prompt:**
   - Open app in browser
   - Wait 3 seconds
   - Verify install prompt appears
   - Click "Install" or "Not Now"
   - Verify prompt doesn't reappear immediately

2. **Offline Mode:**
   - Open app
   - Open DevTools > Network tab
   - Enable "Offline" mode
   - Verify yellow offline banner appears
   - Try navigating (should work with cached pages)
   - Try API requests (should queue)
   - Disable offline mode
   - Verify green "Back online" banner
   - Verify queued actions sync

3. **App Update:**
   - Make a change to service worker
   - Increment cache version
   - Reload app
   - Verify update notification appears
   - Click "Update Now"
   - Verify app reloads with new version

4. **Caching:**
   - Open app online
   - Navigate to different pages
   - Go offline
   - Navigate to previously visited pages
   - Verify pages load from cache

### Chrome DevTools Testing

1. **Application Tab:**
   - Check "Service Workers" section
   - Verify service worker is active
   - Check "Cache Storage"
   - Verify assets are cached

2. **Network Tab:**
   - Enable offline mode
   - Verify requests show "(from ServiceWorker)"
   - Check response times

3. **Console:**
   - Monitor service worker logs
   - Check for errors
   - Verify queue processing messages

## Browser Support

### Service Worker Support:
- ✅ Chrome 40+
- ✅ Firefox 44+
- ✅ Safari 11.1+
- ✅ Edge 17+
- ✅ Opera 27+

### Background Sync Support:
- ✅ Chrome 49+
- ✅ Edge 79+
- ⚠️ Firefox (behind flag)
- ❌ Safari (not supported)
- Fallback: Manual sync on reconnection

### Install Prompt Support:
- ✅ Chrome 68+ (Android)
- ✅ Edge 79+
- ⚠️ Safari (Add to Home Screen via share menu)
- ⚠️ Firefox (limited support)

## Performance Considerations

### Cache Size Management:
- Static assets: ~2-5 MB
- API responses: ~1-2 MB
- Total cache: ~5-10 MB
- Automatic cleanup of old caches

### Network Optimization:
- Cache-first for static assets (instant load)
- Network-first for API (fresh data)
- Background updates for cached assets
- Selective caching (only successful responses)

### Battery Impact:
- Minimal background activity
- Sync only when online
- No polling or timers
- Event-driven architecture

## Future Enhancements

### Phase 2 (Optional):
1. **IndexedDB Storage:**
   - Store farm profiles offline
   - Cache annual strategies
   - Offline marketplace browsing

2. **Advanced Sync:**
   - Conflict resolution
   - Optimistic UI updates
   - Sync status indicators

3. **Offline Analytics:**
   - Track offline usage
   - Queue analytics events
   - Sync when online

4. **Progressive Enhancement:**
   - Offline image optimization
   - Lazy loading strategies
   - Adaptive quality based on connection

## Troubleshooting

### Service Worker Not Registering:
- Check HTTPS (required for service workers)
- Verify `sw.js` is in `public/` directory
- Check browser console for errors
- Clear browser cache and reload

### Install Prompt Not Showing:
- Check if app is already installed
- Verify manifest.json is valid
- Check if prompt was dismissed recently
- Test in Chrome on Android (best support)

### Offline Mode Not Working:
- Verify service worker is active
- Check cache storage in DevTools
- Ensure assets are being cached
- Check network tab for service worker responses

### Queue Not Syncing:
- Check browser console for errors
- Verify online event is firing
- Check localStorage for queued actions
- Manually call `processQueue()`

## Resources

- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [Background Sync API](https://developer.mozilla.org/en-US/docs/Web/API/Background_Synchronization_API)
- [PWA Best Practices](https://web.dev/pwa/)
- [Workbox (Advanced PWA Library)](https://developers.google.com/web/tools/workbox)

## Maintenance

### Updating Service Worker:
1. Make changes to `sw.js`
2. Increment `CACHE_NAME` version
3. Test in development
4. Deploy to production
5. Users will see update notification

### Adding New Cached Assets:
1. Add URLs to `STATIC_ASSETS` array in `sw.js`
2. Or use `CACHE_URLS` message from app
3. Assets will be cached on next service worker update

### Monitoring:
- Check service worker logs in production
- Monitor cache hit rates
- Track offline usage patterns
- Measure sync success rates
