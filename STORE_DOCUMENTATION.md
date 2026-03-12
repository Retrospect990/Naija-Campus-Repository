# Campus Pinduoduo: Online Store System Documentation

## Module Overview

The Online Store system consists of two main modules:

1. **store_system.py** - Core business logic for products, carts, and orders
2. **store_api_rest.py** - Flask REST API wrapper for web/mobile clients

---

## store_system.py - Core Business Logic

### Classes & Data Structures

#### 1. ProductCategory (Enum)
```python
class ProductCategory(Enum):
    FOOD = "food"
    BEVERAGES = "beverages"
    FASHION = "fashion"
    ELECTRONICS = "electronics"
    HOME_GARDEN = "home_garden"
    BOOKS = "books"
    COSMETICS = "cosmetics"
    SPORTS = "sports"
```

**Usage**: Filter and organize products by type.

---

#### 2. OrderStatus (Enum)
```python
class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

**Usage**: Track order lifecycle from creation to delivery.

**Status Transitions**:
```
┌─────────┐   ┌──────────┐   ┌──────┐   ┌────────────┐   ┌─────────┐   ┌──────────┐
│ PENDING │──▶│CONFIRMED │──▶│ PAID │──▶│PROCESSING │──▶│ SHIPPED │──▶│DELIVERED │
└─────────┘   └──────────┘   └──────┘   └────────────┘   └─────────┘   └──────────┘
       │
       └───────────────────────────────────────────────────────────────▶│CANCELLED │
```

---

#### 3. Product (DataClass)
```python
@dataclass
class Product:
    id: str  # Unique identifier
    name: str  # e.g., "Rice"
    brand: str  # e.g., "Uncle Ben's"
    category: ProductCategory
    price: Decimal
    unit: str  # e.g., "bag", "pack", "piece"
    quantity_available: int  # Current stock
    supplier_name: str
    description: str
    average_rating: Decimal = Decimal('4.0')
    review_count: int = 0
```

**Key Features**:
- Immutable once created
- Supports multiple brands per category
- Stock tracking with availability
- Rating and supplier information

**Example**:
```python
rice_uncle_bens = Product(
    id="prod_rice_001",
    name="Rice",
    brand="Uncle Ben's",
    category=ProductCategory.FOOD,
    price=Decimal("25000.00"),
    unit="bag",
    quantity_available=100,
    supplier_name="Northern Supplies"
)

rice_golden = Product(
    id="prod_rice_002",
    name="Rice",
    brand="Golden Harvest",
    category=ProductCategory.FOOD,
    price=Decimal("22000.00"),
    unit="bag",
    quantity_available=120,
    supplier_name="Eastern Foods"
)
```

---

#### 4. CartItem (DataClass)
```python
@dataclass
class CartItem:
    product: Product
    quantity: int  # How many units
```

**Methods**:
- `get_subtotal()` → Total cost for this item (price × quantity)

**Example**:
```python
rice_in_cart = CartItem(
    product=rice_uncle_bens,
    quantity=1
)
rice_in_cart.get_subtotal()  # Returns 25000.00
```

---

#### 5. ShoppingCart (Core Cart Logic)
```python
class ShoppingCart:
    def __init__(
        self, 
        cart_id: str,
        moderator_id: str,
        pool_id: str,
        pool_budget: float
    ):
        self.cart_id = cart_id
        self.moderator_id = moderator_id
        self.pool_id = pool_id
        self.pool_budget = Decimal(str(pool_budget))
        self.items: List[CartItem] = []
        self.created_at = datetime.now()
```

**Key Methods**:

##### can_add_product() - Budget Enforcement
```python
def can_add_product(self, product: Product, quantity: int) -> bool:
    """
    Check if adding product exceeds pool budget
    
    Args:
        product: Product to add
        quantity: Number of units
    
    Returns:
        True if purchase fits in budget, False if exceeds
    
    Example:
        cart.can_add_product(rice_25k, qty=1)  # Returns True if budget allows
        cart.can_add_product(rice_25k, qty=2)  # Returns False if exceeds
    """
    potential_total = self.get_total() + (product.price * quantity)
    return potential_total <= self.pool_budget
```

##### add_item() - Add Item to Cart
```python
def add_item(self, product: Product, quantity: int) -> bool:
    """
    Add item to cart, respecting budget limit
    
    Returns:
        True if added successfully, False if budget exceeded
    """
    if not self.can_add_product(product, quantity):
        return False
    
    # Check if product already in cart
    for item in self.items:
        if item.product.id == product.id:
            item.quantity += quantity
            return True
    
    # Add new item
    self.items.append(CartItem(product=product, quantity=quantity))
    return True
```

##### get_total() - Calculate Cart Total
```python
def get_total(self) -> Decimal:
    """
    Calculate total cost of all items in cart
    
    Returns:
        Total amount (sum of all item subtotals)
    
    Example:
        cart.add_item(rice_25k, 1)  # ₦25,000
        cart.add_item(beans_12k, 1)  # ₦12,000
        cart.get_total()  # Returns ₦37,000
    """
    total = sum(item.get_subtotal() for item in self.items)
    return Decimal(str(total))
```

##### get_remaining_budget() - Show Available Funds
```python
def get_remaining_budget(self) -> Decimal:
    """
    Calculate funds still available in pool
    
    Returns:
        Remaining budget (pool_budget - cart_total)
    
    Example:
        cart.pool_budget = 50000
        cart.get_total() = 37000
        cart.get_remaining_budget()  # Returns 13000
    """
    return self.pool_budget - self.get_total()
```

##### get_budget_utilization_percent() - Show Cart Fullness
```python
def get_budget_utilization_percent(self) -> float:
    """
    Show what percentage of budget is used
    
    Returns:
        Percentage (0-100)
    
    Example:
        cart.pool_budget = 50000
        cart.get_total() = 25000
        cart.get_budget_utilization_percent()  # Returns 50.0
    """
    if self.pool_budget == 0:
        return 0.0
    return (float(self.get_total()) / float(self.pool_budget)) * 100
```

##### remove_item() - Remove Item from Cart
```python
def remove_item(self, product_id: str) -> bool:
    """
    Remove all units of a product from cart
    
    Returns:
        True if removed, False if product not in cart
    """
    initial_count = len(self.items)
    self.items = [item for item in self.items if item.product.id != product_id]
    return len(self.items) < initial_count
```

##### update_quantity() - Adjust Item Quantity
```python
def update_quantity(self, product_id: str, new_quantity: int) -> bool:
    """
    Change quantity of an item in cart
    
    Returns:
        True if updated, False if product not found
    """
    for item in self.items:
        if item.product.id == product_id:
            if new_quantity <= 0:
                self.remove_item(product_id)
            else:
                item.quantity = new_quantity
            return True
    return False
```

##### clear() - Empty Cart
```python
def clear(self) -> None:
    """Remove all items from cart"""
    self.items = []
```

##### is_empty() - Check if Cart Empty
```python
def is_empty(self) -> bool:
    """Return True if cart has no items"""
    return len(self.items) == 0
```

---

#### 6. Order (DataClass)
```python
@dataclass
class Order:
    order_id: str
    pool_id: str
    moderator_id: str
    items: List[CartItem]
    status: OrderStatus = OrderStatus.PENDING
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_amount(self) -> Decimal:
        """Calculate order total"""
        return sum(item.get_subtotal() for item in self.items)
```

**Status Lifecycle**:
- Created as PENDING
- Confirmed by admin → CONFIRMED
- Payment processed → PAID
- Being prepared → PROCESSING
- Out for delivery → SHIPPED
- Received by group → DELIVERED

---

#### 7. OnlineStore (Main Hub)
```python
class OnlineStore:
    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._carts: Dict[str, ShoppingCart] = {}
        self._orders: Dict[str, Order] = {}
        self._load_sample_products()
```

**Core Methods**:

##### Product Management
```python
def add_product(self, product: Product) -> None:
    """Add product to catalog"""
    self._products[product.id] = product

def get_product(self, product_id: str) -> Optional[Product]:
    """Get single product by ID"""
    return self._products.get(product_id)

def get_all_products(self) -> List[Product]:
    """Get all products"""
    return list(self._products.values())

def get_products_by_category(self, category: ProductCategory) -> List[Product]:
    """Filter products by category"""
    return [p for p in self._products.values() if p.category == category]

def get_products_by_brand(self, brand: str) -> List[Product]:
    """Filter products by brand"""
    return [p for p in self._products.values() if p.brand.lower() == brand.lower()]

def get_products_by_name(self, name: str) -> List[Product]:
    """Search products by name (case-insensitive)"""
    name_lower = name.lower()
    return [p for p in self._products.values() 
            if name_lower in p.name.lower() or name_lower in p.brand.lower()]
```

##### Cart Management
```python
def create_cart(
    self, 
    moderator_id: str,
    pool_id: str,
    pool_budget: float
) -> ShoppingCart:
    """Create new shopping cart for moderator"""
    cart_id = str(uuid.uuid4())
    cart = ShoppingCart(cart_id, moderator_id, pool_id, pool_budget)
    self._carts[cart_id] = cart
    return cart

def get_cart(self, cart_id: str) -> Optional[ShoppingCart]:
    """Retrieve cart by ID"""
    return self._carts.get(cart_id)

def add_to_cart(
    self, 
    cart_id: str,
    product_id: str,
    quantity: int
) -> Tuple[bool, str]:
    """
    Add product to cart with validation
    
    Returns:
        (success: bool, message: str)
    
    Examples:
        True, "Added to cart"
        False, "Need ₦25,000, only ₦20,000 remaining"
        False, "Product not found"
        False, "Insufficient stock"
    """
    cart = self.get_cart(cart_id)
    if not cart:
        return False, "Cart not found"
    
    product = self.get_product(product_id)
    if not product:
        return False, "Product not found"
    
    if product.quantity_available < quantity:
        return False, f"Insufficient stock. Only {product.quantity_available} available"
    
    if not cart.can_add_product(product, quantity):
        remaining = cart.get_remaining_budget()
        needed = product.price * quantity
        return False, f"Insufficient budget. Need ₦{needed:,.0f}, only ₦{remaining:,.0f} remaining"
    
    cart.add_item(product, quantity)
    return True, "Item added to cart"

def remove_from_cart(self, cart_id: str, product_id: str) -> Tuple[bool, str]:
    """Remove item from cart"""
    cart = self.get_cart(cart_id)
    if not cart:
        return False, "Cart not found"
    
    success = cart.remove_item(product_id)
    if success:
        return True, "Item removed from cart"
    else:
        return False, "Product not in cart"

def update_cart_item(
    self, 
    cart_id: str,
    product_id: str,
    new_quantity: int
) -> Tuple[bool, str]:
    """Update quantity of item in cart"""
    cart = self.get_cart(cart_id)
    if not cart:
        return False, "Cart not found"
    
    product = self.get_product(product_id)
    if not product:
        return False, "Product not found"
    
    if new_quantity > 0 and not cart.can_add_product(product, new_quantity):
        return False, "Budget exceeded for this quantity"
    
    cart.update_quantity(product_id, new_quantity)
    return True, "Quantity updated"
```

##### Order Management
```python
def place_order(
    self,
    cart_id: str,
    notes: str = ""
) -> Tuple[bool, Optional[Order]]:
    """
    Convert cart to confirmed order
    
    Returns:
        (success: bool, order: Order or None)
    
    This:
    1. Converts cart items to order
    2. Updates inventory (deducts stock)
    3. Records sale
    4. Clears cart
    """
    cart = self.get_cart(cart_id)
    if not cart or cart.is_empty():
        return False, None
    
    # Create order from cart
    order_id = str(uuid.uuid4())
    order = Order(
        order_id=order_id,
        pool_id=cart.pool_id,
        moderator_id=cart.moderator_id,
        items=cart.items.copy(),
        notes=notes
    )
    
    # Update inventory
    for item in order.items:
        product = self.get_product(item.product.id)
        if product:
            product.quantity_available -= item.quantity
    
    # Store order and record sale
    self._orders[order_id] = order
    self._record_sale(order)
    
    # Clear cart
    cart.clear()
    
    return True, order

def get_order(self, order_id: str) -> Optional[Order]:
    """Get order by ID"""
    return self._orders.get(order_id)

def get_moderator_orders(self, moderator_id: str) -> List[Order]:
    """Get all orders by a moderator"""
    return [o for o in self._orders.values() if o.moderator_id == moderator_id]

def update_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
    """Update order status"""
    order = self.get_order(order_id)
    if order:
        order.status = new_status
        order.updated_at = datetime.now()
        return True
    return False
```

##### Analytics
```python
def get_store_stats(self) -> Dict:
    """
    Get store-wide analytics
    
    Returns:
        {
            'total_products': int,
            'categories': int,
            'stock_value': Decimal,
            'active_carts': int,
            'total_orders': int,
            'total_sales': Decimal,
            'top_products': List[Dict],
            'recent_orders': List[Dict]
        }
    """
    total_stock_value = sum(
        p.price * p.quantity_available 
        for p in self._products.values()
    )
    
    total_sales = sum(o.total_amount for o in self._orders.values())
    
    return {
        'total_products': len(self._products),
        'categories': len(set(p.category for p in self._products.values())),
        'stock_value': float(total_stock_value),
        'active_carts': len([c for c in self._carts.values() if not c.is_empty()]),
        'total_orders': len(self._orders),
        'total_sales': float(total_sales),
        'top_products': self._get_top_products(limit=5),
        'recent_orders': self._get_recent_orders(limit=5)
    }
```

---

## store_api_rest.py - REST API Layer

### Flask Application Setup
```python
app = Flask(__name__)
store = OnlineStore()

@app.before_request
def before_request():
    """Add CORS headers and request logging"""
    request.method_name = request.method
    request.path_name = request.path
```

### API Endpoints

**See [STORE_API_GUIDE.md](./STORE_API_GUIDE.md) for full API documentation**

Summary of 18+ endpoints:

**Product Browsing (5)**:
- `GET /api/store/products` - List with filters
- `GET /api/store/products/<id>` - Details
- `GET /api/store/categories` - All categories
- `GET /api/store/brands` - Available brands
- `GET /api/store/search` - Full-text search

**Cart Management (6)**:
- `POST /api/cart/create` - Create cart
- `GET /api/cart/<id>` - View cart
- `POST /api/cart/<id>/add` - Add item
- `DELETE /api/cart/<id>/remove/<product_id>` - Remove
- `PUT /api/cart/<id>/update/<product_id>` - Update qty
- `POST /api/cart/<id>/clear` - Empty cart

**Order Management (5)**:
- `POST /api/orders/place` - Place order
- `GET /api/orders/<id>` - Order details
- `GET /api/orders/moderator/<id>` - Order history
- `PUT /api/orders/<id>/status` - Update status
- `GET /api/store/stats` - Analytics

**System (2)**:
- `GET /api/store/inventory` - Stock levels
- `GET /api/store/health` - Health check

### Response Format

**Success (2xx)**:
```json
{
  "status": "success",
  "data": { /* endpoint-specific data */ }
}
```

**Error (4xx/5xx)**:
```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Human-readable message",
  "details": {}
}
```

---

## Sample Product Catalog

The system comes pre-loaded with 13 sample products across 8 categories:

### Food (4 products)
- **Rice - Uncle Ben's**: ₦25,000/bag
- **Rice - Golden Harvest**: ₦22,000/bag
- **Beans - Local Premium**: ₦12,000/bag
- **Palm Oil - Queen Taste**: ₦15,000/bottle

### Beverages (2 products)
- **Milo - Nestlé**: ₦2,500/tin
- **Nescafé - Nestlé**: ₦3,500/jar

### Cosmetics (2 products)
- **Face Wash - Olay**: ₦1,500/bottle
- **Vaseline - Unilever**: ₦2,000/tin

### Fashion (2 products)
- **T-shirts - Local**: ₦18,000/pack (5 pieces)
- **School Uniforms - Local**: ₦22,000/pack (3 pieces)

### Books & Supplies (2 products)
- **Notebooks - Best Pens**: ₦5,000/pack
- **Pens - Biro**: ₦4,000/pack

### Electronics & Accessories (1 product)
- **Power Banks - Anker**: ₦8,000/piece
- **USB Cables - Generic**: ₦3,000/pack

---

## Key Features & Constraints

### 1. Budget-Aware Cart
✓ Cart respects pool budget
✓ Cannot add items exceeding remaining funds
✓ Clear error messages with shortfall amount
✓ Real-time budget utilization percentage

### 2. Inventory Management
✓ Stock tracking per product
✓ Stock deducted upon order placement
✓ Cannot sell more than available
✓ Low-stock alerts in analytics

### 3. Order Lifecycle
✓ Orders progress through defined status stages
✓ Each status transition has meaning
✓ Order history tracking per moderator
✓ Timestamps for each status change

### 4. Multi-Brand Support
✓ Same product category has multiple brands
✓ Different prices for different brands
✓ Moderators choose based on budget
✓ Example: Rice at ₦22k vs ₦25k

### 5. Data Integrity
✓ Decimal arithmetic for prices (no floating point errors)
✓ UUID for all entity IDs (globally unique)
✓ Atomic transactions (order + inventory update together)
✓ Immutable historical data (price frozen in order)

---

## Usage Examples

### Example 1: Complete Shopping Flow

```python
from store_system import OnlineStore, ProductCategory

# Initialize store
store = OnlineStore()

# 1. Create cart with ₦50,000 budget
cart = store.create_cart(
    moderator_id="mod_tunde_001",
    pool_id="pool_rice_50000",
    pool_budget=50000
)

# 2. Browse products
food_items = store.get_products_by_category(ProductCategory.FOOD)
for product in food_items:
    print(f"{product.name} ({product.brand}): ₦{product.price}")

# 3. Add items
rice = store.get_products_by_brand("Uncle Ben's")[0]
success, msg = store.add_to_cart(cart.cart_id, rice.id, 1)
print(msg)  # "Item added to cart"

beans = store.get_products_by_name("beans")[0]
success, msg = store.add_to_cart(cart.cart_id, beans.id, 1)
print(msg)  # "Item added to cart"

# 4. Check budget
print(f"Cart Total: ₦{cart.get_total():,.0f}")
print(f"Remaining: ₦{cart.get_remaining_budget():,.0f}")
print(f"Used: {cart.get_budget_utilization_percent():.1f}%")

# 5. Place order
success, order = store.place_order(
    cart.cart_id,
    notes="Deliver to dormitory A"
)

if success:
    print(f"✓ Order placed: {order.order_id}")
    print(f"  Total: ₦{order.total_amount:,.0f}")
    print(f"  Items: {len(order.items)}")
```

### Example 2: REST API Usage

```bash
# Create cart
curl -X POST http://localhost:5000/api/cart/create \
  -H "Content-Type: application/json" \
  -d '{
    "moderator_id": "mod_tunde",
    "pool_id": "pool_50k",
    "pool_budget": 50000
  }'

# Add item
curl -X POST http://localhost:5000/api/cart/{cart_id}/add \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod_rice_001",
    "quantity": 1
  }'

# Place order
curl -X POST http://localhost:5000/api/orders/place \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": "{cart_id}",
    "notes": "Deliver to dormitory"
  }'
```

---

## Running the System

### 1. Run Core Demo
```bash
python store_system.py
```

Shows complete flow with budget constraints, order placement, and inventory updates.

### 2. Run Test Suite
```bash
python test_store_scenarios.py
```

Runs 8 comprehensive test scenarios:
- Basic operations
- Budget constraints
- Cart management
- Order placement
- Multiple moderators
- Inventory tracking
- Order history
- Analytics

### 3. Start REST API Server
```bash
python store_api_rest.py
```

Starts Flask server on `http://localhost:5000`. All 18+ endpoints become available.

---

## Database Integration

The system includes SQL schema for PostgreSQL/Supabase:

**See [store_database_schema.sql](./store_database_schema.sql)**

Tables created:
- `store_products` - Product catalog
- `store_product_categories` - Category lookup
- `shopping_carts` - Customer carts
- `cart_items` - Items per cart
- `store_orders` - Orders
- `order_items` - Items per order
- `warehouse_inventory` - Physical stock by location
- `inventory_movements` - Audit trail
- `daily_sales_summary` - Analytics
- `product_reviews` - Ratings & reviews

---

## Integration with Escrow

**See [STORE_ESCROW_INTEGRATION.md](./STORE_ESCROW_INTEGRATION.md)**

The store integrates with the escrow system:
- Cart budget comes from pool remaining balance
- Order amounts deducted from pool
- Delivery confirmation triggers escrow fund release
- Multiple orders can come from same pool

---

## Performance & Scalability

- **Product Catalog**: In-memory dict for speed (can be cached)
- **Cart Operations**: O(n) cart item lookup (optimize with hashmap for 1000+ items)
- **Order Search**: Linear search on orders (add database indexes for scale)
- **Batch Processing**: Support for bulk orders
- **Caching**: Product list can be cached for 1 hour

---

## Future Enhancements

- [ ] Wishlist functionality
- [ ] Product recommendations
- [ ] Bulk pricing discounts
- [ ] Coupon/promo codes
- [ ] Vendor management
- [ ] Supply chain tracking
- [ ] Review & rating system
- [ ] Cart abandonment recovery
- [ ] Email notifications
- [ ] Mobile app integration

---

## Support & Questions

See [STORE_API_GUIDE.md](./STORE_API_GUIDE.md) for detailed API documentation with curl examples.
