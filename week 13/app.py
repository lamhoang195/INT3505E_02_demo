"""
Buổi 13: API as a Product – demo nhỏ nhất.

Chạy:
    python "week 13/app.py"
Sau đó mở: http://127.0.0.1:5013/portal
"""

from flask import Flask, jsonify, render_template

app = Flask(__name__, template_folder="templates")


@app.get("/api/info")
def api_info():
    """Thông tin sản phẩm API + mô hình kiếm tiền (JSON đơn giản)."""
    return jsonify(
        {
            "name": "Library Payment API",
            "version": "v1",
            "description": "API thanh toán cho hệ thống thư viện, thiết kế như một sản phẩm.",
            # KPIs demo
            "kpis": {
                "registered_developers": 120,
                "monthly_call_volume": 150_000,
                "error_rate": 0.004,  # 0.4%
            },
            # Business model canvas tóm tắt ngắn gọn
            "business_model": {
                "customer_segments": [
                    "Fintech startup",
                    "Trường đại học",
                    "App quản lý thư viện",
                ],
                "value_proposition": "Tích hợp thanh toán mượn sách nhanh, an toàn, có báo cáo.",
                "revenue_model": {
                    "type": "freemium + pay_per_call",
                    "free_tier": "10.000 calls/tháng",
                    "paid_tier": "0.001 USD/call sau khi vượt free",
                },
            },
            "developer_portal_url": "/portal",
        }
    )


@app.get("/portal")
def developer_portal():
    """Trang developer portal – dùng template HTML có giao diện."""
    return render_template("portal.html")


if __name__ == "__main__":
    app.run(debug=True, port=5013)



