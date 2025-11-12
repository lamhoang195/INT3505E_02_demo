"""
Script test đơn giản cho API thanh toán V1 và V2
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def print_response(title, response):
    """In response đẹp"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_v1_api():
    """Test API V1"""
    print("\n" + "="*60)
    print("TEST API V1 - Thanh toán đơn giản")
    print("="*60)
    
    # Test tạo thanh toán V1
    data = {
        "borrow_id": "1",
        "user_id": "1",
        "amount": 140000,
        "payment_method": "cash"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/payments", json=data)
    print_response("1. Tạo thanh toán V1", response)
    
    if response.status_code == 201:
        payment_id = response.json()['data']['id']
        
        # Test lấy thông tin thanh toán
        response = requests.get(f"{BASE_URL}/api/v1/payments/{payment_id}")
        print_response("2. Lấy thông tin thanh toán V1", response)

def test_v2_api():
    """Test API V2"""
    print("\n" + "="*60)
    print("TEST API V2 - Thanh toán nâng cao")
    print("="*60)
    
    # Test tính phí
    data = {
        "borrow_days": 14,
        "late_days": 0
    }
    response = requests.post(f"{BASE_URL}/api/v2/payments/calculate", json=data)
    print_response("1. Tính phí mượn sách", response)
    
    # Test tạo giao dịch thanh toán V2
    data = {
        "borrow_id": "2",
        "user_id": "1",
        "borrow_days": 14,
        "late_days": 0,
        "payment_method": "card",
        "installments": 1
    }
    response = requests.post(f"{BASE_URL}/api/v2/payments", json=data)
    print_response("2. Tạo giao dịch thanh toán V2", response)
    
    if response.status_code == 201:
        payment_id = response.json()['data']['id']
        
        # Test lấy thông tin
        response = requests.get(f"{BASE_URL}/api/v2/payments/{payment_id}")
        print_response("3. Lấy thông tin thanh toán V2", response)
        
        # Test hoàn tất thanh toán
        response = requests.post(f"{BASE_URL}/api/v2/payments/{payment_id}/complete")
        print_response("4. Hoàn tất thanh toán", response)
    
    # Test tính phí với trễ
    data = {
        "borrow_days": 14,
        "late_days": 3
    }
    response = requests.post(f"{BASE_URL}/api/v2/payments/calculate", json=data)
    print_response("5. Tính phí với trễ 3 ngày", response)

def test_api_info():
    """Test API info"""
    response = requests.get(f"{BASE_URL}/api")
    print_response("Thông tin API", response)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DEMO API THANH TOÁN MƯỢN SÁCH V1 & V2")
    print("="*60)
    
    try:
        # Test API info
        test_api_info()
        
        # Test V1
        test_v1_api()
        
        # Test V2
        test_v2_api()
        
        print("\n" + "="*60)
        print("TEST HOÀN TẤT!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Lỗi: Không thể kết nối đến server!")
        print("Hãy chạy: python app.py")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")

