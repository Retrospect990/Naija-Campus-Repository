# 🚀 Supabase Integration Checklist

Complete these steps to deploy your Campus Pinduoduo system to Supabase.

---

## ✅ Phase 1: Supabase Setup (5-10 minutes)

- [ ] **1.1** Go to [https://supabase.com](https://supabase.com)
- [ ] **1.2** Click "Start your project" → Create account
- [ ] **1.3** Create new project called "campus-pinduoduo"
- [ ] **1.4** Wait for project to initialize (2-3 minutes)
- [ ] **1.5** Go to **Settings** → **API** (left sidebar)
- [ ] **1.6** Copy **Project URL** 
- [ ] **1.7** Copy **Anon Key** (public)
- [ ] **1.8** Copy **Service Role Key** (keep secret!)
- [ ] **1.9** Save **Database Password** from setup

---

## ✅ Phase 2: Local Configuration (2-3 minutes)

- [ ] **2.1** Open `.env` file in workspace
- [ ] **2.2** Update `SUPABASE_URL` with your project URL
- [ ] **2.3** Update `SUPABASE_ANON_KEY` with anon key
- [ ] **2.4** Update `SUPABASE_SERVICE_KEY` with service role key
- [ ] **2.5** Set `ENVIRONMENT=development`
- [ ] **2.6** Set `APP_PORT=5000`
- [ ] **2.7** Save `.env` file

---

## ✅ Phase 3: Install Dependencies (2-3 minutes)

```bash
pip install -r requirements.txt
```

Wait for installation to complete. Should see:
- ✅ flask
- ✅ supabase
- ✅ python-dotenv
- ✅ requests
- ✅ pytest
- ✅ psycopg2-binary

---

## ✅ Phase 4: Initialize Database (3-5 minutes)

### Option A: Supabase SQL Editor (Easiest)

1. [ ] **4.1** Open Supabase Dashboard
2. [ ] **4.2** Go to **SQL Editor** (left sidebar)
3. [ ] **4.3** Click **"New query"**
4. [ ] **4.4** Copy contents of [database_schema.sql](database_schema.sql)
5. [ ] **4.5** Paste into query box
6. [ ] **4.6** Click **"Run"**
7. [ ] **4.7** Wait for success message ✅
8. [ ] **4.8** Repeat steps 4.3-4.7 for **store_database_schema.sql**
9. [ ] **4.9** Repeat steps 4.3-4.7 for **rls_policies.sql**

### Option B: Python Script

```bash
python initialize_database.py
```

Then follow the on-screen instructions.

---

## ✅ Phase 5: Test Connection (1-2 minutes)

```bash
python test_supabase_connection.py
```

**Expected output:**
```
✅ Connection Successful!
✅ store_products
✅ shopping_carts
✅ store_orders
✅ pools
✅ pool_participants
```

If you see ❌ errors:
- Check `.env` values are correct
- Verify no extra spaces in `.env`
- Wait 30 seconds and try again
- Check Supabase SQL Editor for error messages

---

## ✅ Phase 6: Test with Sample Data (2-3 minutes)

### Option A: Store System Demo

```bash
python store_system.py
```

**Expected:**
- ✅ Products loaded from Supabase
- ✅ Cart created
- ✅ Budget enforced
- ✅ Order placed

### Option B: Escrow System Demo

```bash
python escrow_demo.py
```

**Expected:**
- ✅ Pool created
- ✅ Participants join
- ✅ Funds held in escrow
- ✅ Automatic release at threshold

---

## ✅ Phase 7: Run REST API (2-3 minutes)

```bash
python store_api_rest.py
```

**Expected output:**
```
 * Serving Flask app 'store_api_rest'
 * Running on http://127.0.0.1:5000
 * Debug mode: off
```

In another terminal, test endpoints:

```bash
# Test health check
curl http://localhost:5000/api/store/health

# Get products
curl http://localhost:5000/api/store/products

# Get categories
curl http://localhost:5000/api/store/categories
```

---

## ✅ Phase 8: Populate Test Data (5-10 minutes)

The system comes with seed data. Load it into database:

```bash
python seed_database.py
```

This will add:
- ✅ 50 sample products
- ✅ 8 categories
- ✅ 10 test users
- ✅ 3 sample pools

---

## ✅ Phase 9: Run Full Test Suite (3-5 minutes)

```bash
# Test store scenarios
python test_store_scenarios.py

# Test escrow scenarios
python test_scenarios.py

# Test API endpoints
python test_api.py
```

**All tests should pass:** ✅

---

## ✅ Phase 10: Deploy (Optional - for production)

For production deployment:

- [ ] **10.1** Set `ENVIRONMENT=production`
- [ ] **10.2** Create `.env.production` with prod credentials
- [ ] **10.3** Enable RLS policies (already done in phase 4)
- [ ] **10.4** Set up automated backups in Supabase
- [ ] **10.5** Configure SSL/HTTPS for API
- [ ] **10.6** Deploy API to cloud (Heroku, Railway, AWS, etc.)

---

## 🔍 Verification Checklist

Run this to verify everything is working:

```bash
echo "Checking dependencies..."
python -c "import supabase; print('✅ supabase')"
python -c "import flask; print('✅ flask')"
python -c "import dotenv; print('✅ python-dotenv')"

echo "Checking environment..."
python test_supabase_connection.py

echo "Running tests..."
python test_store_scenarios.py
python test_scenarios.py
```

---

## 📚 Documentation Reference

If you need more details:

- **API Endpoints**: See [STORE_API_GUIDE.md](STORE_API_GUIDE.md)
- **Database Schema**: See [store_database_schema.sql](store_database_schema.sql)
- **Escrow Integration**: See [STORE_ESCROW_INTEGRATION.md](STORE_ESCROW_INTEGRATION.md)
- **Full Setup Guide**: See [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

---

## ❓ Troubleshooting

### "Connection refused"
```bash
# Check Supabase URL is correct
grep SUPABASE_URL .env
# Should be: https://xxxxx.supabase.co
```

### "Authentication failed"
```bash
# Check keys are correct (no trailing spaces)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(len(os.getenv('SUPABASE_ANON_KEY')))"
# Should be around 200+ characters
```

### "Table does not exist"
```bash
# Re-run SQL schema initialization
# Go to Supabase SQL Editor and run the SQL files again
python initialize_database.py
```

### "RLS policy blocks query"
```bash
# Verify RLS policies are enabled
# In Supabase: Authentication → Policies
# Should see policies on all tables
```

---

## 🎉 Success!

Once all phases complete, you have:

✅ Supabase PostgreSQL database deployed
✅ 23 production-ready tables
✅ REST API with 18+ endpoints
✅ Complete escrow system
✅ Complete store system
✅ All tests passing
✅ All data persisted to cloud
✅ Ready for production deployment

**Next:** Connect your frontend (mobile/web) to the REST API!

---

**Need help?** Check:
- Supabase docs: https://supabase.com/docs
- Flask docs: https://flask.palletsprojects.com
- Python docs: https://docs.python.org/3/
