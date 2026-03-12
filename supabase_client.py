"""
Campus Pinduoduo: Supabase Client Module
Handles all database operations with Supabase PostgreSQL backend
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError(
        "supabase-py not installed. Run: pip install supabase"
    )

# ============================================================================
# SUPABASE CLIENT INITIALIZATION
# ============================================================================

class SupabaseManager:
    """Singleton for Supabase database operations"""
    
    _instance = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase connection"""
        if self._client is None:
            self._connect()
    
    @staticmethod
    def _connect():
        """Establish connection to Supabase"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError(
                "Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env file. "
                "See SUPABASE_SETUP.md for configuration instructions."
            )
        
        SupabaseManager._client = create_client(url, key)
    
    @property
    def client(self) -> Client:
        """Get Supabase client"""
        if self._client is None:
            self._connect()
        return self._client
    
    # ========================================================================
    # STORE TABLES - PRODUCTS
    # ========================================================================
    
    def get_all_products(self, active_only: bool = True) -> List[Dict]:
        """Get all products from inventory"""
        query = self.client.table("store_products").select("*")
        
        if active_only:
            query = query.eq("is_active", True)
        
        response = query.execute()
        return response.data or []
    
    def get_products_by_category(self, category_id: str) -> List[Dict]:
        """Get products in specific category"""
        response = (
            self.client.table("store_products")
            .select("*")
            .eq("category_id", category_id)
            .eq("is_active", True)
            .execute()
        )
        return response.data or []
    
    def get_products_by_brand(self, brand: str) -> List[Dict]:
        """Get products by brand"""
        response = (
            self.client.table("store_products")
            .select("*")
            .eq("brand", brand)
            .eq("is_active", True)
            .execute()
        )
        return response.data or []
    
    def search_products(self, search_term: str) -> List[Dict]:
        """Search products by name or description"""
        response = (
            self.client.table("store_products")
            .select("*")
            .ilike("product_name", f"%{search_term}%")
            .execute()
        )
        return response.data or []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get single product by ID"""
        response = (
            self.client.table("store_products")
            .select("*")
            .eq("product_id", product_id)
            .single()
            .execute()
        )
        return response.data if response.data else None
    
    def update_product_inventory(
        self, product_id: str, new_quantity: int
    ) -> bool:
        """Update product inventory after order"""
        response = (
            self.client.table("store_products")
            .update({"quantity_available": new_quantity})
            .eq("product_id", product_id)
            .execute()
        )
        return bool(response.data)
    
    # ========================================================================
    # STORE TABLES - SHOPPING CARTS
    # ========================================================================
    
    def create_cart(self, pool_id: str, moderator_id: str, budget: float) -> str:
        """Create new shopping cart"""
        response = (
            self.client.table("shopping_carts")
            .insert({
                "pool_id": pool_id,
                "moderator_id": moderator_id,
                "pool_budget": budget,
                "status": "ACTIVE"
            })
            .execute()
        )
        return response.data[0]["cart_id"] if response.data else None
    
    def add_to_cart(
        self, 
        cart_id: str, 
        product_id: str, 
        quantity: int, 
        unit_price: float
    ) -> bool:
        """Add item to shopping cart"""
        response = (
            self.client.table("cart_items")
            .insert({
                "cart_id": cart_id,
                "product_id": product_id,
                "quantity_requested": quantity,
                "unit_price": unit_price
            })
            .execute()
        )
        return bool(response.data)
    
    def get_cart_contents(self, cart_id: str) -> List[Dict]:
        """Get all items in cart"""
        response = (
            self.client.table("cart_items")
            .select("*")
            .eq("cart_id", cart_id)
            .execute()
        )
        return response.data or []
    
    def remove_from_cart(self, cart_item_id: str) -> bool:
        """Remove item from cart"""
        response = (
            self.client.table("cart_items")
            .delete()
            .eq("cart_item_id", cart_item_id)
            .execute()
        )
        return bool(response.data)
    
    # ========================================================================
    # STORE TABLES - ORDERS
    # ========================================================================
    
    def create_order(
        self,
        pool_id: str,
        moderator_id: str,
        total_amount: float,
        delivery_address: str = None
    ) -> Optional[str]:
        """Create new order from cart"""
        response = (
            self.client.table("store_orders")
            .insert({
                "pool_id": pool_id,
                "moderator_id": moderator_id,
                "status": "PENDING",
                "total_amount": total_amount,
                "delivery_address": delivery_address
            })
            .execute()
        )
        return response.data[0]["order_id"] if response.data else None
    
    def add_order_item(
        self,
        order_id: str,
        product_id: str,
        quantity: int,
        unit_price: float
    ) -> bool:
        """Add item to order"""
        response = (
            self.client.table("order_items")
            .insert({
                "order_id": order_id,
                "product_id": product_id,
                "quantity_ordered": quantity,
                "unit_price": unit_price,
                "line_total": quantity * unit_price
            })
            .execute()
        )
        return bool(response.data)
    
    def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Update order status"""
        response = (
            self.client.table("store_orders")
            .update({"status": new_status})
            .eq("order_id", order_id)
            .execute()
        )
        return bool(response.data)
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order details"""
        response = (
            self.client.table("store_orders")
            .select("*")
            .eq("order_id", order_id)
            .single()
            .execute()
        )
        return response.data if response.data else None
    
    def get_pool_orders(self, pool_id: str) -> List[Dict]:
        """Get all orders for a pool"""
        response = (
            self.client.table("store_orders")
            .select("*")
            .eq("pool_id", pool_id)
            .execute()
        )
        return response.data or []
    
    # ========================================================================
    # ESCROW TABLES - POOLS & PARTICIPANTS
    # ========================================================================
    
    def create_pool(
        self,
        pool_name: str,
        goal_amount: float,
        moderator_id: str,
        description: str = None
    ) -> Optional[str]:
        """Create new escrow pool"""
        response = (
            self.client.table("pools")
            .insert({
                "pool_name": pool_name,
                "goal_amount": goal_amount,
                "moderator_id": moderator_id,
                "description": description,
                "status": "open",
                "total_collected": 0
            })
            .execute()
        )
        return response.data[0]["id"] if response.data else None
    
    def join_pool(
        self,
        pool_id: str,
        user_id: str,
        amount: float
    ) -> bool:
        """Add participant to pool"""
        # Add to participants table
        response = (
            self.client.table("pool_participants")
            .insert({
                "pool_id": pool_id,
                "user_id": user_id,
                "contributed_amount": amount,
                "status": "active"
            })
            .execute()
        )
        
        if not response.data:
            return False
        
        # Create escrow transaction
        self.create_escrow_transaction(
            pool_id,
            user_id,
            amount,
            "deposit"
        )
        
        return True
    
    def get_pool(self, pool_id: str) -> Optional[Dict]:
        """Get pool details"""
        response = (
            self.client.table("pools")
            .select("*")
            .eq("id", pool_id)
            .single()
            .execute()
        )
        return response.data if response.data else None
    
    def update_pool_status(self, pool_id: str, status: str) -> bool:
        """Update pool status"""
        response = (
            self.client.table("pools")
            .update({"status": status})
            .eq("id", pool_id)
            .execute()
        )
        return bool(response.data)
    
    # ========================================================================
    # ESCROW TABLES - TRANSACTIONS & LEDGER
    # ========================================================================
    
    def create_escrow_transaction(
        self,
        pool_id: str,
        user_id: str,
        amount: float,
        transaction_type: str,
        description: str = None
    ) -> bool:
        """Record escrow transaction"""
        response = (
            self.client.table("escrow_transactions")
            .insert({
                "pool_id": pool_id,
                "user_id": user_id,
                "amount": amount,
                "transaction_type": transaction_type,
                "description": description,
                "status": "completed"
            })
            .execute()
        )
        return bool(response.data)
    
    def record_confirmation(
        self,
        pool_id: str,
        user_id: str,
        confirmation_pin: str
    ) -> bool:
        """Record participant confirmation"""
        response = (
            self.client.table("participant_confirmations")
            .insert({
                "pool_id": pool_id,
                "user_id": user_id,
                "pin_entered": confirmation_pin,
                "confirmation_status": "confirmed"
            })
            .execute()
        )
        return bool(response.data)
    
    def get_escrow_ledger(self, pool_id: str) -> List[Dict]:
        """Get all transactions for pool"""
        response = (
            self.client.table("escrow_transactions")
            .select("*")
            .eq("pool_id", pool_id)
            .execute()
        )
        return response.data or []
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def health_check(self) -> bool:
        """Test connection to Supabase"""
        try:
            response = self.client.table("users").select("*").limit(1).execute()
            return True
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        response = self.client.table("users").select("*").execute()
        return response.data or []
    
    def get_categories(self) -> List[Dict]:
        """Get all product categories"""
        response = (
            self.client.table("store_product_categories")
            .select("*")
            .order("display_order")
            .execute()
        )
        return response.data or []


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

db = SupabaseManager()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_db() -> SupabaseManager:
    """Get database instance"""
    return db


def check_connection() -> bool:
    """Check if database is connected"""
    return db.health_check()
