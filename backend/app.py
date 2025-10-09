"""
Main Flask Application
Registers all API versions
"""
from flask import Flask, render_template
from flask_cors import CORS
from flasgger import Swagger

# Import V1 API blueprints
from backend.api.v1.books import books_v1
from backend.api.v1.users import users_v1
from backend.api.v1.borrows import borrows_v1

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
        """User dashboard"""
        return render_template('dashboard.html')
    
    @app.route('/admin')
    def admin():
        """Admin dashboard"""
        return render_template('admin.html')
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        """API information"""
        return {
            'name': 'Library Management System API',
            'description': 'RESTful API demonstrating REST architectural constraints',
            'version': 'v1',
            'status': 'active',
            'description_detail': 'Client-Server architecture',
            'base_url': '/api/v1',
            'constraints': ['Client-Server'],
            'endpoints': {
                'books': '/api/v1/books',
                'users': '/api/v1/users',
                'borrows': '/api/v1/borrows',
                'auth': '/api/v1/auth/login'
            },
            '_links': {
                'self': {'href': '/api'},
                'documentation': {'href': '/api/docs'},
                'openapi-spec': {'href': '/apispec.json'}
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

