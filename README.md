## Demo Library App (Flask)

Ứng dụng web thư viện đơn giản: đăng ký/đăng nhập, phân quyền admin/user, quản lý sách, mượn/trả. Dữ liệu lưu ở file JSON.

### Yêu cầu
- Python 3.10+

### Cài đặt
```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows PowerShell
pip install -r requirements.txt
```

### Chạy ứng dụng
```bash
python run.py
```
Mở `http://localhost:5000`.

### Tài khoản mặc định
- Admin: username `admin`, password `admin123`.

### Chức năng
- Admin (`/admin`): thêm/sửa/xóa sách, xem và xóa record mượn (đồng thời trả sách, đặt lại `available`).
- User (`/user`): xem danh sách sách, mượn/trả sách.

### Cấu trúc dự án
```
backend/
  app.py           # app factory, seed admin
  storage.py       # tiện ích đọc/ghi JSON an toàn
  admin/routes.py  # route cho admin
  auth/routes.py   # login/register/logout
  user/routes.py   # route cho user
frontend/templates/
  base.html, login.html, register.html, admin.html, user.html
run.py
requirements.txt
README.md
```


