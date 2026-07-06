# Content Security Policy (CSP) Fix

## Issue

Frontend application was unable to connect to the backend API due to Content Security Policy restrictions:

```
Fetch API cannot load http://localhost:8000/auth/signup. 
Refused to connect because it violates the document's Content Security Policy.
```

## Root Causes

1. **CSP Restriction**: The `connect-src` directive in index.html only allowed connections to `'self'` and `https://*.amazonaws.com`, blocking localhost:8000
2. **Missing Environment Configuration**: No .env file existed to configure the API base URL

## Solutions Applied

### 1. Updated Content Security Policy (index.html)

**Before:**
```html
<meta http-equiv="Content-Security-Policy" 
      content="... connect-src 'self' https://*.amazonaws.com; ..." />
```

**After:**
```html
<meta http-equiv="Content-Security-Policy" 
      content="... connect-src 'self' http://localhost:* http://127.0.0.1:* https://*.amazonaws.com; ..." />
```

**Changes:**
- Added `http://localhost:*` to allow connections to any localhost port
- Added `http://127.0.0.1:*` to allow connections to loopback address
- Kept `https://*.amazonaws.com` for production AWS services

### 2. Created Environment Configuration

**New Files:**
- `.env` - Development environment configuration
- `.env.example` - Template for environment variables

**Configuration:**
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_ENV=development
```

## Files Modified

1. `rural-farming-platform/solidjs/index.html` - Updated CSP policy
2. `rural-farming-platform/solidjs/.env` - Created (new file)
3. `rural-farming-platform/solidjs/.env.example` - Created (new file)

## How It Works

### Development Environment
- Frontend runs on: `http://localhost:3000` (Vite dev server)
- Backend runs on: `http://localhost:8000` (FastAPI/Uvicorn)
- CSP allows: `http://localhost:*` connections

### Production Environment
For production, update the CSP policy to:
```html
<meta http-equiv="Content-Security-Policy" 
      content="... connect-src 'self' https://api.yourdomain.com https://*.amazonaws.com; ..." />
```

And set the environment variable:
```env
VITE_API_URL=https://api.yourdomain.com/api/v1
```

## Testing

### 1. Restart the Frontend Dev Server
```bash
cd rural-farming-platform/solidjs
npm run dev
```

### 2. Verify API Connection
- Open browser to http://localhost:3000
- Open browser console (F12)
- Try to sign up or sign in
- API requests should now succeed

### 3. Check CSP in Browser
- Open browser DevTools → Network tab
- Look for requests to localhost:8000
- Should see successful connections (200 status)

## Security Considerations

### Development
- Localhost connections are safe for development
- CSP is relaxed to allow local API connections

### Production
- Remove localhost from CSP `connect-src`
- Use HTTPS for all API connections
- Restrict `connect-src` to specific domains
- Consider using a reverse proxy or API gateway

### Recommended Production CSP
```html
<meta http-equiv="Content-Security-Policy" 
      content="
        default-src 'self'; 
        script-src 'self'; 
        style-src 'self' 'unsafe-inline'; 
        img-src 'self' data: https:; 
        font-src 'self' data:; 
        connect-src 'self' https://api.yourdomain.com https://*.amazonaws.com; 
        frame-ancestors 'none'; 
        base-uri 'self'; 
        form-action 'self';
      " />
```

## Additional Notes

### Why CSP is Important
- Prevents XSS (Cross-Site Scripting) attacks
- Restricts resource loading to trusted sources
- Provides defense-in-depth security layer

### Development vs Production
- Development: Relaxed CSP for localhost connections
- Production: Strict CSP with specific domain whitelist

### Environment Variables
- `.env` is gitignored (not committed to repository)
- `.env.example` is committed as a template
- Each developer creates their own `.env` from `.env.example`

## Troubleshooting

### Issue: Still getting CSP errors
**Solution**: Hard refresh the browser (Ctrl+Shift+R or Cmd+Shift+R)

### Issue: API requests fail with CORS error
**Solution**: Check backend CORS configuration in FastAPI

### Issue: Environment variables not loading
**Solution**: Restart Vite dev server after changing .env

### Issue: Production build not working
**Solution**: Update CSP in index.html for production domain

## Related Documentation

- See `API_CLIENT_DOCUMENTATION.md` for API client usage
- See `OFFLINE_SUPPORT.md` for offline functionality
- See backend CORS configuration in `app/main.py`

## Date
February 28, 2026
