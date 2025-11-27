"""
Simple Flask API for Product CRUD operations
"""
from flask import Flask, jsonify, request
from datetime import datetime
import json
import os

app = Flask(__name__)

# Path to data file
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'products.json')


def load_products():
    """Load products from JSON file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_products(products):
    """Save products to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)


def get_next_id(products):
    """Get next available ID"""
    if not products:
        return 1
    return max(p['id'] for p in products) + 1


@app.route('/api/v1/products', methods=['GET'])
def get_products():
    """Get all products with optional filters"""
    products = load_products()
    
    # Apply filters
    name = request.args.get('name')
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    if name:
        products = [p for p in products if name.lower() in p['name'].lower()]
    
    if category:
        products = [p for p in products if p['category'].lower() == category.lower()]
    
    if min_price is not None:
        products = [p for p in products if p['price'] >= min_price]
    
    if max_price is not None:
        products = [p for p in products if p['price'] <= max_price]
    
    return jsonify({
        'success': True,
        'data': products,
        'count': len(products)
    }), 200


@app.route('/api/v1/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """Get a single product by ID"""
    products = load_products()
    
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({
            'success': False,
            'error': f'Product with ID {product_id} not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': product
    }), 200


@app.route('/api/v1/products', methods=['POST'])
def create_product():
    """Create a new product"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'price', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'error': f'Missing required field: {field}'
            }), 400
    
    # Validate price
    try:
        price = float(data['price'])
        if price < 0:
            return jsonify({
                'success': False,
                'error': 'Price must be non-negative'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'error': 'Invalid price value'
        }), 400
    
    products = load_products()
    
    # Create new product
    new_product = {
        'id': get_next_id(products),
        'name': data['name'],
        'description': data.get('description', ''),
        'price': price,
        'category': data['category'],
        'stock': data.get('stock', 0),
        'created_at': datetime.now().isoformat()
    }
    
    products.append(new_product)
    save_products(products)
    
    return jsonify({
        'success': True,
        'message': 'Product created successfully',
        'data': new_product
    }), 201


@app.route('/api/v1/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'price', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'error': f'Missing required field: {field}'
            }), 400
    
    # Validate price
    try:
        price = float(data['price'])
        if price < 0:
            return jsonify({
                'success': False,
                'error': 'Price must be non-negative'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'error': 'Invalid price value'
        }), 400
    
    products = load_products()
    
    # Find product
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({
            'success': False,
            'error': f'Product with ID {product_id} not found'
        }), 404
    
    # Update product
    product['name'] = data['name']
    product['description'] = data.get('description', product.get('description', ''))
    product['price'] = price
    product['category'] = data['category']
    product['stock'] = data.get('stock', product.get('stock', 0))
    product['updated_at'] = datetime.now().isoformat()
    
    save_products(products)
    
    return jsonify({
        'success': True,
        'message': 'Product updated successfully',
        'data': product
    }), 200


@app.route('/api/v1/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    products = load_products()
    
    # Find product
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({
            'success': False,
            'error': f'Product with ID {product_id} not found'
        }), 404
    
    # Remove product
    products = [p for p in products if p['id'] != product_id]
    save_products(products)
    
    return jsonify({
        'success': True,
        'message': 'Product deleted successfully'
    }), 200


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Product API is running',
        'version': '1.0.0'
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)














