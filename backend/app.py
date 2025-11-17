"""
Main Flask Application
Registers all API versions
"""
import logging
import os
import time
from logging.config import dictConfig

from flask import Flask, render_template, request, Response
from flask_cors import CORS
from flasgger import Swagger
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

# Import V1 API blueprints
from backend.api.v1.books import books_v1
from backend.api.v1.users import users_v1
from backend.api.v1.borrows import borrows_v1

# Import V2 API blueprints
from backend.api.v2.books import books_v2

# Import V3 API blueprints
from backend.api.v3.auth import auth_v3

# Import V4 API blueprints
from backend.api.v4.books_cache_control import books_v4_cache
from backend.api.v4.books_etag import books_v4_etag

# Import V5 API blueprints
from backend.api.v5.auth_storage import auth_storage_v5

# Import V6 API blueprints
from backend.api.v6.borrows import borrows_v6


def _configure_logging():
    """Configure application-wide logging."""
    log_level = os.getenv('APP_LOG_LEVEL', 'INFO')
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': log_level
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'level': log_level,
                'filename': os.path.join(log_dir, 'app.log'),
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 3,
                'encoding': 'utf-8'
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console', 'file']
        }
    })


_configure_logging()
logger = logging.getLogger(__name__)

# Prometheus metrics for V1 API
REQUEST_COUNT = Counter(
    'v1_api_requests_total',
    'Total number of requests to V1 API endpoints',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'v1_api_request_duration_seconds',
    'Latency of V1 API endpoints in seconds',
    ['method', 'endpoint']
)


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Enable CORS for API requests
    CORS(app)
    
    # Configure app
    app.config['JSON_AS_ASCII'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Configure Swagger/OpenAPI
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Library Management System API",
            "description": "RESTful API cho hệ thống quản lý sách với kiến trúc phân tầng theo nguyên tắc REST",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "url": "http://localhost:5000"
            }
        },
        "host": "localhost:5000",
        "basePath": "/",
        "schemes": ["http"],
        "tags": [
            {
                "name": "V1 - Books",
                "description": "API V1 - Quản lý sách (Client-Server)"
            },
            {
                "name": "V1 - Users",
                "description": "API V1 - Quản lý người dùng (Client-Server)"
            },
            {
                "name": "V1 - Authentication",
                "description": "API V1 - Xác thực người dùng (Client-Server)"
            },
            {
                "name": "V1 - Borrows",
                "description": "API V1 - Quản lý mượn trả sách (Client-Server)"
            },
            {
                "name": "V2 - Books (Uniform Interface)",
                "description": "API V2 - Quản lý sách với HATEOAS"
            },
            {
                "name": "V3 - Authentication (Stateless JWT)",
                "description": "API V3 - Xác thực với JWT (Stateless)"
            },
            {
                "name": "V4 - Books (Cache-Control)",
                "description": "API V4 - Quản lý sách với Cache-Control headers"
            },
            {
                "name": "V4 - Books (ETag)",
                "description": "API V4 - Quản lý sách với ETag headers"
            },
            {
                "name": "V5 - Auth Storage Demo",
                "description": "API V5 - Demo các phương pháp lưu trữ token (localStorage, sessionStorage, HTTP-Only Cookie)"
            },
            {
                "name": "V6 - Borrows with Donation (Deprecated)",
                "description": "API V6 - Mượn sách với chức năng donate tiền cho thư viện (Deprecated - sẽ ngừng hỗ trợ sau 31/12/2025)"
            }
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header. Example: 'Bearer {token}'"
            }
        }
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # Register V1 API blueprints
    app.register_blueprint(books_v1)
    app.register_blueprint(users_v1)
    app.register_blueprint(borrows_v1)
    
    # Register V2 API blueprints
    app.register_blueprint(books_v2)
    
    # Register V3 API blueprints
    app.register_blueprint(auth_v3)
    
    # Register V4 API blueprints
    app.register_blueprint(books_v4_cache)
    app.register_blueprint(books_v4_etag)
    
    # Register V5 API blueprints
    app.register_blueprint(auth_storage_v5)
    
    # Register V6 API blueprints
    app.register_blueprint(borrows_v6)
    
    logger.info("Flask application configured with logging and Prometheus metrics.")

    @app.before_request
    def start_timer():
        """Record start time for V1 API requests."""
        if request.path.startswith('/api/v1'):
            request._v1_request_start_time = time.perf_counter()

    @app.after_request
    def record_metrics(response):
        """Record metrics for V1 API requests."""
        if request.path.startswith('/api/v1'):
            endpoint = request.endpoint or 'unknown'
            method = request.method
            status_code = response.status_code

            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            start_time = getattr(request, '_v1_request_start_time', None)
            if start_time is not None:
                duration = time.perf_counter() - start_time
                REQUEST_LATENCY.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

        return response

    @app.route('/metrics')
    def metrics():
        """Expose Prometheus metrics."""
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    # Frontend routes
    @app.route('/')
    def index():
        """Home page"""
        return render_template('index.html')
    
    @app.route('/login')
    def login_page():
        """Login page"""
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        """Register page"""
        return render_template('register.html')
    
    @app.route('/dashboard')
    def dashboard():
        """User dashboard V1"""
        return render_template('dashboard.html')
    
    @app.route('/dashboard_v2')
    def dashboard_v2():
        """User dashboard V2 - demonstrates HATEOAS"""
        return render_template('dashboard_v2.html')
    
    @app.route('/admin')
    def admin():
        """Admin dashboard"""
        return render_template('admin.html')
    
    @app.route('/auth-storage-demo')
    def auth_storage_demo():
        """V5 Authentication Storage Demo"""
        return render_template('auth_storage_demo.html')
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        """API information"""
        info = {
            'name': 'Library Management System API',
            'description': 'RESTful API demonstrating REST architectural constraints',
            'versions': {
                'v1': {
                    'status': 'active',
                    'description': 'Client-Server architecture',
                    'base_url': '/api/v1',
                    'constraints': ['Client-Server'],
                    'endpoints': {
                        'books': '/api/v1/books',
                        'users': '/api/v1/users',
                        'borrows': '/api/v1/borrows',
                        'auth': '/api/v1/auth/login'
                    }
                },
                'v2': {
                    'status': 'active',
                    'description': 'Uniform Interface with HATEOAS',
                    'base_url': '/api/v2',
                    'constraints': ['Client-Server', 'Uniform Interface'],
                    'features': ['HATEOAS', 'Self-descriptive messages', 'Standard HTTP methods'],
                    'note': 'V2 only implements Books API with HATEOAS. Other resources use V1.',
                    'endpoints': {
                        'books': '/api/v2/books (with HATEOAS)',
                        'users': '/api/v1/users (uses V1)',
                        'borrows': '/api/v1/borrows (uses V1)',
                        'auth': '/api/v1/auth/login (uses V1)'
                    }
                },
                'v3': {
                    'status': 'active',
                    'description': 'Stateless with JWT Authentication',
                    'base_url': '/api/v3',
                    'constraints': ['Client-Server', 'Stateless'],
                    'features': ['JWT Authentication', 'Stateless - no server session', 'Bearer token', 'Token verification'],
                    'note': 'V3 only implements JWT Auth. Books/Users/Borrows use V1 API with JWT protection.',
                    'endpoints': {
                        'login': '/api/v3/auth/login (get JWT token)',
                        'verify': '/api/v3/auth/verify (verify token)',
                        'decode': '/api/v3/auth/decode (decode token)',
                        'protected': '/api/v3/auth/protected (test protected route)',
                        'refresh': '/api/v3/auth/refresh (refresh token)',
                        'books': '/api/v1/books (uses V1)',
                        'users': '/api/v1/users (uses V1)',
                        'borrows': '/api/v1/borrows (uses V1)'
                    }
                },
                'v4': {
                    'status': 'active',
                    'description': 'Cacheable with Cache-Control and ETag',
                    'base_url': '/api/v4',
                    'constraints': ['Client-Server', 'Cacheable'],
                    'features': [
                        'Cache-Control headers (max-age, no-cache, must-revalidate)',
                        'ETag headers (Strong and Weak)',
                        'Conditional requests (If-None-Match, If-Match)',
                        'Last-Modified header',
                        'Optimistic locking with ETags'
                    ],
                    'note': 'V4 có 2 implementations: Cache-Control và ETag cho Books API. Other resources use V1.',
                    'endpoints': {
                        'cache-control-info': '/api/v4/cache-control',
                        'cache-control-books': '/api/v4/cache-control/books (Cache-Control)',
                        'etag-info': '/api/v4/etag',
                        'etag-books': '/api/v4/etag/books (ETag)',
                        'users': '/api/v1/users (uses V1)',
                        'borrows': '/api/v1/borrows (uses V1)',
                        'auth': '/api/v3/auth/login (uses V3)'
                    }
                },
                'v5': {
                    'status': 'active',
                    'description': 'Authentication Storage Methods Demo',
                    'base_url': '/api/v5',
                    'features': [
                        'localStorage - Persistent client storage',
                        'sessionStorage - Session-only client storage',
                        'HTTP-Only Cookie - Secure server-managed cookie',
                        'Token storage comparison',
                        'Security considerations'
                    ],
                    'note': 'V5 demonstrates different ways to store authentication tokens on the client side.',
                    'endpoints': {
                        'info': '/api/v5',
                        'login-localstorage': '/api/v5/auth/login/localstorage',
                        'login-sessionstorage': '/api/v5/auth/login/sessionstorage',
                        'login-cookie': '/api/v5/auth/login/cookie',
                        'verify': '/api/v5/auth/verify',
                        'logout': '/api/v5/auth/logout',
                        'protected': '/api/v5/auth/protected',
                        'compare': '/api/v5/auth/compare'
                    }
                },
                'v6': {
                    'status': 'deprecated',
                    'sunset_date': '2025-12-31',
                    'description': 'Borrow with Donation Feature (Deprecated)',
                    'base_url': '/api/v6',
                    'features': [
                        'Borrow books with optional donation',
                        'Donate money to library when borrowing',
                        'Track donations',
                        'View donation history'
                    ],
                    'note': 'V6 sẽ ngừng hoạt động sau 31/12/2025. Không phát triển tính năng mới trên phiên bản này.',
                    'deprecation_notice': 'Vui lòng chuẩn bị migrate các workflow sử dụng V6 sang phiên bản mới hơn khi có thông báo chính thức.',
                    'endpoints': {
                        'info': '/api/v6',
                        'borrows': '/api/v6/borrows (POST - borrow with donation)',
                        'donations': '/api/v6/donations (GET - list donations)'
                    }
                }
            },
            '_links': {
                'self': {'href': '/api'},
                'v1': {'href': '/api/v1'},
                'v2': {'href': '/api/v2'},
                'v3': {'href': '/api/v3'},
                'v4-cache-control': {'href': '/api/v4/cache-control'},
                'v4-etag': {'href': '/api/v4/etag'},
                'v5': {'href': '/api/v5'},
                'v6': {'href': '/api/v6'},
                'documentation': {'href': '/api/docs'},
                'openapi-spec': {'href': '/apispec.json'}
            }
        }
        logger.info("API info requested")
        return info
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

