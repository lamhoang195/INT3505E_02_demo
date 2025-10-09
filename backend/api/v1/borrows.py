"""
V1 Borrows Controller - Client-Server architecture
Simple borrow/return operations
"""
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from backend.services.borrow_service import BorrowService
from backend.services.book_service import BookService

# Create blueprint for V1 borrows
borrows_v1 = Blueprint('borrows_v1', __name__)
borrow_service = BorrowService()
book_service = BookService()

@borrows_v1.route('/api/v1/borrows', methods=['GET'])
def get_borrows():
    """
    Lấy danh sách phiếu mượn sách
    ---
    tags:
      - V1 - Borrows
    parameters:
      - name: user_id
        in: query
        type: string
        required: false
        description: Lọc theo ID người dùng
        example: "1"
      - name: status
        in: query
        type: string
        required: false
        description: Lọc theo trạng thái (active = đang mượn)
        enum: ["active"]
        example: "active"
    responses:
      200:
        description: Danh sách phiếu mượn sách
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
                  user_id:
                    type: string
                    example: "1"
                  book_id:
                    type: string
                    example: "1"
                  borrow_date:
                    type: string
                    format: date-time
                  due_date:
                    type: string
                    format: date-time
                  return_date:
                    type: string
                    nullable: true
                  status:
                    type: string
                    enum: ["borrowed", "returned"]
                    example: "borrowed"
    """
    user_id = request.args.get('user_id')
    status = request.args.get('status')
    
    if status == 'active':
        borrows = borrow_service.get_active_borrows(user_id)
    elif user_id:
        borrows = borrow_service.get_borrows_by_user(user_id)
    else:
        borrows = borrow_service.get_all_borrows()
    
    return jsonify({
        'success': True,
        'data': borrows
    }), 200

@borrows_v1.route('/api/v1/borrows/<borrow_id>', methods=['GET'])
def get_borrow(borrow_id):
    """Get a specific borrow record"""
    borrow = borrow_service.get_borrow_by_id(borrow_id)
    if borrow:
        return jsonify({
            'success': True,
            'data': borrow
        }), 200
    return jsonify({
        'success': False,
        'message': 'Borrow record not found'
    }), 404

@borrows_v1.route('/api/v1/borrows', methods=['POST'])
def create_borrow():
    """
    Mượn sách
    ---
    tags:
      - V1 - Borrows
    parameters:
      - name: body
        in: body
        required: true
        description: Thông tin mượn sách
        schema:
          type: object
          required:
            - user_id
            - book_id
          properties:
            user_id:
              type: string
              example: "1"
              description: ID người dùng
            book_id:
              type: string
              example: "1"
              description: ID sách cần mượn
    responses:
      201:
        description: Mượn sách thành công
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
                user_id:
                  type: string
                  example: "1"
                book_id:
                  type: string
                  example: "1"
                borrow_date:
                  type: string
                  format: date-time
                  example: "2024-01-01T10:00:00"
                due_date:
                  type: string
                  format: date-time
                  example: "2024-01-15T10:00:00"
                return_date:
                  type: string
                  nullable: true
                  example: null
                status:
                  type: string
                  example: "borrowed"
            message:
              type: string
              example: "Book borrowed successfully"
      400:
        description: Thiếu thông tin hoặc sách không có sẵn
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Book not available"
      404:
        description: Không tìm thấy sách
      500:
        description: Lỗi server
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('user_id') or not data.get('book_id'):
            return jsonify({
                'success': False,
                'message': 'User ID and Book ID are required'
            }), 400
        
        # Check if book is available
        book = book_service.get_book_by_id(data['book_id'])
        if not book:
            return jsonify({
                'success': False,
                'message': 'Book not found'
            }), 404
        
        if book.get('available', 0) <= 0:
            return jsonify({
                'success': False,
                'message': 'Book not available'
            }), 400
        
        # Create borrow record
        borrow = borrow_service.create_borrow(data)
        
        # Update book availability
        book_service.update_availability(data['book_id'], -1)
        
        return jsonify({
            'success': True,
            'data': borrow,
            'message': 'Book borrowed successfully'
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@borrows_v1.route('/api/v1/borrows/<borrow_id>/return', methods=['POST'])
def return_book(borrow_id):
    """
    Trả sách
    ---
    tags:
      - V1 - Borrows
    parameters:
      - name: borrow_id
        in: path
        type: string
        required: true
        description: ID của phiếu mượn sách
        example: "1"
    responses:
      200:
        description: Trả sách thành công
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
                user_id:
                  type: string
                  example: "1"
                book_id:
                  type: string
                  example: "1"
                borrow_date:
                  type: string
                  format: date-time
                  example: "2024-01-01T10:00:00"
                due_date:
                  type: string
                  format: date-time
                  example: "2024-01-15T10:00:00"
                return_date:
                  type: string
                  format: date-time
                  example: "2024-01-10T14:30:00"
                status:
                  type: string
                  example: "returned"
            message:
              type: string
              example: "Book returned successfully"
      400:
        description: Sách đã được trả trước đó
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Book already returned"
      404:
        description: Không tìm thấy phiếu mượn
      500:
        description: Lỗi server
    """
    try:
        borrow = borrow_service.get_borrow_by_id(borrow_id)
        
        if not borrow:
            return jsonify({
                'success': False,
                'message': 'Borrow record not found'
            }), 404
        
        if borrow['status'] != 'borrowed':
            return jsonify({
                'success': False,
                'message': 'Book already returned'
            }), 400
        
        # Update borrow record
        updated_borrow = borrow_service.return_book(borrow_id)
        
        # Update book availability
        book_service.update_availability(borrow['book_id'], 1)
        
        return jsonify({
            'success': True,
            'data': updated_borrow,
            'message': 'Book returned successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@borrows_v1.route('/api/v1/borrows/history', methods=['GET'])
def get_history():
    """Get borrow history"""
    user_id = request.args.get('user_id')
    book_id = request.args.get('book_id')
    
    history = borrow_service.get_borrow_history(user_id, book_id)
    
    return jsonify({
        'success': True,
        'data': history
    }), 200

