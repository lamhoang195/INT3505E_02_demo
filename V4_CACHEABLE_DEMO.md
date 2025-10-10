# API V4 - Cacheable Demo

## So sánh các phiên bản API

### V1 - Client-Server
- **Constraint**: Client-Server
- **Đặc điểm**: Tách biệt client và server, giao tiếp qua HTTP/JSON
- **Response**: Dữ liệu thuần túy, không có cache headers

### V2 - Uniform Interface (HATEOAS)
- **Constraint**: Client-Server + Uniform Interface
- **Đặc điểm**: Thêm HATEOAS links, self-descriptive messages
- **Response**: Dữ liệu + _links để điều hướng

### V3 - Stateless (JWT)
- **Constraint**: Client-Server + Stateless
- **Đặc điểm**: Không lưu session, mỗi request chứa JWT token
- **Response**: Stateless authentication, token-based

### V4 - Cacheable ⭐ NEW
- **Constraint**: Client-Server + Cacheable
- **Đặc điểm**: HTTP caching với Cache-Control và ETag
- **Response**: Dữ liệu + cache headers, hỗ trợ conditional requests
- **2 Implementations**:
  - **Cache-Control**: Time-based caching (max-age, Last-Modified)
  - **ETag**: Content-based caching (Strong/Weak ETags, If-None-Match/If-Match)

---

## V4 Cache-Control Implementation

### Endpoint: `/api/v4/cache-control/books`

### 1. GET All Books - First Request

**Request:**
```http
GET /api/v4/cache-control/books HTTP/1.1
Host: localhost:5000
```

**Response:**
```http
HTTP/1.1 200 OK
Cache-Control: public, max-age=60
Last-Modified: Fri, 10 Oct 2025 10:30:00 GMT
Content-Type: application/json

{
  "success": true,
  "data": [
    {
      "id": "1",
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "isbn": "978-0132350884",
      "quantity": 5,
      "available": 3
    }
  ],
  "_cache_info": {
    "cacheable": true,
    "max_age": 60,
    "directive": "public, max-age=60",
    "last_modified": "2025-10-10T10:30:00"
  }
}
```

**📌 Giải thích:**
- `Cache-Control: public, max-age=60` → Client cache 60 giây
- `Last-Modified` → Thời điểm resource được sửa đổi lần cuối

### 2. GET All Books - Second Request (Within 60s)

**Request:**
```http
GET /api/v4/cache-control/books HTTP/1.1
Host: localhost:5000
If-Modified-Since: Fri, 10 Oct 2025 10:30:00 GMT
```

**Response:**
```http
HTTP/1.1 304 Not Modified
Cache-Control: public, max-age=60
Last-Modified: Fri, 10 Oct 2025 10:30:00 GMT
```

**📌 Giải thích:**
- Client gửi `If-Modified-Since` header
- Server kiểm tra: resource không thay đổi
- Trả về `304 Not Modified` → Không transfer data
- **Lợi ích**: Tiết kiệm bandwidth, response nhanh hơn

### 3. GET Single Book

**Request:**
```http
GET /api/v4/cache-control/books/1 HTTP/1.1
Host: localhost:5000
```

**Response:**
```http
HTTP/1.1 200 OK
Cache-Control: public, max-age=120, must-revalidate
Last-Modified: Fri, 10 Oct 2025 10:30:00 GMT
Content-Type: application/json

{
  "success": true,
  "data": {
    "id": "1",
    "title": "Clean Code",
    "author": "Robert C. Martin"
  },
  "_cache_info": {
    "cacheable": true,
    "max_age": 120,
    "directive": "public, max-age=120, must-revalidate",
    "explanation": "must-revalidate: cache must check with server when stale"
  }
}
```

**📌 Giải thích:**
- `max-age=120` → Cache 120 giây (lâu hơn collection)
- `must-revalidate` → Khi hết hạn, PHẢI check với server

### 4. POST Create Book (Invalidates Cache)

**Request:**
```http
POST /api/v4/cache-control/books HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "title": "Design Patterns",
  "author": "Gang of Four"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Cache-Control: no-cache, no-store, must-revalidate
Location: /api/v4/cache-control/books/2
Content-Type: application/json

{
  "success": true,
  "data": {
    "id": "2",
    "title": "Design Patterns",
    "author": "Gang of Four"
  },
  "_cache_info": {
    "cacheable": false,
    "directive": "no-cache, no-store, must-revalidate",
    "explanation": "POST requests should not be cached",
    "invalidated": ["collection cache", "book 2 cache"]
  }
}
```

**📌 Giải thích:**
- `Cache-Control: no-cache, no-store` → Không cache POST
- Server update `Last-Modified` time → Invalidate old caches

---

## V4 ETag Implementation

### Endpoint: `/api/v4/etag/books`

### 1. GET All Books - First Request

**Request:**
```http
GET /api/v4/etag/books HTTP/1.1
Host: localhost:5000
```

**Response:**
```http
HTTP/1.1 200 OK
ETag: W/"a1b2c3d4e5f6"
Cache-Control: public, max-age=60
Content-Type: application/json

{
  "success": true,
  "data": [
    {
      "id": "1",
      "title": "Clean Code",
      "author": "Robert C. Martin"
    }
  ],
  "_cache_info": {
    "cacheable": true,
    "etag_type": "weak",
    "etag": "W/\"a1b2c3d4e5f6\"",
    "explanation": "Weak ETag because collection may have minor differences"
  }
}
```

**📌 Giải thích:**
- `ETag: W/"..."` → Weak ETag cho collection
- ETag = hash của data → Content-based validation

### 2. GET All Books - With If-None-Match

**Request:**
```http
GET /api/v4/etag/books HTTP/1.1
Host: localhost:5000
If-None-Match: W/"a1b2c3d4e5f6"
```

**Response:**
```http
HTTP/1.1 304 Not Modified
ETag: W/"a1b2c3d4e5f6"
Cache-Control: public, max-age=60
```

**📌 Giải thích:**
- Client gửi `If-None-Match` với ETag đã có
- Server so sánh ETags → Giống nhau
- Trả về `304` → Không transfer data

### 3. GET Single Book

**Request:**
```http
GET /api/v4/etag/books/1 HTTP/1.1
Host: localhost:5000
```

**Response:**
```http
HTTP/1.1 200 OK
ETag: "7g8h9i0j1k2l"
Cache-Control: public, max-age=120
Content-Type: application/json

{
  "success": true,
  "data": {
    "id": "1",
    "title": "Clean Code",
    "author": "Robert C. Martin"
  },
  "_cache_info": {
    "cacheable": true,
    "etag_type": "strong",
    "etag": "\"7g8h9i0j1k2l\"",
    "explanation": "Strong ETag for exact byte-for-byte comparison"
  }
}
```

**📌 Giải thích:**
- `ETag: "..."` → Strong ETag (không có W/)
- Strong ETag: Byte-for-byte identical

### 4. PUT Update Book - With If-Match (Optimistic Locking)

**Request:**
```http
PUT /api/v4/etag/books/1 HTTP/1.1
Host: localhost:5000
If-Match: "7g8h9i0j1k2l"
Content-Type: application/json

{
  "title": "Clean Code - 2nd Edition"
}
```

**Response (Success):**
```http
HTTP/1.1 200 OK
ETag: "m3n4o5p6q7r8"
Cache-Control: no-cache
Content-Type: application/json

{
  "success": true,
  "data": {
    "id": "1",
    "title": "Clean Code - 2nd Edition",
    "author": "Robert C. Martin"
  },
  "_cache_info": {
    "old_etag": "\"7g8h9i0j1k2l\"",
    "new_etag": "\"m3n4o5p6q7r8\"",
    "conditional_update": true,
    "explanation": "ETag changed after update, caches are invalidated"
  }
}
```

**📌 Giải thích:**
- `If-Match` → Chỉ update nếu ETag khớp
- **Optimistic Locking**: Ngăn chặn lost updates
- ETag mới được generate → Old caches invalidated

### 5. PUT Update Book - ETag Conflict

**Request:**
```http
PUT /api/v4/etag/books/1 HTTP/1.1
Host: localhost:5000
If-Match: "OLD_ETAG_123"
Content-Type: application/json

{
  "title": "Clean Code - 3rd Edition"
}
```

**Response (Conflict):**
```http
HTTP/1.1 412 Precondition Failed
ETag: "m3n4o5p6q7r8"
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "PRECONDITION_FAILED",
    "message": "Resource was modified by another request",
    "current_etag": "\"m3n4o5p6q7r8\"",
    "explanation": "The ETag you provided does not match the current resource version"
  },
  "current_data": {
    "id": "1",
    "title": "Clean Code - 2nd Edition",
    "author": "Robert C. Martin"
  }
}
```

**📌 Giải thích:**
- ETag không khớp → Resource đã được người khác sửa
- Trả về `412 Precondition Failed`
- Client nhận current data + current ETag → Có thể retry

---

## So sánh Cache-Control vs ETag

| Feature | Cache-Control | ETag |
|---------|--------------|------|
| **Cơ chế** | Time-based | Content-based |
| **Validation** | Last-Modified time | Content hash |
| **Header (GET)** | `If-Modified-Since` | `If-None-Match` |
| **Header (PUT)** | - | `If-Match` (optimistic lock) |
| **Strong point** | Đơn giản, dễ implement | Chính xác, ngăn lost updates |
| **Weak point** | Phụ thuộc thời gian | Phức tạp hơn |
| **Use case** | Data ít thay đổi | Data hay thay đổi, cần chính xác |

---

## Demo Script - Test V4 APIs

### Test Cache-Control

```bash
# 1. GET books - First request (200 OK)
curl -i http://localhost:5000/api/v4/cache-control/books

# 2. GET books - With If-Modified-Since (304 Not Modified)
curl -i -H "If-Modified-Since: Fri, 10 Oct 2025 10:30:00 GMT" \
  http://localhost:5000/api/v4/cache-control/books

# 3. Create a book (invalidates cache)
curl -i -X POST http://localhost:5000/api/v4/cache-control/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Design Patterns","author":"Gang of Four"}'

# 4. GET books again - Should get fresh data
curl -i http://localhost:5000/api/v4/cache-control/books
```

### Test ETag

```bash
# 1. GET books - First request, save ETag
curl -i http://localhost:5000/api/v4/etag/books

# Output: ETag: W/"abc123..."

# 2. GET books - With If-None-Match (304 Not Modified)
curl -i -H 'If-None-Match: W/"abc123..."' \
  http://localhost:5000/api/v4/etag/books

# 3. GET single book - Get ETag
curl -i http://localhost:5000/api/v4/etag/books/1

# Output: ETag: "xyz789..."

# 4. Update with If-Match - Success
curl -i -X PUT http://localhost:5000/api/v4/etag/books/1 \
  -H "Content-Type: application/json" \
  -H 'If-Match: "xyz789..."' \
  -d '{"title":"Clean Code - Updated"}'

# 5. Update with wrong If-Match - Conflict (412)
curl -i -X PUT http://localhost:5000/api/v4/etag/books/1 \
  -H "Content-Type: application/json" \
  -H 'If-Match: "WRONG_ETAG"' \
  -d '{"title":"Clean Code - Another Update"}'
```

---

## Lợi ích của V4 Cacheable

### 1. **Tiết kiệm Bandwidth**
- 304 responses không chứa body
- Chỉ transfer data khi thực sự cần

### 2. **Tăng Performance**
- Client dùng cached data → Không cần wait server
- Giảm load cho server

### 3. **Ngăn chặn Conflicts** (ETag)
- If-Match header → Optimistic locking
- Phát hiện và prevent lost updates

### 4. **Flexible Caching Strategy**
- `public` vs `private`
- `max-age` custom per endpoint
- `no-cache`, `no-store` cho sensitive data

### 5. **Standard HTTP Caching**
- Browsers tự động support
- CDN/Proxy có thể cache
- Infrastructure-level optimization

---

## Kết luận

**V4 Cacheable** là constraint quan trọng của REST:
- ✅ Giảm latency
- ✅ Tiết kiệm bandwidth
- ✅ Tăng scalability
- ✅ Better user experience

**2 Implementations**:
- **Cache-Control**: Đơn giản, time-based, phù hợp cho data ổn định
- **ETag**: Chính xác, content-based, phù hợp cho data thay đổi thường xuyên

Cả 2 đều follow REST principles và HTTP standards! 🚀

