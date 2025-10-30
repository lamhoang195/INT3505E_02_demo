"""
V5 API - Authentication Storage Methods Demo
Demonstrates different client-side storage methods:
- localStorage: Persistent storage, survives browser restart
- sessionStorage: Session-only storage, cleared when tab closes
- HTTP-Only Cookie: Server-set cookie, not accessible from JavaScript
"""

from backend.api.v5.auth_storage import auth_storage_v5
