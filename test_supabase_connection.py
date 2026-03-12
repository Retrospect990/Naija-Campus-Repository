"""
Campus Pinduoduo: Test Supabase Connection
Verify that Supabase is properly configured and connected
Run this after setting up your .env file
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_connection():
    """Test Supabase connection"""
    
    print("\n" + "="*70)
    print("🔍 Testing Supabase Connection")
    print("="*70 + "\n")
    
    # Check environment variables
    print("📋 Checking environment variables...")
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url:
        print("   ❌ SUPABASE_URL not found in .env")
        return False
    print(f"   ✅ SUPABASE_URL: {url}")
    
    if not anon_key:
        print("   ❌ SUPABASE_ANON_KEY not found in .env")
        return False
    print(f"   ✅ SUPABASE_ANON_KEY: {anon_key[:20]}...")
    
    if service_key:
        print(f"   ✅ SUPABASE_SERVICE_KEY: {service_key[:20]}...")
    else:
        print("   ⚠️  SUPABASE_SERVICE_KEY not found (optional for read-only)")
    
    print()
    
    # Test Supabase import
    print("📦 Checking dependencies...")
    try:
        from supabase import create_client, Client
        print("   ✅ supabase library installed\n")
    except ImportError:
        print("   ❌ supabase library not installed")
        print("      Run: pip install supabase\n")
        return False
    
    # Connect to Supabase
    print("🔗 Attempting connection to Supabase...")
    try:
        client = create_client(url, anon_key)
        print("   ✅ Client created\n")
    except Exception as e:
        print(f"   ❌ Failed to create client: {e}\n")
        return False
    
    # Test health check
    print("❤️  Performing health check...")
    try:
        response = client.table("users").select("*").limit(1).execute()
        print(f"   ✅ Health check passed")
        print(f"   ✅ Successfully queried 'users' table\n")
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg:
            print(f"   ⚠️  'users' table doesn't exist yet")
            print(f"      Run: python initialize_database.py")
        else:
            print(f"   ❌ Health check failed: {e}")
        print()
        return False
    
    # Try other tables
    print("📊 Checking database schema...")
    tables_to_check = [
        "store_products",
        "shopping_carts",
        "store_orders",
        "pools",
        "pool_participants",
    ]
    
    tables_found = 0
    for table_name in tables_to_check:
        try:
            response = client.table(table_name).select("*").limit(1).execute()
            print(f"   ✅ {table_name}")
            tables_found += 1
        except Exception as e:
            if "does not exist" in str(e):
                print(f"   ❌ {table_name} (not created yet)")
            else:
                print(f"   ❌ {table_name} (error: {str(e)[:50]})")
    
    print()
    
    # Summary
    print("="*70)
    if tables_found > 0:
        print(f"✅ Connection Successful! ({tables_found} tables found)")
        print("="*70 + "\n")
        print("🎉 Your Supabase database is ready to use!")
        print("\n📖 Next steps:")
        print("   1. Run store system: python store_system.py")
        print("   2. Run escrow system: python escrow_demo.py")
        print("   3. Run API server: python store_api_rest.py")
        return True
    else:
        print("⚠️  Connection Successful, but database not initialized")
        print("="*70 + "\n")
        print("📋 Next steps:")
        print("   1. Run: python initialize_database.py")
        print("   2. Follow instructions to set up database schema")
        print("   3. Then run: python test_supabase_connection.py")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
