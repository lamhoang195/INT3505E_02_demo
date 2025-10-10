"""
V3 Authentication Controller - Stateless with JWT
Demonstrates REST constraint: Stateless
- Server không lưu session
- Mỗi request tự chứa đầy đủ thông tin (JWT token)
- Token được mã hóa và giải mã
- Không phụ thuộc vào server state
"""
from flask import Blueprint, request, jsonify
from flasgger import swag_from
import jwt
from datetime import datetime, timedelta
from functools import wraps
from backend.services.user_service import UserService

# Create blueprint for V3 auth
auth_v3 = Blueprint('auth_v3', __name__)
user_service = UserService()

# JWT Configuration
JWT_SECRET_KEY = 'your-secret-key-change-in-production'
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

def require_jwt_token(f):
    """Decorator to protect routes with JWT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Format: "Bearer <token>"
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_TOKEN_FORMAT',
                        'message': 'Token format should be: Bearer <token>'
                    }
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TOKEN_MISSING',
                    'message': 'Authentication token is required'
                }
            }), 401
        
        # Decode token
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TOKEN_INVALID',
                    'message': 'Invalid or expired token'
                }
            }), 401
        
        # Add user info to request context
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

@auth_v3.route('/api/v3', methods=['GET'])
def v3_info():
    """API V3 Information"""
    return jsonify({
        'version': 'v3',
        'name': 'Stateless with JWT Authentication',
        'description': 'Server không lưu session, mỗi request tự chứa JWT token',
        'constraints': ['Client-Server', 'Stateless'],
        'features': [
            'JWT (JSON Web Token) authentication',
            'Stateless - server không lưu session',
            'Self-contained tokens',
            'Token expiration và verification',
            'Bearer token authentication'
        ],
        'note': 'V3 only implements JWT Auth. Books/Users/Borrows use V1 API with JWT protection.',
        'endpoints': {
            'login': 'POST /api/v3/auth/login - Login và nhận JWT token',
            'verify': 'GET /api/v3/auth/verify - Verify JWT token',
            'decode': 'POST /api/v3/auth/decode - Decode JWT token',
            'protected': 'GET /api/v3/auth/protected - Test protected route'
        },
        '_links': {
            'self': '/api/v3',
            'login': '/api/v3/auth/login',
            'verify': '/api/v3/auth/verify',
            'documentation': '/api/docs'
        }
    }), 200

@auth_v3.route('/api/v3/auth/login', methods=['POST'])
def login():
    """
    Đăng nhập và nhận JWT token
    ---
    tags:
      - V3 - Authentication (Stateless JWT)
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
        description: Login thành công, trả về JWT token
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            token_type:
              type: string
              example: "Bearer"
            expires_in:
              type: integer
              example: 86400
            user:
              type: object
              properties:
                id:
                  type: string
                username:
                  type: string
                role:
                  type: string
      401:
        description: Sai thông tin đăng nhập
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
        
        # Authenticate user
        user = user_service.authenticate(username, password)
        
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Invalid username or password'
                }
            }), 401
        
        # Generate JWT token
        token = generate_jwt_token(user)
        
        # Remove password from response
        user_data = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'token_type': 'Bearer',
            'expires_in': JWT_EXPIRATION_HOURS * 3600,  # in seconds
            'user': user_data,
            '_metadata': {
                'authentication_type': 'JWT',
                'stateless': True,
                'token_algorithm': JWT_ALGORITHM,
                'expires_at': (datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)).isoformat() + 'Z'
            },
            '_instructions': {
                'usage': 'Include token in Authorization header as: Bearer <token>',
                'example': f'Authorization: Bearer {token[:20]}...'
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

@auth_v3.route('/api/v3/auth/verify', methods=['GET'])
@require_jwt_token
def verify_token():
    """
    Verify JWT token (Protected route example)
    ---
    tags:
      - V3 - Authentication (Stateless JWT)
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token
        example: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      200:
        description: Token hợp lệ
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Token is valid"
            user:
              type: object
      401:
        description: Token không hợp lệ hoặc hết hạn
    """
    return jsonify({
        'success': True,
        'message': 'Token is valid',
        'user': request.current_user,
        '_metadata': {
            'stateless': True,
            'note': 'Server không lưu session, chỉ verify token',
            'token_issued_at': datetime.fromtimestamp(request.current_user['iat']).isoformat(),
            'token_expires_at': datetime.fromtimestamp(request.current_user['exp']).isoformat()
        }
    }), 200

@auth_v3.route('/api/v3/auth/decode', methods=['POST'])
def decode_token():
    """
    Decode JWT token (không cần authentication)
    ---
    tags:
      - V3 - Authentication (Stateless JWT)
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - token
          properties:
            token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      200:
        description: Token decoded successfully
      400:
        description: Invalid token
    """
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Token is required'
                }
            }), 400
        
        # Decode token
        payload = decode_jwt_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Invalid or expired token'
                }
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Token decoded successfully',
            'payload': payload,
            '_metadata': {
                'stateless': True,
                'decoded_at': datetime.utcnow().isoformat() + 'Z',
                'token_algorithm': JWT_ALGORITHM
            },
            '_info': {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'role': payload.get('role'),
                'issued_at': datetime.fromtimestamp(payload['iat']).isoformat(),
                'expires_at': datetime.fromtimestamp(payload['exp']).isoformat(),
                'time_to_expire': str(datetime.fromtimestamp(payload['exp']) - datetime.utcnow())
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

@auth_v3.route('/api/v3/auth/protected', methods=['GET'])
@require_jwt_token
def protected_route():
    """
    Test protected route - Yêu cầu JWT token
    ---
    tags:
      - V3 - Authentication (Stateless JWT)
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token
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
            'stateless': True,
            'note': 'Server không cần lưu session, chỉ verify JWT token từ request'
        }
    }), 200

@auth_v3.route('/api/v3/auth/refresh', methods=['POST'])
@require_jwt_token
def refresh_token():
    """
    Refresh JWT token
    ---
    tags:
      - V3 - Authentication (Stateless JWT)
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token
    responses:
      200:
        description: New token issued
      401:
        description: Invalid token
    """
    try:
        # Get user from current token
        user_data = {
            'id': request.current_user['user_id'],
            'username': request.current_user['username'],
            'role': request.current_user['role']
        }
        
        # Generate new token
        new_token = generate_jwt_token(user_data)
        
        return jsonify({
            'success': True,
            'message': 'Token refreshed successfully',
            'token': new_token,
            'token_type': 'Bearer',
            'expires_in': JWT_EXPIRATION_HOURS * 3600,
            '_metadata': {
                'stateless': True,
                'old_token_expires_at': datetime.fromtimestamp(request.current_user['exp']).isoformat(),
                'new_token_expires_at': (datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)).isoformat() + 'Z'
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

