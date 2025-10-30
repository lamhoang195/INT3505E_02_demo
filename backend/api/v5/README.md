# V5 API - Authentication Storage Methods Demo

## Overview
API V5 demonstrates three different methods for storing authentication tokens on the client side:

1. **localStorage** - Persistent browser storage
2. **sessionStorage** - Session-only browser storage  
3. **HTTP-Only Cookie** - Secure server-managed cookie

## Endpoints

### 1. API Info
```
GET /api/v5
```
Returns information about V5 API and available endpoints.

### 2. Login with localStorage
```
POST /api/v5/auth/login/localstorage
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "storage_method": "localStorage",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": { ... },
  "_instructions": {
    "how_to_store": "localStorage.setItem('auth_token', token)",
    "how_to_retrieve": "localStorage.getItem('auth_token')",
    "how_to_use": "Add to Authorization header: Bearer <token>"
  }
}
```

**Client-side JavaScript:**
```javascript
// Store token
localStorage.setItem('auth_token', token);

// Retrieve token
const token = localStorage.getItem('auth_token');

// Use token in API requests
fetch('/api/v5/auth/protected', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Clear token
localStorage.removeItem('auth_token');
```

### 3. Login with sessionStorage
```
POST /api/v5/auth/login/sessionstorage
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "storage_method": "sessionStorage",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": { ... },
  "_instructions": {
    "how_to_store": "sessionStorage.setItem('auth_token', token)",
    "how_to_retrieve": "sessionStorage.getItem('auth_token')"
  }
}
```

**Client-side JavaScript:**
```javascript
// Store token
sessionStorage.setItem('auth_token', token);

// Retrieve token
const token = sessionStorage.getItem('auth_token');

// Use token in API requests
fetch('/api/v5/auth/protected', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Clear token (or close tab/window)
sessionStorage.removeItem('auth_token');
```

### 4. Login with HTTP-Only Cookie
```
POST /api/v5/auth/login/cookie
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "storage_method": "HTTP-Only Cookie",
  "user": { ... },
  "_instructions": {
    "how_stored": "Server automatically sets HTTP-Only cookie",
    "how_to_use": "Browser automatically sends cookie with requests",
    "javascript_access": "document.cookie will NOT show this cookie"
  }
}
```

**Important:** Server automatically sets cookie in response headers:
```
Set-Cookie: auth_token=eyJhbGci...; HttpOnly; SameSite=Lax; Max-Age=86400
```

**Client-side JavaScript:**
```javascript
// Login - server sets cookie automatically
await fetch('/api/v5/auth/login/cookie', {
  method: 'POST',
  credentials: 'include',  // IMPORTANT: Include cookies
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ username, password })
});

// Make authenticated requests - cookie sent automatically
await fetch('/api/v5/auth/verify', {
  credentials: 'include'  // IMPORTANT: Include cookies
});

// Logout - server clears cookie
await fetch('/api/v5/auth/logout', {
  method: 'POST',
  credentials: 'include'
});
```

### 5. Verify Token (Cookie)
```
GET /api/v5/auth/verify
Cookie: auth_token=eyJhbGci... (automatically sent by browser)
```

**Response:**
```json
{
  "success": true,
  "message": "Token is valid",
  "user": {
    "user_id": "1",
    "username": "admin",
    "role": "admin"
  }
}
```

### 6. Logout (Clear Cookie)
```
POST /api/v5/auth/logout
```

**Response:**
```json
{
  "success": true,
  "message": "Logout successful",
  "_instructions": {
    "localStorage": "Also clear: localStorage.removeItem('auth_token')",
    "sessionStorage": "Also clear: sessionStorage.removeItem('auth_token')",
    "cookie": "HTTP-Only cookie has been cleared by server"
  }
}
```

### 7. Protected Route (Cookie)
```
GET /api/v5/auth/protected
Cookie: auth_token=eyJhbGci... (automatically sent by browser)
```

**Response:**
```json
{
  "success": true,
  "message": "Access granted to protected route",
  "data": {
    "current_user": { ... },
    "server_time": "2025-10-30T10:30:00Z"
  }
}
```

### 8. Compare Storage Methods
```
GET /api/v5/auth/compare
```

Returns a detailed comparison of all three storage methods.

## Testing

### Using cURL

**1. localStorage/sessionStorage (manual token handling):**
```bash
# Login
curl -X POST http://localhost:5000/api/v5/auth/login/localstorage \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Copy token from response, then use it:
curl -X GET http://localhost:5000/api/v5/auth/protected \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**2. HTTP-Only Cookie (automatic):**
```bash
# Login and save cookie
curl -X POST http://localhost:5000/api/v5/auth/login/cookie \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt

# Verify using saved cookie
curl -X GET http://localhost:5000/api/v5/auth/verify \
  -b cookies.txt

# Access protected route
curl -X GET http://localhost:5000/api/v5/auth/protected \
  -b cookies.txt

# Logout
curl -X POST http://localhost:5000/api/v5/auth/logout \
  -b cookies.txt -c cookies.txt
```

### Using the Demo Page

Visit: `http://localhost:5000/auth-storage-demo`

## Implementation Details

### Cookie Configuration
```python
response.set_cookie(
    'auth_token',
    token,
    httponly=True,      # Not accessible via JavaScript
    secure=False,       # Set True in production (HTTPS only)
    samesite='Lax',     # CSRF protection
    max_age=86400       # 24 hours
)
```

### Token Format
All methods use the same JWT token format:
```json
{
  "user_id": "1",
  "username": "admin",
  "role": "admin",
  "exp": 1698675600,
  "iat": 1698589200
}
```