"""
V4 Books Controller - ETag
Demonstrates REST constraint: Cacheable with ETag headers
- ETag for resource versioning
- If-None-Match for conditional GET
- If-Match for conditional PUT/DELETE
- Weak vs Strong ETags
"""
from flask import Blueprint, request, jsonify, make_response
from backend.services.book_service import BookService
import hashlib
import json

# Create blueprint for V4 ETag books
books_v4_etag = Blueprint('books_v4_etag', __name__)
book_service = BookService()

def generate_etag(data):
    """Generate ETag from data"""
    # Convert data to JSON string and hash it
    data_string = json.dumps(data, sort_keys=True, ensure_ascii=False)
    etag = hashlib.md5(data_string.encode('utf-8')).hexdigest()
    return f'"{etag}"'  # Strong ETag

def generate_weak_etag(data):
    """Generate weak ETag (for collections or less strict matching)"""
    data_string = json.dumps(data, sort_keys=True, ensure_ascii=False)
    etag = hashlib.md5(data_string.encode('utf-8')).hexdigest()
    return f'W/"{etag}"'  # Weak ETag

def parse_etag(etag_header):
    """Parse ETag header and remove quotes"""
    if not etag_header:
        return None
    # Remove W/ prefix for weak ETags and quotes
    return etag_header.replace('W/', '').strip('"')

@books_v4_etag.route('/api/v4/etag', methods=['GET'])
def v4_etag_info():
    """API V4 ETag Information"""
    response_data = {
        'version': 'v4-etag',
        'name': 'Cacheable with ETag',
        'description': 'HTTP caching với ETag headers',
        'constraints': ['Client-Server', 'Cacheable'],
        'features': [
            'ETag headers (Strong và Weak)',
            'Conditional GET với If-None-Match',
            'Conditional PUT/DELETE với If-Match',
            'Content-based versioning',
            'Automatic cache validation'
        ],
        'endpoints': {
            'list': 'GET /api/v4/etag/books - Danh sách sách với ETag',
            'get': 'GET /api/v4/etag/books/{id} - Chi tiết sách với ETag',
            'create': 'POST /api/v4/etag/books - Tạo sách',
            'update': 'PUT /api/v4/etag/books/{id} - Cập nhật với If-Match',
            'delete': 'DELETE /api/v4/etag/books/{id} - Xóa với If-Match'
        },
        'etag_strategy': {
            'GET /books': 'Weak ETag W/"..." (collection)',
            'GET /books/{id}': 'Strong ETag "..." (individual resource)',
            'Conditional GET': 'If-None-Match header returns 304 if match',
            'Conditional PUT/DELETE': 'If-Match header prevents lost updates'
        },
        '_links': {
            'self': '/api/v4/etag',
            'books': '/api/v4/etag/books',
            'documentation': '/api/docs'
        }
    }
    
    response = make_response(jsonify(response_data), 200)
    etag = generate_etag(response_data)
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response

@books_v4_etag.route('/api/v4/etag/books', methods=['GET'])
def get_books():
    """
    Lấy danh sách sách với ETag
    ---
    tags:
      - V4 - Books (ETag)
    parameters:
      - name: If-None-Match
        in: header
        type: string
        required: false
        description: ETag từ lần request trước
    responses:
      200:
        description: Danh sách sách với ETag header
        headers:
          ETag:
            type: string
            description: Weak ETag cho collection
          Cache-Control:
            type: string
      304:
        description: Not Modified - ETag matches, use cached version
    """
    # Get books
    books = book_service.get_all_books()
    
    # Generate weak ETag for collection (because order might change, items might be added/removed)
    etag = generate_weak_etag(books)
    
    # Check If-None-Match header
    if_none_match = request.headers.get('If-None-Match')
    if if_none_match:
        # Compare ETags (strip W/ and quotes for comparison)
        request_etag = parse_etag(if_none_match)
        current_etag = parse_etag(etag)
        
        if request_etag == current_etag:
            # ETags match, return 304 Not Modified
            response = make_response('', 304)
            response.headers['ETag'] = etag
            response.headers['Cache-Control'] = 'public, max-age=60'
            return response
    
    response_data = {
        'success': True,
        'data': books,
        '_metadata': {
            'total': len(books),
            'cached': True,
            'cache_strategy': 'ETag-based validation'
        },
        '_cache_info': {
            'cacheable': True,
            'etag_type': 'weak',
            'etag': etag,
            'directive': 'public, max-age=60',
            'explanation': 'Weak ETag because collection may have minor differences that are acceptable'
        }
    }
    
    response = make_response(jsonify(response_data), 200)
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=60'
    
    return response

@books_v4_etag.route('/api/v4/etag/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """
    Lấy thông tin sách với ETag
    ---
    tags:
      - V4 - Books (ETag)
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
        description: ID của sách
      - name: If-None-Match
        in: header
        type: string
        required: false
        description: ETag từ lần request trước
    responses:
      200:
        description: Thông tin sách với ETag header
        headers:
          ETag:
            type: string
            description: Strong ETag cho resource
      304:
        description: Not Modified - ETag matches
      404:
        description: Không tìm thấy sách
    """
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
        response.headers['Cache-Control'] = 'no-cache'
        return response
    
    # Generate strong ETag for individual resource
    etag = generate_etag(book)
    
    # Check If-None-Match header
    if_none_match = request.headers.get('If-None-Match')
    if if_none_match:
        request_etag = parse_etag(if_none_match)
        current_etag = parse_etag(etag)
        
        if request_etag == current_etag:
            # ETags match, return 304 Not Modified
            response = make_response('', 304)
            response.headers['ETag'] = etag
            response.headers['Cache-Control'] = 'public, max-age=120'
            return response
    
    response_data = {
        'success': True,
        'data': book,
        '_metadata': {
            'cached': True,
            'cache_strategy': 'ETag-based validation'
        },
        '_cache_info': {
            'cacheable': True,
            'etag_type': 'strong',
            'etag': etag,
            'directive': 'public, max-age=120',
            'explanation': 'Strong ETag for exact byte-for-byte comparison of individual resource'
        }
    }
    
    response = make_response(jsonify(response_data), 200)
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=120'
    
    return response

@books_v4_etag.route('/api/v4/etag/books', methods=['POST'])
def create_book():
    """
    Tạo sách mới
    ---
    tags:
      - V4 - Books (ETag)
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
        headers:
          ETag:
            type: string
            description: ETag của resource mới
          Location:
            type: string
            description: URL của resource mới
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
        etag = generate_etag(book)
        
        response_data = {
            'success': True,
            'data': book,
            'message': 'Book created successfully',
            '_cache_info': {
                'etag': etag,
                'etag_type': 'strong',
                'explanation': 'New resource has fresh ETag'
            }
        }
        
        response = make_response(jsonify(response_data), 201)
        response.headers['ETag'] = etag
        response.headers['Location'] = f'/api/v4/etag/books/{book["id"]}'
        response.headers['Cache-Control'] = 'no-cache'
        
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

@books_v4_etag.route('/api/v4/etag/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Cập nhật sách với conditional request (If-Match)
    ---
    tags:
      - V4 - Books (ETag)
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
      - name: If-Match
        in: header
        type: string
        required: false
        description: ETag để đảm bảo không bị ghi đè (optimistic locking)
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Cập nhật thành công
        headers:
          ETag:
            type: string
            description: ETag mới sau khi update
      404:
        description: Không tìm thấy sách
      412:
        description: Precondition Failed - ETag không khớp (conflict)
    """
    try:
        # Get current book first
        current_book = book_service.get_book_by_id(book_id)
        
        if not current_book:
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
        
        # Check If-Match header for conditional update (prevent lost updates)
        if_match = request.headers.get('If-Match')
        if if_match:
            current_etag = parse_etag(generate_etag(current_book))
            request_etag = parse_etag(if_match)
            
            if request_etag != current_etag:
                # ETags don't match - resource was modified by someone else
                response_data = {
                    'success': False,
                    'error': {
                        'code': 'PRECONDITION_FAILED',
                        'message': 'Resource was modified by another request',
                        'current_etag': generate_etag(current_book),
                        'explanation': 'The ETag you provided does not match the current resource version'
                    },
                    'current_data': current_book
                }
                response = make_response(jsonify(response_data), 412)
                response.headers['ETag'] = generate_etag(current_book)
                return response
        
        # Perform update
        data = request.get_json()
        updated_book = book_service.update_book(book_id, data)
        
        if not updated_book:
            response_data = {
                'success': False,
                'error': {
                    'code': 'UPDATE_FAILED',
                    'message': 'Failed to update book'
                }
            }
            response = make_response(jsonify(response_data), 500)
            return response
        
        # Generate new ETag
        new_etag = generate_etag(updated_book)
        
        response_data = {
            'success': True,
            'data': updated_book,
            'message': 'Book updated successfully',
            '_cache_info': {
                'old_etag': generate_etag(current_book) if if_match else None,
                'new_etag': new_etag,
                'conditional_update': bool(if_match),
                'explanation': 'ETag changed after update, caches are invalidated'
            }
        }
        
        response = make_response(jsonify(response_data), 200)
        response.headers['ETag'] = new_etag
        response.headers['Cache-Control'] = 'no-cache'
        
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

@books_v4_etag.route('/api/v4/etag/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Xóa sách với conditional request (If-Match)
    ---
    tags:
      - V4 - Books (ETag)
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
      - name: If-Match
        in: header
        type: string
        required: false
        description: ETag để đảm bảo xóa đúng version
    responses:
      200:
        description: Xóa thành công
      404:
        description: Không tìm thấy sách
      412:
        description: Precondition Failed - ETag không khớp
    """
    try:
        # Get current book first
        current_book = book_service.get_book_by_id(book_id)
        
        if not current_book:
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
        
        # Check If-Match header for conditional delete
        if_match = request.headers.get('If-Match')
        if if_match:
            current_etag = parse_etag(generate_etag(current_book))
            request_etag = parse_etag(if_match)
            
            if request_etag != current_etag:
                response_data = {
                    'success': False,
                    'error': {
                        'code': 'PRECONDITION_FAILED',
                        'message': 'Resource was modified, cannot delete',
                        'current_etag': generate_etag(current_book),
                        'explanation': 'The ETag you provided does not match. Resource may have been modified.'
                    },
                    'current_data': current_book
                }
                response = make_response(jsonify(response_data), 412)
                response.headers['ETag'] = generate_etag(current_book)
                return response
        
        # Perform delete
        success = book_service.delete_book(book_id)
        
        if not success:
            response_data = {
                'success': False,
                'error': {
                    'code': 'DELETE_FAILED',
                    'message': 'Failed to delete book'
                }
            }
            response = make_response(jsonify(response_data), 500)
            return response
        
        response_data = {
            'success': True,
            'message': 'Book deleted successfully',
            '_cache_info': {
                'deleted_etag': generate_etag(current_book),
                'conditional_delete': bool(if_match),
                'explanation': 'Resource deleted, all caches invalidated'
            }
        }
        
        response = make_response(jsonify(response_data), 200)
        response.headers['Cache-Control'] = 'no-cache'
        
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

