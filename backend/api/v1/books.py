"""
V1 Books Controller - Client-Server architecture
Simple CRUD operations for books
"""
import logging
import os

from flask import Blueprint, request, jsonify

from backend.extensions import limiter
from backend.services.book_service import BookService

# Create blueprint for V1 books
books_v1 = Blueprint('books_v1', __name__)
book_service = BookService()
logger = logging.getLogger(__name__)
V1_RATE_LIMIT = os.getenv('V1_RATE_LIMIT', '60/minute')

@books_v1.route('/api/v1', methods=['GET'])
@limiter.limit(V1_RATE_LIMIT)
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
@limiter.limit(V1_RATE_LIMIT)
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
    logger.info("Fetched %d books", len(books))
    return jsonify({
        'success': True,
        'data': books
    }), 200

@books_v1.route('/api/v1/books/search', methods=['GET'])
@limiter.limit(V1_RATE_LIMIT)
def search_books():
    """
    Tìm kiếm và phân trang sách
    ---
    tags:
      - V1 - Books
    parameters:
      - name: search
        in: query
        type: string
        required: false
        description: Từ khóa tìm kiếm (tìm trong tiêu đề và tác giả)
        example: "Clean"
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Số trang (bắt đầu từ 1)
        example: 1
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
        description: Số lượng sách trên mỗi trang
        example: 10
    responses:
      200:
        description: Kết quả tìm kiếm và phân trang
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                items:
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
                pagination:
                  type: object
                  properties:
                    page:
                      type: integer
                      example: 1
                    per_page:
                      type: integer
                      example: 10
                    total:
                      type: integer
                      example: 25
                    total_pages:
                      type: integer
                      example: 3
                    has_prev:
                      type: boolean
                      example: false
                    has_next:
                      type: boolean
                      example: true
      400:
        description: Tham số không hợp lệ
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Invalid parameters"
    """
    try:
        # Get query parameters
        search = request.args.get('search', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        logger.info(
            "Searching books with params search=%s page=%s per_page=%s",
            search, page, per_page
        )

        # Validate parameters
        if page < 1:
            logger.warning("Invalid page parameter: %s", page)
            return jsonify({
                'success': False,
                'error': 'Page must be greater than 0'
            }), 400
        
        if per_page < 1 or per_page > 100:
            logger.warning("Invalid per_page parameter: %s", per_page)
            return jsonify({
                'success': False,
                'error': 'Per_page must be between 1 and 100'
            }), 400
        
        # Get paginated results
        result = book_service.search_and_paginate_books(search, page, per_page)
        
        logger.info(
            "Search returned %d items (page %s)",
            len(result.get('items', [])), result.get('pagination', {}).get('page')
        )

        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except ValueError:
        logger.exception("Invalid pagination parameters")
        return jsonify({
            'success': False,
            'error': 'Invalid parameters: page and per_page must be integers'
        }), 400

@books_v1.route('/api/v1/books/<book_id>', methods=['GET'])
@limiter.limit(V1_RATE_LIMIT)
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
    logger.info("Fetching book detail for id=%s", book_id)
    book = book_service.get_book_by_id(book_id)
    if book:
        return jsonify({
            'success': True,
            'data': book
        }), 200
    logger.warning("Book id=%s not found", book_id)
    return jsonify({
        'success': False,
        'message': 'Book not found'
    }), 404

@books_v1.route('/api/v1/books', methods=['POST'])
@limiter.limit(V1_RATE_LIMIT)
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
            logger.warning("Book creation missing required fields: %s", data)
            return jsonify({
                'success': False,
                'message': 'Title and author are required'
            }), 400
        
        book = book_service.create_book(data)
        logger.info("Created book id=%s title=%s", book['id'], book['title'])
        return jsonify({
            'success': True,
            'data': book,
            'message': 'Book created successfully'
        }), 201
    
    except Exception as e:
        logger.exception("Failed to create book")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@books_v1.route('/api/v1/books/<book_id>', methods=['PUT'])
@limiter.limit(V1_RATE_LIMIT)
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
            logger.info("Updated book id=%s", book_id)
            return jsonify({
                'success': True,
                'data': book,
                'message': 'Book updated successfully'
            }), 200
        
        logger.warning("Attempted to update missing book id=%s", book_id)
        return jsonify({
            'success': False,
            'message': 'Book not found'
        }), 404
    
    except Exception as e:
        logger.exception("Failed to update book id=%s", book_id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@books_v1.route('/api/v1/books/<book_id>', methods=['DELETE'])
@limiter.limit(V1_RATE_LIMIT)
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
            logger.info("Deleted book id=%s", book_id)
            return jsonify({
                'success': True,
                'message': 'Book deleted successfully'
            }), 200
        
        logger.warning("Attempted to delete missing book id=%s", book_id)
        return jsonify({
            'success': False,
            'message': 'Book not found'
        }), 404
    
    except Exception as e:
        logger.exception("Failed to delete book id=%s", book_id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

