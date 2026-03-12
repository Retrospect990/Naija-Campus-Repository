"""
Campus Pinduoduo: Online Store REST API
API endpoints for product browsing, cart management, and order placement
Integrates with Flask backend
"""

from flask import Flask, jsonify, request
from datetime import datetime
import json
from store_system import OnlineStore, ProductCategory, OrderStatus

app = Flask(__name__)
app.json.sort_keys = False

# Initialize store
store = OnlineStore()

# ============================================================================
# STORE BROWSING ENDPOINTS
# ============================================================================

@app.route('/api/store/products', methods=['GET'])
def get_all_products():
    """Get all products with optional filtering"""
    
    category = request.args.get('category')
    search = request.args.get('search')
    brand = request.args.get('brand')
    
    if category:
        try:
            cat = ProductCategory[category.upper()]
            products = store.get_products_by_category(cat)
        except KeyError:
            return jsonify({'error': f'Unknown category: {category}'}), 400
    elif search:
        products = store.get_products_by_name(search)
    elif brand:
        products = store.get_products_by_brand(brand)
    else:
        products = store.get_all_products()
    
    return jsonify({
        'status': 'success',
        'count': len(products),
        'products': [
            {
                'id': p.id,
                'name': p.name,
                'brand': p.brand,
                'category': p.category.value,
                'price': p.price,
                'description': p.description,
                'available': p.quantity_available,
                'unit': p.unit,
                'rating': p.ratings,
                'reviews': p.reviews_count,
                'supplier': p.supplier
            }
            for p in products
        ]
    }), 200

@app.route('/api/store/products/<product_id>', methods=['GET'])
def get_product_details(product_id):
    """Get detailed product information"""
    
    product = store.get_product(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify({
        'status': 'success',
        'product': {
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'category': product.category.value,
            'price': product.price,
            'description': product.description,
            'available': product.quantity_available,
            'unit': product.unit,
            'rating': product.ratings,
            'reviews': product.reviews_count,
            'supplier': product.supplier,
            'image_url': product.image_url
        }
    }), 200

@app.route('/api/store/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    
    categories = [
        {
            'name': cat.value,
            'display_name': cat.name.replace('_', ' ').title(),
            'count': len(store.get_products_by_category(cat))
        }
        for cat in ProductCategory
    ]
    
    return jsonify({
        'status': 'success',
        'categories': categories
    }), 200

@app.route('/api/store/brands', methods=['GET'])
def get_brands():
    """Get all available brands"""
    
    brands = list(set(p.brand for p in store.get_all_products()))
    brands.sort()
    
    return jsonify({
        'status': 'success',
        'brands': brands,
        'count': len(brands)
    }), 200

@app.route('/api/store/search', methods=['GET'])
def search_products():
    """Search products by query"""
    
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'error': 'Search query too short'}), 400
    
    results = store.get_products_by_name(query)
    
    return jsonify({
        'status': 'success',
        'query': query,
        'results': len(results),
        'products': [
            {
                'id': p.id,
                'name': p.name,
                'brand': p.brand,
                'price': p.price,
                'available': p.quantity_available
            }
            for p in results
        ]
    }), 200

# ============================================================================
# SHOPPING CART ENDPOINTS
# ============================================================================

@app.route('/api/cart/create', methods=['POST'])
def create_cart():
    """Create a new shopping cart for moderator"""
    
    data = request.get_json()
    moderator_id = data.get('moderator_id')
    pool_id = data.get('pool_id')
    pool_budget = data.get('pool_budget', 0)
    
    if not moderator_id or not pool_id or pool_budget <= 0:
        return jsonify({'error': 'Missing required fields'}), 400
    
    cart = store.create_cart(moderator_id, pool_id, pool_budget)
    
    return jsonify({
        'status': 'success',
        'message': 'Cart created',
        'cart': {
            'id': cart.cart_id,
            'moderator_id': cart.moderator_id,
            'pool_id': cart.pool_id,
            'budget': cart.pool_budget,
            'items_count': 0,
            'total': 0.0,
            'remaining': cart.pool_budget,
            'utilization_percent': 0.0
        }
    }), 201

@app.route('/api/cart/<cart_id>', methods=['GET'])
def get_cart(cart_id):
    """Get cart details"""
    
    cart = store.get_cart(cart_id)
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    return jsonify({
        'status': 'success',
        'cart': {
            'id': cart.cart_id,
            'moderator_id': cart.moderator_id,
            'pool_id': cart.pool_id,
            'budget': cart.pool_budget,
            'items_count': len(cart.items),
            'items': [
                {
                    'product_id': item.product.id,
                    'name': f"{item.product.brand} {item.product.name}",
                    'quantity': item.quantity,
                    'unit': item.product.unit,
                    'price': item.product.price,
                    'subtotal': item.get_subtotal()
                }
                for item in cart.items
            ],
            'total': cart.get_total(),
            'remaining': cart.get_remaining_budget(),
            'utilization_percent': round(cart.get_budget_utilization_percent(), 2)
        }
    }), 200

@app.route('/api/cart/<cart_id>/add', methods=['POST'])
def add_to_cart(cart_id):
    """Add product to cart"""
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id or quantity <= 0:
        return jsonify({'error': 'Invalid product or quantity'}), 400
    
    success, message = store.add_to_cart(cart_id, product_id, quantity)
    
    if success:
        cart = store.get_cart(cart_id)
        return jsonify({
            'status': 'success',
            'message': message,
            'cart_total': cart.get_total(),
            'remaining_budget': cart.get_remaining_budget()
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': message
        }), 400

@app.route('/api/cart/<cart_id>/remove/<product_id>', methods=['DELETE'])
def remove_from_cart(cart_id, product_id):
    """Remove product from cart"""
    
    success, message = store.remove_from_cart(cart_id, product_id)
    
    if success:
        cart = store.get_cart(cart_id)
        return jsonify({
            'status': 'success',
            'message': message,
            'cart_total': cart.get_total(),
            'items_count': len(cart.items)
        }), 200
    else:
        return jsonify({'error': message}), 404

@app.route('/api/cart/<cart_id>/update/<product_id>', methods=['PUT'])
def update_cart_item(cart_id, product_id):
    """Update quantity of item in cart"""
    
    data = request.get_json()
    new_quantity = data.get('quantity', 1)
    
    if new_quantity < 0:
        return jsonify({'error': 'Invalid quantity'}), 400
    
    success, message = store.update_cart_item(cart_id, product_id, new_quantity)
    
    if success:
        cart = store.get_cart(cart_id)
        return jsonify({
            'status': 'success',
            'message': message,
            'cart_total': cart.get_total(),
            'remaining_budget': cart.get_remaining_budget()
        }), 200
    else:
        return jsonify({'error': message}), 400

@app.route('/api/cart/<cart_id>/clear', methods=['POST'])
def clear_cart(cart_id):
    """Clear all items from cart"""
    
    cart = store.get_cart(cart_id)
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    cart.clear()
    
    return jsonify({
        'status': 'success',
        'message': 'Cart cleared',
        'cart_total': 0.0
    }), 200

# ============================================================================
# ORDER PLACEMENT & MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/orders/place', methods=['POST'])
def place_order():
    """Place order from cart"""
    
    data = request.get_json()
    cart_id = data.get('cart_id')
    notes = data.get('notes', '')
    
    if not cart_id:
        return jsonify({'error': 'Cart ID required'}), 400
    
    success, order = store.place_order(cart_id, notes)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Order placed successfully',
            'order': {
                'order_id': order.order_id,
                'moderator_id': order.moderator_id,
                'pool_id': order.pool_id,
                'status': order.status.value,
                'items_count': len(order.items),
                'total': order.total_amount,
                'created_at': order.created_at.isoformat(),
                'confirmed_at': order.confirmed_at.isoformat() if order.confirmed_at else None
            }
        }), 201
    else:
        return jsonify({'error': 'Failed to place order'}), 400

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    
    order = store.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify({
        'status': 'success',
        'order': {
            'order_id': order.order_id,
            'moderator_id': order.moderator_id,
            'pool_id': order.pool_id,
            'status': order.status.value,
            'items': order.items,
            'total': order.total_amount,
            'notes': order.notes,
            'created_at': order.created_at.isoformat(),
            'confirmed_at': order.confirmed_at.isoformat() if order.confirmed_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None
        }
    }), 200

@app.route('/api/orders/moderator/<moderator_id>', methods=['GET'])
def get_moderator_orders(moderator_id):
    """Get all orders for a moderator"""
    
    orders = store.get_moderator_orders(moderator_id)
    
    return jsonify({
        'status': 'success',
        'moderator_id': moderator_id,
        'orders_count': len(orders),
        'orders': [
            {
                'order_id': o.order_id,
                'pool_id': o.pool_id,
                'status': o.status.value,
                'items_count': len(o.items),
                'total': o.total_amount,
                'created_at': o.created_at.isoformat()
            }
            for o in orders
        ]
    }), 200

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status (admin only)"""
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Status required'}), 400
    
    try:
        status = OrderStatus[new_status.upper()]
    except KeyError:
        return jsonify({'error': f'Invalid status: {new_status}'}), 400
    
    if store.update_order_status(order_id, status):
        order = store.get_order(order_id)
        return jsonify({
            'status': 'success',
            'message': f'Order status updated to {new_status}',
            'order_status': order.status.value
        }), 200
    else:
        return jsonify({'error': 'Order not found'}), 404

# ============================================================================
# ANALYTICS & STATISTICS ENDPOINTS
# ============================================================================

@app.route('/api/store/stats', methods=['GET'])
def get_store_stats():
    """Get store statistics"""
    
    stats = store.get_store_stats()
    
    return jsonify({
        'status': 'success',
        'statistics': {
            'total_products': stats['total_products'],
            'total_orders': stats['total_orders'],
            'total_sales': stats['total_sales'],
            'active_carts': stats['active_carts'],
            'stock_value': stats['stock_value'],
            'categories': stats['categories']
        }
    }), 200

@app.route('/api/store/inventory', methods=['GET'])
def get_inventory():
    """Get inventory status"""
    
    products = store.get_all_products()
    low_stock = [p for p in products if p.quantity_available < 5]
    
    return jsonify({
        'status': 'success',
        'total_items': len(products),
        'low_stock_count': len(low_stock),
        'low_stock_items': [
            {
                'id': p.id,
                'name': f"{p.brand} {p.name}",
                'available': p.quantity_available,
                'alert': f'Only {p.quantity_available} {p.unit} left'
            }
            for p in low_stock
        ]
    }), 200

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/store/health', methods=['GET'])
def store_health():
    """Store API health check"""
    
    return jsonify({
        'status': 'running',
        'service': 'Campus Pinduoduo - Online Store API',
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n🏪 Starting Campus Pinduoduo Online Store API...")
    print("📍 Available at http://localhost:5000/api/store")
    print("📚 Documentation: See store_api_rest.py\n")
    app.run(debug=True, port=5000)
