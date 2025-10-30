"""
V5 Authentication Storage Demo
Demonstrates three different client-side storage methods for JWT tokens:
1. localStorage - Token stored in localStorage (persistent across browser restarts)
2. sessionStorage - Token stored in sessionStorage (cleared when tab closes)
3. HTTP-Only Cookie - Token stored in secure HTTP-only cookie (not accessible via JS)
"""
from flask import Blueprint, request, jsonify, make_response
from datetime import datetime, timedelta
import jwt
from functools import wraps
from backend.services.user_service import UserService

# Create blueprint for V5 auth storage demo
auth_storage_v5 = Blueprint('auth_storage_v5', __name__)
user_service = UserService()

# JWT Configuration
JWT_SECRET_KEY = 'v5-storage-demo-secret-key'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def generate_jwt_token(user_data):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_data['id'],
        'username': user_data['username'],
        'role': user_data['role'],
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt_token(token):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_token_from_cookie(f):
    """Decorator to protect routes - read token from HTTP-Only cookie"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TOKEN_MISSING',
                    'message': 'Authentication token cookie is required'
                }
            }), 401
        
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TOKEN_INVALID',
                    'message': 'Invalid or expired token'
                }
            }), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

@auth_storage_v5.route('/api/v5', methods=['GET'])
def v5_info():
    """API V5 Information"""
    return jsonify({
        'version': 'v5',
        'name': 'Authentication Storage Methods Demo',
        'description': 'So sánh 3 cách lưu trữ token ở client-side',
        'storage_methods': [
            {
                'name': 'localStorage',
                'persistent': True,
                'accessible_by_js': True,
                'cleared_when': 'Manual or browser cache clear',
                'security_note': 'Vulnerable to XSS attacks'
            },
            {
                'name': 'sessionStorage',
                'persistent': False,
                'accessible_by_js': True,
                'cleared_when': 'Browser tab/window closes',
                'security_note': 'Vulnerable to XSS attacks'
            },
            {
                'name': 'HTTP-Only Cookie',
                'persistent': True,
                'accessible_by_js': False,
                'cleared_when': 'Cookie expires or manual clear',
                'security_note': 'Protected from XSS, vulnerable to CSRF (use with CSRF tokens)'
            }
        ],
        'endpoints': {
            'localStorage': 'POST /api/v5/auth/login/localstorage - Returns token in response body',
            'sessionStorage': 'POST /api/v5/auth/login/sessionstorage - Returns token in response body',
            'httpOnlyCookie': 'POST /api/v5/auth/login/cookie - Sets token in HTTP-Only cookie',
            'verify_cookie': 'GET /api/v5/auth/verify - Verify token from cookie',
            'logout_cookie': 'POST /api/v5/auth/logout - Clear HTTP-Only cookie'
        },
        '_links': {
            'self': '/api/v5',
            'documentation': '/api/docs'
        }
    }), 200

@auth_storage_v5.route('/api/v5/auth/login/localstorage', methods=['POST'])
def login_localstorage():
    """
    Login - Token for localStorage
    Client should store token in localStorage after receiving
    ---
    tags:
      - V5 - Auth Storage Demo
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "admin"
            password:
              type: string
              example: "admin123"
    responses:
      200:
        description: Login successful, token returned for localStorage storage
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Username and password are required'
                }
            }), 400
        
        user = user_service.authenticate(username, password)
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Invalid username or password'
                }
            }), 401
        
        token = generate_jwt_token(user)
        user_data = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'storage_method': 'localStorage',
            'token': token,
            'user': user_data,
            '_instructions': {
                'how_to_store': 'localStorage.setItem("auth_token", token)',
                'how_to_retrieve': 'localStorage.getItem("auth_token")',
                'how_to_use': 'Add to Authorization header: Bearer <token>',
                'how_to_clear': 'localStorage.removeItem("auth_token")'
            },
            '_characteristics': {
                'persistent': True,
                'survives_browser_restart': True,
                'accessible_by_javascript': True,
                'security_risk': 'XSS (Cross-Site Scripting)',
                'best_for': 'Simple apps, remember me features'
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500

@auth_storage_v5.route('/api/v5/auth/login/sessionstorage', methods=['POST'])
def login_sessionstorage():
    """
    Login - Token for sessionStorage
    Client should store token in sessionStorage after receiving
    ---
    tags:
      - V5 - Auth Storage Demo
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "admin"
            password:
              type: string
              example: "admin123"
    responses:
      200:
        description: Login successful, token returned for sessionStorage storage
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Username and password are required'
                }
            }), 400
        
        user = user_service.authenticate(username, password)
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Invalid username or password'
                }
            }), 401
        
        token = generate_jwt_token(user)
        user_data = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'storage_method': 'sessionStorage',
            'token': token,
            'user': user_data,
            '_instructions': {
                'how_to_store': 'sessionStorage.setItem("auth_token", token)',
                'how_to_retrieve': 'sessionStorage.getItem("auth_token")',
                'how_to_use': 'Add to Authorization header: Bearer <token>',
                'how_to_clear': 'sessionStorage.removeItem("auth_token")'
            },
            '_characteristics': {
                'persistent': False,
                'survives_browser_restart': False,
                'cleared_when': 'Browser tab or window closes',
                'accessible_by_javascript': True,
                'security_risk': 'XSS (Cross-Site Scripting)',
                'best_for': 'Temporary sessions, single tab usage'
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500

@auth_storage_v5.route('/api/v5/auth/login/cookie', methods=['POST'])
def login_cookie():
    """
    Login - Token in HTTP-Only Cookie
    Server sets token in HTTP-Only cookie (not accessible by JavaScript)
    ---
    tags:
      - V5 - Auth Storage Demo
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "admin"
            password:
              type: string
              example: "admin123"
    responses:
      200:
        description: Login successful, token set in HTTP-Only cookie
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Username and password are required'
                }
            }), 400
        
        user = user_service.authenticate(username, password)
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Invalid username or password'
                }
            }), 401
        
        token = generate_jwt_token(user)
        user_data = {k: v for k, v in user.items() if k != 'password'}
        
        # Create response
        response = make_response(jsonify({
            'success': True,
            'message': 'Login successful',
            'storage_method': 'HTTP-Only Cookie',
            'user': user_data,
            '_instructions': {
                'how_stored': 'Server automatically sets HTTP-Only cookie',
                'how_to_use': 'Browser automatically sends cookie with requests to same domain',
                'how_to_clear': 'Call POST /api/v5/auth/logout',
                'javascript_access': 'document.cookie will NOT show this cookie (HTTP-Only)'
            },
            '_characteristics': {
                'persistent': True,
                'survives_browser_restart': True,
                'accessible_by_javascript': False,
                'http_only': True,
                'security_risk': 'CSRF (Cross-Site Request Forgery) - use CSRF tokens',
                'security_benefit': 'Protected from XSS attacks',
                'best_for': 'Production apps with high security requirements'
            }
        }), 200)
        
        # Set HTTP-Only cookie
        # httponly=True: Not accessible via JavaScript
        # secure=True: Only sent over HTTPS (set False for development)
        # samesite='Lax': Provides CSRF protection
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax',
            max_age=JWT_EXPIRATION_HOURS * 3600  # in seconds
        )
        
        return response
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500

@auth_storage_v5.route('/api/v5/auth/verify', methods=['GET'])
@require_token_from_cookie
def verify_token():
    """
    Verify token from HTTP-Only cookie
    ---
    tags:
      - V5 - Auth Storage Demo
    responses:
      200:
        description: Token is valid
      401:
        description: Token missing or invalid
    """
    return jsonify({
        'success': True,
        'message': 'Token is valid',
        'user': request.current_user,
        '_metadata': {
            'storage_method': 'HTTP-Only Cookie',
            'token_read_from': 'Cookie header (automatically sent by browser)',
            'javascript_accessible': False
        }
    }), 200

@auth_storage_v5.route('/api/v5/auth/logout', methods=['POST'])
def logout():
    """
    Logout - Clear HTTP-Only cookie
    ---
    tags:
      - V5 - Auth Storage Demo
    responses:
      200:
        description: Logout successful, cookie cleared
    """
    response = make_response(jsonify({
        'success': True,
        'message': 'Logout successful',
        '_instructions': {
            'localStorage': 'Also clear: localStorage.removeItem("auth_token")',
            'sessionStorage': 'Also clear: sessionStorage.removeItem("auth_token")',
            'cookie': 'HTTP-Only cookie has been cleared by server'
        }
    }), 200)
    
    # Clear cookie by setting empty value and max_age=0
    response.set_cookie('auth_token', '', max_age=0)
    
    return response

@auth_storage_v5.route('/api/v5/auth/protected', methods=['GET'])
@require_token_from_cookie
def protected_route():
    """
    Protected route - Requires HTTP-Only cookie
    ---
    tags:
      - V5 - Auth Storage Demo
    responses:
      200:
        description: Access granted
      401:
        description: Unauthorized
    """
    return jsonify({
        'success': True,
        'message': 'Access granted to protected route',
        'data': {
            'current_user': request.current_user,
            'server_time': datetime.utcnow().isoformat() + 'Z'
        },
        '_metadata': {
            'authentication_method': 'HTTP-Only Cookie',
            'secure': True
        }
    }), 200

@auth_storage_v5.route('/api/v5/auth/compare', methods=['GET'])
def compare_storage_methods():
    """
    Compare all three storage methods
    ---
    tags:
      - V5 - Auth Storage Demo
    responses:
      200:
        description: Comparison of storage methods
    """
    return jsonify({
        'success': True,
        'comparison': {
            'localStorage': {
                'persistence': 'Permanent (until cleared)',
                'survives_restart': True,
                'survives_tab_close': True,
                'js_accessible': True,
                'auto_sent_with_request': False,
                'xss_vulnerable': True,
                'csrf_vulnerable': False,
                'storage_limit': '5-10MB',
                'best_use_case': 'Remember me, user preferences',
                'implementation': 'Manual (store/retrieve in JS)'
            },
            'sessionStorage': {
                'persistence': 'Session only',
                'survives_restart': False,
                'survives_tab_close': False,
                'js_accessible': True,
                'auto_sent_with_request': False,
                'xss_vulnerable': True,
                'csrf_vulnerable': False,
                'storage_limit': '5-10MB',
                'best_use_case': 'Single session, temporary data',
                'implementation': 'Manual (store/retrieve in JS)'
            },
            'httpOnlyCookie': {
                'persistence': 'Until expiry or cleared',
                'survives_restart': True,
                'survives_tab_close': True,
                'js_accessible': False,
                'auto_sent_with_request': True,
                'xss_vulnerable': False,
                'csrf_vulnerable': True,
                'storage_limit': '4KB per cookie',
                'best_use_case': 'Production auth, high security',
                'implementation': 'Automatic (browser handles)'
            }
        },
        'recommendations': {
            'development': 'localStorage or sessionStorage (easier to debug)',
            'production': 'HTTP-Only Cookie with CSRF protection (most secure)',
            'high_security': 'HTTP-Only Cookie + Secure + SameSite + CSRF tokens',
            'mobile_app': 'Secure storage in native app (not web storage)'
        }
    }), 200

