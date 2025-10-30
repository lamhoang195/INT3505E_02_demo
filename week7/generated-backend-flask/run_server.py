#!/usr/bin/env python3
"""Simple script to run the OpenAPI server"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from openapi_server.__main__ import main
    print("Starting server on http://localhost:5001")
    print("API endpoint: http://localhost:5001/api/v1/books")
    main()
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()

