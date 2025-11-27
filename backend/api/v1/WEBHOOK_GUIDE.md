# Hướng dẫn sử dụng Webhook Notifications

## Tổng quan

Hệ thống webhook cho phép bạn đăng ký URL để nhận thông báo tự động khi có các sự kiện xảy ra trong hệ thống quản lý sách.

## Các sự kiện được hỗ trợ

- `book.borrowed`: Khi có người mượn sách
- `book.returned`: Khi có người trả sách
- `all`: Nhận tất cả các sự kiện

## API Endpoints

### 1. Đăng ký Webhook

**POST** `/api/v1/webhooks`

**Request Body:**
```json
{
  "url": "https://example.com/webhook",
  "event_type": "book.borrowed",
  "secret": "my-secret-key",
  "description": "Notification khi mượn sách"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "1",
    "url": "https://example.com/webhook",
    "event_type": "book.borrowed",
    "active": true,
    "created_at": "2024-01-01T10:00:00",
    "description": "Notification khi mượn sách"
  },
  "message": "Webhook registered successfully"
}
```

### 2. Lấy danh sách Webhooks

**GET** `/api/v1/webhooks`

**Query Parameters:**
- `event_type` (optional): Lọc theo loại sự kiện

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "1",
      "url": "https://example.com/webhook",
      "event_type": "book.borrowed",
      "active": true,
      "created_at": "2024-01-01T10:00:00",
      "description": "Notification khi mượn sách"
    }
  ]
}
```

### 3. Lấy thông tin Webhook

**GET** `/api/v1/webhooks/<webhook_id>`

### 4. Hủy đăng ký Webhook

**DELETE** `/api/v1/webhooks/<webhook_id>`

## Format của Webhook Payload

Khi có sự kiện xảy ra, hệ thống sẽ gửi POST request đến URL đã đăng ký với payload:

### Event: `book.borrowed`

```json
{
  "event_type": "book.borrowed",
  "timestamp": "2024-01-01T10:00:00",
  "data": {
    "borrow_id": "1",
    "user_id": "1",
    "book_id": "1",
    "book_title": "Tên sách",
    "borrow_date": "2024-01-01T10:00:00",
    "due_date": "2024-01-15T10:00:00"
  }
}
```

### Event: `book.returned`

```json
{
  "event_type": "book.returned",
  "timestamp": "2024-01-01T10:00:00",
  "data": {
    "borrow_id": "1",
    "user_id": "1",
    "book_id": "1",
    "book_title": "Tên sách",
    "borrow_date": "2024-01-01T10:00:00",
    "return_date": "2024-01-10T14:30:00"
  }
}
```

## Webhook Headers

Mỗi webhook request sẽ có các headers sau:

- `Content-Type: application/json`
- `User-Agent: Library-Management-System/1.0`
- `X-Webhook-Signature`: (nếu có secret) - SHA256 hash của payload + secret

## Xác thực Webhook

Nếu bạn cung cấp `secret` khi đăng ký, hệ thống sẽ gửi kèm header `X-Webhook-Signature` để bạn có thể verify tính xác thực của webhook.

**Ví dụ verify signature (Python):**
```python
import hashlib
import json

def verify_webhook(payload, signature, secret):
    payload_str = json.dumps(payload, sort_keys=True)
    expected_signature = hashlib.sha256(
        f"{payload_str}{secret}".encode()
    ).hexdigest()
    return signature == expected_signature
```

## Ví dụ sử dụng

### 1. Đăng ký webhook để nhận thông báo khi mượn sách

```bash
curl -X POST http://localhost:5000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "event_type": "book.borrowed",
    "description": "Notification khi mượn sách"
  }'
```

### 2. Đăng ký webhook để nhận tất cả sự kiện

```bash
curl -X POST http://localhost:5000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "event_type": "all",
    "secret": "my-secret-key",
    "description": "Nhận tất cả notifications"
  }'
```

### 3. Lấy danh sách webhooks

```bash
curl http://localhost:5000/api/v1/webhooks
```

### 4. Hủy đăng ký webhook

```bash
curl -X DELETE http://localhost:5000/api/v1/webhooks/1
```

## Lưu ý

1. Webhook được gửi **bất đồng bộ** (asynchronous), không block request chính
2. Timeout cho mỗi webhook request là **5 giây**
3. Nếu webhook URL không phản hồi hoặc lỗi, hệ thống sẽ log lỗi nhưng không ảnh hưởng đến request chính
4. Webhook chỉ được gửi đến các webhook **active**
5. Secret không được trả về trong API response để bảo mật

## Testing với ngrok (Local Development)

Nếu bạn muốn test webhook trên localhost, có thể sử dụng ngrok:

1. Cài đặt ngrok: https://ngrok.com/
2. Tạo tunnel: `ngrok http 3000` (port của webhook receiver)
3. Sử dụng URL ngrok để đăng ký webhook: `https://xxxx.ngrok.io/webhook`

