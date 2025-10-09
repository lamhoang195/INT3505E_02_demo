"""
V1 Books Controller - Client-Server architecture
Simple CRUD operations for books
"""
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from backend.services.book_service import BookService

# Create blueprint for V1 books
books_v1 = Blueprint('books_v1', __name__)
book_service = BookService()

@books_v1.route('/api/v1', methods=['GET'])
def v1_info():
    """API V1 Information"""
    return jsonify({
        'version': 'v1',
        'name': 'Client-Server Architecture',
        'description': 'Tach biet Client va Server, giao tiep qua HTTP/JSON',
        'constraints': ['Client-Server'],
        'endpoints': {
            'books': {
                'list': 'GET /api/v1/books',
                'get': 'GET /api/v1/books/{id}',
                'create': 'POST /api/v1/books',
                'update': 'PUT /api/v1/books/{id}',
                'delete': 'DELETE /api/v1/books/{id}'
            },
            'users': {
                'list': 'GET /api/v1/users',
                'get': 'GET /api/v1/users/{id}',
                'create': 'POST /api/v1/users',
                'update': 'PUT /api/v1/users/{id}',
                'delete': 'DELETE /api/v1/users/{id}'
            },
            'auth': {
                'login': 'POST /api/v1/auth/login'
            },
            'borrows': {
                'list': 'GET /api/v1/borrows',
                'get': 'GET /api/v1/borrows/{id}',
                'create': 'POST /api/v1/borrows',
                'return': 'POST /api/v1/borrows/{id}/return',
                'history': 'GET /api/v1/borrows/history'
            }
        },
        '_links': {
            'self': '/api/v1',
            'documentation': '/api/docs',
            'all-versions': '/api'
        }
    }), 200

@books_v1.route('/api/v1/books', methods=['GET'])
def get_books():
    """
    Lấy danh sách tất cả sách
    ---
    tags:
      - V1 - Books
    responses:
      200:
        description: Danh sách sách
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
                  title:
                    type: string
                    example: "Clean Code"
                  author:
                    type: string
                    example: "Robert C. Martin"
                  isbn:
                    type: string
                    example: "978-0132350884"
                  quantity:
                    type: integer
                    example: 5
                  available:
                    type: integer
                    example: 3
    """
    books = book_service.get_all_books()
    return jsonify({
        'success': True,
        'data': books
    }), 200

@books_v1.route('/api/v1/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """
    Lấy thông tin sách theo ID
    ---
    tags:
      - V1 - Books
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
        description: ID của sách
        example: "1"
    responses:
      200:
        description: Thông tin sách
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
                title:
                  type: string
                  example: "Clean Code"
                author:
                  type: string
                  example: "Robert C. Martin"
                isbn:
                  type: string
                  example: "978-0132350884"
                quantity:
                  type: integer
                  example: 5
                available:
                  type: integer
                  example: 3
      404:
        description: Không tìm thấy sách
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Book not found"
    """
    book = book_service.get_book_by_id(book_id)
    if book:
        return jsonify({
            'success': True,
            'data': book
        }), 200
    return jsonify({
        'success': False,
        'message': 'Book not found'
    }), 404

@books_v1.route('/api/v1/books', methods=['POST'])
def create_book():
    """
    Tạo sách mới
    ---
    tags:
      - V1 - Books
    parameters:
      - name: body
        in: body
        required: true
        description: Thông tin sách cần tạo
        schema:
          type: object
          required:
            - title
            - author
          properties:
            title:
              type: string
              example: "Clean Code"
              description: Tên sách
            author:
              type: string
              example: "Robert C. Martin"
              description: Tác giả
            isbn:
              type: string
              example: "978-0132350884"
              description: Mã ISBN
            quantity:
              type: integer
              example: 5
              description: Số lượng sách
    responses:
      201:
        description: Tạo sách thành công
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
                title:
                  type: string
                  example: "Clean Code"
                author:
                  type: string
                  example: "Robert C. Martin"
                isbn:
                  type: string
                  example: "978-0132350884"
                quantity:
                  type: integer
                  example: 5
                available:
                  type: integer
                  example: 5
            message:
              type: string
              example: "Book created successfully"
      400:
        description: Thiếu thông tin bắt buộc
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Title and author are required"
      500:
        description: Lỗi server
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('author'):
            return jsonify({
                'success': False,
                'message': 'Title and author are required'
            }), 400
        
        book = book_service.create_book(data)
        return jsonify({
            'success': True,
            'data': book,
            'message': 'Book created successfully'
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@books_v1.route('/api/v1/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Cập nhật thông tin sách
    ---
    tags:
      - V1 - Books
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
        description: ID của sách cần cập nhật
        example: "1"
      - name: body
        in: body
        required: true
        description: Thông tin sách cần cập nhật
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Clean Code - 2nd Edition"
            author:
              type: string
              example: "Robert C. Martin"
            isbn:
              type: string
              example: "978-0132350884"
            quantity:
              type: integer
              example: 10
            available:
              type: integer
              example: 7
    responses:
      200:
        description: Cập nhật thành công
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
            message:
              type: string
              example: "Book updated successfully"
      404:
        description: Không tìm thấy sách
      500:
        description: Lỗi server
    """
    try:
        data = request.get_json()
        book = book_service.update_book(book_id, data)
        
        if book:
            return jsonify({
                'success': True,
                'data': book,
                'message': 'Book updated successfully'
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Book not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@books_v1.route('/api/v1/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Xóa sách
    ---
    tags:
      - V1 - Books
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
        description: ID của sách cần xóa
        example: "1"
    responses:
      200:
        description: Xóa thành công
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Book deleted successfully"
      404:
        description: Không tìm thấy sách
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Book not found"
      500:
        description: Lỗi server
    """
    try:
        success = book_service.delete_book(book_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Book deleted successfully'
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Book not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

