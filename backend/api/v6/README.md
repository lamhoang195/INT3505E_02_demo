# API V6 - Borrow with Donation Feature

## ⚠️ DEPRECATED - API V6 đã được đánh dấu là Deprecated

**Trạng thái:** Deprecated  
**Sunset Date:** 31/12/2025  
**Lý do Deprecated:** Thư viện không còn cần chức năng donate từ người dùng

---

## 📋 Thông báo Deprecation

API V6 đã được đánh dấu là **deprecated** và sẽ **ngừng hoạt động** sau ngày **31 tháng 12 năm 2025**.

### 🎯 Lý do Deprecated

**Thư viện không còn cần mọi người donate nữa.**

Sau khi xem xét và đánh giá lại chính sách vận hành, thư viện đã quyết định:
- Thư viện đã đủ nguồn tài chính để duy trì hoạt động
- Không cần thiết phải yêu cầu người dùng donate khi mượn sách
- Đơn giản hóa quy trình mượn sách cho người dùng
- Tập trung vào các tính năng cốt lõi của hệ thống

### 📅 Timeline

- **Ngày bắt đầu deprecation:** Hiện tại
- **Sunset Date:** 31/12/2025 23:59:59 GMT
- **Sau ngày sunset:** API V6 sẽ không còn hoạt động

---

## 🔍 API Endpoints

API V6 cung cấp các endpoint sau:

### 1. Thông tin API V6
```
GET /api/v6
```

### 2. Mượn sách với donation (tùy chọn)
```
POST /api/v6/borrows
```

**Request Body:**
```json
{
  "user_id": "1",
  "book_id": "1",
  "donation_amount": 50000,      // Tùy chọn (sẽ bị bỏ qua)
  "donation_message": "Cảm ơn!"  // Tùy chọn (sẽ bị bỏ qua)
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "borrow": {
      "id": "1",
      "user_id": "1",
      "book_id": "1",
      "borrow_date": "2024-01-01T10:00:00",
      "due_date": "2024-01-15T10:00:00",
      "status": "borrowed"
    },
    "donation": null  // Sẽ luôn là null do deprecated
  },
  "message": "Book borrowed successfully",
  "deprecation_warning": "⚠️ API V6 is deprecated and will be sunset on 2025-12-31. Please migrate to a newer version."
}
```

### 3. Xem danh sách donations
```
GET /api/v6/donations
GET /api/v6/donations?user_id=1
```

**Note:** Endpoint này chỉ để xem lịch sử donations trước đó. Không còn chấp nhận donations mới.

---

## ⚠️ Cảnh báo cho Developers

### ❌ Không nên làm:

1. **Không phát triển tính năng mới** phụ thuộc vào API V6
2. **Không tích hợp API V6** vào các ứng dụng mới
3. **Không sử dụng donation feature** - tính năng này sẽ bị loại bỏ

### ✅ Nên làm:

1. **Migrate sang API V1** cho chức năng mượn sách cơ bản:
   ```
   POST /api/v1/borrows
   ```

2. **Chuẩn bị migration plan** trước ngày sunset (31/12/2025)

3. **Cập nhật documentation** và code để loại bỏ các tham chiếu đến API V6

4. **Test migration** trên môi trường development trước khi deploy

---

## 🔄 Hướng dẫn Migration

### Từ V6 sang V1

**API V6 (Deprecated):**
```javascript
POST /api/v6/borrows
{
  "user_id": "1",
  "book_id": "1",
  "donation_amount": 50000,      // Sẽ bị bỏ qua
  "donation_message": "Cảm ơn!"  // Sẽ bị bỏ qua
}
```

**API V1 (Recommended):**
```javascript
POST /api/v1/borrows
{
  "user_id": "1",
  "book_id": "1"
}
```

### Các thay đổi chính:

1. **Endpoint:** `/api/v6/borrows` → `/api/v1/borrows`
2. **Request body:** Loại bỏ `donation_amount` và `donation_message`
3. **Response:** Không còn field `donation` trong response
4. **Headers:** Không còn deprecation warnings

### Ví dụ Migration Code

**Trước (V6):**
```javascript
const response = await fetch('http://localhost:5000/api/v6/borrows', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: currentUser.id,
    book_id: bookId,
    donation_amount: donationAmount,  // Sẽ bị bỏ qua
    donation_message: donationMessage // Sẽ bị bỏ qua
  })
});
```

**Sau (V1):**
```javascript
const response = await fetch('http://localhost:5000/api/v1/borrows', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: currentUser.id,
    book_id: bookId
    // Loại bỏ donation_amount và donation_message
  })
});
```

---

## 📊 HTTP Response Headers

Khi gọi API V6, bạn sẽ nhận được các headers sau:

```
Deprecation: true
Sunset: Tue, 31 Dec 2025 23:59:59 GMT
Link: </api>; rel="deprecation"; type="text/html"
```

Các headers này báo hiệu rằng API đã deprecated và sẽ ngừng hoạt động sau ngày sunset.

---

## 📝 Lịch sử

### Version History

- **V6.0.0** (2024): Phiên bản đầu tiên với chức năng donate
- **V6.0.1** (2024): Thêm endpoint xem danh sách donations
- **V6.1.0** (2024): **Deprecated** - Thư viện không còn cần donate

---

## 🤝 Liên hệ

Nếu bạn có câu hỏi về việc migration hoặc cần hỗ trợ, vui lòng:

1. Xem tài liệu API tại `/api/docs`
2. Kiểm tra endpoint `/api` để xem các phiên bản API khả dụng
3. Sử dụng API V1 cho chức năng mượn sách: `/api/v1/borrows`

---

## 📚 Tài liệu liên quan

- [API Documentation](/api/docs)
- [API V1 - Borrows](/api/v1/borrows)
- [Main README](../../../README.md)

---

## ⚡ Quick Links

- [API Info](/api)
- [API V1](/api/v1)
- [Swagger UI](/api/docs)

---

**Last Updated:** 2024  
**Status:** ⚠️ Deprecated  
**Sunset Date:** 31/12/2025

