# V5 API Testing Guide

## Quick Start

### 1. Start the Server
```bash
python run.py
```

The server will start at `http://localhost:5000`

### 2. Access the Demo Page
Open your browser and navigate to:
```
http://localhost:5000/auth-storage-demo
```

This provides an interactive demo with:
- Three side-by-side login forms (one for each storage method)
- Visual feedback for each action
- Comparison table
- Security notes

## Manual API Testing

### Test 1: localStorage Method

**Step 1 - Login:**
```bash
curl -X POST http://localhost:5000/api/v5/auth/login/localstorage \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

**Expected Response:**
```json
{
  "success": true,
  "storage_method": "localStorage",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "1",
    "username": "admin",
    "role": "admin"
  },
  "_instructions": { ... }
}
```

**Step 2 - Copy the token and test protected route:**
```bash
# Replace YOUR_TOKEN with the token from previous response
curl -X GET http://localhost:5000/api/v5/auth/protected \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 2: sessionStorage Method

**Step 1 - Login:**
```bash
curl -X POST http://localhost:5000/api/v5/auth/login/sessionstorage \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

**Step 2 - Use token (same as localStorage):**
```bash
curl -X GET http://localhost:5000/api/v5/auth/protected \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 3: HTTP-Only Cookie Method

**Step 1 - Login and save cookie:**
```bash
curl -X POST http://localhost:5000/api/v5/auth/login/cookie \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}" \
  -c cookies.txt
```

**Expected Response:**
```json
{
  "success": true,
  "storage_method": "HTTP-Only Cookie",
  "user": { ... },
  "_instructions": { ... }
}
```

The cookie is automatically saved to `cookies.txt`

**Step 2 - Verify token using saved cookie:**
```bash
curl -X GET http://localhost:5000/api/v5/auth/verify \
  -b cookies.txt
```

**Step 3 - Access protected route:**
```bash
curl -X GET http://localhost:5000/api/v5/auth/protected \
  -b cookies.txt
```

**Step 4 - Logout (clear cookie):**
```bash
curl -X POST http://localhost:5000/api/v5/auth/logout \
  -b cookies.txt -c cookies.txt
```

### Test 4: Compare All Methods

**Get comparison data:**
```bash
curl -X GET http://localhost:5000/api/v5/auth/compare
```

## Testing with Browser Console

### localStorage Test
```javascript
// 1. Login
const response1 = await fetch('http://localhost:5000/api/v5/auth/login/localstorage', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const data1 = await response1.json();
console.log(data1);

// 2. Store token
localStorage.setItem('auth_token', data1.token);

// 3. Verify
const token = localStorage.getItem('auth_token');
const response2 = await fetch('http://localhost:5000/api/v5/auth/protected', {
  headers: { 'Authorization': `Bearer ${token}` }
});
console.log(await response2.json());

// 4. Clear
localStorage.removeItem('auth_token');
```

### sessionStorage Test
```javascript
// 1. Login
const response1 = await fetch('http://localhost:5000/api/v5/auth/login/sessionstorage', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const data1 = await response1.json();
console.log(data1);

// 2. Store token
sessionStorage.setItem('auth_token', data1.token);

// 3. Verify
const token = sessionStorage.getItem('auth_token');
const response2 = await fetch('http://localhost:5000/api/v5/auth/protected', {
  headers: { 'Authorization': `Bearer ${token}` }
});
console.log(await response2.json());

// 4. Clear (or just close the tab)
sessionStorage.removeItem('auth_token');
```

### HTTP-Only Cookie Test
```javascript
// 1. Login (cookie set automatically)
const response1 = await fetch('http://localhost:5000/api/v5/auth/login/cookie', {
  method: 'POST',
  credentials: 'include',  // IMPORTANT!
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
console.log(await response1.json());

// 2. Verify (cookie sent automatically)
const response2 = await fetch('http://localhost:5000/api/v5/auth/verify', {
  credentials: 'include'  // IMPORTANT!
});
console.log(await response2.json());

// 3. Access protected route (cookie sent automatically)
const response3 = await fetch('http://localhost:5000/api/v5/auth/protected', {
  credentials: 'include'  // IMPORTANT!
});
console.log(await response3.json());

// 4. Try to access cookie (will fail - that's the point!)
console.log(document.cookie); // auth_token will NOT appear (HTTP-Only)

// 5. Logout
const response4 = await fetch('http://localhost:5000/api/v5/auth/logout', {
  method: 'POST',
  credentials: 'include'
});
console.log(await response4.json());
```

## Available Test Accounts

Default test account:
- **Username:** `admin`
- **Password:** `admin123`

You can also use:
- Username: `user1`, Password: `password1` (user role)
- Username: `user2`, Password: `password2` (user role)

## Expected Behaviors

### localStorage
- ✓ Token persists after browser restart
- ✓ Token visible in DevTools > Application > Local Storage
- ✓ Must manually include token in requests
- ✓ Can access from any script on same origin

### sessionStorage
- ✓ Token cleared when tab/window closes
- ✓ Token visible in DevTools > Application > Session Storage
- ✓ Must manually include token in requests
- ✗ Lost on browser restart

### HTTP-Only Cookie
- ✓ Token persists after browser restart
- ✓ Token visible in DevTools > Application > Cookies (but NOT in document.cookie)
- ✓ Automatically sent with requests to same domain
- ✗ NOT accessible via JavaScript (this is good for security!)
- ⚠ Requires `credentials: 'include'` in fetch requests

## Common Issues

### Issue 1: Cookie not working in fetch
**Error:** 401 Unauthorized when calling cookie endpoints

**Solution:** Add `credentials: 'include'` to fetch options:
```javascript
fetch(url, { credentials: 'include' })
```

### Issue 2: Can't see auth_token in document.cookie
**Error:** Cookie not visible in console

**Solution:** This is **correct behavior**! HTTP-Only cookies are intentionally hidden from JavaScript. Check DevTools > Application > Cookies to see it.

### Issue 3: CORS errors with cookies
**Error:** Cross-origin request blocked

**Solution:** 
1. Server must have proper CORS configuration
2. Use `credentials: 'include'` on client
3. Make sure you're testing from the same origin (localhost:5000)

## Cleanup

After testing, you can clean up:

```bash
# Delete cookies file
rm cookies.txt

# Or in browser console:
localStorage.clear();
sessionStorage.clear();
```

## Next Steps

1. ✓ Try the interactive demo at `/auth-storage-demo`
2. ✓ Test each storage method with curl
3. ✓ Test in browser console
4. ✓ Compare the security implications
5. ✓ Check the Swagger docs at `/api/docs`

## Swagger Documentation

Full API documentation is available at:
```
http://localhost:5000/api/docs
```

Look for the **"V5 - Auth Storage Demo"** section.

