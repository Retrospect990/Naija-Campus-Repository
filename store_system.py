"""
Campus Pinduoduo: Online Store System
Allows moderators to browse products, manage shopping cart, and place orders
Integrated with escrow system - cart respects pool budget
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal
import uuid

# ============================================================================
# ENUMS & TYPES
# ============================================================================

class ProductCategory(Enum):
    """Product categories"""
    FOOD = "food"
    BEVERAGES = "beverages"
    FASHION = "fashion"
    ELECTRONICS = "electronics"
    HOME = "home_goods"
    BOOKS = "books"
    COSMETICS = "cosmetics"
    SPORTS = "sports"

class OrderStatus(Enum):
    """Order status throughout lifecycle"""
    PENDING = "pending"  # In cart, not confirmed
    CONFIRMED = "confirmed"  # Order placed
    PAID = "paid"  # Payment collected from escrow
    PROCESSING = "processing"  # Being prepared
    SHIPPED = "shipped"  # On the way
    DELIVERED = "delivered"  # Received
    CANCELLED = "cancelled"  # Order cancelled

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Product:
    """Product in the store inventory"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    category: ProductCategory = ProductCategory.FOOD
    description: str = ""
    brand: str = ""
    price: float = 0.0
    quantity_available: int = 0
    unit: str = "pcs"  # pieces, kg, liters, boxes, packs
    supplier: str = ""
    image_url: str = ""
    ratings: float = 4.5  # 0-5
    reviews_count: int = 0
    
    def __str__(self):
        return f"{self.brand} {self.name} - ₦{self.price:,.0f} ({self.quantity_available} {self.unit})"

@dataclass
class CartItem:
    """Item in shopping cart"""
    product: Product
    quantity: int
    added_at: datetime = field(default_factory=datetime.now)
    
    def get_subtotal(self) -> float:
        """Calculate subtotal for this item"""
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.product.brand} {self.product.name} × {self.quantity} = ₦{self.get_subtotal():,.0f}"

@dataclass
class ShoppingCart:
    """Shopping cart for a moderator"""
    cart_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    moderator_id: str = ""
    pool_id: str = ""
    items: List[CartItem] = field(default_factory=list)
    pool_budget: float = 0.0  # Total money available in the pool
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_item(self, product: Product, quantity: int) -> bool:
        """Add item to cart if budget allows"""
        # Check if item already in cart
        for item in self.items:
            if item.product.id == product.id:
                # Item exists, update quantity
                old_quantity = item.quantity
                item.quantity += quantity
                
                # Check if total exceeds budget
                if self.get_total() > self.pool_budget:
                    item.quantity = old_quantity  # Revert
                    return False
                return True
        
        # New item
        new_item = CartItem(product=product, quantity=quantity)
        
        # Check if adding this item exceeds budget
        if self.get_total() + new_item.get_subtotal() > self.pool_budget:
            return False
        
        self.items.append(new_item)
        return True
    
    def remove_item(self, product_id: str) -> bool:
        """Remove item from cart"""
        original_count = len(self.items)
        self.items = [item for item in self.items if item.product.id != product_id]
        return len(self.items) < original_count
    
    def update_quantity(self, product_id: str, new_quantity: int) -> bool:
        """Update quantity of item in cart"""
        for item in self.items:
            if item.product.id == product_id:
                old_quantity = item.quantity
                item.quantity = new_quantity
                
                # Check if new total exceeds budget
                if self.get_total() > self.pool_budget:
                    item.quantity = old_quantity  # Revert
                    return False
                return True
        
        return False
    
    def get_total(self) -> float:
        """Calculate total cart value"""
        return sum(item.get_subtotal() for item in self.items)
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget after cart"""
        return self.pool_budget - self.get_total()
    
    def get_budget_utilization_percent(self) -> float:
        """Get percentage of budget used"""
        if self.pool_budget == 0:
            return 0
        return (self.get_total() / self.pool_budget) * 100
    
    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self.items) == 0
    
    def can_add_product(self, product: Product, quantity: int) -> bool:
        """Check if product can be added to cart"""
        potential_total = self.get_total() + (product.price * quantity)
        return potential_total <= self.pool_budget
    
    def clear(self):
        """Clear all items from cart"""
        self.items = []
    
    def __str__(self):
        if self.is_empty():
            return "🛒 Cart is empty"
        
        output = f"🛒 Cart ({len(self.items)} items)\n"
        output += "─" * 80 + "\n"
        for i, item in enumerate(self.items, 1):
            output += f"  {i}. {item}\n"
        output += "─" * 80 + "\n"
        output += f"  Total: ₦{self.get_total():,.0f}\n"
        output += f"  Budget: ₦{self.pool_budget:,.0f}\n"
        output += f"  Remaining: ₦{self.get_remaining_budget():,.0f}\n"
        output += f"  Utilization: {self.get_budget_utilization_percent():.1f}%\n"
        return output

@dataclass
class Order:
    """Confirmed order"""
    order_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    moderator_id: str = ""
    pool_id: str = ""
    items: List[Dict] = field(default_factory=list)  # {product_id, name, quantity, price, subtotal}
    total_amount: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    notes: str = ""
    
    def __str__(self):
        return f"Order {self.order_id} - ₦{self.total_amount:,.0f} ({self.status.value})"

# ============================================================================
# ONLINE STORE CLASS
# ============================================================================

class OnlineStore:
    """Central store managing products, inventory, and orders"""
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.carts: Dict[str, ShoppingCart] = {}  # cart_id -> cart
        self.orders: Dict[str, Order] = {}  # order_id -> order
        self.moderator_carts: Dict[str, str] = {}  # moderator_id -> cart_id
        self.total_sales: float = 0.0
        
        # Initialize sample products
        self._load_sample_products()
    
    def _load_sample_products(self):
        """Load sample products into store"""
        sample_products = [
            # Food Category
            Product(
                name="Rice (50kg bag)",
                category=ProductCategory.FOOD,
                brand="Uncle Ben's",
                description="Premium long-grain white rice",
                price=25000,
                quantity_available=5,
                unit="bags",
                supplier="FoodMart Wholesale",
                ratings=4.8,
                reviews_count=512
            ),
            Product(
                name="Rice (50kg bag)",
                category=ProductCategory.FOOD,
                brand="Golden Harvest",
                description="Budget-friendly white rice",
                price=22000,
                quantity_available=8,
                unit="bags",
                supplier="FoodMart Wholesale",
                ratings=4.5,
                reviews_count=298
            ),
            Product(
                name="Beans (10kg)",
                category=ProductCategory.FOOD,
                brand="Agro King",
                description="High-quality sorted beans",
                price=12000,
                quantity_available=10,
                unit="bags",
                supplier="Farm Fresh",
                ratings=4.6,
                reviews_count=423
            ),
            Product(
                name="Palm Oil (25 liters)",
                category=ProductCategory.FOOD,
                brand="Pure Harvest",
                description="Cold-pressed palm oil",
                price=15000,
                quantity_available=6,
                unit="tins",
                supplier="Oil Company",
                ratings=4.7,
                reviews_count=567
            ),
            
            # Beverages
            Product(
                name="Milo (400g)",
                category=ProductCategory.BEVERAGES,
                brand="Milo",
                description="Chocolate malted drink",
                price=2500,
                quantity_available=50,
                unit="boxes",
                supplier="Nestle Distribution",
                ratings=4.9,
                reviews_count=1200
            ),
            Product(
                name="Nescafé (200g)",
                category=ProductCategory.BEVERAGES,
                brand="Nescafé",
                description="Instant coffee",
                price=3500,
                quantity_available=30,
                unit="jars",
                supplier="Nestle Distribution",
                ratings=4.7,
                reviews_count=890
            ),
            
            # Cosmetics
            Product(
                name="Face Wash (100ml)",
                category=ProductCategory.COSMETICS,
                brand="Clean & Clear",
                description="Deep cleaning face wash",
                price=1500,
                quantity_available=40,
                unit="bottles",
                supplier="Beauty Cosmetics",
                ratings=4.6,
                reviews_count=756
            ),
            Product(
                name="Body Lotion (500ml)",
                category=ProductCategory.COSMETICS,
                brand="Vaseline",
                description="Moisturizing body lotion",
                price=2000,
                quantity_available=35,
                unit="bottles",
                supplier="Beauty Cosmetics",
                ratings=4.8,
                reviews_count=2100
            ),
            
            # Fashion
            Product(
                name="Plain T-Shirt (Pack of 10)",
                category=ProductCategory.FASHION,
                brand="Basic Wear",
                description="Cotton crew neck t-shirts",
                price=18000,
                quantity_available=7,
                unit="packs",
                supplier="Fashion Wholesale",
                ratings=4.4,
                reviews_count=234
            ),
            Product(
                name="School Uniforms (Pack of 5)",
                category=ProductCategory.FASHION,
                brand="EduWear",
                description="Standard school uniforms",
                price=22000,
                quantity_available=4,
                unit="packs",
                supplier="Fashion Wholesale",
                ratings=4.5,
                reviews_count=189
            ),
            
            # Books & Stationery
            Product(
                name="Notebook (100 pages, Pack of 10)",
                category=ProductCategory.BOOKS,
                brand="School Essentials",
                description="Ruled notebooks for students",
                price=5000,
                quantity_available=20,
                unit="packs",
                supplier="Stationery Hub",
                ratings=4.3,
                reviews_count=445
            ),
            Product(
                name="Pens (50-pack)",
                category=ProductCategory.BOOKS,
                brand="BIC",
                description="Ballpoint pens assorted colors",
                price=4000,
                quantity_available=25,
                unit="packs",
                supplier="Stationery Hub",
                ratings=4.7,
                reviews_count=678
            ),
            
            # Electronics
            Product(
                name="Power Bank (20000mAh)",
                category=ProductCategory.ELECTRONICS,
                brand="Anker",
                description="Fast charging power bank",
                price=8000,
                quantity_available=15,
                unit="pcs",
                supplier="Tech Store",
                ratings=4.8,
                reviews_count=2300
            ),
            Product(
                name="USB Cable (2 meters, Pack of 5)",
                category=ProductCategory.ELECTRONICS,
                brand="Generic",
                description="Durable charging cables",
                price=3000,
                quantity_available=50,
                unit="packs",
                supplier="Tech Store",
                ratings=4.2,
                reviews_count=567
            ),
        ]
        
        for product in sample_products:
            self.products[product.id] = product
    
    def get_products_by_category(self, category: ProductCategory) -> List[Product]:
        """Get all products in a category"""
        return [p for p in self.products.values() if p.category == category]
    
    def get_products_by_name(self, search_term: str) -> List[Product]:
        """Search products by name"""
        term = search_term.lower()
        return [p for p in self.products.values() 
                if term in p.name.lower() or term in p.brand.lower()]
    
    def get_products_by_brand(self, brand: str) -> List[Product]:
        """Get all products from a specific brand"""
        return [p for p in self.products.values() if p.brand.lower() == brand.lower()]
    
    def get_all_products(self) -> List[Product]:
        """Get all products sorted by rating"""
        return sorted(self.products.values(), 
                     key=lambda x: (x.ratings, x.reviews_count), 
                     reverse=True)
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        return self.products.get(product_id)
    
    def create_cart(self, moderator_id: str, pool_id: str, pool_budget: float) -> ShoppingCart:
        """Create new shopping cart for moderator"""
        cart = ShoppingCart(
            moderator_id=moderator_id,
            pool_id=pool_id,
            pool_budget=pool_budget
        )
        self.carts[cart.cart_id] = cart
        self.moderator_carts[moderator_id] = cart.cart_id
        return cart
    
    def get_cart(self, cart_id: str) -> Optional[ShoppingCart]:
        """Get cart by ID"""
        return self.carts.get(cart_id)
    
    def get_moderator_cart(self, moderator_id: str) -> Optional[ShoppingCart]:
        """Get cart for a moderator"""
        cart_id = self.moderator_carts.get(moderator_id)
        if cart_id:
            return self.carts.get(cart_id)
        return None
    
    def add_to_cart(self, cart_id: str, product_id: str, quantity: int) -> tuple[bool, str]:
        """Add product to cart"""
        cart = self.get_cart(cart_id)
        if not cart:
            return False, "Cart not found"
        
        product = self.get_product(product_id)
        if not product:
            return False, "Product not found"
        
        if quantity <= 0:
            return False, "Quantity must be positive"
        
        if quantity > product.quantity_available:
            return False, f"Only {product.quantity_available} {product.unit} available in stock"
        
        if not cart.can_add_product(product, quantity):
            remaining = cart.get_remaining_budget()
            needed = product.price * quantity
            return False, f"Insufficient budget. Need ₦{needed:,.0f}, but only ₦{remaining:,.0f} remaining"
        
        if cart.add_item(product, quantity):
            return True, f"Added {quantity} × {product.brand} {product.name} to cart"
        
        return False, "Failed to add item to cart"
    
    def remove_from_cart(self, cart_id: str, product_id: str) -> tuple[bool, str]:
        """Remove product from cart"""
        cart = self.get_cart(cart_id)
        if not cart:
            return False, "Cart not found"
        
        if cart.remove_item(product_id):
            return True, "Item removed from cart"
        
        return False, "Item not found in cart"
    
    def update_cart_item(self, cart_id: str, product_id: str, new_quantity: int) -> tuple[bool, str]:
        """Update quantity of item in cart"""
        cart = self.get_cart(cart_id)
        if not cart:
            return False, "Cart not found"
        
        if new_quantity <= 0:
            return self.remove_from_cart(cart_id, product_id)
        
        if cart.update_quantity(product_id, new_quantity):
            return True, f"Updated quantity to {new_quantity}"
        
        return False, "Could not update quantity (exceeds budget or item not found)"
    
    def place_order(self, cart_id: str, notes: str = "") -> tuple[bool, Order]:
        """Convert cart to confirmed order"""
        cart = self.get_cart(cart_id)
        if not cart:
            return False, None
        
        if cart.is_empty():
            return False, None
        
        # Create order from cart
        order = Order(
            moderator_id=cart.moderator_id,
            pool_id=cart.pool_id,
            total_amount=cart.get_total(),
            notes=notes
        )
        
        # Add items to order
        for item in cart.items:
            order.items.append({
                'product_id': item.product.id,
                'name': f"{item.product.brand} {item.product.name}",
                'brand': item.product.brand,
                'quantity': item.quantity,
                'unit': item.product.unit,
                'price': item.product.price,
                'subtotal': item.get_subtotal()
            })
        
        order.status = OrderStatus.CONFIRMED
        order.confirmed_at = datetime.now()
        
        # Save order
        self.orders[order.order_id] = order
        
        # Update inventory
        for item in cart.items:
            product = self.get_product(item.product.id)
            if product:
                product.quantity_available -= item.quantity
        
        # Update sales
        self.total_sales += order.total_amount
        
        # Clear cart
        cart.clear()
        
        return True, order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def get_moderator_orders(self, moderator_id: str) -> List[Order]:
        """Get all orders for a moderator"""
        return [o for o in self.orders.values() if o.moderator_id == moderator_id]
    
    def update_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """Update order status"""
        order = self.get_order(order_id)
        if order:
            order.status = new_status
            if new_status == OrderStatus.DELIVERED:
                order.delivered_at = datetime.now()
            return True
        return False
    
    def get_store_stats(self) -> Dict:
        """Get store statistics"""
        return {
            'total_products': len(self.products),
            'total_orders': len(self.orders),
            'total_sales': self.total_sales,
            'active_carts': len([c for c in self.carts.values() if not c.is_empty()]),
            'stock_value': sum(p.price * p.quantity_available for p in self.products.values()),
            'categories': len(ProductCategory)
        }

# ============================================================================
# DEMO & TESTING
# ============================================================================

def demo_store():
    """Interactive demonstration of online store"""
    
    print("\n" + "="*80)
    print("CAMPUS PINDUODUO: ONLINE STORE SYSTEM")
    print("="*80)
    
    # Initialize store
    store = OnlineStore()
    
    # Create mock moderator and pool
    moderator_id = "mod_chioma_001"
    pool_id = "pool_rice_50000"
    pool_budget = 50000.0
    
    print(f"\n📋 SCENARIO: Moderator browsing store for ₦{pool_budget:,.0f} pool")
    print(f"   Moderator: {moderator_id}")
    print(f"   Pool: {pool_id}")
    
    # ===== STEP 1: BROWSE PRODUCTS =====
    print("\n" + "─"*80)
    print("STEP 1: BROWSING PRODUCTS")
    print("─"*80)
    
    foodProducts = store.get_products_by_category(ProductCategory.FOOD)
    print(f"\n🍚 Available Food Products ({len(foodProducts)} items):")
    print("-" * 80)
    for i, product in enumerate(foodProducts, 1):
        print(f"{i}. {product.brand:15} | {product.name:20} | ₦{product.price:>8,.0f} | {product.quantity_available} {product.unit}")
        print(f"   Rating: ⭐ {product.ratings}/5 ({product.reviews_count} reviews)")
    
    # ===== STEP 2: CREATE CART =====
    print("\n" + "─"*80)
    print("STEP 2: CREATING SHOPPING CART")
    print("─"*80)
    
    cart = store.create_cart(moderator_id, pool_id, pool_budget)
    print(f"\n✅ Cart created: {cart.cart_id}")
    print(f"   Budget: ₦{cart.pool_budget:,.0f}")
    
    # ===== STEP 3: ADD ITEMS TO CART =====
    print("\n" + "─"*80)
    print("STEP 3: ADDING ITEMS TO CART")
    print("─"*80)
    
    # Add Uncle Ben's rice (25000 × 1 = 25000)
    uncle_bens = foodProducts[0]
    success, msg = store.add_to_cart(cart.cart_id, uncle_bens.id, 1)
    print(f"\n1. {msg}")
    
    # Add beans (12000 × 2 = 24000)
    beans = foodProducts[2]
    success, msg = store.add_to_cart(cart.cart_id, beans.id, 2)
    print(f"2. {msg}")
    
    # Print cart status
    print(cart)
    
    # Try to add more than budget allows
    print("\n💳 Testing budget limit...")
    palm_oil = [p for p in store.get_all_products() if "Palm Oil" in p.name][0]
    success, msg = store.add_to_cart(cart.cart_id, palm_oil.id, 1)
    print(f"   Trying to add ₦{palm_oil.price:,.0f} palm oil: {msg}")
    
    # ===== STEP 4: MODIFY CART =====
    print("\n" + "─"*80)
    print("STEP 4: MODIFYING CART")
    print("─"*80)
    
    # Update beans quantity
    success, msg = store.update_cart_item(cart.cart_id, beans.id, 1)
    print(f"\n✏️  {msg}")
    print(cart)
    
    # ===== STEP 5: BROWSE DIFFERENT CATEGORY =====
    print("\n" + "─"*80)
    print("STEP 5: BROWSING OTHER CATEGORIES")
    print("─"*80)
    
    cosmetics = store.get_products_by_category(ProductCategory.COSMETICS)
    print(f"\n💄 Available Cosmetics ({len(cosmetics)} items):")
    print("-" * 80)
    for i, product in enumerate(cosmetics, 1):
        if store.get_cart(cart.cart_id).can_add_product(product, 1):
            budget_ok = "✅"
        else:
            budget_ok = "❌"
        print(f"{i}. {product.brand:15} | {product.name:25} | ₦{product.price:>7,.0f} | {budget_ok}")
    
    # Add some cosmetics
    vaseline = cosmetics[1]
    success, msg = store.add_to_cart(cart.cart_id, vaseline.id, 5)
    print(f"\nAdding Vaseline: {msg}")
    print(cart)
    
    # ===== STEP 6: PLACE ORDER =====
    print("\n" + "─"*80)
    print("STEP 6: PLACING ORDER")
    print("─"*80)
    
    success, order = store.place_order(
        cart.cart_id, 
        notes="Deliver to faculty of sciences, room 203"
    )
    
    if success:
        print(f"\n✅ ORDER CONFIRMED!")
        print(f"   Order ID: {order.order_id}")
        print(f"   Status: {order.status.value}")
        print(f"   Items ({len(order.items)}):")
        for item in order.items:
            print(f"      • {item['brand']} {item['name']} × {item['quantity']} {item['unit']} = ₦{item['subtotal']:,.0f}")
        print(f"   Total: ₦{order.total_amount:,.0f}")
        print(f"   Notes: {order.notes}")
    
    # ===== STEP 7: STORE STATISTICS =====
    print("\n" + "─"*80)
    print("STEP 7: STORE STATISTICS")
    print("─"*80)
    
    stats = store.get_store_stats()
    print(f"\n📊 Store Status:")
    print(f"   Total Products: {stats['total_products']}")
    print(f"   Total Orders: {stats['total_orders']}")
    print(f"   Total Sales: ₦{stats['total_sales']:,.0f}")
    print(f"   Active Carts: {stats['active_carts']}")
    print(f"   Stock Value: ₦{stats['stock_value']:,.0f}")
    
    # ===== STEP 8: VIEW ORDER HISTORY =====
    print("\n" + "─"*80)
    print("STEP 8: ORDER HISTORY FOR MODERATOR")
    print("─"*80)
    
    orders = store.get_moderator_orders(moderator_id)
    print(f"\n📦 {len(orders)} order(s) for {moderator_id}:")
    for order in orders:
        print(f"   • {order}")
    
    print("\n" + "="*80)
    print("STORE DEMO COMPLETED!")
    print("="*80 + "\n")

if __name__ == "__main__":
    demo_store()
