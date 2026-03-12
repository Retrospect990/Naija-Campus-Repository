# 🚀 Supabase Integration Guide

## Step 1: Create a Supabase Project (2 minutes)

1. Go to [supabase.com](https://supabase.com)
2. Click **"Start your project"** or sign in
3. Click **"New project"**
4. Fill in details:
   - **Project name**: `campus-pinduoduo`
   - **Database password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
5. Click **"Create new project"** and wait 2-3 minutes

---

## Step 2: Get Your Credentials (1 minute)

After project is created:

1. Go to **Settings** → **API** (left sidebar)
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Anon Key**: `ey...` (public key, safe to share)
   - **Service Role Key**: `ey...` (KEEP SECRET! Use for backend)
3. Also save your **Database Password** from step 1

---

## Step 3: Configure Environment (1 minute)

Create `.env` file in `campus-pinduoduo/` folder:

```bash
# Supabase API
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=ey...
SUPABASE_SERVICE_KEY=ey...

# Database (optional - direct connection)
# DB_HOST=xxxxx.supabase.co
# DB_USER=postgres
# DB_PASSWORD=your_database_password
# DB_NAME=postgres

# Application
ENVIRONMENT=development
APP_PORT=5000
MODERATOR_COMMISSION_RATE=0.10
DELIVERY_CONFIRMATION_THRESHOLD=0.70
```

> **Never commit `.env` to git!** It's already in `.gitignore`

---

## Step 4: Initialize Database (1 minute)

### Option A: Using Supabase SQL Editor (Easiest)

1. In Supabase dashboard, go to **SQL Editor**
2. Click **"New query"**
3. Copy-paste contents of **`database_schema.sql`** (escrow tables)
4. Click **"Run"**
5. Repeat for **`store_database_schema.sql`**
6. Repeat for **`rls_policies.sql`**

### Option B: Using Python Script

```bash
python initialize_database.py
```

This will automatically run all SQL files.

---

## Step 5: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

This now includes:
- `supabase` - PostgreSQL client
- `python-dotenv` - Environment configuration
- `flask` - API server
- `requests` - HTTP calls
- `pytest` - Testing

---

## Step 6: Test Connection (1 minute)

```bash
python test_supabase_connection.py
```

**Expected output:**
```
✅ Connected to Supabase!
✅ Database schema initialized
✅ Ready for production
```

---

## Step 7: Run System with Supabase (1 minute)

### Option A: Store System Only
```bash
python store_system.py
```

### Option B: Escrow System Only
```bash
python escrow_demo.py
```

### Option C: API Server (Recommended)
```bash
python store_api_rest.py
```

Then in another terminal:
```bash
curl http://localhost:5000/api/store/products
```

---

## Security Best Practices

### 1. Keep Service Key Secret
- Never commit `.env` to git
- Never share Service Key in code
- Use environment variables for production

### 2. Row Level Security (RLS)
- All tables have RLS policies
- Users can only see their own data
- Moderators can see pool data
- Run `rls_policies.sql` to enable

### 3. API Key Rotation
- Rotate keys every 90 days in production
- Supabase dashboard → Settings → API Keys

---

## Troubleshooting

### "Connection refused"
- Check SUPABASE_URL is correct
- Ensure internet connection
- Verify internet isn't blocking

### "Authentication failed"
- Check SUPABASE_ANON_KEY is copied correctly
- Verify no trailing spaces in `.env`
- Try SUPABASE_SERVICE_KEY instead

### "Table does not exist"
- Ensure all SQL files were executed
- Check table names match (case-sensitive)
- Run `python initialize_database.py` again

### "RLS policy blocks query"
- Run `rls_policies.sql` in SQL Editor
- Ensure user is authenticated
- Check policy matches users table IDs

---

## What Gets Stored in Supabase

### Escrow System Tables (10)
- `users`, `pools`, `pool_participants`
- `escrow_accounts`, `escrow_transactions`
- `participant_confirmations`
- `moderator_commissions`
- `audit_log`, `notifications`, `notifications_log`

### Store System Tables (13)
- `store_product_categories`, `store_products`
- `store_product_variants`, `store_product_reviews`
- `shopping_carts`, `cart_items`
- `store_orders`, `order_items`, `order_status_history`
- `warehouse_inventory`, `inventory_transactions`
- `store_analytics`

**Total: 23 tables, all ready for production**

---

## Next Steps

1. ✅ Create Supabase project
2. ✅ Add credentials to `.env`
3. ✅ Run SQL initialization
4. ✅ Test connection
5. ✅ Deploy API server
6. 🔄 Connect frontend to `/api/` endpoints
7. 🔄 Set up monitoring & backups

---

**Questions?** Check documentation in:
- [STORE_API_GUIDE.md](STORE_API_GUIDE.md) - API endpoints
- [STORE_ESCROW_INTEGRATION.md](STORE_ESCROW_INTEGRATION.md) - Integration guide
- [store_database_schema.sql](store_database_schema.sql) - Table structure
