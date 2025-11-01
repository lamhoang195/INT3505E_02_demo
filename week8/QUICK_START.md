# Hướng Dẫn Test Nhanh - Week 8

## 🎯 Mục Tiêu
Test 5 endpoints chính của Library Management API:
1. GET Books
2. POST Create Book
3. POST Login V1
4. POST Login JWT (V3)
5. GET Verify JWT

---

## ⚡ Test Nhanh với Unit Test

```bash
# Chạy tất cả tests
python week8/test_api.py
```

**Kết quả mong đợi:** 9 tests pass, 0 failures

---

## 📮 Test Nhanh với Postman

### Bước 1: Import Collection
1. Mở Postman
2. Click **Import** → Chọn file `week8/Library_API_Tests.postman_collection.json`
3. Collection xuất hiện với 9 requests

### Bước 2: Chạy Collection
1. Click vào collection "Library Management API - Week 8 Tests"
2. Click **Run** 
3. Click **Run Library Management...** button
4. Xem kết quả: tất cả tests sẽ pass ✅

### Bước 3: Test Từng Endpoint

**Request 1: GET Books**
- URL: `http://localhost:5000/api/v1/books`
- Method: GET
- Click **Send** → Response 200 OK

**Request 2: POST Create Book**
- URL: `http://localhost:5000/api/v1/books`
- Method: POST
- Body đã có sẵn
- Click **Send** → Response 201 Created

**Request 3: POST Login V1**
- URL: `http://localhost:5000/api/v1/auth/login`
- Method: POST
- Credentials: admin/admin123
- Click **Send** → Response 200 OK

**Request 4: POST Login JWT**
- URL: `http://localhost:5000/api/v3/auth/login`
- Method: POST
- Click **Send** → Response 200 OK
- ⚠️ JWT token tự động lưu vào environment!

**Request 5: GET Verify JWT**
- URL: `http://localhost:5000/api/v3/auth/verify`
- Method: GET
- Authorization header tự động dùng token từ Request 4
- Click **Send** → Response 200 OK

---

## ✅ Checklist

- [ ] Server đang chạy: `python run.py`
- [ ] Unit tests pass: `python week8/test_api.py`
- [ ] Postman collection imported
- [ ] Tất cả 9 requests trong Postman pass

---

## 📚 Chi Tiết Đầy Đủ

Xem file **TEST_GUIDE.md** để có hướng dẫn chi tiết hơn.

---

**Thời gian:** ~5 phút để test hoàn chỉnh! 🚀
