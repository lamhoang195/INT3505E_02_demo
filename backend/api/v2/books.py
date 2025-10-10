"""
V2 Books Controller - Uniform Interface with HATEOAS
Demonstrates REST constraint: Uniform Interface
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Self-descriptive messages with HATEOAS links
- Resource-based URIs
- Standard media types (application/json)
"""
from flask import Blueprint, request, jsonify, url_for
from flasgger import swag_from
from backend.services.book_service import BookService

# Create blueprint for V2 books
books_v2 = Blueprint('books_v2', __name__)
book_service = BookService()

def add_book_links(book, include_collection=True):
    """Add HATEOAS links to a book resource"""
    links = {
        'self': {
            'href': url_for('books_v2.get_book', book_id=book['id'], _external=True),
            'method': 'GET',
            'description': 'Get this book'
        },
        'update': {
            'href': url_for('books_v2.update_book', book_id=book['id'], _external=True),
            'method': 'PUT',
            'description': 'Update this book'
        },
        'delete': {
            'href': url_for('books_v2.delete_book', book_id=book['id'], _external=True),
            'method': 'DELETE',
            'description': 'Delete this book'
        }
    }
    
    if include_collection:
        links['collection'] = {
            'href': url_for('books_v2.get_books', _external=True),
            'method': 'GET',
            'description': 'Get all books'
        }
    
    # Add borrow link if book is available (using V1 borrow API)
    if book.get('available', 0) > 0:
        links['borrow'] = {
            'href': 'http://localhost:5000/api/v1/borrows',
            'method': 'POST',
            'description': 'Borrow this book',
            'requires': {'book_id': book['id'], 'user_id': '<user_id>'}
        }
    
    return links

@books_v2.route('/api/v2', methods=['GET'])
def v2_info():
    """API V2 Information with HATEOAS"""
    return jsonify({
        'version': 'v2',
        'name': 'Uniform Interface',
        'description': 'Standard HTTP methods, HATEOAS, self-descriptive messages',
        'constraints': ['Client-Server', 'Uniform Interface'],
        'features': [
            'HATEOAS (Hypermedia as the Engine of Application State)',
            'Self-descriptive messages',
            'Resource-based URIs',
            'Standard HTTP methods',
            'Standard media types (application/json)'
        ],
        'note': 'V2 only implements Books API with HATEOAS to demonstrate Uniform Interface. Other endpoints use V1.',
        '_links': {
            'self': {
                'href': url_for('books_v2.v2_info', _external=True),
                'method': 'GET'
            },
            'books-v2': {
                'href': url_for('books_v2.get_books', _external=True),
                'method': 'GET',
                'description': 'Get all books with HATEOAS (V2)'
            },
            'users-v1': {
                'href': 'http://localhost:5000/api/v1/users',
                'method': 'GET',
                'description': 'Get all users (uses V1)'
            },
            'borrows-v1': {
                'href': 'http://localhost:5000/api/v1/borrows',
                'method': 'GET',
                'description': 'Get all borrows (uses V1)'
            },
            'auth-v1': {
                'href': 'http://localhost:5000/api/v1/auth/login',
                'method': 'POST',
                'description': 'Login (uses V1)'
            },
            'documentation': {
                'href': '/api/docs',
                'method': 'GET'
            }
        }
    }), 200

@books_v2.route('/api/v2/books', methods=['GET'])
def get_books():
    """
    Lấy danh sách tất cả sách với HATEOAS links
    ---
    tags:
      - V2 - Books (Uniform Interface)
    responses:
      200:
        description: Danh sách sách với HATEOAS links
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
                  title:
                    type: string
                  author:
                    type: string
                  isbn:
                    type: string
                  quantity:
                    type: integer
                  available:
                    type: integer
                  _links:
                    type: object
                    description: HATEOAS links for this resource
            _links:
              type: object
              description: Links related to the collection
    """
    books = book_service.get_all_books()
    
    # Add HATEOAS links to each book
    books_with_links = []
    for book in books:
        book_data = book.copy()
        book_data['_links'] = add_book_links(book, include_collection=False)
        books_with_links.append(book_data)
    
    return jsonify({
        'success': True,
        'data': books_with_links,
        '_links': {
            'self': {
                'href': url_for('books_v2.get_books', _external=True),
                'method': 'GET'
            },
            'create': {
                'href': url_for('books_v2.create_book', _external=True),
                'method': 'POST',
                'description': 'Create a new book'
            }
        },
        '_metadata': {
            'total': len(books_with_links),
            'type': 'collection',
            'item_type': 'book'
        }
    }), 200

@books_v2.route('/api/v2/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """
    Lấy thông tin sách theo ID với HATEOAS links
    ---
    tags:
      - V2 - Books (Uniform Interface)
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
        description: ID của sách
    responses:
      200:
        description: Thông tin sách với HATEOAS links
      404:
        description: Không tìm thấy sách
    """
    book = book_service.get_book_by_id(book_id)
    if book:
        book_data = book.copy()
        book_data['_links'] = add_book_links(book)
        
        return jsonify({
            'success': True,
            'data': book_data,
            '_metadata': {
                'type': 'resource',
                'resource_type': 'book'
            }
        }), 200
    
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Book not found',
            'details': f'No book found with id: {book_id}'
        },
        '_links': {
            'collection': {
                'href': url_for('books_v2.get_books', _external=True),
                'method': 'GET'
            }
        }
    }), 404

@books_v2.route('/api/v2/books', methods=['POST'])
def create_book():
    """
    Tạo sách mới với HATEOAS response
    ---
    tags:
      - V2 - Books (Uniform Interface)
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
        description: Tạo sách thành công với HATEOAS links
      400:
        description: Dữ liệu không hợp lệ
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('author'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Title and author are required',
                    'fields': {
                        'title': 'required' if not data.get('title') else None,
                        'author': 'required' if not data.get('author') else None
                    }
                },
                '_links': {
                    'collection': {
                        'href': url_for('books_v2.get_books', _external=True),
                        'method': 'GET'
                    }
                }
            }), 400
        
        book = book_service.create_book(data)
        book_data = book.copy()
        book_data['_links'] = add_book_links(book)
        
        return jsonify({
            'success': True,
            'data': book_data,
            'message': 'Book created successfully',
            '_metadata': {
                'type': 'resource',
                'resource_type': 'book',
                'operation': 'create'
            }
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500

@books_v2.route('/api/v2/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Cập nhật thông tin sách với HATEOAS response
    ---
    tags:
      - V2 - Books (Uniform Interface)
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
      200:
        description: Cập nhật thành công
      404:
        description: Không tìm thấy sách
    """
    try:
        data = request.get_json()
        book = book_service.update_book(book_id, data)
        
        if book:
            book_data = book.copy()
            book_data['_links'] = add_book_links(book)
            
            return jsonify({
                'success': True,
                'data': book_data,
                'message': 'Book updated successfully',
                '_metadata': {
                    'type': 'resource',
                    'resource_type': 'book',
                    'operation': 'update'
                }
            }), 200
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Book not found',
                'details': f'No book found with id: {book_id}'
            },
            '_links': {
                'collection': {
                    'href': url_for('books_v2.get_books', _external=True),
                    'method': 'GET'
                }
            }
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500

@books_v2.route('/api/v2/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Xóa sách với HATEOAS response
    ---
    tags:
      - V2 - Books (Uniform Interface)
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
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Book deleted successfully',
                '_links': {
                    'collection': {
                        'href': url_for('books_v2.get_books', _external=True),
                        'method': 'GET',
                        'description': 'View all books'
                    }
                },
                '_metadata': {
                    'operation': 'delete',
                    'deleted_id': book_id
                }
            }), 200
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Book not found',
                'details': f'No book found with id: {book_id}'
            },
            '_links': {
                'collection': {
                    'href': url_for('books_v2.get_books', _external=True),
                    'method': 'GET'
                }
            }
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500

