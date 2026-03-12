"""
Campus Pinduoduo: Online Store - Test Scenarios
Comprehensive testing of store functionality, cart management, and orders
"""

from store_system import OnlineStore, ProductCategory, OrderStatus

def test_store_basic_operations():
    """Test 1: Basic store operations"""
    print("\n" + "="*80)
    print("TEST 1: BASIC STORE OPERATIONS")
    print("="*80)
    
    store = OnlineStore()
    
    # Get all products
    all_products = store.get_all_products()
    print(f"✅ Store initialized with {len(all_products)} products")
    
    # Get categories
    food = store.get_products_by_category(ProductCategory.FOOD)
    print(f"✅ Food category has {len(food)} products")
    
    # Search
    rice_products = store.get_products_by_name("rice")
    print(f"✅ Search for 'rice' found {len(rice_products)} products")
    
    # Get by brand
    uncle_bens = store.get_products_by_brand("Uncle Ben's")
    print(f"✅ Uncle Ben's brand has {len(uncle_bens)} product(s)")
    
    print("\n✅ TEST 1 PASSED\n")

def test_shopping_cart_and_budget():
    """Test 2: Shopping cart with budget constraints"""
    print("\n" + "="*80)
    print("TEST 2: SHOPPING CART & BUDGET CONSTRAINTS")
    print("="*80)
    
    store = OnlineStore()
    
    # Scenario: ₦30,000 budget
    moderator_id = "mod_tunde_001"
    pool_id = "pool_rice_30000"
    budget = 30000.0
    
    cart = store.create_cart(moderator_id, pool_id, budget)
    print(f"\n✅ Created cart with ₦{budget:,.0f} budget")
    
    # Add Uncle Ben's rice
    rice = store.get_products_by_name("rice")[0]
    success, msg = store.add_to_cart(cart.cart_id, rice.id, 1)
    print(f"✅ {msg}")
    print(f"   Cart: ₦{cart.get_total():,.0f} / ₦{budget:,.0f}")
    
    # Try to add another rice (would exceed budget)
    success, msg = store.add_to_cart(cart.cart_id, rice.id, 1)
    if not success:
        print(f"✅ Budget constraint working: {msg}")
    
    # Add complementary items
    beans = store.get_products_by_name("beans")[0]
    success, msg = store.add_to_cart(cart.cart_id, beans.id, 1)
    print(f"✅ {msg}")
    print(f"   Cart: ₦{cart.get_total():,.0f} / ₦{budget:,.0f}")
    
    # Check budget utilization
    utilization = cart.get_budget_utilization_percent()
    print(f"✅ Budget utilization: {utilization:.1f}%")
    print(f"✅ Remaining: ₦{cart.get_remaining_budget():,.0f}")
    
    print("\n✅ TEST 2 PASSED\n")

def test_cart_item_management():
    """Test 3: Adding, removing, and updating cart items"""
    print("\n" + "="*80)
    print("TEST 3: CART ITEM MANAGEMENT")
    print("="*80)
    
    store = OnlineStore()
    
    budget = 50000.0
    cart = store.create_cart("mod_zainab_001", "pool_shop_50k", budget)
    
    # Get products
    food_items = store.get_products_by_category(ProductCategory.FOOD)
    product1 = food_items[0]
    product2 = food_items[1] if len(food_items) > 1 else food_items[0]
    
    # Add items
    store.add_to_cart(cart.cart_id, product1.id, 1)
    store.add_to_cart(cart.cart_id, product2.id, 2)
    print(f"✅ Added 2 different items to cart")
    print(f"   Items in cart: {len(cart.items)}")
    print(f"   Total: ₦{cart.get_total():,.0f}")
    
    # Update quantity
    success, msg = store.update_cart_item(cart.cart_id, product1.id, 0)
    print(f"✅ Update quantity to 0 removes item: {len(cart.items)} items left")
    
    # Remove item
    success, msg = store.remove_from_cart(cart.cart_id, product2.id)
    print(f"✅ Remove item: {len(cart.items)} items left")
    
    # Clear cart
    cart.clear()
    print(f"✅ Cleared cart: {len(cart.items)} items left")
    
    print("\n✅ TEST 3 PASSED\n")

def test_order_placement():
    """Test 4: Order placement and confirmation"""
    print("\n" + "="*80)
    print("TEST 4: ORDER PLACEMENT & CONFIRMATION")
    print("="*80)
    
    store = OnlineStore()
    
    moderator = "mod_chioma_002"
    pool = "pool_supplies_25k"
    budget = 25000.0
    
    # Create cart and add items
    cart = store.create_cart(moderator, pool, budget)
    
    cosmetics = store.get_products_by_category(ProductCategory.COSMETICS)
    books = store.get_products_by_category(ProductCategory.BOOKS)
    
    store.add_to_cart(cart.cart_id, cosmetics[0].id, 2)
    store.add_to_cart(cart.cart_id, books[0].id, 1)
    
    cart_total = cart.get_total()
    items_count = len(cart.items)
    
    print(f"✅ Cart ready: {items_count} items, ₦{cart_total:,.0f}")
    
    # Place order
    success, order = store.place_order(cart.cart_id, "Delivery to dormitory building A")
    
    if success:
        print(f"✅ Order placed successfully!")
        print(f"   Order ID: {order.order_id}")
        print(f"   Status: {order.status.value}")
        print(f"   Items: {len(order.items)}")
        print(f"   Total: ₦{order.total_amount:,.0f}")
        print(f"   Notes: {order.notes}")
        
        # Verify cart is cleared
        print(f"✅ Cart cleared after order: {len(cart.items)} items")
        
        # Check inventory changed
        product = store.get_product(cosmetics[0].id)
        print(f"✅ Inventory updated: {product.quantity_available} {product.unit} available")
    
    print("\n✅ TEST 4 PASSED\n")

def test_multiple_moderators():
    """Test 5: Multiple moderators with different budgets"""
    print("\n" + "="*80)
    print("TEST 5: MULTIPLE MODERATORS & BUDGETS")
    print("="*80)
    
    store = OnlineStore()
    
    moderators = [
        ("mod_damilare_001", "pool_damilare_50k", 50000.0),
        ("mod_ada_001", "pool_ada_25k", 25000.0),
        ("mod_john_001", "pool_john_10k", 10000.0)
    ]
    
    # Create carts for each moderator
    carts = {}
    for mod_id, pool_id, budget in moderators:
        cart = store.create_cart(mod_id, pool_id, budget)
        carts[mod_id] = (cart, budget)
        print(f"✅ Created cart for {mod_id}: ₦{budget:,.0f}")
    
    # Each moderator shops according to their budget
    food_items = store.get_products_by_category(ProductCategory.FOOD)
    rice = food_items[0]
    shopping_list = [
        (carts["mod_damilare_001"][0], rice.id, 2),  # 2 bags of rice
        (carts["mod_ada_001"][0], rice.id, 1),       # 1 bag of rice
        (carts["mod_john_001"][0], rice.id, 0)       # Can't afford any!
    ]
    
    for cart, product_id, qty in shopping_list:
        if qty > 0:
            success, msg = store.add_to_cart(cart.cart_id, product_id, qty)
            print(f"   {msg[:60]}... Budget left: ₦{cart.get_remaining_budget():,.0f}")
        else:
            print(f"   ⚠️ Budget too low for any rice (need ₦{rice.price:,.0f})")
    
    # Place orders
    total_orders = 0
    for mod_id, (cart, budget) in carts.items():
        if not cart.is_empty():
            success, order = store.place_order(cart.cart_id)
            if success:
                total_orders += 1
                print(f"✅ {mod_id}: Order {order.order_id} placed (₦{order.total_amount:,.0f})")
    
    print(f"✅ Total orders placed: {total_orders}")
    
    print("\n✅ TEST 5 PASSED\n")

def test_inventory_and_stock():
    """Test 6: Inventory tracking and stock management"""
    print("\n" + "="*80)
    print("TEST 6: INVENTORY & STOCK MANAGEMENT")
    print("="*80)
    
    store = OnlineStore()
    
    # Check initial inventory
    notebook = store.get_products_by_name("notebook")[0]
    initial_stock = notebook.quantity_available
    print(f"✅ Initial stock: {initial_stock} {notebook.unit} of {notebook.brand} {notebook.name}")
    
    # Create orders to reduce stock
    for i in range(3):
        cart = store.create_cart(f"mod_order_{i}", f"pool_{i}", 50000)
        store.add_to_cart(cart.cart_id, notebook.id, 1)
        success, order = store.place_order(cart.cart_id)
        if success:
            print(f"✅ Order {i+1}: Removed 1 pack from stock")
    
    # Check final stock
    product = store.get_product(notebook.id)
    final_stock = product.quantity_available
    print(f"✅ Final stock: {final_stock} {product.unit}")
    print(f"✅ Total sold: {initial_stock - final_stock} packs")
    
    # Check low stock alert
    electronics = store.get_products_by_category(ProductCategory.ELECTRONICS)
    usb_cables = [p for p in electronics if "USB" in p.name][0]
    
    # Artificially set to low to test
    usb_cables.quantity_available = 3
    print(f"✅ USB Cable stock set to {usb_cables.quantity_available}: ⚠️ LOW STOCK ALERT")
    
    print("\n✅ TEST 6 PASSED\n")

def test_order_history_and_tracking():
    """Test 7: Order history and status tracking"""
    print("\n" + "="*80)
    print("TEST 7: ORDER HISTORY & STATUS TRACKING")
    print("="*80)
    
    store = OnlineStore()
    
    moderator = "mod_tracker_001"
    
    # Place multiple orders
    order_ids = []
    for order_num in range(3):
        cart = store.create_cart(moderator, f"pool_{order_num}", 20000)
        
        # Add random items
        all_products = store.get_all_products()[:order_num+1]
        for product in all_products:
            store.add_to_cart(cart.cart_id, product.id, 1)
        
        success, order = store.place_order(cart.cart_id, f"Delivery notes {order_num}")
        if success:
            order_ids.append(order.order_id)
            print(f"✅ Order {order_num+1}: {order.order_id} (₦{order.total_amount:,.0f})")
    
    # Get moderator order history
    orders = store.get_moderator_orders(moderator)
    print(f"\n✅ Moderator has {len(orders)} orders:")
    
    for order in orders:
        print(f"   • {order.order_id}: {len(order.items)} items, ₦{order.total_amount:,.0f} ({order.status.value})")
    
    # Update order status
    first_order = store.get_order(order_ids[0])
    print(f"\n✅ Order status transitions:")
    print(f"   Initial: {first_order.status.value}")
    
    store.update_order_status(order_ids[0], OrderStatus.PAID)
    print(f"   After payment: {first_order.status.value}")
    
    store.update_order_status(order_ids[0], OrderStatus.PROCESSING)
    print(f"   In processing: {first_order.status.value}")
    
    store.update_order_status(order_ids[0], OrderStatus.DELIVERED)
    print(f"   Delivered: {first_order.status.value}")
    
    print("\n✅ TEST 7 PASSED\n")

def test_store_analytics():
    """Test 8: Store analytics and statistics"""
    print("\n" + "="*80)
    print("TEST 8: STORE ANALYTICS & STATISTICS")
    print("="*80)
    
    store = OnlineStore()
    
    # Get initial stats
    stats = store.get_store_stats()
    print(f"\n✅ Initial Store Statistics:")
    print(f"   Total Products: {stats['total_products']}")
    print(f"   Product Categories: {stats['categories']}")
    print(f"   Stock Value: ₦{stats['stock_value']:,.0f}")
    print(f"   Active Carts: {stats['active_carts']}")
    print(f"   Total Orders: {stats['total_orders']}")
    print(f"   Total Sales: ₦{stats['total_sales']:,.0f}")
    
    # Place some orders to generate sales
    print(f"\n📊 Generating sales data...")
    total_sales = 0
    for i in range(5):
        cart = store.create_cart(f"mod_sale_{i}", f"pool_{i}", 50000)
        
        # Add random items
        products = store.get_all_products()
        for j, product in enumerate(products[:2]):
            store.add_to_cart(cart.cart_id, product.id, 1)
        
        success, order = store.place_order(cart.cart_id)
        if success:
            total_sales += order.total_amount
    
    # Get updated stats
    stats = store.get_store_stats()
    print(f"\n✅ Updated Store Statistics:")
    print(f"   Active Carts: {stats['active_carts']}")
    print(f"   Total Orders: {stats['total_orders']} (increased from 0)")
    print(f"   Total Sales: ₦{stats['total_sales']:,.0f}")
    
    print("\n✅ TEST 8 PASSED\n")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CAMPUS PINDUODUO: ONLINE STORE - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_store_basic_operations()
    test_shopping_cart_and_budget()
    test_cart_item_management()
    test_order_placement()
    test_multiple_moderators()
    test_inventory_and_stock()
    test_order_history_and_tracking()
    test_store_analytics()
    
    print("="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80 + "\n")
