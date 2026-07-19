"""
Crypto Payment API Server
A lightweight Flask backend for the crypto payment system
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import uuid
import json
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__, static_folder='.')
CORS(app)

# In-memory storage (replace with database in production)
orders_db = {}
payments_db = {}
products_db = {
    "prod_1": {"id": "prod_1", "name": "Premium AI Agent", "price": 99.99, "type": "digital"},
    "prod_2": {"id": "prod_2", "name": "Enterprise Solution", "price": 199.99, "type": "digital"},
    "prod_3": {"id": "prod_3", "name": "Starter Package", "price": 49.99, "type": "digital"},
}
wallets_db = {
    "TRC20": {"address": "TLa2D6vLBEi67CYRLdHpMrocsWmpdHEfPZ", "currency": "USDT", "network": "TRC20"},
    "ERC20": {"address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F", "currency": "USDT", "network": "ERC20"},
    "BEP20": {"address": "0x8Ba1f109551bD432803012645Hac136E8761fCE8", "currency": "USDT", "network": "BEP20"},
    "BTC": {"address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", "currency": "BTC", "network": "BTC"},
    "ETH": {"address": "0xdF3e18d64BC6A983f67334d0eB050617777CdC77", "currency": "ETH", "network": "ERC20"},
}

# Statistics
stats = {
    "today_revenue": 0.0,
    "month_revenue": 0.0,
    "pending_orders": 0,
    "completed_orders": 0,
    "total_orders": 0,
    "currency_breakdown": defaultdict(float),
}

def generate_order_number():
    date = datetime.now().strftime("%Y%m%d")
    return f"ORD-{date}-{str(uuid.uuid4())[:6].upper()}"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# ============ PUBLIC API ============

@app.route('/api/v1/products', methods=['GET'])
def list_products():
    return jsonify({
        "success": True,
        "data": list(products_db.values())
    })

@app.route('/api/v1/products/<product_id>', methods=['GET'])
def get_product(product_id):
    if product_id not in products_db:
        return jsonify({"success": False, "error": "Product not found"}), 404
    
    return jsonify({
        "success": True,
        "data": products_db[product_id]
    })

@app.route('/api/v1/currencies', methods=['GET'])
def get_currencies():
    return jsonify({
        "success": True,
        "data": [
            {"currency": "USDT", "networks": [
                {"network": "TRC20", "label": "TRON (TRC20)", "confirmations": 19},
                {"network": "ERC20", "label": "Ethereum (ERC20)", "confirmations": 12},
                {"network": "BEP20", "label": "Binance (BEP20)", "confirmations": 1},
            ]},
            {"currency": "BTC", "networks": [
                {"network": "BTC", "label": "Bitcoin", "confirmations": 3},
            ]},
            {"currency": "ETH", "networks": [
                {"network": "ERC20", "label": "Ethereum (ERC20)", "confirmations": 12},
            ]},
        ]
    })

@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    
    # Validate required fields
    required = ['product_id', 'name', 'email', 'crypto_currency', 'network']
    for field in required:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing field: {field}"}), 400
    
    # Validate product
    product_id = data['product_id']
    if product_id not in products_db:
        return jsonify({"success": False, "error": "Product not found"}), 404
    
    product = products_db[product_id]
    quantity = data.get('quantity', 1)
    network = data['network']
    
    # Get wallet
    if network not in wallets_db:
        return jsonify({"success": False, "error": "Unsupported network"}), 400
    
    wallet = wallets_db[network]
    
    # Calculate crypto amount (simplified - use real exchange rates in production)
    price_usd = product['price'] * quantity
    rates = {"USDT": 1.0, "BTC": 0.000033, "ETH": 0.0005}
    rate = rates.get(data['crypto_currency'], 1.0)
    crypto_amount = round(price_usd * rate, 8)
    
    # Create order
    order_id = str(uuid.uuid4())
    order_number = generate_order_number()
    expires_at = datetime.now() + timedelta(hours=2)
    
    order = {
        "id": order_id,
        "order_number": order_number,
        "product_id": product_id,
        "product_name": product['name'],
        "customer_name": data['name'],
        "customer_email": data['email'],
        "country": data.get('country', 'Unknown'),
        "quantity": quantity,
        "price_usd": price_usd,
        "crypto_amount": crypto_amount,
        "crypto_currency": data['crypto_currency'],
        "network": network,
        "wallet_address": wallet['address'],
        "status": "pending",
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now().isoformat(),
        "paid_at": None,
        "confirmed_at": None,
        "delivered_at": None,
    }
    
    orders_db[order_id] = order
    stats['total_orders'] += 1
    stats['pending_orders'] += 1
    
    return jsonify({
        "success": True,
        "data": {
            "order_id": order_id,
            "order_number": order_number,
            "status": "pending",
            "crypto_amount": str(crypto_amount),
            "crypto_currency": data['crypto_currency'],
            "network": network,
            "wallet_address": wallet['address'],
            "expires_at": expires_at.isoformat(),
            "checkout_url": f"/#/checkout/{order_number}",
        }
    }), 201

@app.route('/api/v1/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders_db.get(order_id)
    if not order:
        # Try order number
        for o in orders_db.values():
            if o['order_number'] == order_id:
                order = o
                break
    
    if not order:
        return jsonify({"success": False, "error": "Order not found"}), 404
    
    return jsonify({
        "success": True,
        "data": order
    })

@app.route('/api/v1/orders/<order_id>/status', methods=['GET'])
def get_order_status(order_id):
    order = orders_db.get(order_id)
    if not order:
        for o in orders_db.values():
            if o['order_number'] == order_id:
                order = o
                break
    
    if not order:
        return jsonify({"success": False, "error": "Order not found"}), 404
    
    # Check expiry
    expires_at = datetime.fromisoformat(order['expires_at'])
    is_expired = datetime.now() > expires_at
    
    return jsonify({
        "success": True,
        "data": {
            "order_number": order['order_number'],
            "status": "expired" if is_expired else order['status'],
            "crypto_amount": str(order['crypto_amount']),
            "crypto_currency": order['crypto_currency'],
            "network": order['network'],
            "wallet_address": order['wallet_address'],
            "is_expired": is_expired,
            "expires_at": order['expires_at'],
            "created_at": order['created_at'],
        }
    })

@app.route('/api/v1/payments/verify', methods=['POST'])
def verify_payment():
    data = request.get_json()
    
    required = ['tx_hash', 'network', 'order_id']
    for field in required:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing field: {field}"}), 400
    
    order = orders_db.get(data['order_id'])
    if not order:
        for o in orders_db.values():
            if o['order_number'] == data['order_id']:
                order = o
                break
    
    if not order:
        return jsonify({"success": False, "error": "Order not found"}), 404
    
    # Create payment record (simulate verification)
    payment_id = str(uuid.uuid4())
    payment = {
        "id": payment_id,
        "order_id": order['id'],
        "tx_hash": data['tx_hash'],
        "amount": data.get('amount', order['crypto_amount']),
        "currency": order['crypto_currency'],
        "network": order['network'],
        "status": "confirmed",
        "confirmations": 20,
        "created_at": datetime.now().isoformat(),
    }
    
    payments_db[payment_id] = payment
    
    # Update order
    order['status'] = 'confirmed'
    order['paid_at'] = datetime.now().isoformat()
    order['confirmed_at'] = datetime.now().isoformat()
    order['delivered_at'] = datetime.now().isoformat()
    
    # Update stats
    stats['pending_orders'] = max(0, stats['pending_orders'] - 1)
    stats['completed_orders'] += 1
    stats['today_revenue'] += float(order['price_usd'])
    stats['month_revenue'] += float(order['price_usd'])
    stats['currency_breakdown'][order['crypto_currency']] += float(order['price_usd'])
    
    return jsonify({
        "success": True,
        "data": {
            "payment_id": payment_id,
            "status": "confirmed",
            "order_status": "confirmed",
            "confirmations": 20,
        }
    })

# ============ ADMIN API ============

@app.route('/api/v1/admin/dashboard', methods=['GET'])
def admin_dashboard():
    return jsonify({
        "success": True,
        "data": {
            "today_revenue": stats['today_revenue'],
            "month_revenue": stats['month_revenue'],
            "pending_orders": stats['pending_orders'],
            "completed_orders": stats['completed_orders'],
            "total_orders": stats['total_orders'],
            "conversion_rate": round(stats['completed_orders'] / max(1, stats['total_orders']) * 100, 2),
            "currency_breakdown": dict(stats['currency_breakdown']),
        }
    })

@app.route('/api/v1/admin/wallets', methods=['GET'])
def admin_wallets():
    return jsonify({
        "success": True,
        "data": list(wallets_db.values())
    })

@app.route('/api/v1/admin/orders', methods=['GET'])
def admin_orders():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    orders = list(orders_db.values())
    orders.sort(key=lambda x: x['created_at'], reverse=True)
    
    start = (page - 1) * limit
    end = start + limit
    
    return jsonify({
        "success": True,
        "data": {
            "orders": orders[start:end],
            "total": len(orders),
            "page": page,
            "limit": limit,
        }
    })

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Crypto Payment API Server")
    print("=" * 40)
    print("📍 Endpoints:")
    print("   - API: http://localhost:5000/api/v1/")
    print("   - Checkout: http://localhost:5000/")
    print("   - Dashboard: http://localhost:5000/dashboard")
    print("=" * 40)
    app.run(host='0.0.0.0', port=5000, debug=True)
