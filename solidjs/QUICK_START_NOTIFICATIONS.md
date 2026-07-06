# Quick Start: Web Push Notifications

## 🚀 Get Started in 5 Minutes

### Step 1: Generate VAPID Keys (Backend)

```bash
# Option A: Using Node.js
npm install -g web-push
web-push generate-vapid-keys

# Option B: Using Python
pip install py-vapid
python -c "from py_vapid import Vapid; v = Vapid(); v.generate_keys(); print('Public:', v.public_key.decode()); print('Private:', v.private_key.decode())"
```

### Step 2: Configure Environment

Create `.env` file in `solidjs/` directory:

```env
VITE_VAPID_PUBLIC_KEY=BNxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Create Icons (Optional for Testing)

For quick testing, you can skip this step. The app will work without icons (they'll just show as broken images).

For production, create these files in `public/`:
- `icon-192.png` (192x192 pixels)
- `icon-512.png` (512x512 pixels)
- `badge-72.png` (72x72 pixels)

Use any online tool like https://realfavicongenerator.net/

### Step 4: Run the App

```bash
cd solidjs
npm install
npm run dev
```

Open http://localhost:3000

### Step 5: Test Notifications

1. Navigate to `/dashboard` (after login)
2. Wait 2 seconds for permission prompt
3. Click "Enable" button
4. Grant permission in browser dialog
5. You should see a test notification!

### Step 6: Test from Settings

1. Go to dashboard
2. Scroll to notification settings (if added to settings page)
3. Click "Send Test Notification"
4. You should see a notification appear

---

## 🔧 Backend Integration

### Install Dependencies

```bash
# Python
pip install pywebpush

# Node.js
npm install web-push
```

### Create Subscribe Endpoint (Python/FastAPI)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()

class PushSubscription(BaseModel):
    endpoint: str
    keys: dict

@router.post("/notifications/subscribe")
async def subscribe_to_notifications(
    subscription: PushSubscription,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Store subscription in database
    db_subscription = NotificationSubscription(
        user_id=current_user.id,
        endpoint=subscription.endpoint,
        p256dh_key=subscription.keys["p256dh"],
        auth_key=subscription.keys["auth"]
    )
    db.add(db_subscription)
    db.commit()
    
    return {"message": "Subscribed successfully"}

@router.post("/notifications/unsubscribe")
async def unsubscribe_from_notifications(
    subscription: PushSubscription,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Remove subscription from database
    db.query(NotificationSubscription).filter(
        NotificationSubscription.user_id == current_user.id,
        NotificationSubscription.endpoint == subscription.endpoint
    ).delete()
    db.commit()
    
    return {"message": "Unsubscribed successfully"}
```

### Send Notification (Python)

```python
from pywebpush import webpush, WebPushException
import json

def send_notification(user_id: int, notification_data: dict):
    # Get user's subscriptions from database
    subscriptions = db.query(NotificationSubscription).filter(
        NotificationSubscription.user_id == user_id
    ).all()
    
    for sub in subscriptions:
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": {
                "p256dh": sub.p256dh_key,
                "auth": sub.auth_key
            }
        }
        
        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(notification_data),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:admin@example.com"
                }
            )
        except WebPushException as ex:
            print(f"Failed to send notification: {ex}")
            # Remove invalid subscription
            if ex.response and ex.response.status_code in [404, 410]:
                db.delete(sub)
                db.commit()

# Example usage:
send_notification(
    user_id=123,
    notification_data={
        "title": "New Buyer Interest",
        "body": "A buyer is interested in your wheat crop",
        "url": "/marketplace/listing/456",
        "type": "buyer_interest",
        "id": "interest_789"
    }
)
```

---

## 📱 Testing on Mobile

### Android Chrome
1. Open Chrome on Android
2. Navigate to your app (must be HTTPS in production)
3. Click "Add to Home Screen"
4. Open app from home screen
5. Grant notification permission
6. Test notifications

### iOS Safari (16.4+)
1. Open Safari on iOS 16.4+
2. Navigate to your app (must be HTTPS)
3. Tap Share button
4. Tap "Add to Home Screen"
5. Open app from home screen
6. Grant notification permission
7. Test notifications

**Note:** iOS requires the app to be added to home screen for notifications to work.

---

## 🐛 Troubleshooting

### Notifications Not Showing

**Check browser support:**
```javascript
console.log('Service Worker:', 'serviceWorker' in navigator);
console.log('Push Manager:', 'PushManager' in window);
console.log('Notification:', 'Notification' in window);
```

**Check permission:**
```javascript
console.log('Permission:', Notification.permission);
```

**Check service worker:**
```javascript
navigator.serviceWorker.getRegistrations().then(console.log);
```

### Service Worker Not Registering

1. Check browser console for errors
2. Ensure `public/sw.js` exists
3. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
4. Check DevTools > Application > Service Workers

### VAPID Key Issues

- Ensure key is in correct format (starts with 'B')
- Check that key is set in `.env` file
- Restart dev server after changing `.env`

---

## 📚 More Information

See `NOTIFICATIONS_IMPLEMENTATION.md` for complete documentation.

---

## ✅ Quick Checklist

- [ ] VAPID keys generated
- [ ] `.env` file configured
- [ ] Backend endpoints implemented
- [ ] Icons created (optional for testing)
- [ ] App running on localhost
- [ ] Permission granted in browser
- [ ] Test notification received
- [ ] Notification click works
- [ ] Action buttons work

---

## 🎉 Success!

If you can see notifications, you're all set! The system is working correctly.

For production deployment:
1. Ensure HTTPS is enabled
2. Create proper app icons
3. Test on multiple devices
4. Monitor notification delivery rates
