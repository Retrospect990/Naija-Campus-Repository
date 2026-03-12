"""
Campus Pinduoduo: Database Seeding Script
Populates Supabase with sample data for testing and demo
Run this after database schema is initialized
"""

import sys
from datetime import datetime, timedelta
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase_client import db
except ImportError:
    print("❌ supabase_client not found!")
    print("   Make sure you're in the campus-pinduoduo directory")
    sys.exit(1)


def seed_database():
    """Populate database with sample data"""
    
    print("\n" + "="*70)
    print("🌱 Campus Pinduoduo - Database Seeding")
    print("="*70 + "\n")
    
    # Test connection first
    print("🔍 Testing Supabase connection...")
    if not db.health_check():
        print("❌ Cannot connect to Supabase!\n")
        sys.exit(1)
    print("✅ Connected to Supabase\n")
    
    print("📊 Seeding sample data...\n")
    
    # Sample data: Users
    print("  Creating sample users...")
    users = [
        {
            "id": str(uuid4()),
            "name": "Damilare Okafor",
            "email": "damilare@campus.edu",
            "university": "University of Lagos",
            "is_moderator": True,
            "bank_account": "0001234567"
        },
        {
            "id": str(uuid4()),
            "name": "Tunde Adebayo",
            "email": "tunde@campus.edu",
            "university": "University of Ibadan",
            "is_moderator": False,
            "bank_account": ""
        },
        {
            "id": str(uuid4()),
            "name": "Zainab Muhammad",
            "email": "zainab@campus.edu",
            "university": "Ahmadu Bello University",
            "is_moderator": False,
            "bank_account": ""
        },
        {
            "id": str(uuid4()),
            "name": "Chioma Nwosu",
            "email": "chioma@campus.edu",
            "university": "University of Nigeria",
            "is_moderator": True,
            "bank_account": "0007654321"
        },
    ]
    
    try:
        for user in users:
            db.client.table("users").upsert(user).execute()
        print(f"     ✅ Created {len(users)} users\n")
    except Exception as e:
        print(f"     ℹ️  Users table may already exist: {str(e)[:50]}\n")
    
    # Sample data: Product Categories
    print("  Creating product categories...")
    categories = [
        {"category_name": "Food & Grains", "description": "Rice, beans, spices"},
        {"category_name": "Beverages", "description": "Drinks, juice, water"},
        {"category_name": "Fashion", "description": "Clothing and accessories"},
        {"category_name": "Electronics", "description": "Gadgets and devices"},
        {"category_name": "Home Goods", "description": "Kitchen and home items"},
        {"category_name": "Books", "description": "Textbooks and reading materials"},
        {"category_name": "Health & Beauty", "description": "Cosmetics and wellness"},
        {"category_name": "Sports", "description": "Sports equipment and apparel"},
    ]
    
    category_ids = {}
    try:
        for cat in categories:
            response = db.client.table("store_product_categories").insert(cat).execute()
            if response.data:
                category_ids[cat["category_name"]] = response.data[0]["category_id"]
        print(f"     ✅ Created {len(categories)} categories\n")
    except Exception as e:
        print(f"     ℹ️  Categories may already exist: {str(e)[:50]}\n")
    
    # Sample data: Products
    print("  Creating sample products...")
    products = [
        # Food & Grains
        {"category_id": category_ids.get("Food & Grains"), "product_name": "Uncle Ben's Rice", "brand": "Uncle Ben's", "description": "Long grain white rice", "price": 25000, "quantity_available": 50},
        {"category_id": category_ids.get("Food & Grains"), "product_name": "Golden Harvest Rice", "brand": "Golden Harvest", "description": "Premium rice", "price": 22000, "quantity_available": 40},
        {"category_id": category_ids.get("Food & Grains"), "product_name": "Beans", "brand": "Local Farmer", "description": "High quality beans", "price": 15000, "quantity_available": 60},
        {"category_id": category_ids.get("Food & Grains"), "product_name": "Seasoning Mix", "brand": "Maggi", "description": "All-purpose seasoning", "price": 5000, "quantity_available": 100},
        
        # Beverages
        {"category_id": category_ids.get("Beverages"), "product_name": "Pure Water", "brand": "Aquafina", "description": "Drinking water 500ml", "price": 500, "quantity_available": 200},
        {"category_id": category_ids.get("Beverages"), "product_name": "Orange Juice", "brand": "Minute Maid", "description": "100% orange juice", "price": 2500, "quantity_available": 80},
        {"category_id": category_ids.get("Beverages"), "product_name": "Energy Drink", "brand": "Red Bull", "description": "Energy beverage", "price": 3000, "quantity_available": 75},
        
        # Fashion
        {"category_id": category_ids.get("Fashion"), "product_name": "T-Shirt", "brand": "Gildan", "description": "Comfortable cotton shirt", "price": 8000, "quantity_available": 120},
        {"category_id": category_ids.get("Fashion"), "product_name": "Jeans", "brand": "Lee", "description": "Classic blue jeans", "price": 18000, "quantity_available": 50},
        
        # Electronics
        {"category_id": category_ids.get("Electronics"), "product_name": "Phone Charger", "brand": "Anker", "description": "USB-C fast charger", "price": 12000, "quantity_available": 90},
        {"category_id": category_ids.get("Electronics"), "product_name": "Power Bank", "brand": "Aukey", "description": "20000mAh power bank", "price": 15000, "quantity_available": 60},
        
        # Home Goods
        {"category_id": category_ids.get("Home Goods"), "product_name": "Cooking Oil", "brand": "Golden Palm", "description": "1 liter cooking oil", "price": 8000, "quantity_available": 100},
        {"category_id": category_ids.get("Home Goods"), "product_name": "Plates Set", "brand": "Luminarc", "description": "6-piece plate set", "price": 12000, "quantity_available": 40},
        
        # Books
        {"category_id": category_ids.get("Books"), "product_name": "Calculus Textbook", "brand": "Stewart", "description": "Advanced calculus", "price": 18000, "quantity_available": 20},
        
        # Health & Beauty
        {"category_id": category_ids.get("Health & Beauty"), "product_name": "Face Wash", "brand": "Cetaphil", "description": "Gentle face cleanser", "price": 4000, "quantity_available": 70},
        
        # Sports
        {"category_id": category_ids.get("Sports"), "product_name": "Running Shoes", "brand": "Nike", "description": "Comfortable running shoes", "price": 35000, "quantity_available": 30},
    ]
    
    product_count = 0
    try:
        for product in products:
            if product["category_id"]:
                response = db.client.table("store_products").insert(product).execute()
                if response.data:
                    product_count += 1
        print(f"     ✅ Created {product_count} products\n")
    except Exception as e:
        print(f"     ℹ️  Products may already exist: {str(e)[:50]}\n")
    
    # Sample data: Pools
    print("  Creating sample pools...")
    pools = [
        {
            "id": str(uuid4()),
            "pool_name": "Campus Grocery Bulk Buy",
            "goal_amount": 50000,
            "moderator_id": users[0]["id"] if users else None,
            "description": "Group buying for campus groceries",
            "status": "open",
            "total_collected": 0
        },
        {
            "id": str(uuid4()),
            "pool_name": "Textbook Pool Spring 2026",
            "goal_amount": 80000,
            "moderator_id": users[3]["id"] if len(users) > 3 else None,
            "description": "Shared textbook purchase",
            "status": "open",
            "total_collected": 0
        },
    ]
    
    try:
        for pool in pools:
            if pool["moderator_id"]:
                db.client.table("pools").insert(pool).execute()
        print(f"     ✅ Created {len(pools)} pools\n")
    except Exception as e:
        print(f"     ℹ️  Pools may already exist: {str(e)[:50]}\n")
    
    print("="*70)
    print("✅ Database Seeding Complete!")
    print("="*70 + "\n")
    
    print("📊 Summary:")
    print(f"   • {len(users)} users")
    print(f"   • {len(categories)} product categories")
    print(f"   • {product_count} products")
    print(f"   • {len(pools)} pools")
    print()
    
    print("🎯 Next steps:")
    print("   1. Run: python store_system.py")
    print("   2. Or: python store_api_rest.py")
    print("   3. Or: python test_store_scenarios.py")
    print()


if __name__ == "__main__":
    seed_database()
