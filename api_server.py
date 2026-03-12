"""
Campus Pinduoduo: Demo API Server
A simple Flask server showing the escrow system APIs in action
"""

from flask import Flask, jsonify, request
from datetime import datetime
import json

# Import the escrow system
import sys
sys.path.insert(0, '.')
from escrow_demo import EscrowSystem, PoolStatus

app = Flask(__name__)
app.json.sort_keys = False

# Global system instance
system = EscrowSystem()

# Pre-populate with demo data
MODERATOR_ID = None
STUDENTS = []
POOL_ID = None

def init_demo_data():
    """Initialize demo data"""
    global MODERATOR_ID, STUDENTS, POOL_ID
    
    MODERATOR_ID = system.create_user("Chioma (Moderator)", "chioma@example.com", "LASU", is_moderator=True)
    STUDENTS = [
        system.create_user("Tunde", "tunde@example.com", "LASU"),
        system.create_user("Zainab", "zainab@example.com", "LASU"),
        system.create_user("Damilare", "damilare@example.com", "LASU"),
    ]
    POOL_ID = system.create_pool(
        moderator_id=MODERATOR_ID,
        item_name="Premium Rice - 50kg bags",
        total_goal=30000.0,
        cost_per_slot=10000.0,
        total_slots=3
    )

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Campus Pinduoduo - Escrow System',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/pools', methods=['GET'])
def list_pools():
    """Get all pools"""
    pools_data = []
    for pool_id, pool in system.pools.items():
        pools_data.append({
            'id': pool_id,
            'item': pool.item_name,
            'goal': pool.total_goal_amount,
            'raised': pool.amount_raised,
            'slots': f"{pool.slots_filled}/{pool.total_slots}",
            'status': pool.pool_status.value,
            'moderator': system.users[pool.moderator_id].name
        })
    
    return jsonify({
        'total_pools': len(pools_data),
        'pools': pools_data
    })

@app.route('/api/pools/<pool_id>', methods=['GET'])
def get_pool(pool_id):
    """Get pool details"""
    if pool_id not in system.pools:
        return jsonify({'error': 'Pool not found'}), 404
    
    pool = system.pools[pool_id]
    return jsonify({
        'id': pool_id,
        'item': pool.item_name,
        'moderator': system.users[pool.moderator_id].name,
        'goal': pool.total_goal_amount,
        'raised': pool.amount_raised,
        'slots': {
            'total': pool.total_slots,
            'filled': pool.slots_filled
        },
        'status': pool.pool_status.value,
        'participants': [
            {
                'name': system.users[p.participant_id].name,
                'amount': p.contribution_amount,
                'status': p.status.value
            } for p in pool.participants
        ],
        'progress_percent': (pool.amount_raised / pool.total_goal_amount * 100) if pool.total_goal_amount > 0 else 0
    })

@app.route('/api/pools/<pool_id>/join', methods=['POST'])
def join_pool(pool_id):
    """Join a pool (simulate student deposit)"""
    if pool_id not in system.pools:
        return jsonify({'error': 'Pool not found'}), 404
    
    data = request.get_json()
    student_id = data.get('student_id')
    
    if student_id not in system.users:
        return jsonify({'error': 'Student not found'}), 404
    
    try:
        participant = system.student_joins_pool(student_id, pool_id)
        pool = system.pools[pool_id]
        
        return jsonify({
            'status': 'success',
            'message': f"Joined pool successfully",
            'participant': {
                'id': participant.id,
                'amount': participant.contribution_amount,
                'confirmation_pin': participant.confirmation_pin
            },
            'pool_status': pool.pool_status.value,
            'progress': {
                'raised': pool.amount_raised,
                'goal': pool.total_goal_amount,
                'percent': (pool.amount_raised / pool.total_goal_amount * 100) if pool.total_goal_amount > 0 else 0
            },
            'escrow_status': 'HELD (money secured in escrow)'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/pools/<pool_id>/confirm-receipt', methods=['POST'])
def confirm_receipt(pool_id):
    """Student confirms item receipt via PIN"""
    if pool_id not in system.pools:
        return jsonify({'error': 'Pool not found'}), 404
    
    data = request.get_json()
    student_id = data.get('student_id')
    pin = data.get('pin')
    
    try:
        system.student_confirms_receipt(student_id, pool_id, pin)
        
        # Calculate confirmation status
        pool = system.pools[pool_id]
        confirmed = len([p for p in pool.participants 
                        if p.status.value == 'confirmed_received'])
        total = len(pool.participants)
        confirmation_pct = (confirmed / total * 100) if total > 0 else 0
        
        return jsonify({
            'status': 'success',
            'message': 'Item receipt confirmed',
            'confirmations': {
                'count': confirmed,
                'total': total,
                'percentage': round(confirmation_pct, 1)
            },
            'pool_status': pool.pool_status.value,
            'funds_released': pool.pool_status == PoolStatus.COMPLETED
        }), 200
    
    except AssertionError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/escrow/ledger', methods=['GET'])
def escrow_ledger():
    """Get complete escrow transaction ledger"""
    pool_id = request.args.get('pool_id')
    
    if pool_id:
        transactions = [t for t in system.all_escrow_transactions if t.pool_id == pool_id]
    else:
        transactions = system.all_escrow_transactions
    
    txn_data = []
    total_in = 0
    total_out = 0
    
    for txn in transactions:
        # Get participant name
        participant_name = 'System'
        if txn.participant_id and txn.participant_id in system.users:
            participant_name = system.users[txn.participant_id].name
        
        txn_data.append({
            'id': txn.id,
            'type': txn.transaction_type,
            'amount': txn.amount,
            'escrow_status': txn.escrow_status.value,
            'timestamp': txn.timestamp.isoformat(),
            'participant': participant_name
        })
        
        if txn.transaction_type == 'deposit':
            total_in += txn.amount
        else:
            total_out += txn.amount
    
    return jsonify({
        'total_transactions': len(txn_data),
        'transactions': txn_data,
        'summary': {
            'total_deposits': total_in,
            'total_released_refunded': total_out,
            'balance': total_in - total_out
        }
    })

@app.route('/api/users', methods=['GET'])
def list_users():
    """Get all users and their balances"""
    users_data = []
    for user_id, user in system.users.items():
        users_data.append({
            'id': user_id,
            'name': user.name,
            'email': user.email,
            'balance': user.balance,
            'is_moderator': user.is_moderator,
            'university': user.university
        })
    
    return jsonify({
        'total_users': len(users_data),
        'users': users_data
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    total_deposits = sum(t.amount for t in system.all_escrow_transactions if t.transaction_type == 'deposit')
    total_released = sum(t.amount for t in system.all_escrow_transactions if t.transaction_type == 'release_to_moderator')
    total_refunded = sum(t.amount for t in system.all_escrow_transactions if t.transaction_type == 'refund')
    
    return jsonify({
        'total_pools': len(system.pools),
        'total_users': len(system.users),
        'total_transactions': len(system.all_escrow_transactions),
        'financials': {
            'total_deposits': total_deposits,
            'total_released_to_moderators': total_released,
            'total_refunded': total_refunded,
            'balance_in_escrow': total_deposits - total_released - total_refunded
        }
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("CAMPUS PINDUODUO: DEMO API SERVER")
    print("="*80)
    
    # Initialize demo data
    init_demo_data()
    
    print("\nInitializing demo environment...")
    print(f"  ✅ Moderator created: {system.users[MODERATOR_ID].name}")
    print(f"  ✅ Students created: {len(STUDENTS)} users")
    print(f"  ✅ Pool created: {system.pools[POOL_ID].item_name}")
    
    print("\nAvailable API Endpoints:")
    print("  🔍 GET  /api/health              - Health check")
    print("  📋 GET  /api/pools               - List all pools")
    print("  📊 GET  /api/pools/<pool_id>     - Get pool details")
    print("  💰 POST /api/pools/<pool_id>/join - Join a pool (deposit)")
    print("  ✅ POST /api/pools/<pool_id>/confirm-receipt - Confirm item receipt")
    print("  📖 GET  /api/escrow/ledger       - View escrow transactions")
    print("  👥 GET  /api/users               - List all users")
    print("  📈 GET  /api/stats               - System statistics")
    
    print("\n" + "="*80)
    print("Starting Flask development server...")
    print("="*80 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=False)
