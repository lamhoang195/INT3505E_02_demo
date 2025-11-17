"""
V1 Users Controller - Client-Server architecture
Simple user management operations
"""
import logging

from flask import Blueprint, request, jsonify

from backend.services.user_service import UserService

# Create blueprint for V1 users
users_v1 = Blueprint('users_v1', __name__)
user_service = UserService()
logger = logging.getLogger(__name__)

@users_v1.route('/api/v1/users', methods=['GET'])
def get_users():
    """
    Lấy danh sách tất cả người dùng
    ---
    tags:
      - V1 - Users
    responses:
      200:
        description: Danh sách người dùng (không bao gồm mật khẩu)
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: "1"
                  username:
                    type: string
                    example: "admin"
                  full_name:
                    type: string
                    example: "Administrator"
                  role:
                    type: string
                    example: "admin"
    """
    users = user_service.get_all_users()
    logger.info("Fetched %d users", len(users))
    return jsonify({
        'success': True,
        'data': users
    }), 200

@users_v1.route('/api/v1/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    logger.info("Fetching user id=%s", user_id)
    user = user_service.get_user_by_id(user_id)
    if user:
        return jsonify({
            'success': True,
            'data': user
        }), 200
    logger.warning("User id=%s not found", user_id)
    return jsonify({
        'success': False,
        'message': 'User not found'
    }), 404

@users_v1.route('/api/v1/users', methods=['POST'])
def create_user():
    """
    Đăng ký người dùng mới
    ---
    tags:
      - V1 - Users
    parameters:
      - name: body
        in: body
        required: true
        description: Thông tin người dùng cần đăng ký
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "john_doe"
              description: Tên đăng nhập (duy nhất)
            password:
              type: string
              example: "password123"
              description: Mật khẩu
            full_name:
              type: string
              example: "John Doe"
              description: Họ tên đầy đủ
            role:
              type: string
              example: "user"
              enum: ["user", "admin"]
              description: Vai trò (mặc định là user)
    responses:
      201:
        description: Đăng ký thành công
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: string
                  example: "2"
                username:
                  type: string
                  example: "john_doe"
                full_name:
                  type: string
                  example: "John Doe"
                role:
                  type: string
                  example: "user"
            message:
              type: string
              example: "User registered successfully"
      400:
        description: Thông tin không hợp lệ hoặc username đã tồn tại
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Username already exists"
      500:
        description: Lỗi server
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            logger.warning("User registration missing credentials: %s", data)
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        user = user_service.create_user(data)
        logger.info("Created user id=%s username=%s", user['id'], user['username'])
        return jsonify({
            'success': True,
            'data': user,
            'message': 'User registered successfully'
        }), 201
    
    except ValueError as e:
        logger.warning("User registration failed validation: %s", e)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.exception("Failed to create user")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@users_v1.route('/api/v1/auth/login', methods=['POST'])
def login():
    """
    Đăng nhập
    ---
    tags:
      - V1 - Authentication
    parameters:
      - name: body
        in: body
        required: true
        description: Thông tin đăng nhập
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "admin"
              description: Tên đăng nhập
            password:
              type: string
              example: "admin123"
              description: Mật khẩu
    responses:
      200:
        description: Đăng nhập thành công
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: string
                  example: "1"
                username:
                  type: string
                  example: "admin"
                full_name:
                  type: string
                  example: "Administrator"
                role:
                  type: string
                  example: "admin"
            message:
              type: string
              example: "Login successful"
      400:
        description: Thiếu thông tin đăng nhập
      401:
        description: Thông tin đăng nhập không chính xác
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Invalid credentials"
      500:
        description: Lỗi server
    """
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            logger.warning("Login request missing credentials")
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        user = user_service.authenticate(username, password)
        
        if user:
            logger.info("User %s logged in successfully", username)
            return jsonify({
                'success': True,
                'data': user,
                'message': 'Login successful'
            }), 200
        
        logger.warning("Invalid credentials for username=%s", username)
        return jsonify({
            'success': False,
            'message': 'Invalid credentials'
        }), 401
    
    except Exception as e:
        logger.exception("Login failed for username=%s", data.get('username') if 'data' in locals() and isinstance(data, dict) else 'unknown')
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@users_v1.route('/api/v1/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    try:
        data = request.get_json()
        user = user_service.update_user(user_id, data)
        
        if user:
            logger.info("Updated user id=%s", user_id)
            return jsonify({
                'success': True,
                'data': user,
                'message': 'User updated successfully'
            }), 200
        
        logger.warning("Attempted to update missing user id=%s", user_id)
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404
    
    except Exception as e:
        logger.exception("Failed to update user id=%s", user_id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@users_v1.route('/api/v1/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        success = user_service.delete_user(user_id)
        
        if success:
            logger.info("Deleted user id=%s", user_id)
            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            }), 200
        
        logger.warning("Attempted to delete missing user id=%s", user_id)
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404
    
    except Exception as e:
        logger.exception("Failed to delete user id=%s", user_id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

