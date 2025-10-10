"""
V4 Books Controller - Cache-Control
Demonstrates REST constraint: Cacheable with Cache-Control headers
- max-age for cache duration
- no-cache for validation required
- must-revalidate for strict validation
- Last-Modified header
"""
from flask import Blueprint, request, jsonify, make_response
from datetime import datetime, timedelta
from backend.services.book_service import BookService
import hashlib
import json

# Create blueprint for V4 cache-control books
books_v4_cache = Blueprint('books_v4_cache', __name__)
book_service = BookService()

# Store last modified times for resources
last_modified_store = {}

def get_resource_last_modified(resource_id=None):
    """Get last modified time for a resource"""
    key = f"book_{resource_id}" if resource_id else "books_collection"
    if key not in last_modified_store:
        last_modified_store[key] = datetime.utcnow()
    return last_modified_store[key]

def update_resource_last_modified(resource_id=None):
    """Update last modified time for a resource"""
    key = f"book_{resource_id}" if resource_id else "books_collection"
    last_modified_store[key] = datetime.utcnow()

@books_v4_cache.route('/api/v4/cache-control', methods=['GET'])
def v4_cache_control_info():
    """API V4 Cache-Control Information"""
    response_data = {
        'version': 'v4-cache-control',
        'name': 'Cacheable with Cache-Control',
        'description': 'HTTP caching với Cache-Control headers',
        'constraints': ['Client-Server', 'Cacheable'],
        'features': [
            'Cache-Control headers (max-age, no-cache, must-revalidate)',
            'Last-Modified header',
            'Conditional requests với If-Modified-Since',
            'Public/Private cache directives',
            'Cache expiration'
        ],
        'endpoints': {
            'list': 'GET /api/v4/cache-control/books - Danh sách sách với cache',
            'get': 'GET /api/v4/cache-control/books/{id} - Chi tiết sách với cache',
            'create': 'POST /api/v4/cache-control/books - Tạo sách (invalidate cache)',
            'update': 'PUT /api/v4/cache-control/books/{id} - Cập nhật (invalidate cache)',
            'delete': 'DELETE /api/v4/cache-control/books/{id} - Xóa (invalidate cache)'
        },
        'cache_strategy': {
            'GET /books': 'max-age=60 (cache 60 seconds)',
            'GET /books/{id}': 'max-age=120, must-revalidate',
            'POST/PUT/DELETE': 'no-cache (always revalidate)'
        },
        '_links': {
            'self': '/api/v4/cache-control',
            'books': '/api/v4/cache-control/books',
            'documentation': '/api/docs'
        }
    }
    
    response = make_response(jsonify(response_data), 200)
    # Cache info endpoint for 5 minutes
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response

@books_v4_cache.route('/api/v4/cache-control/books', methods=['GET'])
def get_books():
    """
    Lấy danh sách sách với Cache-Control
    ---
    tags:
      - V4 - Books (Cache-Control)
    responses:
      200:
        description: Danh sách sách với cache headers
        headers:
          Cache-Control:
            type: string
            description: Cache control directives
          Last-Modified:
            type: string
            description: Last modification time
      304:
        description: Not Modified - use cached version
    """
    # Check If-Modified-Since header
    if_modified_since = request.headers.get('If-Modified-Since')
    last_modified = get_resource_last_modified()
    
    if if_modified_since:
        try:
            # Parse If-Modified-Since header
            if_modified_dt = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT')
            # Compare with last modified (ignore microseconds)
            if last_modified.replace(microsecond=0) <= if_modified_dt.replace(microsecond=0):
                # Resource hasn't been modified
                response = make_response('', 304)
                response.headers['Cache-Control'] = 'public, max-age=60'
                response.headers['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
                return response
        except ValueError:
            pass  # Invalid date format, proceed with normal response
    
    # Get books
    books = book_service.get_all_books()
    
    response_data = {
        'success': True,
        'data': books,
        '_metadata': {
            'total': len(books),
            'cached': True,
            'cache_strategy': 'Cache-Control with max-age'
        },
        '_cache_info': {
            'cacheable': True,
            'max_age': 60,
            'directive': 'public, max-age=60',
            'last_modified': last_modified.isoformat()
        }
    }
    
    response = make_response(jsonify(response_data), 200)
    # Cache for 60 seconds, public (can be cached by proxies)
    response.headers['Cache-Control'] = 'public, max-age=60'
    response.headers['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    return response

@books_v4_cache.route('/api/v4/cache-control/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """
    Lấy thông tin sách với Cache-Control
    ---
    tags:
      - V4 - Books (Cache-Control)
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
        description: ID của sách
    responses:
      200:
        description: Thông tin sách với cache headers
      304:
        description: Not Modified - use cached version
      404:
        description: Không tìm thấy sách
    """
    # Check If-Modified-Since header
    if_modified_since = request.headers.get('If-Modified-Since')
    last_modified = get_resource_last_modified(book_id)
    
    if if_modified_since:
        try:
            if_modified_dt = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT')
            if last_modified.replace(microsecond=0) <= if_modified_dt.replace(microsecond=0):
                response = make_response('', 304)
                response.headers['Cache-Control'] = 'public, max-age=120, must-revalidate'
                response.headers['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
                return response
        except ValueError:
            pass
    
    # Get book
    book = book_service.get_book_by_id(book_id)
    
    if not book:
        response_data = {
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Book not found'
            }
        }
        response = make_response(jsonify(response_data), 404)
        # Don't cache 404 responses
        response.headers['Cache-Control'] = 'no-cache'
        return response
    
    response_data = {
        'success': True,
        'data': book,
        '_metadata': {
            'cached': True,
            'cache_strategy': 'Cache-Control with max-age and must-revalidate'
        },
        '_cache_info': {
            'cacheable': True,
            'max_age': 120,
            'directive': 'public, max-age=120, must-revalidate',
            'last_modified': last_modified.isoformat(),
            'explanation': 'must-revalidate: cache must check with server when stale'
        }
    }
    
    response = make_response(jsonify(response_data), 200)
    # Cache for 120 seconds, must revalidate when stale
    response.headers['Cache-Control'] = 'public, max-age=120, must-revalidate'
    response.headers['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    return response

@books_v4_cache.route('/api/v4/cache-control/books', methods=['POST'])
def create_book():
    """
    Tạo sách mới (invalidates cache)
    ---
    tags:
      - V4 - Books (Cache-Control)
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - author
          properties:
            title:
              type: string
            author:
              type: string
            isbn:
              type: string
            quantity:
              type: integer
    responses:
      201:
        description: Tạo sách thành công
      400:
        description: Dữ liệu không hợp lệ
    """
    try:
        data = request.get_json()
        
        if not data.get('title') or not data.get('author'):
            response_data = {
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Title and author are required'
                }
            }
            response = make_response(jsonify(response_data), 400)
            response.headers['Cache-Control'] = 'no-cache'
            return response
        
        book = book_service.create_book(data)
        
        # Invalidate collection cache
        update_resource_last_modified()
        update_resource_last_modified(book['id'])
        
        response_data = {
            'success': True,
            'data': book,
            'message': 'Book created successfully',
            '_cache_info': {
                'cacheable': False,
                'directive': 'no-cache, no-store, must-revalidate',
                'explanation': 'POST requests should not be cached',
                'invalidated': ['collection cache', f'book {book["id"]} cache']
            }
        }
        
        response = make_response(jsonify(response_data), 201)
        # Don't cache POST responses
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Location'] = f'/api/v4/cache-control/books/{book["id"]}'
        
        return response
    
    except Exception as e:
        response_data = {
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }
        response = make_response(jsonify(response_data), 500)
        response.headers['Cache-Control'] = 'no-cache'
        return response

@books_v4_cache.route('/api/v4/cache-control/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Cập nhật sách (invalidates cache)
    ---
    tags:
      - V4 - Books (Cache-Control)
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Cập nhật thành công
      404:
        description: Không tìm thấy sách
    """
    try:
        data = request.get_json()
        book = book_service.update_book(book_id, data)
        
        if not book:
            response_data = {
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Book not found'
                }
            }
            response = make_response(jsonify(response_data), 404)
            response.headers['Cache-Control'] = 'no-cache'
            return response
        
        # Invalidate caches
        update_resource_last_modified()
        update_resource_last_modified(book_id)
        
        response_data = {
            'success': True,
            'data': book,
            'message': 'Book updated successfully',
            '_cache_info': {
                'cacheable': False,
                'directive': 'no-cache, no-store, must-revalidate',
                'explanation': 'PUT requests should not be cached',
                'invalidated': ['collection cache', f'book {book_id} cache']
            }
        }
        
        response = make_response(jsonify(response_data), 200)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        return response
    
    except Exception as e:
        response_data = {
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }
        response = make_response(jsonify(response_data), 500)
        response.headers['Cache-Control'] = 'no-cache'
        return response

@books_v4_cache.route('/api/v4/cache-control/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Xóa sách (invalidates cache)
    ---
    tags:
      - V4 - Books (Cache-Control)
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Xóa thành công
      404:
        description: Không tìm thấy sách
    """
    try:
        success = book_service.delete_book(book_id)
        
        if not success:
            response_data = {
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Book not found'
                }
            }
            response = make_response(jsonify(response_data), 404)
            response.headers['Cache-Control'] = 'no-cache'
            return response
        
        # Invalidate caches
        update_resource_last_modified()
        if f"book_{book_id}" in last_modified_store:
            del last_modified_store[f"book_{book_id}"]
        
        response_data = {
            'success': True,
            'message': 'Book deleted successfully',
            '_cache_info': {
                'cacheable': False,
                'directive': 'no-cache, no-store, must-revalidate',
                'explanation': 'DELETE requests should not be cached',
                'invalidated': ['collection cache', f'book {book_id} cache removed']
            }
        }
        
        response = make_response(jsonify(response_data), 200)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        return response
    
    except Exception as e:
        response_data = {
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }
        response = make_response(jsonify(response_data), 500)
        response.headers['Cache-Control'] = 'no-cache'
        return response

