"""
Flask Application cho V2 Payment API
Đơn giản nhất có thể
"""
import sys
import os

# Thêm parent directory vào path để import week9 module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Flask, jsonify
from flask_cors import CORS
from week9.api.v2.payment import payment_v2

def create_app():
    """Tạo và cấu hình Flask application"""
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Configure app
    app.config['JSON_AS_ASCII'] = False
    app.config['SECRET_KEY'] = 'payment-secret-key'
    
    # Register V2 Payment API blueprint
    app.register_blueprint(payment_v2)
    
    # API info endpoint
    @app.route('/api/v2')
    def v2_info():
        """V2 Payment API Information"""
        return jsonify({
            'version': 'v2',
            'name': 'Payment API',
            'description': 'API thanh toán mượn sách - đơn giản nhất',
            'endpoints': {
                'create_payment': 'POST /api/v2/payment',
                'get_payment': 'GET /api/v2/payment/<id>',
                'get_payments': 'GET /api/v2/payment',
                'pay_and_borrow': 'POST /api/v2/payment/borrow'
            }
        }), 200
    
    @app.route('/')
    def index():
        """Home page"""
        return jsonify({
            'message': 'V2 Payment API for Book Borrowing',
            'version': 'v2',
            'endpoints': {
                'info': '/api/v2',
                'create_payment': 'POST /api/v2/payment',
                'get_payment': 'GET /api/v2/payment/<id>',
                'get_payments': 'GET /api/v2/payment',
                'pay_and_borrow': 'POST /api/v2/payment/borrow'
            }
        }), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)

