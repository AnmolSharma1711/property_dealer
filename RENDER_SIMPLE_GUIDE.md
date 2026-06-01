# Back to Render - Simple Cron Job Deployment

## 🚀 Simple Step-by-Step

### Step 1: Create PostgreSQL Database First

1. Go to **https://render.com**
2. Click **"New +"** → **"PostgreSQL"**
3. Fill in:
   - **Name:** `broker-db`
   - **Region:** Ohio (or your choice)
   - **Plan:** Free tier
4. Click **"Create"**
5. **COPY** the **Internal Connection String** (you'll need it)
   - Format: `postgresql://...`

---

### Step 2: Create Backend Web Service

1. Click **"New +"** → **"Web Service"**
2. Select your repo: `AnmolSharma1711/property_dealer`
3. Fill in:
   - **Name:** `broker-backend`
   - **Branch:** `main`
   - **Runtime:** Python
   - **Region:** Ohio (same as DB)
   - **Build Command:**
     ```
     pip install -r backend/requirements.txt && cd backend/core && python manage.py migrate && python manage.py collectstatic --noinput && python create_admin.py
     ```
   - **Start Command:**
     ```
     cd backend/core && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2
     ```

4. Click **"Advanced"** → **"Add Environment Variables":**
   - `DEBUG` = `False`
   - `PYTHONUNBUFFERED` = `1`
   - `PYTHON_VERSION` = `3.12`
   - `DATABASE_URL` = (paste from PostgreSQL)
   - `SECRET_KEY` = (generate random string)
   - `REDIS_URL` = (your Redis URL)
   - `GROQ_API_KEY` = (your API key)
   - `SERPAPI_API_KEY` = (your API key)
   - `ADMIN_USERNAME` = `admin`
   - `ADMIN_PASSWORD` = (your password)
   - `ADMIN_EMAIL` = `admin@example.com`

5. Click **"Create Web Service"**
6. Wait 5-10 minutes for deploy

---

### Step 3: Create Frontend Static Site

1. Click **"New +"** → **"Static Site"**
2. Select your repo: `AnmolSharma1711/property_dealer`
3. Fill in:
   - **Name:** `broker-frontend`
   - **Branch:** `main`
   - **Build Command:**
     ```
     cd frontend && npm install && npm run build
     ```
   - **Publish Directory:** `frontend/dist`

4. Click **"Advanced"** → **"Add Environment Variables":**
   - `VITE_API_URL` = `https://broker-backend.onrender.com/api`
     (replace with your actual backend URL)

5. Click **"Create"**
6. Wait 3-5 minutes

---

### Step 4: Create Celery Cron Job

1. Click **"New +"** → **"Cron Job"**
2. Select your repo: `AnmolSharma1711/property_dealer`
3. Fill in:
   - **Name:** `broker-celery-worker`
   - **Branch:** `main`
   - **Schedule:** `*/15 * * * *` (every 15 minutes)
   - **Runtime:** Python
   - **Region:** Ohio
   - **Build Command:**
     ```
     pip install -r backend/requirements.txt
     ```
   - **Run Command:**
     ```
     cd backend/core && celery -A core worker -l info --concurrency=1 -t 300
     ```

4. Click **"Advanced"** → **"Add Environment Variables"** (SAME as backend):
   - `DEBUG` = `False`
   - `PYTHONUNBUFFERED` = `1`
   - `PYTHON_VERSION` = `3.12`
   - `DATABASE_URL` = (paste from PostgreSQL)
   - `SECRET_KEY` = (same as backend)
   - `REDIS_URL` = (same as backend)
   - `GROQ_API_KEY` = (same as backend)
   - `SERPAPI_API_KEY` = (same as backend)
   - `ADMIN_USERNAME` = `admin`
   - `ADMIN_PASSWORD` = (same as backend)
   - `ADMIN_EMAIL` = (same as backend)

5. Click **"Create"**

---

### Step 5: Add Persistent Disk to Backend

1. Go to **broker-backend** service
2. Click **"Settings"** tab
3. Scroll to **"Disks"**
4. Click **"Add Disk"**
5. Fill in:
   - **Name:** `broker-data`
   - **Mount Path:** `/var/data`
   - **Size:** `5 GB`
6. Click **"Create"**
7. Service will redeploy

---

### Step 6: Update Frontend API URL

After backend deploys:

1. Go to **broker-frontend** service
2. Click **"Environment"**
3. Update `VITE_API_URL` to actual backend URL
   - Get URL from broker-backend service page
   - Format: `https://broker-backend-xxxxx.onrender.com/api`
4. Click **"Save"**
5. Frontend will redeploy

---

## ✅ Verification

### Check Backend
- Open: `https://broker-backend-xxxxx.onrender.com/admin/`
- Should show Django login ✓

### Check Frontend
- Open: `https://broker-frontend-xxxxx.onrender.com/`
- Should show React app ✓

### Check Cron Job
- Dashboard → `broker-celery-worker`
- Click **"Events"** tab
- Should show runs every 15 minutes ✓
- Click **"Logs"** tab
- Should show: `worker: Ready to accept tasks` ✓

---

## 🔄 Cron Job Schedule

Current: `*/15 * * * *` (every 15 minutes)

Change schedule in `render.yaml` if needed:
- `*/5 * * * *` = Every 5 minutes
- `0 * * * *` = Every hour
- `0 0 * * *` = Daily at midnight

Then push to GitHub and Render redeploys automatically.

---

## 💾 Data Persistence

✅ **PostgreSQL Database** - All data persists
✅ **Disk Mount** (`/var/data`) - Files persist
✅ **Redis** (external) - Task queue data persists

**Result:** No data loss on restarts!

---

## ⚠️ Card Required for Render

Render does require card details to deploy. But:
- You only pay for what you use
- Free tier has generous limits
- Can cancel anytime

Alternatively, use **Railway.app** (no card required) but setup is manual.

---

## 🎯 Done!

Your app is now:
- ✅ Running Django backend with PostgreSQL
- ✅ Running React frontend
- ✅ Running Celery tasks every 15 minutes
- ✅ Data persists across restarts
- ✅ No GitHub Actions needed

Enjoy! 🚀
