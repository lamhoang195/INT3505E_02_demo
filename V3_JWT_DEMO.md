# API V3 - Stateless với JWT Authentication

## 🎯 V3 Khác Gì So Với V1 và V2?

### **Điểm Khác Biệt Chính: STATELESS**

| Đặc điểm | V1 & V2 | V3 (Stateless với JWT) |
|----------|---------|------------------------|
| **Authentication** | Simple (không có session) | JWT Token |
| **Server State** | Không lưu session | Hoàn toàn stateless |
| **Request** | Mỗi request độc lập | Mỗi request tự chứa token |
| **Scalability** | ✅ | ✅✅ Dễ scale hơn |
| **Token** | ❌ | ✅ JWT với expiration |
| **Authorization Header** | ❌ | ✅ Bearer token |

---

## 🔐 Cách Demo V3 - Stateless với JWT

### **Bước 1: Đăng Nhập và Nhận Token**

```bash
# POST /api/v3/auth/login
curl -X POST http://localhost:5000/api/v3/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMSIsInVzZXJuYW1lIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3MjkwMDAwMDAsImlhdCI6MTcyODkxMzYwMH0.xxxxx",
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
    "token_algorithm": "HS256",
    "expires_at": "2025-10-11T07:43:13Z"
  },
  "_instructions": {
    "usage": "Include token in Authorization header as: Bearer <token>",
    "example": "Authorization: Bearer eyJhbGciOiJIUzI1Ni..."
  }
}
```

**📝 Lưu ý:** Token này chứa đầy đủ thông tin user (id, username, role) được mã hóa.

---

### **Bước 2: Sử Dụng Token Để Gửi Request**

```bash
# GET /api/v3/auth/verify - Verify token có hợp lệ không
curl -X GET http://localhost:5000/api/v3/auth/verify \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

**Response:**
```json
{
  "success": true,
  "message": "Token is valid",
  "user": {
    "user_id": "1",
    "username": "admin",
    "role": "admin",
    "exp": 1729000000,
    "iat": 1728913600
  },
  "_metadata": {
    "stateless": true,
    "note": "Server không lưu session, chỉ verify token",
    "token_issued_at": "2025-10-10T07:43:13",
    "token_expires_at": "2025-10-11T07:43:13"
  }
}
```

**🔑 Điểm quan trọng:** Server **KHÔNG LƯU** session, chỉ giải mã và verify token!

---

### **Bước 3: Giải Mã Token (Decode)**

```bash
# POST /api/v3/auth/decode - Decode token để xem payload
curl -X POST http://localhost:5000/api/v3/auth/decode \
  -H "Content-Type: application/json" \
  -d '{
    "token": "<YOUR_TOKEN>"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Token decoded successfully",
  "payload": {
    "user_id": "1",
    "username": "admin",
    "role": "admin",
    "exp": 1729000000,
    "iat": 1728913600
  },
  "_metadata": {
    "stateless": true,
    "decoded_at": "2025-10-10T08:00:00Z",
    "token_algorithm": "HS256"
  },
  "_info": {
    "user_id": "1",
    "username": "admin",
    "role": "admin",
    "issued_at": "2025-10-10T07:43:13",
    "expires_at": "2025-10-11T07:43:13",
    "time_to_expire": "23:43:13"
  }
}
```

---

### **Bước 4: Test Protected Route**

```bash
# GET /api/v3/auth/protected - Route yêu cầu JWT token
curl -X GET http://localhost:5000/api/v3/auth/protected \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

**Response khi có token hợp lệ:**
```json
{
  "success": true,
  "message": "Access granted to protected route",
  "data": {
    "current_user": {
      "user_id": "1",
      "username": "admin",
      "role": "admin"
    },
    "server_time": "2025-10-10T08:00:00Z"
  },
  "_metadata": {
    "stateless": true,
    "note": "Server không cần lưu session, chỉ verify JWT token từ request"
  }
}
```

**Response khi KHÔNG có token:**
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_MISSING",
    "message": "Authentication token is required"
  }
}
```

---

### **Bước 5: Refresh Token**

```bash
# POST /api/v3/auth/refresh - Làm mới token
curl -X POST http://localhost:5000/api/v3/auth/refresh \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

**Response:**
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "token": "<NEW_TOKEN>",
  "token_type": "Bearer",
  "expires_in": 86400,
  "_metadata": {
    "stateless": true,
    "old_token_expires_at": "2025-10-11T07:43:13",
    "new_token_expires_at": "2025-10-12T08:00:00Z"
  }
}
```

---

## 🎓 Giải Thích Stateless

### **V1/V2 (Không stateless hoàn toàn):**
```
Client → Request → Server
                   ↓
                   Check localStorage/session (nếu có)
                   ↓
                   Response
```

### **V3 (Stateless với JWT):**
```
Client → Request + JWT Token → Server
                                ↓
                                Decode & Verify Token (không cần database)
                                ↓
                                Response
```

**Ưu điểm:**
- ✅ Server không cần lưu session → Dễ scale
- ✅ Token tự chứa thông tin → Self-contained
- ✅ Có thể verify offline → Không cần query database
- ✅ Có expiration → Tự động hết hạn

---

## 🧪 Test V3 Trên Swagger UI

1. Mở Swagger: http://localhost:5000/api/docs
2. Tìm section **"V3 - Authentication (Stateless JWT)"**
3. Test theo thứ tự:
   - `POST /api/v3/auth/login` → Lấy token
   - Copy token
   - Click "Authorize" button ở góc trên
   - Paste: `Bearer <your_token>`
   - Test các endpoint khác

---

## 📊 So Sánh 3 Versions

| Feature | V1 | V2 | V3 |
|---------|----|----|-----|
| **Constraint Demo** | Client-Server | Uniform Interface | Stateless |
| **HATEOAS** | ❌ | ✅ | ❌ |
| **JWT Token** | ❌ | ❌ | ✅ |
| **Stateless** | Partial | Partial | ✅ Full |
| **Books API** | ✅ | ✅ HATEOAS | ✅ (use V1) |
| **Auth** | Simple | Simple | JWT |
| **Scale** | Good | Good | Better |

---

## 💡 Khi Nào Dùng V3?

**Nên dùng V3 khi:**
- ✅ Cần scale horizontally (nhiều server)
- ✅ Microservices architecture
- ✅ Mobile apps cần token-based auth
- ✅ Single Page Applications (SPA)
- ✅ API Gateway pattern

**V1/V2 đủ khi:**
- Traditional web apps
- Đơn giản, ít scale
- Không cần distributed system

---

## 🔍 Kiểm Tra Token Expiration

Token sẽ hết hạn sau 24 giờ. Khi token hết hạn:

```json
{
  "success": false,
  "error": {
    "code": "TOKEN_INVALID",
    "message": "Invalid or expired token"
  }
}
```

→ Client cần login lại hoặc dùng refresh token.

---

## 📝 Notes

- V3 **CHỈ implement JWT Auth endpoints**
- Books/Users/Borrows vẫn dùng V1 API
- Có thể kết hợp: Dùng JWT từ V3 để protect routes của V1
- JWT Secret Key nên thay đổi trong production!

