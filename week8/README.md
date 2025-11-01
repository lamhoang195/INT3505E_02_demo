# Week 8 - API Testing

Thư mục này chứa các file test cho Library Management API.

## 📁 Nội dung

| File | Mô tả |
|------|-------|
| `test_api.py` | Unit tests cho 5 endpoints chính (9 test cases) |
| `TEST_GUIDE.md` | Hướng dẫn chi tiết cách test (580+ dòng) |
| `QUICK_START.md` | Hướng dẫn nhanh 5 phút ⚡ |
| `NEWMAN_GUIDE.md` | Hướng dẫn test tự động với Newman CLI 🤖 |
| `Library_API_Tests.postman_collection.json` | Postman collection (9 requests) |
| `SUMMARY.md` | Tóm tắt toàn bộ nội dung week 8 |

## 🚀 Quick Start

### Bắt Đầu Nhanh (Khuyến Nghị)
👉 **Đọc file `QUICK_START.md`** để test trong 5 phút!

### 1. Chạy Unit Tests

```bash
# Từ thư mục gốc project
python week8/test_api.py
```

**Kết quả:** 9/9 tests pass ✅

### 2. Test với Postman

1. Import file `Library_API_Tests.postman_collection.json` vào Postman
2. Click **Run collection** để chạy tất cả 9 requests
3. Hoặc test từng request riêng lẻ

### 3. Test Tự Động với Newman 🤖

```bash
# Cài đặt Newman (chỉ 1 lần)
npm install -g newman

# Chạy tests
cd week8
newman run Library_API_Tests.postman_collection.json
```

**Kết quả:** 24/24 assertions pass ✅ (9 requests, ~846ms)

## 📝 5 Endpoints Được Test

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | GET | `/api/v1/books` | Lấy danh sách sách |
| 2 | POST | `/api/v1/books` | Tạo sách mới |
| 3 | POST | `/api/v1/auth/login` | Đăng nhập V1 |
| 4 | POST | `/api/v3/auth/login` | Đăng nhập JWT (V3) |
| 5 | GET | `/api/v3/auth/verify` | Xác thực JWT token |

## 📚 Tài Liệu

- **Bắt đầu nhanh:** `QUICK_START.md` (5 phút)
- **Chi tiết đầy đủ:** `TEST_GUIDE.md` (hướng dẫn chi tiết)
- **Newman/Automation:** `NEWMAN_GUIDE.md` (test tự động)
- **Tóm tắt:** `SUMMARY.md` (overview toàn bộ)

## ✅ Test Results

### Unit Tests (Python)
```
Tests run: 9
Successes: 9
Failures: 0
Errors: 0
Status: ✅ ALL PASS
```

### Newman Tests (Automated)
```
Requests: 9/9 passed
Assertions: 24/24 passed
Failures: 0
Duration: ~846ms
Average Response: 9ms
Status: ✅ 100% PASS
```
