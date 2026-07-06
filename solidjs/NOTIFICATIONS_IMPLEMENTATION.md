# Web Push Notifications Implementation

This document describes the web push notification system implemented for the Rural Farming Platform.

## Overview

The notification system enables farmers to receive real-time updates about:
- Buyer interest in their marketplace listings
- Crop strategy implementation reminders
- Weather alerts and warnings
- Harvest timing reminders

## Architecture

### Components

1. **Service Worker** (`public/sw.js`)
   - Handles push notification events
   - Manages notification display and click handling
   - Implements offline caching strategies
   - Routes notification clicks to appropriate app sections

2. **Notification Service** (`src/services/notification.service.ts`)
   - Manages service worker registration
   - Handles permission requests
   - Manages push subscriptions
   - Communicates with backend API

3. **UI Components**
   - `NotificationPermissionPrompt.tsx` - Permission request modal
   - `NotificationSettings.tsx` - Settings page component

4. **Utilities**
   - `initServiceWorker.ts` - App initialization helper

## Setup Instructions

### 1. Environment Configuration

Add the VAPID public key to your `.env` file:

```env
VITE_VAPID_PUBLIC_KEY=your_vapid_public_key_here
```

### 2. Generate VAPID Keys (Backend)

On the backend, generate VAPID keys for web push:

```python
# Python example using py-vapid
from py_vapid import Vapid

vapid = Vapid()
vapid.generate_keys()

print("Private Key:", vapid.private_key.decode())
print("Public Key:", vapid.public_key.decode())
```

Or using Node.js:

```bash
npm install web-push
npx web-push generate-vapid-keys
```

### 3. Backend API Endpoints

The frontend expects these endpoints:

#### Subscribe to Notifications
```
POST /notifications/subscribe
Authorization: Bearer <token>
Content-Type: application/json

{
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "keys": {
    "p256dh": "base64_encoded_key",
    "auth": "base64_encoded_key"
  }
}
```

#### Unsubscribe from Notifications
```
POST /notifications/unsubscribe
Authorization: Bearer <token>
Content-Type: application/json

{
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "keys": {
    "p256dh": "base64_encoded_key",
    "auth": "base64_encoded_key"
  }
}
```

#### Send Notification (Backend to User)
```python
# Python example using pywebpush
from pywebpush import webpush, WebPushException

subscription_info = {
    "endpoint": user_subscription.endpoint,
    "keys": {
        "p256dh": user_subscription.p256dh_key,
        "auth": user_subscription.auth_key
    }
}

notification_data = {
    "title": "New Buyer Interest",
    "body": "A buyer is interested in your wheat crop",
    "icon": "/icon-192.png",
    "url": "/marketplace/listing/123",
    "type": "buyer_interest",
    "id": "interest_456",
    "actions": [
        {"action": "view", "title": "View Details"},
        {"action": "dismiss", "title": "Dismiss"}
    ]
}

try:
    webpush(
        subscription_info=subscription_info,
        data=json.dumps(notification_data),
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims={
            "sub": "mailto:your-email@example.com"
        }
    )
except WebPushException as ex:
    print(f"Failed to send notification: {ex}")
```

### 4. PWA Icons

Create the following icon files in `public/`:
- `icon-72.png` (72x72)
- `icon-96.png` (96x96)
- `icon-128.png` (128x128)
- `icon-144.png` (144x144)
- `icon-152.png` (152x152)
- `icon-192.png` (192x192) - Required
- `icon-384.png` (384x384)
- `icon-512.png` (512x512) - Required
- `badge-72.png` (72x72) - Notification badge

See `public/ICONS_README.md` for icon generation instructions.

## Usage

### Initialize Notifications on App Load

The service worker is automatically initialized in `App.tsx`:

```typescript
import { initServiceWorker } from './utils/initServiceWorker';

onMount(() => {
  initServiceWorker();
});
```

### Request Permission After User Action

Show the permission prompt after a user action (e.g., after login):

```typescript
import NotificationPermissionPrompt from './components/notifications/NotificationPermissionPrompt';

<NotificationPermissionPrompt
  autoShow={true}
  onPermissionGranted={() => console.log('Notifications enabled')}
  onPermissionDenied={() => console.log('Notifications denied')}
/>
```

### Add Settings Page

Include the settings component in your settings/profile page:

```typescript
import NotificationSettings from './components/notifications/NotificationSettings';

<NotificationSettings />
```

### Send Test Notification

```typescript
import { notificationService } from './services/notification.service';

await notificationService.showLocalNotification({
  title: 'Test Notification',
  body: 'This is a test',
  type: 'general',
  url: '/',
});
```

## Notification Types

The system supports these notification types:

1. **buyer_interest** - Buyer expressed interest in a listing
   - Routes to: `/marketplace/listing/{id}`
   - Priority: High

2. **strategy_reminder** - Crop strategy implementation reminder
   - Routes to: `/strategy/view/{id}`
   - Priority: Medium

3. **weather_alert** - Weather warning or alert
   - Routes to: `/dashboard`
   - Priority: High

4. **harvest_reminder** - Harvest timing reminder
   - Routes to: `/farm/{id}`
   - Priority: Medium

5. **general** - General platform notifications
   - Routes to: `/dashboard`
   - Priority: Low

## Notification Payload Format

```typescript
{
  title: string;              // Notification title
  body: string;               // Notification body text
  icon?: string;              // Icon URL (default: /icon-192.png)
  badge?: string;             // Badge URL (default: /badge-72.png)
  tag?: string;               // Notification tag for grouping
  url?: string;               // URL to navigate on click
  type?: NotificationType;    // Notification type
  id?: string;                // Unique notification ID
  requireInteraction?: boolean; // Keep notification visible
  actions?: Array<{           // Action buttons
    action: string;
    title: string;
    icon?: string;
  }>;
}
```

## Browser Support

- ✅ Chrome 50+
- ✅ Firefox 44+
- ✅ Edge 17+
- ✅ Safari 16+ (iOS 16.4+)
- ✅ Opera 37+
- ❌ Internet Explorer (not supported)

## Testing

### Test Notification Permission Flow

1. Open the app in a supported browser
2. Navigate to a protected route (triggers auto-prompt after 2 seconds)
3. Click "Enable" in the permission prompt
4. Browser will show native permission dialog
5. Grant permission
6. Test notification should appear

### Test Notification Display

```typescript
// In browser console
const registration = await navigator.serviceWorker.ready;
registration.showNotification('Test', {
  body: 'This is a test notification',
  icon: '/icon-192.png',
  badge: '/badge-72.png',
  tag: 'test',
  data: { url: '/' }
});
```

### Test Service Worker

```bash
# Open Chrome DevTools
# Go to Application > Service Workers
# Check if sw.js is registered and activated
# Click "Update" to reload service worker
# Click "Unregister" to remove service worker
```

## Troubleshooting

### Notifications Not Showing

1. **Check browser support:**
   ```javascript
   console.log('Service Worker:', 'serviceWorker' in navigator);
   console.log('Push Manager:', 'PushManager' in window);
   console.log('Notification:', 'Notification' in window);
   ```

2. **Check permission state:**
   ```javascript
   console.log('Permission:', Notification.permission);
   ```

3. **Check service worker registration:**
   ```javascript
   navigator.serviceWorker.getRegistrations().then(registrations => {
     console.log('Registrations:', registrations);
   });
   ```

4. **Check push subscription:**
   ```javascript
   navigator.serviceWorker.ready.then(registration => {
     registration.pushManager.getSubscription().then(subscription => {
       console.log('Subscription:', subscription);
     });
   });
   ```

### Service Worker Not Updating

1. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
2. Clear cache in DevTools
3. Unregister service worker and reload
4. Check for service worker errors in console

### HTTPS Required

Service workers require HTTPS in production. Exceptions:
- `localhost` (development)
- `127.0.0.1` (development)

### iOS Safari Limitations

- Requires iOS 16.4+ and Safari 16.4+
- User must add app to home screen for full PWA features
- Notifications only work when app is added to home screen

## Security Considerations

1. **VAPID Keys**: Keep private key secure on backend
2. **Subscription Validation**: Verify subscriptions belong to authenticated users
3. **Rate Limiting**: Implement rate limits on notification endpoints
4. **Content Validation**: Sanitize notification content to prevent XSS
5. **HTTPS Only**: Always use HTTPS in production

## Performance

- Service worker caches static assets for offline access
- Notification subscriptions stored in backend database
- Push notifications delivered via browser push service (FCM, APNs, etc.)
- Minimal impact on app performance

## Future Enhancements

1. **Notification Preferences**: Allow users to customize notification types
2. **Quiet Hours**: Respect user's quiet hours settings
3. **Notification History**: Store notification history in app
4. **Rich Notifications**: Add images and more interactive elements
5. **Notification Grouping**: Group related notifications
6. **Analytics**: Track notification delivery and engagement rates

## References

- [Web Push Notifications Guide](https://web.dev/push-notifications-overview/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [Notification API](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API)
- [VAPID Protocol](https://datatracker.ietf.org/doc/html/rfc8292)
