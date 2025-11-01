# Hướng Dẫn Test Tự Động với Newman

## 🎯 Newman là gì?

**Newman** là command-line tool cho phép chạy Postman collections từ terminal, rất hữu ích cho:
- ✅ Automated testing trong CI/CD pipeline
- ✅ Test tự động không cần mở Postman GUI
- ✅ Integration testing
- ✅ Regression testing

---

## 📦 Cài Đặt Newman

### Yêu Cầu
- Node.js đã cài đặt (kiểm tra: `node --version`)
- npm đã cài đặt (kiểm tra: `npm --version`)

### Cài Đặt
```bash
npm install -g newman
```

### Verify Cài Đặt
```bash
newman --version
```

---

## 🚀 Chạy Tests với Newman

### Cách 1: Chạy Collection Cơ Bản
```bash
# Từ thư mục week8
newman run Library_API_Tests.postman_collection.json
```

### Cách 2: Chạy với Environment Variables
```bash
# Nếu có file environment
newman run Library_API_Tests.postman_collection.json -e environment.json
```

### Cách 3: Chạy với Options
```bash
# Với nhiều options
newman run Library_API_Tests.postman_collection.json \
  --reporters cli,html \
  --reporter-html-export newman-report.html \
  --delay-request 100
```

---

## 📊 Kết Quả Test Thực Tế

```
D:\KTHDV\demo-book\week8>newman run Library_API_Tests.postman_collection.json
newman

Library Management API - Week 8 Tests

→ 1. GET Books List
  GET http://localhost:5000/api/v1/books [200 OK, 3.25kB, 29ms]
  ✓  Status code is 200
  ✓  Response has success field
  ✓  Data is an array
  ✓  Books have required fields

→ 2. POST Create Book
  POST http://localhost:5000/api/v1/books [201 CREATED, 445B, 8ms]
  ✓  Status code is 201
  ✓  Book created successfully
  ✓  Book data is correct

→ 2b. POST Create Book (Validation Error)
  POST http://localhost:5000/api/v1/books [400 BAD REQUEST, 276B, 6ms]
  ✓  Status code is 400
  ✓  Validation error returned

→ 3. POST Login V1
  POST http://localhost:5000/api/v1/auth/login [200 OK, 369B, 9ms]
  ✓  Status code is 200
  ✓  Login successful
  ✓  Password not in response

→ 3b. POST Login V1 (Wrong Password)
  POST http://localhost:5000/api/v1/auth/login [401 UNAUTHORIZED, 267B, 6ms]
  ✓  Status code is 401
  ✓  Invalid credentials rejected

→ 4. POST Login JWT (V3)
  POST http://localhost:5000/api/v3/auth/login [200 OK, 955B, 9ms]
  ✓  Status code is 200
  ✓  JWT token received
  ┌
  │ '✓ JWT token saved to environment:', 'eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...'
  └
  ✓  User data present

→ 5. GET Verify JWT Token
  GET http://localhost:5000/api/v3/auth/verify [200 OK, 588B, 6ms]
  ✓  Status code is 200
  ✓  Token is valid
  ✓  User data decoded from token

→ 5b. GET Verify JWT (Invalid Token)
  GET http://localhost:5000/api/v3/auth/verify [401 UNAUTHORIZED, 322B, 6ms]
  ✓  Status code is 401
  ✓  Invalid token rejected

→ 5c. GET Verify JWT (No Token)
  GET http://localhost:5000/api/v3/auth/verify [401 UNAUTHORIZED, 330B, 6ms]
  ✓  Status code is 401
  ✓  Token missing error

┌─────────────────────────┬─────────────────┬─────────────────┐
│                         │        executed │          failed │
├─────────────────────────┼─────────────────┼─────────────────┤
│              iterations │               1 │               0 │
├─────────────────────────┼─────────────────┼─────────────────┤
│                requests │               9 │               0 │
├─────────────────────────┼─────────────────┼─────────────────┤
│            test-scripts │               9 │               0 │
├─────────────────────────┼─────────────────┼─────────────────┤
│      prerequest-scripts │               0 │               0 │
├─────────────────────────┼─────────────────┼─────────────────┤
│              assertions │              24 │               0 │
├─────────────────────────┴─────────────────┴─────────────────┤
│ total run duration: 846ms                                   │
├─────────────────────────────────────────────────────────────┤
│ total data received: 4.97kB (approx)                        │
├─────────────────────────────────────────────────────────────┤
│ average response time: 9ms [min: 6ms, max: 29ms, s.d.: 7ms] │
└─────────────────────────────────────────────────────────────┘
```

### 📈 Phân Tích Kết Quả

| Metric | Value | Status |
|--------|-------|--------|
| **Requests** | 9/9 | ✅ Pass |
| **Assertions** | 24/24 | ✅ Pass |
| **Test Scripts** | 9/9 | ✅ Pass |
| **Failed** | 0 | ✅ Perfect |
| **Total Duration** | 846ms | ⚡ Fast |
| **Average Response** | 9ms | ⚡ Excellent |
| **Data Received** | 4.97kB | 📦 Minimal |

---

## 📊 Phân Tích Test Results

### Key Metrics từ Output

1. **Iterations**: Số lần chạy toàn bộ collection
2. **Requests**: Số API calls được thực hiện
3. **Test Scripts**: Số test scripts được execute
4. **Assertions**: Tổng số assertions (checks)
5. **Failed**: Số lượng failures
6. **Run Duration**: Tổng thời gian chạy
7. **Response Time**: Thời gian response trung bình

### Đánh Giá Performance

| Response Time | Rating |
|---------------|--------|
| < 100ms | ⚡ Excellent |
| 100-500ms | ✅ Good |
| 500ms-1s | ⚠️ Average |
| > 1s | ❌ Slow |

Kết quả của chúng ta: **9ms average = ⚡ Excellent!**

---

## 🎉 Tóm Tắt

### Quick Commands

```bash
# Cài đặt
npm install -g newman

# Chạy tests
cd week8
newman run Library_API_Tests.postman_collection.json

# Chạy với HTML report
newman run Library_API_Tests.postman_collection.json \
  --reporters cli,html \
  --reporter-html-export newman-report.html
```

### Kết Quả Hiện Tại
- ✅ 9/9 requests passed
- ✅ 24/24 assertions passed
- ✅ 0 failures
- ⚡ 9ms average response time
- 🎯 846ms total duration

**Status: 100% PASS! 🎉**