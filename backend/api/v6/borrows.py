"""
V6 Borrows Controller - Borrow with Donation Feature
Khi mượn sách, người dùng có thể donate tiền cho thư viện
"""
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from backend.services.borrow_service import BorrowService
from backend.services.book_service import BookService
from backend.services.donation_service import DonationService

# Create blueprint for V6 borrows
borrows_v6 = Blueprint('borrows_v6', __name__)
borrow_service = BorrowService()
book_service = BookService()
donation_service = DonationService()

@borrows_v6.route('/api/v6', methods=['GET'])
def v6_info():
    """API V6 Information"""
    return jsonify({
        'version': 'v6',
        'name': 'Borrow with Donation',
        'description': 'Mượn sách với chức năng donate tiền cho thư viện',
        'features': ['Borrow books', 'Optional donation when borrowing'],
        'endpoints': {
            'borrows': {
                'create': 'POST /api/v6/borrows',
                'description': 'Mượn sách với tùy chọn donate'
            }
        }
    }), 200

@borrows_v6.route('/api/v6/borrows', methods=['POST'])
def create_borrow_with_donation():
    """
    Mượn sách với chức năng donate tiền cho thư viện
    ---
    tags:
      - V6 - Borrows with Donation
    parameters:
      - name: body
        in: body
        required: true
        description: Thông tin mượn sách và donate (nếu có)
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
            donation_amount:
              type: number
              example: 50000
              description: Số tiền donate (tùy chọn, mặc định 0)
            donation_message:
              type: string
              example: "Cảm ơn thư viện!"
              description: Lời nhắn khi donate (tùy chọn)
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
                borrow:
                  type: object
                  description: Thông tin phiếu mượn
                donation:
                  type: object
                  description: Thông tin donation (nếu có)
                  nullable: true
            message:
              type: string
              example: "Book borrowed successfully"
      400:
        description: Thiếu thông tin hoặc sách không có sẵn
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
        borrow = borrow_service.create_borrow({
            'user_id': data['user_id'],
            'book_id': data['book_id']
        })
        
        # Update book availability
        book_service.update_availability(data['book_id'], -1)
        
        # Handle donation if provided
        donation = None
        donation_amount = data.get('donation_amount', 0)
        
        if donation_amount and donation_amount > 0:
            donation = donation_service.create_donation({
                'user_id': data['user_id'],
                'borrow_id': borrow['id'],
                'amount': donation_amount,
                'message': data.get('donation_message', '')
            })
        
        response_data = {
            'borrow': borrow
        }
        
        if donation:
            response_data['donation'] = donation
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'Book borrowed successfully' + (' with donation' if donation else '')
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@borrows_v6.route('/api/v6/donations', methods=['GET'])
def get_donations():
    """
    Lấy danh sách donations
    ---
    tags:
      - V6 - Borrows with Donation
    parameters:
      - name: user_id
        in: query
        type: string
        required: false
        description: Lọc theo ID người dùng
    responses:
      200:
        description: Danh sách donations
    """
    user_id = request.args.get('user_id')
    
    if user_id:
        donations = donation_service.get_donations_by_user(user_id)
    else:
        donations = donation_service.get_all_donations()
    
    return jsonify({
        'success': True,
        'data': donations,
        'total_amount': donation_service.get_total_donations()
    }), 200

