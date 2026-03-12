"""
Campus Pinduoduo: Database Initialization Script
Sets up Supabase PostgreSQL schema for both escrow and store systems
Run this ONCE to initialize the database
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def read_sql_file(filename: str) -> str:
    """Read SQL file from workspace"""
    filepath = Path(__file__).parent / filename
    if not filepath.exists():
        print(f"❌ File not found: {filename}")
        return ""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def initialize_database():
    """Initialize Supabase database with schemas"""
    
    print("\n" + "="*70)
    print("🚀 Campus Pinduoduo - Database Initialization")
    print("="*70 + "\n")
    
    # Check environment variables
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not anon_key:
        print("❌ ERROR: Missing Supabase credentials!")
        print("\n📋 Steps to fix:")
        print("1. Go to https://supabase.com and create a project")
        print("2. Get your SUPABASE_URL and SUPABASE_ANON_KEY from Settings → API")
        print("3. Create .env file with these values:")
        print("   SUPABASE_URL=your_url")
        print("   SUPABASE_ANON_KEY=your_key")
        print("4. Run this script again\n")
        sys.exit(1)
    
    print("✅ Found Supabase credentials")
    print(f"   URL: {url}")
    print(f"   Key: {anon_key[:20]}...\n")
    
    # Import Supabase after checking credentials
    try:
        from supabase import create_client, Client
        print("✅ Supabase library imported\n")
    except ImportError:
        print("❌ supabase-py not installed!")
        print("   Run: pip install supabase\n")
        sys.exit(1)
    
    # Connect to Supabase
    try:
        client = create_client(url, anon_key)
        print("✅ Connected to Supabase\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}\n")
        sys.exit(1)
    
    # SQL files to execute
    sql_files = [
        ("database_schema.sql", "Escrow System Schema"),
        ("store_database_schema.sql", "Store System Schema"),
        ("rls_policies.sql", "Row Level Security (RLS) Policies"),
    ]
    
    print("📊 Initializing database tables...\n")
    
    for filename, description in sql_files:
        print(f"  Loading {description}...")
        sql_content = read_sql_file(filename)
        
        if not sql_content:
            print(f"    ⚠️  Skipped (file not found)\n")
            continue
        
        try:
            # Execute SQL through REST API
            # Note: For production, you might want to use a different method
            # For now, we'll just indicate what needs to be done
            
            print(f"    ⏳ Ready to execute ({len(sql_content)} chars)")
            print(f"    📝 Instructions:")
            print(f"       1. Open Supabase Dashboard")
            print(f"       2. Go to SQL Editor → New Query")
            print(f"       3. Copy contents of {filename}")
            print(f"       4. Paste into SQL Editor and Run")
            print()
            
        except Exception as e:
            print(f"    ❌ Error: {e}\n")
    
    print("="*70)
    print("✅ Database Initialization Guide Complete!")
    print("="*70 + "\n")
    
    print("📋 NEXT STEPS:")
    print("1. Use Supabase SQL Editor (GUI method - easiest)")
    print("   - Supabase Dashboard → SQL Editor")
    print("   - Create new query for each SQL file")
    print("   - Copy-paste and run\n")
    
    print("2. Or use psql command line:")
    print("   - psql -h your-db.supabase.co -U postgres -d postgres")
    print("   - \\i database_schema.sql")
    print("   - \\i store_database_schema.sql")
    print("   - \\i rls_policies.sql\n")
    
    print("3. Test connection:")
    print("   python test_supabase_connection.py\n")
    

if __name__ == "__main__":
    initialize_database()
