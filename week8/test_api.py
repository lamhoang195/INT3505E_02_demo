"""
Unit Tests cho Library Management API
Test 5 endpoints chính của hệ thống
"""
import unittest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app import create_app


class TestLibraryAPI(unittest.TestCase):
    """Test suite cho Library Management API"""
    
    @classmethod
    def setUpClass(cls):
        """Khởi tạo test client một lần cho tất cả test cases"""
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.app.config['TESTING'] = True
        
        # Test data
        cls.test_book = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "978-1234567890",
            "quantity": 5
        }
        
        cls.test_user = {
            "username": "admin",
            "password": "admin123"
        }
        
    def setUp(self):
        """Chạy trước mỗi test case"""
        print(f"\n▶ Running: {self._testMethodName}")
        
    def tearDown(self):
        """Chạy sau mỗi test case"""
        print(f"✓ Completed: {self._testMethodName}")
    
    # Test 1: GET /api/v1/books - Lấy danh sách sách
    def test_01_get_books_list(self):
        """Test lấy danh sách tất cả sách"""
        print("  Testing GET /api/v1/books")
        
        response = self.client.get('/api/v1/books')
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 200, "Status code phải là 200")
        self.assertTrue(data['success'], "Response phải có success=True")
        self.assertIn('data', data, "Response phải có field 'data'")
        self.assertIsInstance(data['data'], list, "Data phải là list")
        
        # Kiểm tra structure của book nếu có data
        if len(data['data']) > 0:
            book = data['data'][0]
            self.assertIn('id', book, "Book phải có field 'id'")
            self.assertIn('title', book, "Book phải có field 'title'")
            self.assertIn('author', book, "Book phải có field 'author'")
            
        print(f"  ✓ Found {len(data['data'])} books")
        
    # Test 2: POST /api/v1/books - Tạo sách mới
    def test_02_create_book(self):
        """Test tạo sách mới"""
        print("  Testing POST /api/v1/books")
        
        response = self.client.post(
            '/api/v1/books',
            data=json.dumps(self.test_book),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 201, "Status code phải là 201")
        self.assertTrue(data['success'], "Response phải có success=True")
        self.assertIn('data', data, "Response phải có field 'data'")
        
        # Kiểm tra dữ liệu sách đã tạo
        book = data['data']
        self.assertEqual(book['title'], self.test_book['title'])
        self.assertEqual(book['author'], self.test_book['author'])
        self.assertIn('id', book, "Book phải có ID")
        
        print(f"  ✓ Created book with ID: {book['id']}")
        
    # Test 3: POST /api/v1/books - Validation error
    def test_03_create_book_validation_error(self):
        """Test tạo sách với dữ liệu không hợp lệ"""
        print("  Testing POST /api/v1/books (validation)")
        
        invalid_book = {"title": "Only Title"}  # Missing author
        
        response = self.client.post(
            '/api/v1/books',
            data=json.dumps(invalid_book),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 400, "Status code phải là 400")
        self.assertFalse(data['success'], "Response phải có success=False")
        self.assertIn('message', data, "Response phải có error message")
        
        print(f"  ✓ Validation working: {data['message']}")
        
    # Test 4: POST /api/v1/auth/login - Đăng nhập V1
    def test_04_login_v1_success(self):
        """Test đăng nhập thành công (V1)"""
        print("  Testing POST /api/v1/auth/login")
        
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(self.test_user),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 200, "Status code phải là 200")
        self.assertTrue(data['success'], "Response phải có success=True")
        self.assertIn('data', data, "Response phải có field 'data'")
        
        # Kiểm tra user data
        user = data['data']
        self.assertEqual(user['username'], self.test_user['username'])
        self.assertNotIn('password', user, "Password không được trả về")
        
        print(f"  ✓ Login successful for user: {user['username']}")
        
    # Test 5: POST /api/v1/auth/login - Login failed
    def test_05_login_v1_failed(self):
        """Test đăng nhập thất bại (V1)"""
        print("  Testing POST /api/v1/auth/login (wrong password)")
        
        wrong_credentials = {
            "username": "admin",
            "password": "wrongpassword"
        }
        
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(wrong_credentials),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 401, "Status code phải là 401")
        self.assertFalse(data['success'], "Response phải có success=False")
        
        print(f"  ✓ Invalid credentials rejected: {data['message']}")
        
    # Test 6: POST /api/v3/auth/login - Đăng nhập JWT (V3)
    def test_06_login_v3_jwt(self):
        """Test đăng nhập và nhận JWT token (V3)"""
        print("  Testing POST /api/v3/auth/login (JWT)")
        
        response = self.client.post(
            '/api/v3/auth/login',
            data=json.dumps(self.test_user),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 200, "Status code phải là 200")
        self.assertTrue(data['success'], "Response phải có success=True")
        self.assertIn('token', data, "Response phải có JWT token")
        self.assertIn('user', data, "Response phải có user data")
        self.assertEqual(data['token_type'], 'Bearer')
        
        # Lưu token để test khác sử dụng
        self.__class__.jwt_token = data['token']
        
        print(f"  ✓ JWT token received: {data['token'][:30]}...")
        
    # Test 7: GET /api/v3/auth/verify - Xác thực JWT token
    def test_07_verify_jwt_token(self):
        """Test xác thực JWT token"""
        print("  Testing GET /api/v3/auth/verify")
        
        # Đăng nhập trước để có token
        login_response = self.client.post(
            '/api/v3/auth/login',
            data=json.dumps(self.test_user),
            content_type='application/json'
        )
        login_data = json.loads(login_response.data)
        token = login_data['token']
        
        # Test verify với token hợp lệ
        response = self.client.get(
            '/api/v3/auth/verify',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 200, "Status code phải là 200")
        self.assertTrue(data['success'], "Response phải có success=True")
        self.assertIn('user', data, "Response phải có user data")
        self.assertIn('user_id', data['user'])
        
        print(f"  ✓ Token verified for user: {data['user']['username']}")
        
    # Test 8: GET /api/v3/auth/verify - Token không hợp lệ
    def test_08_verify_invalid_token(self):
        """Test xác thực với token không hợp lệ"""
        print("  Testing GET /api/v3/auth/verify (invalid token)")
        
        invalid_token = "invalid.jwt.token"
        
        response = self.client.get(
            '/api/v3/auth/verify',
            headers={'Authorization': f'Bearer {invalid_token}'}
        )
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 401, "Status code phải là 401")
        self.assertFalse(data['success'], "Response phải có success=False")
        self.assertIn('error', data)
        
        print(f"  ✓ Invalid token rejected: {data['error']['message']}")
        
    # Test 9: GET /api/v3/auth/verify - Missing token
    def test_09_verify_missing_token(self):
        """Test xác thực khi thiếu token"""
        print("  Testing GET /api/v3/auth/verify (no token)")
        
        response = self.client.get('/api/v3/auth/verify')
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 401, "Status code phải là 401")
        self.assertFalse(data['success'], "Response phải có success=False")
        
        print(f"  ✓ Request without token rejected: {data['error']['message']}")


def run_tests():
    """Chạy tất cả test cases"""
    print("=" * 70)
    print("Library Management API - Unit Tests")
    print("=" * 70)
    
    # Tạo test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLibraryAPI)
    
    # Chạy tests với verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
