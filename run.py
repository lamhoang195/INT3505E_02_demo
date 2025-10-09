"""
Main entry point for the application
Run this file to start the Flask server
"""
from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("Library Management System - RESTful API")
    print("=" * 60)
    print("API Version: V1 - Client-Server Architecture")
    print("=" * 60)
    print("\nURLs:")
    print("  Frontend:       http://localhost:5000")
    print("  API:            http://localhost:5000/api/v1")
    print("  API Info:       http://localhost:5000/api")
    print("  Swagger UI:     http://localhost:5000/api/docs")
    print("  OpenAPI Spec:   http://localhost:5000/apispec.json")
    print("=" * 60)
    print("\nDefault admin account:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 60)
    print("\nTips:")
    print("  - Use Swagger UI to explore and test APIs")
    print("  - All endpoints are documented with examples")
    print("  - You can export OpenAPI spec to Postman")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

