"""
V1 Webhooks Controller - Quản lý webhook registrations
"""
import logging
import os

from flask import Blueprint, request, jsonify

from backend.extensions import limiter
from backend.services.webhook_service import WebhookService

# Create blueprint for V1 webhooks
webhooks_v1 = Blueprint('webhooks_v1', __name__)
webhook_service = WebhookService()
logger = logging.getLogger(__name__)
V1_RATE_LIMIT = os.getenv('V1_RATE_LIMIT', '60/minute')


@webhooks_v1.route('/api/v1/webhooks', methods=['GET'])
@limiter.limit(V1_RATE_LIMIT)
def get_webhooks():
    """
    Lấy danh sách webhooks đã đăng ký
    ---
    tags:
      - V1 - Webhooks
    parameters:
      - name: event_type
        in: query
        type: string
        required: false
        description: Lọc theo loại sự kiện
        enum: ["book.borrowed", "book.returned", "all"]
        example: "book.borrowed"
    responses:
      200:
        description: Danh sách webhooks
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
                  url:
                    type: string
                    example: "https://example.com/webhook"
                  event_type:
                    type: string
                    example: "book.borrowed"
                  active:
                    type: boolean
                    example: true
                  created_at:
                    type: string
                    format: date-time
                  description:
                    type: string
                    example: "Notification khi mượn sách"
    """
    try:
        event_type = request.args.get('event_type')
        webhooks = webhook_service.get_webhooks(event_type)
        
        # Remove secret from response for security
        safe_webhooks = []
        for webhook in webhooks:
            safe_webhook = {k: v for k, v in webhook.items() if k != 'secret'}
            safe_webhooks.append(safe_webhook)
        
        logger.info("Fetched %d webhooks event_type=%s", len(safe_webhooks), event_type)
        
        return jsonify({
            'success': True,
            'data': safe_webhooks
        }), 200
    
    except Exception as e:
        logger.exception("Failed to get webhooks")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@webhooks_v1.route('/api/v1/webhooks', methods=['POST'])
@limiter.limit(V1_RATE_LIMIT)
def register_webhook():
    """
    Đăng ký webhook mới
    ---
    tags:
      - V1 - Webhooks
    parameters:
      - name: body
        in: body
        required: true
        description: Thông tin webhook
        schema:
          type: object
          required:
            - url
          properties:
            url:
              type: string
              example: "https://example.com/webhook"
              description: URL nhận webhook notifications
            event_type:
              type: string
              enum: ["book.borrowed", "book.returned", "all"]
              example: "book.borrowed"
              description: "Loại sự kiện muốn nhận (mặc định: all)"
            secret:
              type: string
              example: "my-secret-key"
              description: "Secret key để verify webhook (tùy chọn)"
            description:
              type: string
              example: "Notification khi mượn sách"
              description: "Mô tả webhook (tùy chọn)"
    responses:
      201:
        description: Đăng ký webhook thành công
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
                url:
                  type: string
                  example: "https://example.com/webhook"
                event_type:
                  type: string
                  example: "book.borrowed"
                active:
                  type: boolean
                  example: true
                created_at:
                  type: string
                  format: date-time
            message:
              type: string
              example: "Webhook registered successfully"
      400:
        description: Dữ liệu không hợp lệ
      500:
        description: Lỗi server
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        webhook = webhook_service.register_webhook(data)
        
        # Remove secret from response
        safe_webhook = {k: v for k, v in webhook.items() if k != 'secret'}
        
        logger.info("Registered webhook id=%s url=%s", webhook['id'], webhook['url'])
        
        return jsonify({
            'success': True,
            'data': safe_webhook,
            'message': 'Webhook registered successfully'
        }), 201
    
    except ValueError as e:
        logger.warning("Webhook registration failed: %s", str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.exception("Failed to register webhook")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@webhooks_v1.route('/api/v1/webhooks/<webhook_id>', methods=['DELETE'])
@limiter.limit(V1_RATE_LIMIT)
def unregister_webhook(webhook_id):
    """
    Hủy đăng ký webhook
    ---
    tags:
      - V1 - Webhooks
    parameters:
      - name: webhook_id
        in: path
        type: string
        required: true
        description: ID của webhook cần hủy
        example: "1"
    responses:
      200:
        description: Hủy đăng ký thành công
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Webhook unregistered successfully"
      404:
        description: Không tìm thấy webhook
      500:
        description: Lỗi server
    """
    try:
        success = webhook_service.unregister_webhook(webhook_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Webhook not found'
            }), 404
        
        logger.info("Unregistered webhook id=%s", webhook_id)
        
        return jsonify({
            'success': True,
            'message': 'Webhook unregistered successfully'
        }), 200
    
    except Exception as e:
        logger.exception("Failed to unregister webhook id=%s", webhook_id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@webhooks_v1.route('/api/v1/webhooks/<webhook_id>', methods=['GET'])
@limiter.limit(V1_RATE_LIMIT)
def get_webhook(webhook_id):
    """
    Lấy thông tin webhook theo ID
    ---
    tags:
      - V1 - Webhooks
    parameters:
      - name: webhook_id
        in: path
        type: string
        required: true
        description: ID của webhook
        example: "1"
    responses:
      200:
        description: Thông tin webhook
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
                url:
                  type: string
                  example: "https://example.com/webhook"
                event_type:
                  type: string
                  example: "book.borrowed"
                active:
                  type: boolean
                  example: true
                created_at:
                  type: string
                  format: date-time
                description:
                  type: string
                  example: "Notification khi mượn sách"
      404:
        description: Không tìm thấy webhook
      500:
        description: Lỗi server
    """
    try:
        webhook = webhook_service.get_webhook_by_id(webhook_id)
        
        if not webhook:
            return jsonify({
                'success': False,
                'message': 'Webhook not found'
            }), 404
        
        # Remove secret from response
        safe_webhook = {k: v for k, v in webhook.items() if k != 'secret'}
        
        return jsonify({
            'success': True,
            'data': safe_webhook
        }), 200
    
    except Exception as e:
        logger.exception("Failed to get webhook id=%s", webhook_id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

