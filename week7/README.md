# Book Management API

RESTful API để quản lý sách được sinh tự động từ OpenAPI specification.

## Các công cụ sinh code từ OpenAPI

### 1. Sử dụng OpenAPI Generator (Khuyên dùng cho production)

```bash
# Cài đặt OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# Sinh code Flask server từ OpenAPI spec
openapi-generator-cli generate -i openapi.yaml -g python-flask -o ./generated

# Hoặc dùng Docker
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -i /local/openapi.yaml \
  -g python-flask \
  -o /local/generated
```

### 2. Sử dụng Connexion (Khuyên dùng cho Flask)

Connexion là framework Python tự động ánh xạ OpenAPI spec vào Flask routes.

```bash
# Cài đặt
pip install connexion[swagger-ui]

# Code sẽ tự động đọc OpenAPI và map vào controllers
```

### 3. Sử dụng Swagger Codegen

```bash
# Cài đặt
npm install -g swagger-codegen

# Sinh code
swagger-codegen generate -i openapi.yaml -l python-flask -o ./generated
```

## Cấu trúc project

```
week7/
├── openapi.yaml           # OpenAPI specification
├── app.py                 # Flask application với Connexion
├── controllers/           # Controllers được ánh xạ từ operationId
│   └── books_controller.py
├── services/              # Business logic layer
│   └── book_service.py
├── data/                  # JSON data storage
│   └── books.json
└── requirements.txt       # Python dependencies
```

## Cài đặt và chạy

```bash
# 1. Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Chạy ứng dụng
python app.py
```

## API Endpoints

API sẽ chạy tại: `http://localhost:5000`

### Swagger UI
Truy cập: `http://localhost:5000/api/ui`

### Endpoints:

- **GET** `/api/v1/books` - Lấy danh sách sách
- **GET** `/api/v1/books/{id}` - Lấy thông tin sách theo ID
- **POST** `/api/v1/books` - Tạo sách mới
- **PUT** `/api/v1/books/{id}` - Cập nhật toàn bộ thông tin sách
- **PATCH** `/api/v1/books/{id}` - Cập nhật một phần thông tin sách
- **DELETE** `/api/v1/books/{id}` - Xóa sách

## Test API

```bash
# Lấy tất cả sách
curl http://localhost:5000/api/v1/books

# Tạo sách mới
curl -X POST http://localhost:5000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "publisher": "Prentice Hall",
    "year": 2008,
    "category": "Programming",
    "quantity": 5,
    "description": "A handbook of agile software craftsmanship"
  }'

# Lấy sách theo ID
curl http://localhost:5000/api/v1/books/1

# Cập nhật sách
curl -X PUT http://localhost:5000/api/v1/books/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code - Updated",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "year": 2008
  }'

# Xóa sách
curl -X DELETE http://localhost:5000/api/v1/books/1
```

## Ưu điểm của việc dùng OpenAPI-first approach

1. **API Documentation tự động** - Swagger UI được tạo tự động
2. **Validation tự động** - Request/Response được validate theo schema
3. **Code generation** - Tiết kiệm thời gian viết boilerplate code
4. **Contract-first** - API contract được định nghĩa trước khi code
5. **Dễ maintain** - Thay đổi spec sẽ tự động update code

## So sánh các công cụ

| Công cụ | Ưu điểm | Nhược điểm |
|---------|---------|------------|
| **Connexion** | - Tích hợp tốt với Flask<br>- Swagger UI built-in<br>- Validation tự động | - Chỉ cho Python |
| **OpenAPI Generator** | - Hỗ trợ nhiều ngôn ngữ<br>- Sinh full code | - Code sinh ra phức tạp<br>- Cần customize nhiều |
| **Swagger Codegen** | - Stable, mature | - Ít features hơn OpenAPI Generator |

