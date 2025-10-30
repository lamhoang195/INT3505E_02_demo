# 🚀 Quick Start - OpenAPI Code Generation

## 3 bước đơn giản

### 1️⃣ Cài đặt tool

```bash
pip install openapi-generator-cli
```

### 2️⃣ Sinh code backend

```bash
openapi-generator-cli generate -i openapi.yaml -g python-flask -o generated-backend-flask
```

### 3️⃣ Chạy server

```bash
cd generated-backend-flask
pip install -r requirements.txt
python -m openapi_server
```

## ✨ Kết quả

- 🌐 Swagger UI: http://localhost:8080/api/v1/ui/
- 📝 API Docs: http://localhost:8080/api/v1/openapi.json
- ⚡ API Endpoint: http://localhost:8080/api/v1/books

## 📊 Code được sinh tự động

```
generated-backend-flask/
├── openapi_server/
│   ├── controllers/
│   │   └── books_controller.py    ← Implement logic tại đây
│   ├── models/
│   │   ├── book.py                ← Model đã có sẵn
│   │   ├── book_input.py
│   │   └── error.py
│   └── openapi/
│       └── openapi.yaml
├── requirements.txt                ← Dependencies đã có
└── README.md                       ← Hướng dẫn chạy
```