"""
Webhook Service - Quản lý webhook registrations và gửi notifications
"""
import json
import os
import logging
import threading
from typing import List, Optional, Dict
from datetime import datetime
from urllib.parse import urlparse
import requests

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self, data_file='backend/data/webhooks.json'):
        self.data_file = data_file
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure data directory and file exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _read_webhooks(self) -> List[Dict]:
        """Read all webhook registrations from storage"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_webhooks(self, webhooks: List[Dict]):
        """Write webhook registrations to storage"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(webhooks, f, ensure_ascii=False, indent=2)
    
    def register_webhook(self, webhook_data: Dict) -> Dict:
        """Register a new webhook"""
        webhooks = self._read_webhooks()
        
        # Validate URL
        url = webhook_data.get('url')
        if not url:
            raise ValueError("Webhook URL is required")
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid webhook URL format")
        except Exception as e:
            raise ValueError(f"Invalid webhook URL: {str(e)}")
        
        # Check if webhook already exists
        for webhook in webhooks:
            if webhook['url'] == url and webhook.get('event_type') == webhook_data.get('event_type'):
                raise ValueError("Webhook already registered for this URL and event type")
        
        # Generate new ID
        if webhooks:
            max_id = max(int(w['id']) for w in webhooks)
            new_id = str(max_id + 1)
        else:
            new_id = "1"
        
        new_webhook = {
            'id': new_id,
            'url': url,
            'event_type': webhook_data.get('event_type', 'all'),
            'secret': webhook_data.get('secret', ''),
            'active': webhook_data.get('active', True),
            'created_at': datetime.now().isoformat(),
            'description': webhook_data.get('description', '')
        }
        
        webhooks.append(new_webhook)
        self._write_webhooks(webhooks)
        
        logger.info("Registered webhook id=%s url=%s event_type=%s", 
                   new_id, url, new_webhook['event_type'])
        
        return new_webhook
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """Unregister a webhook"""
        webhooks = self._read_webhooks()
        original_count = len(webhooks)
        
        webhooks = [w for w in webhooks if w['id'] != webhook_id]
        
        if len(webhooks) < original_count:
            self._write_webhooks(webhooks)
            logger.info("Unregistered webhook id=%s", webhook_id)
            return True
        
        return False
    
    def get_webhooks(self, event_type: Optional[str] = None) -> List[Dict]:
        """Get all webhooks, optionally filtered by event type"""
        webhooks = self._read_webhooks()
        
        if event_type:
            webhooks = [w for w in webhooks if w['event_type'] == event_type or w['event_type'] == 'all']
        
        # Only return active webhooks
        return [w for w in webhooks if w.get('active', True)]
    
    def get_webhook_by_id(self, webhook_id: str) -> Optional[Dict]:
        """Get a webhook by ID"""
        webhooks = self._read_webhooks()
        for webhook in webhooks:
            if webhook['id'] == webhook_id:
                return webhook
        return None
    
    def _send_webhook(self, webhook: Dict, payload: Dict) -> bool:
        """Send webhook notification to a single webhook URL"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Library-Management-System/1.0'
            }
            
            # Add webhook signature if secret is provided
            if webhook.get('secret'):
                # Simple signature (in production, use HMAC)
                import hashlib
                payload_str = json.dumps(payload, sort_keys=True)
                signature = hashlib.sha256(
                    f"{payload_str}{webhook['secret']}".encode()
                ).hexdigest()
                headers['X-Webhook-Signature'] = signature
            
            response = requests.post(
                webhook['url'],
                json=payload,
                headers=headers,
                timeout=5  # 5 second timeout
            )
            
            response.raise_for_status()
            logger.info("Webhook sent successfully id=%s url=%s status=%d", 
                       webhook['id'], webhook['url'], response.status_code)
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send webhook id=%s url=%s error=%s", 
                        webhook['id'], webhook['url'], str(e))
            return False
        except Exception as e:
            logger.exception("Unexpected error sending webhook id=%s", webhook['id'])
            return False
    
    def notify(self, event_type: str, event_data: Dict):
        """Notify all registered webhooks for a specific event type"""
        webhooks = self.get_webhooks(event_type)
        
        if not webhooks:
            logger.debug("No webhooks registered for event_type=%s", event_type)
            return
        
        # Prepare payload
        payload = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': event_data
        }
        
        # Send webhooks asynchronously to avoid blocking
        def send_async():
            for webhook in webhooks:
                self._send_webhook(webhook, payload)
        
        thread = threading.Thread(target=send_async)
        thread.daemon = True
        thread.start()
        
        logger.info("Triggered webhook notifications event_type=%s webhooks=%d", 
                   event_type, len(webhooks))

