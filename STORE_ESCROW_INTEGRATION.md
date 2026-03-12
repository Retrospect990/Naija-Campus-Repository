# Campus Pinduoduo: Store & Escrow Integration Guide

## Overview

The Online Store and Escrow System are tightly integrated to provide a**complete group buying experience**. This guide explains how they work together to manage funds, orders, and deliveries for campus group buying.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMPUS PINDUODUO PLATFORM                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐        ┌────────▼──────────┐
        │ ESCROW SYSTEM  │        │  ONLINE STORE     │
        ├────────────────┤        ├────────────────────┤
        │• Pool Creation │        │• Product Catalog   │
        │• Deposits      │        │• Shopping Cart     │
        │• Fund Holding  │        │• Order Placement   │
        │• Milestones    │        │• Inventory Mgmt    │
        │• Releases      │        │• Order Tracking    │
        └────────┬───────┘        └────────┬───────────┘
                 │                         │
                 └─────────────┬───────────┘
                      ┌────────▼────────┐
                      │   SHARED STATE  │
                      ├─────────────────┤
                      │• Pool Budget    │
                      │• Transactions   │
                      │• Delivery Info  │
                      └─────────────────┘
```

---

## Key Integration Points

### 1. Pool & Budget Management

**Escrow System** creates and manages pools:
```python
# Escrow creates a pool
pool = {
    "pool_id": "pool_rice_50000",
    "created_by": "group_admin",
    "currency": "NGN",
    "total_amount": 50000.00,
    "status": "ACTIVE"
}
```

**Store System** uses pool budget:
```python
# When moderator creates cart, pool_id and budget are passed
cart = store.create_cart(
    moderator_id="mod_tunde",
    pool_id="pool_rice_50000",
    pool_budget=50000.00  # From escrow pool
)
```

**Integration Point**: Store validates that `pool_budget` equals remaining balance in escrow pool.

---

### 2. Funds Flow Diagram

```
GROUP MEMBERS
      │
      ├─── Member A contributes ₦10,000
      ├─── Member B contributes ₦15,000      
      ├─── Member C contributes ₦12,000
      └─── Member D contributes ₦13,000
                ▼
          [ESCROW HOLDS ₦50,000]    ← Escrow System
                ▼
    Pool is ACTIVE, ready to shop
                ▼
       Moderator creates cart with
       pool_budget=₦50,000
                ▼
      [SHOPPING CART ₦50,000 limit]  ← Store System
                ▼
    Moderator adds:
    • Rice ₦25,000
    • Beans ₦12,000
    • Palm Oil ₦10,000
                ▼
         [CART TOTAL: ₦47,000]
                ▼
          Place Order ✓
                ▼
        [₦47,000 DEDUCTED FROM ESCROW]
        [₦3,000 REMAINING in pool]
                ▼
           Order ships to group
                ▼
     Moderator confirms delivery
                ▼
    [ESCROW RELEASES ₦47,000]
        to vendor/supplier
```

---

## Detailed Integration Workflows

### Workflow A: Group Buying Cycle

#### Phase 1: Pool Creation (Escrow)
```
1. Admin creates pool via Escrow API
   POST /api/escrow/pools
   {
     "name": "Rice for Dorm A",
     "total_amount": 50000,
     "members": ["user1", "user2", "user3", "user4"]
   }
   
2. Pool created with status="PENDING"
3. Members deposit funds
4. Once all funds in: status="ACTIVE"
```

#### Phase 2: Shopping (Store)
```
1. Moderator creates cart
   POST /api/cart/create
   {
     "moderator_id": "mod_tunde",
     "pool_id": "pool_rice_50000",
     "pool_budget": 50000.00
   }
   
2. Moderator browses products
   GET /api/store/products?category=food
   
3. Moderator adds items
   POST /api/cart/{cart_id}/add
   {
     "product_id": "prod_rice",
     "quantity": 1
   }
   
4. Cart enforces: total ≤ 50000
5. Moderator places order
   POST /api/orders/place
```

#### Phase 3: Order Processing (Store)
```
1. Order created with status="PENDING"
2. Inventory updated:
   - Rice qty: 100 → 99
   
3. Order transitions:
   PENDING → CONFIRMED → PAID → 
   PROCESSING → SHIPPED → DELIVERED
```

#### Phase 4: Fund Release (Escrow)
```
1. Upon delivery confirmation:
   PUT /api/escrow/milestones/{milestone_id}/confirm
   {
     "proof": "delivery_photo_url"
   }
   
2. Escrow releases ₦47,000 to vendor
3. Remaining ₦3,000 returns to group (or stays for next order)
```

---

### Workflow B: Multiple Orders from Same Pool

**Scenario**: ₦50,000 rice pool, multiple shopping trips

```
TRIP 1:
├─ Cart A created: budget ₦50,000
├─ Order 1 placed: ₦25,000 (Uncle Ben's rice)
├─ Order 1 DELIVERED
├─ Escrow releases ₦25,000
└─ Pool remaining: ₦25,000

TRIP 2:
├─ Cart B created: budget ₦25,000
├─ Order 2 placed: ₦12,000 (Golden Harvest rice)  
├─ Order 2 DELIVERED
├─ Escrow releases ₦12,000
└─ Pool remaining: ₦13,000

TRIP 3:
├─ Cart C created: budget ₦13,000
├─ Order 3 placed: ₦10,000 (Palm oil)
├─ Order 3 DELIVERED
├─ Escrow releases ₦10,000
└─ Pool remaining: ₦3,000 (dust amount, returned)
```

**Data Model for Multiple Orders**:
```python
# Order table links to pool, not to specific cart
order = {
    "order_id": "ord_001",
    "pool_id": "pool_rice_50000",  # Same pool
    "moderator_id": "mod_tunde",
    "total_amount": 25000,
    "status": "DELIVERED"
}

order2 = {
    "order_id": "ord_002",
    "pool_id": "pool_rice_50000",  # Same pool, different order
    "moderator_id": "mod_tunde",
    "total_amount": 12000,
    "status": "DELIVERED"
}
```

---

### Workflow C: Budget Enforcement

**Cart respects pool budget** through real-time validation:

```python
# In store_system.py
class ShoppingCart:
    def can_add_product(self, product, quantity):
        """
        Check if adding product exceeds pool budget
        Returns: True if purchase allowed, False if budget exceeded
        """
        potential_total = self.get_total() + (product.price * quantity)
        remaining = self.pool_budget - self.get_total()
        
        if potential_total > self.pool_budget:
            return False
        return True
```

**In Practice**:
```
Pool budget: ₦50,000
Cart tries to add: Uncle Ben's rice (₦25,000) + Beans (₦12,000) + Palm Oil (₦15,000) = ₦52,000
                    └── EXCEEDS ₦50,000 budget

Action: API returns
{
  "status": "error",
  "message": "Insufficient budget. Need ₦52,000 but only ₦50,000 available."
}

Moderator can:
1. Remove one item (e.g., skip Palm Oil)
2. Choose cheaper brand (e.g., Golden Harvest instead of Uncle Ben's)
3. Create second order from next pool
```

---

## Database Integration

### Tables & Foreign Keys

```sql
-- Escrow creates pools
pools (id, pool_id, name, total_amount, status)

-- Store creates orders linked to pools
store_orders (order_id, pool_id, moderator_id, total_amount, status)

-- Orders deducted from pool budget
pool_budget_transactions (
    transaction_id,
    pool_id,          -- Links to escrow pool
    order_id,         -- Links to store order
    amount,           -- How much deducted
    transaction_type  -- 'ORDER', 'REFUND', 'ADJUSTMENT'
)
```

### Data Flow Example

```
1. Pool created in escrow
   INSERT INTO pools VALUES (uuid, "pool_rice_50000", ..., 50000)

2. Moderator places order in store
   INSERT INTO store_orders VALUES (..., pool_id="pool_rice_50000", 25000)

3. System records budget deduction
   INSERT INTO pool_budget_transactions VALUES (
       uuid, 
       pool_id="pool_rice_50000",
       order_id=<new_order_id>,
       25000,
       'ORDER'
   )

4. Query remaining budget
   SELECT 
       50000 - COALESCE(SUM(amount), 0) as remaining
   FROM pool_budget_transactions
   WHERE pool_id = "pool_rice_50000"
   AND transaction_type = 'ORDER'
   
   Result: ₦25,000 remaining
```

---

## API Integration Points

### API 1: Get Current Pool Budget (Escrow → Store)

**Escrow API** provides pool balance:
```http
GET /api/escrow/pools/{pool_id}
```

**Response**:
```json
{
  "pool_id": "pool_rice_50000",
  "total_amount": 50000,
  "amount_spent": 25000,
  "remaining_balance": 25000,
  "status": "ACTIVE"
}
```

**Store uses this** when creating new cart:
```python
# Get current balance from escrow
response = requests.get(f"/api/escrow/pools/{pool_id}")
pool = response.json()['data']

# Create cart with current remaining balance
cart = store.create_cart(
    moderator_id="mod_tunde",
    pool_id=pool_id,
    pool_budget=pool['remaining_balance']  # Use remaining, not total
)
```

---

### API 2: Record Order in Escrow (Store → Escrow)

When order is placed in Store, **notify Escrow system**:

```http
POST /api/escrow/budget-transaction
```

**Request**:
```json
{
  "pool_id": "pool_rice_50000",
  "order_id": "ord_001",
  "amount": 25000,
  "transaction_type": "ORDER",
  "description": "Order: Rice + Beans + Palm Oil"
}
```

**Purpose**: Escrow maintains accurate  `remaining_balance` for next orders.

---

### API 3: Confirm Delivery & Release Funds (Store → Escrow)

When order is delivered, **trigger escrow fund release**:

```http
PUT /api/escrow/milestones/{milestone_id}/confirm
```

**Request**:
```json
{
  "order_id": "ord_001",
  "proof": "photo_url_of_delivery",
  "confirmed_by": "mod_tunde"
}
```

**Result**: Escrow releases ₦25,000 to vendor.

---

## Implementation Checklist

### For Developers

- [ ] **Pool Creation**: Escrow API creates pools with unique `pool_id`
- [ ] **Cart Creation**: Store validates `pool_id` exists in Escrow
- [ ] **Budget Sync**: On cart creation, fetch current `remaining_balance` from escrow
- [ ] **Add to Cart**: Validate item cost against `pool_budget` (≤ cart max)
- [ ] **Place Order**: Record transaction in `pool_budget_transactions`
- [ ] **Order Status**: Update order status as items ship
- [ ] **Delivery Confirmation**: Moderator confirms delivery
- [ ] **Fund Release**: Call escrow API to release funds to vendor
- [ ] **Error Handling**: Handle pool not found, budget exceeded, API failures
- [ ] **Logging**: Log all pool ↔ order transactions for audits

### For Frontend / UI

- [ ] **Pool Selection**: Let moderator choose which pool to shop from
- [ ] **Budget Display**: Show available budget as cart value updates
  ```
  Pool Budget: ₦50,000
  Cart Total: ₦37,000
  Remaining: ₦13,000 ✓
  ```
- [ ] **Budget Warnings**: Warn if approaching limit
  ```
  ⚠️ Only ₦5,000 remaining. Add rice anyway? [Yes] [No]
  ```
- [ ] **Order History**: Show orders + delivery status
  - Order 1: ₦25,000 → DELIVERED (Released)
  - Order 2: ₦12,000 → SHIPPED (Releasing soon)
  - Order 3: ₦10,000 → PENDING (Not yet shipped)
  - Total Spent: ₦47,000 | Remaining: ₦3,000
- [ ] **Delivery Proof**: Allow photo upload for delivery confirmation
  ```
  [Upload Proof]  [Delivered]  [Dispute]
  ```

---

## Error Scenarios & Handling

### Scenario 1: Budget Exceeded
```
User tries to add rice ₦25,000 to cart
Pool has only ₦20,000 remaining

Action:
├─ Store API rejects: 400 Bad Request
├─ Message: "Need ₦25,000, only ₦20,000 available"
├─ User can:
│  ├─ Choose cheaper brand
│  ├─ Remove other items
│  └─ Create new order from different pool
└─ No impact on escrow

Recovery: ✓ User completes valid order within budget
```

### Scenario 2: Pool Not Found
```
Moderator provides invalid pool_id

Action:
├─ Store API rejects: 404 Not Found
├─ Message: "Pool not found"
├─ Escrow confirms pool doesn't exist
└─ User cannot proceed

Recovery: ✓ User selects valid pool
```

### Scenario 3: Order Failed to Record in Escrow
```
Order placed in store ✓
But escrow transaction API times out ✗

Action:
├─ Store creates order (optimistic)
├─ Escrow transaction fails
├─ Inconsistency: order exists but budget not deducted
└─ System marked for manual review

Recovery:
├─ Retry escrow transaction API
├─ Rollback store order if retry fails
└─ Notify admin for manual reconciliation
```

### Scenario 4: Delivery Never Confirmed
```
Order is SHIPPED for 30 days
But moderator never confirms delivery
Funds stuck in escrow

Action:
├─ Escrow sends reminder after 7 days
├─ Auto-release after 30 days (dispute period)
├─ Moderator can dispute if goods not received
└─ Admin reviews dispute

Recovery:
├─ Moderator confirms: funds released
├─ Moderator disputes: investigation
├─ Auto-release: vendor gets funds after timeout
```

---

## Testing Integration

### Test Case 1: Complete Happy Path

```python
def test_full_integration():
    # 1. Escrow creates pool
    pool = escrow.create_pool(
        name="Rice Pool",
        total_amount=50000
    )
    
    # 2. Store creates cart with escrow pool
    cart = store.create_cart(
        pool_id=pool.pool_id,
        pool_budget=pool.remaining_balance
    )
    
    # 3. Add items to cart
    store.add_to_cart(cart.cart_id, rice_id, qty=1)  # ₦25,000
    
    # 4. Place order
    order = store.place_order(cart.cart_id)
    
    # 5. Verify escrow recorded deduction
    assert escrow.get_pool_balance(pool.pool_id) == 25000
    
    # 6. Confirm delivery
    escrow.confirm_delivery(order.order_id)
    
    # 7. Verify funds released
    assert escrow.is_released(order.order_id) == True
```

### Test Case 2: Budget Enforcement

```python
def test_budget_enforcement():
    cart = store.create_cart(
        pool_budget=30000
    )
    
    # Try to add items exceeding budget
    success = store.add_to_cart(cart.cart_id, rice_25k, qty=1)
    assert success == True
    
    success = store.add_to_cart(cart.cart_id, beans_12k, qty=1)
    assert success == False  # Would exceed ₦30,000
    assert error_message == "Insufficient budget..."
```

---

## Performance Considerations

### 1. Cache Pool Balance
```python
# Cache escrow balance for 30 seconds to reduce API calls
pool_cache = {}

def get_pool_budget(pool_id):
    if pool_id in pool_cache and pool_cache[pool_id]['expires'] > time.time():
        return pool_cache[pool_id]['budget']
    
    # Fetch from escrow API
    balance = escrow_api.get_pool_balance(pool_id)
    pool_cache[pool_id] = {
        'budget': balance,
        'expires': time.time() + 30
    }
    return balance
```

### 2. Batch Budget Transactions
```python
# Instead of recording each item individually,
# batch all items in order into single transaction
transaction = {
    'pool_id': pool_id,
    'order_id': order_id,
    'amount': total_items_cost,
    'items': [item1, item2, item3],
    'timestamp': now()
}

escrow_api.record_transaction(transaction)
```

### 3. Database Indexes
```sql
-- Quick lookup of remaining budget
CREATE INDEX idx_budget_transactions 
ON pool_budget_transactions(pool_id, created_at DESC);

-- Quick lookup of orders by pool
CREATE INDEX idx_orders_by_pool 
ON store_orders(pool_id, created_at DESC);
```

---

## Deployment Checklist

- [ ] Database migrations applied
- [ ] Escrow API endpoints tested
- [ ] Store API endpoints tested
- [ ] Integration endpoints tested
- [ ] RLS policies configured
- [ ] Error handling deployed
- [ ] Logging enabled for all transactions
- [ ] Backup of database verified
- [ ] Monitoring alerts set up
- [ ] Documentation updated
- [ ] Team trained on workflows

---

## FAQ

**Q: Can a pool be used for multiple orders?**
A: Yes! Same pool can have multiple orders from same moderator. Budget tracks remaining balance across all orders from that pool.

**Q: What happens if escrow API is down?**
A: Store still creates orders optimistically. When escrow comes back, sync transactions. Consider fallback to local queue.

**Q: Can moderators see other moderators' carts?**
A: No. RLS policies ensure each moderator only sees their own carts and orders.

**Q: What's the max number of items per order?**
A: No hard limit, but recommend max 50 items (UX). Budget is real constraint.

**Q: Can funds be refunded?**
A: Yes, if order is cancelled before delivery. Refund recorded as negative transaction.

---

## See Also

- [Escrow System Documentation](./ESCROW_DOCUMENTATION.md)
- [Store System Documentation](./STORE_DOCUMENTATION.md)
- [API Guide](./STORE_API_GUIDE.md)
- [Database Schema](./store_database_schema.sql)
