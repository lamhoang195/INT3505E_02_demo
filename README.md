# Hệ thống Quản lý Sách - RESTful API

Hệ thống quản lý sách với kiến trúc RESTful API, được phát triển theo từng nguyên tắc REST.

## 📋 Tổng quan

Dự án này được xây dựng để demo các nguyên tắc REST API:
- **V1**: Client-Server Architecture ✅

## 🏗️ Kiến trúc

### Cấu trúc thư mục
```
demo-book/
├── backend/
│   ├── api/              # API Controllers (theo version)
│   │   └── v1/           # V1 - Client-Server
│   │       ├── books.py
│   │       ├── users.py
│   │       └── borrows.py
│   ├── services/         # Business Logic (dùng chung)
│   │   ├── book_service.py
│   │   ├── user_service.py
│   │   └── borrow_service.py
│   ├── data/            # JSON storage
│   │   ├── books.json
│   │   ├── users.json
│   │   └── borrows.json
│   └── app.py           # Flask app
├── frontend/
│   └── templates/       # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       └── admin.html
├── requirements.txt
└── run.py              # Entry point
```

### Thiết kế Services

Các **Services** (BookService, UserService, BorrowService) chứa business logic và được chia sẻ giữa tất cả các API versions. Điều này cho phép:
- Tái sử dụng code
- Dễ dàng thêm version mới
- Tách biệt logic nghiệp vụ khỏi API layer


## 🚀 V1 - Client-Server Architecture

### Nguyên tắc được áp dụng

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

4. Chạy ứng dụng:
```bash
python run.py
```

5. Truy cập ứng dụng:
- Frontend: http://localhost:5000
- API: http://localhost:5000/api/v1
- API Info: http://localhost:5000/api

## 🔐 Tài khoản mặc định

**Admin:**
- Username: `admin`
- Password: `admin123`

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

## 💡 Sử dụng

### Cho người dùng thường
1. Truy cập http://localhost:5000
2. Đăng ký tài khoản mới hoặc đăng nhập
3. Xem danh sách sách
4. Mượn và trả sách
5. Xem lịch sử mượn trả

### Cho Admin
1. Đăng nhập với tài khoản admin
2. Quản lý sách (thêm, sửa, xóa)
3. Xem danh sách người dùng
4. Xem tất cả giao dịch mượn trả

## 🧪 Test API

Truy cập http://localhost:5000/api/docs và test trực tiếp trên giao diện web.

### Cách 3: Import vào Postman

1. Tải về OpenAPI spec: http://localhost:5000/apispec.json
2. Mở Postman → Import → Paste link hoặc upload file
3. Tất cả endpoints sẽ được tự động import với đầy đủ documentation


## 📝 Ghi chú

- Dữ liệu được lưu trong các file JSON (backend/data/)
- Mật khẩu được hash bằng SHA256
- Frontend sử dụng localStorage để lưu thông tin user
- API trả về JSON với format: `{success: boolean, data: any, message: string}`


## 📄 License

MIT License

