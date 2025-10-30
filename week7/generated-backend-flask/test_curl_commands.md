# Hướng dẫn Test API bằng Curl/PowerShell

## Khởi động Server

```powershell
cd week7/generated-backend-flask
python run_server.py
```

Server sẽ chạy tại: `http://localhost:5001`

API Base URL: `http://localhost:5001/api/v1`

---

## Các lệnh Test với PowerShell (Windows)

### 1. Lấy tất cả sách (GET /books)

```powershell
Invoke-WebRequest -Uri "http://localhost:5001/api/v1/books" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

Hoặc dùng alias ngắn gọn hơn:

```powershell
(Invoke-WebRequest "http://localhost:5001/api/v1/books").Content
```

### 2. Lọc sách theo title (GET /books?title=clean)

```powershell
Invoke-WebRequest -Uri "http://localhost:5001/api/v1/books?title=clean" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

### 3. Lọc sách theo author (GET /books?author=martin)

```powershell
Invoke-WebRequest -Uri "http://localhost:5001/api/v1/books?author=martin" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

### 4. Xem Response Headers

```powershell
$response = Invoke-WebRequest -Uri "http://localhost:5001/api/v1/books" -Method GET -UseBasicParsing
$response.Headers
$response.Content
```

---

## Các lệnh Test với curl (nếu cài đặt curl thật)

### 1. Lấy tất cả sách

```bash
curl -X GET "http://localhost:5001/api/v1/books"
```

### 2. Lấy sách với format đẹp (có jq)

```bash
curl -X GET "http://localhost:5001/api/v1/books" | jq
```

### 3. Lọc theo title

```bash
curl -X GET "http://localhost:5001/api/v1/books?title=clean"
```

### 4. Lọc theo author

```bash
curl -X GET "http://localhost:5001/api/v1/books?author=martin"
```

### 5. Xem headers

```bash
curl -X GET "http://localhost:5001/api/v1/books" -v
```

---

## Swagger UI

Bạn cũng có thể truy cập Swagger UI để test API trực quan:

```
http://localhost:5001/ui
```

---

## Kết quả mẫu

```json
{
  "count": 3,
  "data": [
    {
      "author": "Robert C. Martin",
      "id": 1,
      "publisher": "Prentice Hall",
      "quantity": 5,
      "title": "Clean Code"
    },
    {
      "author": "Andrew Hunt",
      "id": 2,
      "publisher": "Addison-Wesley",
      "quantity": 3,
      "title": "The Pragmatic Programmer"
    },
    {
      "author": "Gang of Four",
      "id": 3,
      "publisher": "Addison-Wesley",
      "quantity": 4,
      "title": "Design Patterns"
    }
  ],
  "success": true
}


