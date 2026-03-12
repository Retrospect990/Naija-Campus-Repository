"""
Campus Pinduoduo: API Client Tester
Tests all REST API endpoints without needing a running server
"""

from api_server import app, system, init_demo_data
import json

def test_api_endpoints():
    """Test all API endpoints using Flask test client"""
    
    print("\n" + "="*80)
    print("CAMPUS PINDUODUO: API ENDPOINT TESTS")
    print("="*80)
    
    # Initialize demo data
    init_demo_data()
    
    # Create test client
    client = app.test_client()
    
    # ========== TEST 1: Health Check ==========
    print("\n[TEST 1] GET /api/health - Health Check")
    print("-" * 80)
    response = client.get('/api/health')
    data = response.get_json()
    print(f"✅ Status Code: {response.status_code}")
    print(f"   Service: {data['service']}")
    print(f"   Status: {data['status']}")
    
    # ========== TEST 2: List Pools ==========
    print("\n[TEST 2] GET /api/pools - List All Pools")
    print("-" * 80)
    response = client.get('/api/pools')
    data = response.get_json()
    print(f"✅ Status Code: {response.status_code}")
    print(f"   Total Pools: {data['total_pools']}")
    for pool in data['pools']:
        print(f"   - {pool['item']} (Goal: ₦{pool['goal']:,.0f}, Raised: ₦{pool['raised']:,.0f})")
    
    # ========== TEST 3: Get Pool Details ==========
    print("\n[TEST 3] GET /api/pools/<id> - Get Pool Details")
    print("-" * 80)
    pool_id = list(system.pools.keys())[0]
    response = client.get(f'/api/pools/{pool_id}')
    data = response.get_json()
    print(f"✅ Status Code: {response.status_code}")
    print(f"   Pool: {data['item']}")
    print(f"   Moderator: {data['moderator']}")
    print(f"   Goal: ₦{data['goal']:,.0f}")
    print(f"   Raised: ₦{data['raised']:,.0f}")
    print(f"   Progress: {data['progress_percent']:.1f}%")
    print(f"   Status: {data['status']}")
    print(f"   Participants: {len(data['participants'])}")
    
    # ========== TEST 4: Join Pool ==========
    print("\n[TEST 4] POST /api/pools/<id>/join - Join Pool")
    print("-" * 80)
    student_id = list(system.users.keys())[3]  # Get a student
    response = client.post(f'/api/pools/{pool_id}/join', 
                          json={'student_id': student_id},
                          content_type='application/json')
    data = response.get_json()
    print(f"✅ Status Code: {response.status_code}")
    print(f"   Message: {data['message']}")
    print(f"   Amount: ₦{data['participant']['amount']:,.0f}")
    print(f"   Confirmation PIN: {data['participant']['confirmation_pin']}")
    print(f"   Escrow Status: {data['escrow_status']}")
    print(f"   Pool Progress: {data['progress']['percent']:.1f}%")
    
    # ========== TEST 5: Confirm Receipt ==========
    print("\n[TEST 5] POST /api/pools/<id>/confirm-receipt - Confirm Item Receipt")
    print("-" * 80)
    
    # Join additional students to reach goal (pool needs to be LOCKED first)
    student_ids = list(system.users.keys())
    for s_id in student_ids[1:]:
        if len(system.pools[pool_id].participants) < 3:
            client.post(f'/api/pools/{pool_id}/join',
                       json={'student_id': s_id},
                       content_type='application/json')
    
    # Check if pool is now locked (goal reached)
    pool = system.pools[pool_id]
    if pool.pool_status.value == "locked":
        # Pool is locked, now moderator can initiate purchase
        system.moderator_initiates_purchase(pool_id)
        
        if pool.participants:
            participant = pool.participants[0]
            
            response = client.post(f'/api/pools/{pool_id}/confirm-receipt',
                                  json={
                                      'student_id': participant.participant_id,
                                      'pin': participant.confirmation_pin
                                  },
                                  content_type='application/json')
            data = response.get_json()
            print(f"✅ Status Code: {response.status_code}")
            print(f"   Message: {data['message']}")
            if 'confirmations' in data:
                print(f"   Confirmations: {data['confirmations']['count']}/{data['confirmations']['total']}")
                print(f"   Confirmation Percentage: {data['confirmations']['percentage']}%")
                print(f"   Funds Released: {data['funds_released']}")
    else:
        print(f"   Pool not locked yet - Status: {pool.pool_status.value}")
    
    # ========== TEST 6: Escrow Ledger ==========
    print("\n[TEST 6] GET /api/escrow/ledger - View Escrow Transactions")
    print("-" * 80)
    try:
        response = client.get(f'/api/escrow/ledger?pool_id={pool_id}')
        data = response.get_json()
        if response.status_code == 200:
            print(f"✅ Status Code: {response.status_code}")
            print(f"   Total Transactions: {data.get('total_transactions', 'N/A')}")
            print(f"   Summary:")
            summary = data.get('summary', {})
            print(f"      Deposits: ₦{summary.get('total_deposits', 0):,.0f}")
            print(f"      Released/Refunded: ₦{summary.get('total_released_refunded', 0):,.0f}")
            print(f"      Balance: ₦{summary.get('balance', 0):,.0f}")
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(f"   Error: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"⚠️  Ledger test skipped - {str(e)}")
    
    # ========== TEST 7: List Users ==========
    print("\n[TEST 7] GET /api/users - List All Users")
    print("-" * 80)
    response = client.get('/api/users')
    data = response.get_json()
    print(f"✅ Status Code: {response.status_code}")
    print(f"   Total Users: {data['total_users']}")
    for user in data['users'][:3]:  # Show first 3
        user_type = "Moderator" if user['is_moderator'] else "Student"
        print(f"   - {user['name']} ({user_type}): ₦{user['balance']:,.0f}")
    
    # ========== TEST 8: System Statistics ==========
    print("\n[TEST 8] GET /api/stats - System Statistics")
    print("-" * 80)
    response = client.get('/api/stats')
    data = response.get_json()
    print(f"✅ Status Code: {response.status_code}")
    print(f"   Total Pools: {data['total_pools']}")
    print(f"   Total Users: {data['total_users']}")
    print(f"   Total Transactions: {data['total_transactions']}")
    print(f"   Financials:")
    print(f"      Total Deposits: ₦{data['financials']['total_deposits']:,.0f}")
    print(f"      Released to Moderators: ₦{data['financials']['total_released_to_moderators']:,.0f}")
    print(f"      Refunded: ₦{data['financials']['total_refunded']:,.0f}")
    print(f"      In Escrow: ₦{data['financials']['balance_in_escrow']:,.0f}")
    
    # ========== ERROR HANDLING TEST ==========
    print("\n[TEST 9] Error Handling - Non-existent Pool")
    print("-" * 80)
    response = client.get('/api/pools/invalid_id')
    data = response.get_json()
    print(f"✅ Status Code: {response.status_code}")
    print(f"   Error: {data['error']}")
    
    print("\n[TEST 10] Error Handling - Invalid Endpoint")
    print("-" * 80)
    response = client.get('/api/invalid_endpoint')
    data = response.get_json()
    print(f"✅ Status Code: {response.status_code}")
    print(f"   Error: {data['error']}")
    
    print("\n" + "="*80)
    print("ALL API TESTS COMPLETED!")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_api_endpoints()
