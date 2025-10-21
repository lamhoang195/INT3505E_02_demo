# Hệ thống Quản lý Sách - RESTful API Demo

Hệ thống quản lý thư viện với kiến trúc RESTful API, được phát triển để minh họa **từng nguyên tắc REST (REST Constraints)** qua các phiên bản API khác nhau.

## ⚠️ Security Notice

**IMPORTANT:** This is a demo/educational project. Before using in production:

- 🔐 Change all default passwords (`admin/admin123`)
- 🔑 Rotate JWT secret keys (use strong random values)
- 🚫 Never commit `.env` files or real tokens to Git
- ✅ Review `SECURITY_AUDIT_REPORT.md` for security guidelines
- 🔒 Use HTTPS in production
- 📝 Follow the `.env.example` for proper configuration

## 📋 Tổng quan

Dự án này demo các nguyên tắc REST API theo cách tiếp cận từng bước:

| Version | REST Constraint | Tính năng chính |
|---------|----------------|-----------------|
| **V1** | Client-Server | Tách biệt Client/Server, giao tiếp qua HTTP/JSON |
| **V2** | Uniform Interface | HATEOAS, Self-descriptive messages |
| **V3** | Stateless | JWT Authentication, không lưu session |
| **V4** | Cacheable | Cache-Control headers, ETag, Conditional requests |

## 🏗️ Kiến trúc

### Cấu trúc thư mục
```
demo-book/
├── backend/
│   ├── api/                    # API Controllers (theo version)
│   │   ├── v1/                 # V1 - Client-Server
│   │   │   ├── books.py
│   │   │   ├── users.py
│   │   │   └── borrows.py
│   │   ├── v2/                 # V2 - Uniform Interface (HATEOAS)
│   │   │   └── books.py
│   │   ├── v3/                 # V3 - Stateless (JWT)
│   │   │   ├── auth.py
│   │   │   └── v3.json
│   │   └── v4/                 # V4 - Cacheable
│   │       ├── books_cache_control.py
│   │       └── books_etag.py
│   ├── services/               # Business Logic (dùng chung)
│   │   ├── book_service.py
│   │   ├── user_service.py
│   │   └── borrow_service.py
│   ├── data/                   # JSON storage
│   │   ├── books.json
│   │   ├── users.json
│   │   └── borrows.json
│   └── app.py                  # Flask app
├── frontend/
│   └── templates/              # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html      # Dashboard V1
│       ├── dashboard_v2.html   # Dashboard V2 (HATEOAS)
│       └── admin.html
├── requirements.txt
├── run.py                      # Entry point
├── V3_JWT_DEMO.md             # Chi tiết demo V3
└── V4_CACHEABLE_DEMO.md       # Chi tiết demo V4
```

### Thiết kế Services

Các **Services** (BookService, UserService, BorrowService) chứa business logic và được chia sẻ giữa tất cả các API versions. Điều này cho phép:
- Tái sử dụng code
- Dễ dàng thêm version mới
- Tách biệt logic nghiệp vụ khỏi API layer

---

## 🚀 V1 - Client-Server Architecture

### Nguyên tắc REST được áp dụng

**Client-Server**: Tách biệt hoàn toàn giữa Client và Server
- **Server (Backend)**: Flask API xử lý logic và trả về JSON
- **Client (Frontend)**: HTML/JavaScript gửi HTTP requests và hiển thị dữ liệu
- Client và Server phát triển độc lập
- Giao tiếp qua HTTP với JSON format

### Response Format

```json
{
  "success": true,
  "data": {...},
  "message": "Success message"
}
```

### API Endpoints

#### Books
- `GET /api/v1/books` - Lấy danh sách sách
- `GET /api/v1/books/:id` - Lấy thông tin sách
- `POST /api/v1/books` - Tạo sách mới
- `PUT /api/v1/books/:id` - Cập nhật sách
- `DELETE /api/v1/books/:id` - Xóa sách

#### Users
- `GET /api/v1/users` - Lấy danh sách người dùng
- `GET /api/v1/users/:id` - Lấy thông tin người dùng
- `POST /api/v1/users` - Đăng ký người dùng mới
- `PUT /api/v1/users/:id` - Cập nhật người dùng
- `DELETE /api/v1/users/:id` - Xóa người dùng

#### Authentication
- `POST /api/v1/auth/login` - Đăng nhập

#### Borrows
- `GET /api/v1/borrows` - Lấy danh sách mượn trả
- `GET /api/v1/borrows/:id` - Lấy thông tin mượn trả
- `POST /api/v1/borrows` - Mượn sách
- `POST /api/v1/borrows/:id/return` - Trả sách
- `GET /api/v1/borrows/history` - Xem lịch sử

---

## 🔗 V2 - Uniform Interface (HATEOAS)

### Nguyên tắc REST được áp dụng

**Uniform Interface** với HATEOAS (Hypermedia As The Engine Of Application State):
- Mỗi response chứa **_links** để điều hướng
- Client không cần biết trước URL structure
- Self-descriptive messages với metadata
- Standard HTTP methods và status codes

### Đặc điểm

- Chỉ áp dụng cho **Books API**: `/api/v2/books`
- Các resource khác (Users, Borrows, Auth) vẫn dùng V1
- Response bao gồm HATEOAS links cho actions có thể thực hiện

### Response Format với HATEOAS

```json
{
  "success": true,
  "data": {
    "id": "1",
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "quantity": 5
  },
  "_links": {
    "self": {"href": "/api/v2/books/1", "method": "GET"},
    "update": {"href": "/api/v2/books/1", "method": "PUT"},
    "delete": {"href": "/api/v2/books/1", "method": "DELETE"},
    "collection": {"href": "/api/v2/books", "method": "GET"}
  },
  "_metadata": {
    "version": "v2",
    "constraint": "Uniform Interface (HATEOAS)"
  }
}
```

### Giao diện

- **Dashboard V2**: http://localhost:5000/dashboard_v2
- Demo cách client sử dụng HATEOAS links để điều hướng

---

## 🔐 V3 - Stateless (JWT Authentication)

### Nguyên tắc REST được áp dụng

**Stateless**: Server không lưu trạng thái client giữa các requests
- Sử dụng **JWT (JSON Web Token)** cho authentication
- Mỗi request tự chứa đầy đủ thông tin (token trong header)
- Không có server-side session
- Dễ dàng scale horizontal

### Đặc điểm

- Chỉ implement **Authentication API**: `/api/v3/auth/*`
- Các resource khác (Books, Users, Borrows) vẫn dùng V1 nhưng có thể bảo vệ bằng JWT
- Token có thời hạn (configurable expiration)
- Support token refresh

### API Endpoints

#### Authentication
- `POST /api/v3/auth/login` - Đăng nhập và nhận JWT token
- `GET /api/v3/auth/verify` - Verify token validity
- `GET /api/v3/auth/decode` - Decode token payload
- `GET /api/v3/auth/protected` - Test protected route
- `POST /api/v3/auth/refresh` - Refresh token

### Response Format

```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": "1",
    "username": "admin",
    "role": "admin"
  },
  "_metadata": {
    "authentication_type": "JWT",
    "stateless": true,
    "token_algorithm": "HS256"
  }
}
```

### Sử dụng

```bash
# 1. Login để lấy token
curl -X POST http://localhost:5000/api/v3/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Sử dụng token trong Authorization header
curl http://localhost:5000/api/v3/auth/protected \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

📖 **Chi tiết**: Xem file `V3_JWT_DEMO.md`

---

## 💾 V4 - Cacheable

### Nguyên tắc REST được áp dụng

**Cacheable**: Response phải tự định nghĩa có thể cache hay không
- Sử dụng **Cache-Control headers** (max-age, no-cache, must-revalidate)
- Sử dụng **ETag headers** cho content-based caching
- Support **Conditional requests** (If-None-Match, If-Match)
- Last-Modified header cho time-based validation
- Tối ưu performance và giảm bandwidth

### Đặc điểm

V4 có **2 implementations** cho Books API:

#### 1. Cache-Control Implementation
- **Endpoint**: `/api/v4/cache-control/books`
- Time-based caching với `Cache-Control: max-age`
- `Last-Modified` header
- Conditional request với `If-Modified-Since`

#### 2. ETag Implementation
- **Endpoint**: `/api/v4/etag/books`
- Content-based caching với Strong/Weak ETags
- Conditional requests với `If-None-Match` (GET), `If-Match` (PUT/DELETE)
- Optimistic locking để tránh conflicts
- 304 Not Modified response khi content không đổi

### Response Headers

```http
# Cache-Control
HTTP/1.1 200 OK
Cache-Control: public, max-age=60
Last-Modified: Fri, 10 Oct 2025 10:30:00 GMT

# ETag
HTTP/1.1 200 OK
ETag: "abc123xyz"
Cache-Control: no-cache
```

### API Endpoints

#### Cache-Control
- `GET /api/v4/cache-control` - API info
- `GET /api/v4/cache-control/books` - Get all books (with Cache-Control)
- `GET /api/v4/cache-control/books/:id` - Get book (with Cache-Control)
- `POST /api/v4/cache-control/books` - Create book
- `PUT /api/v4/cache-control/books/:id` - Update book
- `DELETE /api/v4/cache-control/books/:id` - Delete book

#### ETag
- `GET /api/v4/etag` - API info
- `GET /api/v4/etag/books` - Get all books (with ETag)
- `GET /api/v4/etag/books/:id` - Get book (with ETag)
- `POST /api/v4/etag/books` - Create book
- `PUT /api/v4/etag/books/:id` - Update book (requires If-Match)
- `DELETE /api/v4/etag/books/:id` - Delete book (requires If-Match)

### Sử dụng

```bash
# 1. First request - nhận ETag
curl -i http://localhost:5000/api/v4/etag/books/1

# 2. Subsequent request - gửi ETag
curl -i http://localhost:5000/api/v4/etag/books/1 \
  -H "If-None-Match: \"abc123xyz\""
  
# Response: 304 Not Modified (nếu không thay đổi)
```

📖 **Chi tiết**: Xem file `V4_CACHEABLE_DEMO.md`

---

## 📦 Cài đặt

### Yêu cầu
- Python 3.8+
- pip

### Các bước cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd demo-book
```

2. Tạo virtual environment (khuyến nghị):
```bash
python -m venv venv
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

4. Cấu hình môi trường (khuyến nghị):
```bash
# Copy file .env.example và chỉnh sửa
cp .env.example .env

# Generate strong secret keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))" >> .env
```

5. Chạy ứng dụng:
```bash
python run.py
```

6. Truy cập ứng dụng:

| URL | Mô tả |
|-----|-------|
| http://localhost:5000 | Frontend - Trang chủ |
| http://localhost:5000/dashboard | Dashboard V1 |
| http://localhost:5000/dashboard_v2 | Dashboard V2 (HATEOAS) |
| http://localhost:5000/admin | Admin dashboard |
| http://localhost:5000/api | API info (tất cả versions) |
| http://localhost:5000/api/docs | Swagger UI Documentation |
| http://localhost:5000/apispec.json | OpenAPI Specification |

---

## 🔐 Tài khoản mặc định

**Admin (Demo only - Change in production!):**
- Username: `admin`
- Password: `admin123`

⚠️ **Security Warning:** These are default credentials for demo purposes only. In a production environment, you MUST change these credentials immediately after first login!

## 📚 OpenAPI/Swagger Documentation

Hệ thống tích hợp **Swagger UI** để tương tác và test API một cách dễ dàng.

### Truy cập Swagger UI

Sau khi chạy server, truy cập:
- **Swagger UI**: http://localhost:5000/api/docs
- **OpenAPI JSON Spec**: http://localhost:5000/apispec.json

### Tính năng Swagger UI

1. **Xem tất cả endpoints**: Liệt kê đầy đủ các API endpoints theo từng nhóm (Books, Users, Authentication, Borrows)
2. **Test API trực tiếp**: Có thể thử nghiệm các API call ngay trên giao diện
3. **Xem schema**: Hiển thị chi tiết request/response schema
4. **Xem ví dụ**: Mỗi endpoint đều có example data
5. **Download spec**: Tải về OpenAPI specification để import vào Postman hoặc các tools khác

### Import vào Postman

1. Tải về OpenAPI spec: http://localhost:5000/apispec.json
2. Mở Postman → Import → Paste link hoặc upload file
3. Tất cả endpoints sẽ được tự động import với đầy đủ documentation

## 🔒 Security

Dự án này bao gồm các biện pháp bảo mật:

- **Pre-commit hooks**: Tự động scan và ngăn chặn commit tokens/secrets
- **Security audit report**: Xem `SECURITY_AUDIT_REPORT.md` để biết chi tiết
- **Environment variables**: Sử dụng `.env` file (không commit vào Git)
- **JWT Authentication**: Stateless authentication với tokens có thời hạn

### Báo cáo lỗ hổng bảo mật

Nếu phát hiện vấn đề bảo mật, vui lòng:
1. KHÔNG tạo public issue
2. Liên hệ trực tiếp với maintainers
3. Cung cấp chi tiết về lỗ hổng

## 📄 License

MIT License

