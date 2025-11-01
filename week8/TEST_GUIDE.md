# Hướng Dẫn Test API - Library Management System

## 📋 Mục Lục
1. [Giới Thiệu](#giới-thiệu)
2. [Chuẩn Bị](#chuẩn-bị)
3. [Unit Test với Python](#unit-test-với-python)
4. [Manual Test với Postman](#manual-test-với-postman)
5. [5 Endpoints Chính](#5-endpoints-chính)

---

## 🎯 Giới Thiệu

Tài liệu này hướng dẫn test 5 endpoints chính của hệ thống Library Management:
1. **GET /api/v1/books** - Lấy danh sách sách
2. **POST /api/v1/books** - Tạo sách mới
3. **POST /api/v1/auth/login** - Đăng nhập V1
4. **POST /api/v3/auth/login** - Đăng nhập JWT (V3)
5. **GET /api/v3/auth/verify** - Xác thực JWT token

---

## 🛠️ Chuẩn Bị

### 1. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 2. Khởi Động Server
```bash
python run.py
```

Server sẽ chạy tại: `http://localhost:5000`

### 3. Cài Đặt Postman
- Download Postman: https://www.postman.com/downloads/
- Hoặc sử dụng Postman Web: https://web.postman.com/

---

## 🧪 Unit Test với Python

### Chạy Tất Cả Tests

```bash
# Từ thư mục gốc của project
python week8/test_api.py
```

### Chạy Test Cụ Thể

```bash
# Chạy 1 test case cụ thể
python week8/test_api.py TestLibraryAPI.test_01_get_books_list
```

### Kết Quả Mong Đợi

```
======================================================================
Library Management API - Unit Tests
======================================================================
▶ Running: test_01_get_books_list
  Testing GET /api/v1/books
  ✓ Found X books
✓ Completed: test_01_get_books_list
.
▶ Running: test_02_create_book
  Testing POST /api/v1/books
  ✓ Created book with ID: X
✓ Completed: test_02_create_book
.
...

======================================================================
Test Summary
======================================================================
Tests run: 9
Successes: 9
Failures: 0
Errors: 0
======================================================================
```

---

## 📮 Manual Test với Postman

### Setup Postman Environment

1. Tạo Environment mới tên "Library API"
2. Thêm các biến:
   - `base_url`: `http://localhost:5000`
   - `jwt_token`: (để trống, sẽ tự động set)

---

## 🎯 5 Endpoints Chính

### 1️⃣ GET /api/v1/books - Lấy Danh Sách Sách

**Postman Setup:**
- Method: `GET`
- URL: `{{base_url}}/api/v1/books`
- Headers: Không cần

**Expected Response (200 OK):**
```json
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
  ]
}
```

**Test Cases:**
- ✅ Status code = 200
- ✅ `success` = true
- ✅ `data` là array
- ✅ Mỗi book có đủ fields: id, title, author

---

### 2️⃣ POST /api/v1/books - Tạo Sách Mới

**Postman Setup:**
- Method: `POST`
- URL: `{{base_url}}/api/v1/books`
- Headers:
  - `Content-Type`: `application/json`
- Body (raw JSON):

```json
{
  "title": "Test Book from Postman",
  "author": "Test Author",
  "isbn": "978-1234567890",
  "quantity": 10
}
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "new_id",
    "title": "Test Book from Postman",
    "author": "Test Author",
    "isbn": "978-1234567890",
    "quantity": 10,
    "available": 10
  },
  "message": "Book created successfully"
}
```

**Test Cases:**
- ✅ Status code = 201
- ✅ `success` = true
- ✅ Book có ID mới
- ✅ Data khớp với input

**Test Validation Error:**
```json
{
  "title": "Only Title"
}
```
Expected: 400 Bad Request với message "Title and author are required"

---

### 3️⃣ POST /api/v1/auth/login - Đăng Nhập V1

**Postman Setup:**
- Method: `POST`
- URL: `{{base_url}}/api/v1/auth/login`
- Headers:
  - `Content-Type`: `application/json`
- Body (raw JSON):

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "1",
    "username": "admin",
    "full_name": "Administrator",
    "role": "admin"
  },
  "message": "Login successful"
}
```

**Test Cases:**
- ✅ Status code = 200
- ✅ `success` = true
- ✅ User data không chứa password
- ✅ Có role và username

**Test Login Failed:**
```json
{
  "username": "admin",
  "password": "wrongpassword"
}
```
Expected: 401 Unauthorized

---

### 4️⃣ POST /api/v3/auth/login - Đăng Nhập JWT

**Postman Setup:**
- Method: `POST`
- URL: `{{base_url}}/api/v3/auth/login`
- Headers:
  - `Content-Type`: `application/json`
- Body (raw JSON):

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Expected Response (200 OK):**
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
    "full_name": "Administrator",
    "role": "admin"
  },
  "_metadata": {
    "authentication_type": "JWT",
    "stateless": true,
    "token_algorithm": "HS256"
  }
}
```

**⚠️ QUAN TRỌNG - Lưu Token:**

Trong Postman Tests tab, thêm script để tự động lưu token:
```javascript
// Lưu JWT token vào environment variable
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("jwt_token", jsonData.token);
    console.log("JWT token saved:", jsonData.token.substring(0, 30) + "...");
}
```

**Test Cases:**
- ✅ Status code = 200
- ✅ `success` = true
- ✅ Có JWT token
- ✅ `token_type` = "Bearer"
- ✅ Token được save vào environment

---

### 5️⃣ GET /api/v3/auth/verify - Xác Thực JWT Token

**Postman Setup:**
- Method: `GET`
- URL: `{{base_url}}/api/v3/auth/verify`
- Headers:
  - `Authorization`: `Bearer {{jwt_token}}`

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "Token is valid",
  "user": {
    "user_id": "1",
    "username": "admin",
    "role": "admin",
    "exp": 1234567890,
    "iat": 1234567890
  },
  "_metadata": {
    "stateless": true,
    "note": "Server không lưu session, chỉ verify token"
  }
}
```

**Test Cases:**
- ✅ Status code = 200
- ✅ `success` = true
- ✅ User data từ token
- ✅ Token còn hạn

**Test Invalid Token:**
- Thay `{{jwt_token}}` bằng `invalid_token`
- Expected: 401 Unauthorized

**Test Missing Token:**
- Xóa header Authorization
- Expected: 401 Unauthorized với message "Authentication token is required"

---

## 🔄 Test Flow Hoàn Chỉnh

### Flow 1: Basic CRUD
```
1. GET /api/v1/books          → Xem danh sách
2. POST /api/v1/books         → Tạo sách mới
3. GET /api/v1/books          → Xác nhận sách đã tạo
```

### Flow 2: Authentication với JWT
```
1. POST /api/v3/auth/login    → Đăng nhập, nhận token
2. GET /api/v3/auth/verify    → Xác thực token
3. (Sử dụng token cho các API khác)
```

---

## 📊 Tạo Postman Collection

### Import Collection

Tạo file `Library_API_Tests.postman_collection.json`:

```json
{
  "info": {
    "name": "Library Management API Tests",
    "description": "Test 5 endpoints chính",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. GET Books",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/api/v1/books",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "books"]
        }
      }
    },
    {
      "name": "2. POST Create Book",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"title\": \"Test Book\",\n  \"author\": \"Test Author\",\n  \"isbn\": \"978-1234567890\",\n  \"quantity\": 10\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/v1/books",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "books"]
        }
      }
    },
    {
      "name": "3. POST Login V1",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"admin\",\n  \"password\": \"admin123\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/v1/auth/login",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "auth", "login"]
        }
      }
    },
    {
      "name": "4. POST Login JWT (V3)",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "if (pm.response.code === 200) {",
              "    var jsonData = pm.response.json();",
              "    pm.environment.set(\"jwt_token\", jsonData.token);",
              "}"
            ]
          }
        }
      ],
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"admin\",\n  \"password\": \"admin123\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/v3/auth/login",
          "host": ["{{base_url}}"],
          "path": ["api", "v3", "auth", "login"]
        }
      }
    },
    {
      "name": "5. GET Verify JWT Token",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{jwt_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v3/auth/verify",
          "host": ["{{base_url}}"],
          "path": ["api", "v3", "auth", "verify"]
        }
      }
    }
  ]
}
```

### Import vào Postman:
1. Mở Postman
2. Click **Import**
3. Chọn file `Library_API_Tests.postman_collection.json`
4. Collection sẽ xuất hiện với 5 requests

---

## ✅ Checklist Test

### Trước Khi Test
- [ ] Server đang chạy tại `http://localhost:5000`
- [ ] Postman đã cài đặt
- [ ] Environment đã setup với `base_url`

### Unit Tests
- [ ] Tất cả 9 test cases pass
- [ ] Không có errors hoặc failures
- [ ] Test coverage đầy đủ cho 5 endpoints

### Postman Tests
- [ ] GET Books - Status 200, trả về array
- [ ] POST Books - Status 201, tạo thành công
- [ ] POST Books (invalid) - Status 400, validation error
- [ ] POST Login V1 - Status 200, trả về user data
- [ ] POST Login V1 (wrong) - Status 401, rejected
- [ ] POST Login JWT - Status 200, trả về token
- [ ] JWT token được save vào environment
- [ ] GET Verify JWT - Status 200 với valid token
- [ ] GET Verify JWT - Status 401 với invalid token
- [ ] GET Verify JWT - Status 401 khi missing token

---

## 🚀 Tips & Tricks

### 1. Debug Request/Response
Trong Postman Console (View → Show Postman Console) để xem:
- Request headers
- Response headers
- Raw response body

### 2. Automated Testing
Thêm Tests trong Postman để tự động kiểm tra:

```javascript
// Test status code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Test response structure
pm.test("Response has success field", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('success');
});

// Test response data
pm.test("Success is true", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.success).to.be.true;
});
```

### 3. Test với cURL (Alternative)

```bash
# 1. GET Books
curl http://localhost:5000/api/v1/books

# 2. POST Create Book
curl -X POST http://localhost:5000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","author":"Author","quantity":5}'

# 3. POST Login V1
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 4. POST Login JWT
curl -X POST http://localhost:5000/api/v3/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 5. GET Verify JWT (thay YOUR_TOKEN)
curl http://localhost:5000/api/v3/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN"
```

