# Deployment Guide - Property Broker AI

## ⭐ Recommended: Deploy to Railway.app (No Card Required)

**Important:** Render now requires card details. Use **Railway instead** - it's free and has no payment required.

👉 **See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for complete Railway deployment steps**

Railway benefits:
- ✅ Free tier with $5/month credit
- ✅ No card required to start
- ✅ PostgreSQL database included
- ✅ Automatic GitHub deployment
- ✅ Better for free/low-cost projects
- ✅ Simpler setup than Render

**Quick start:** Go to https://railway.app → Sign in with GitHub → Deploy from repo

---

## 📋 Deployment Options

Choose one approach below:

### Option A: Quick Deploy with render.yaml (RECOMMENDED ⭐)

**👉 Follow the corrected steps:** See [RENDER_FIXED_BLUEPRINT.md](RENDER_FIXED_BLUEPRINT.md)

This document has:
- ✅ Fixed render.yaml (all YAML errors resolved)
- ✅ Correct deployment steps with Blueprint
- ✅ Post-deployment setup (environment variables, persistent disk)
- ✅ Verification checklist
- ✅ Troubleshooting guide

**Time required:** ~20 minutes  
**Effort:** ⭐ (easiest)

---

### Option B: Manual Deploy (Advanced)

Manually create each service. Not recommended unless you need custom configuration.

#### Step 1: Prepare Code
- [ ] Commit all changes to GitHub: `git add . && git commit -m "ready for deployment" && git push`
- [ ] Verify `.env.example` exists with all required variables
- [ ] Check `requirements.txt` has all dependencies

#### Step 2: Create Database
- [ ] Go to Render → New → PostgreSQL
- [ ] Name: `broker-db`
- [ ] Region: Choose your region
- [ ] Click Create
- [ ] **COPY** the Internal Connection String

#### Step 3: Deploy Backend
- [ ] Go to Render → New → Web Service
- [ ] Select your GitHub repo
- [ ] Name: `broker-backend`
- [ ] Region: Same as database
- [ ] Runtime: Python 3
- [ ] Build Command: `pip install -r backend/requirements.txt && cd backend/core && python manage.py migrate && python manage.py collectstatic --noinput && python create_admin.py`
- [ ] Start Command: `cd backend/core && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
- [ ] Scroll down → Click "Advanced"
- [ ] Add Environment Variables (table below)
- [ ] Click Create Web Service
- [ ] Wait 5-10 minutes for deployment
- [ ] Copy the URL (e.g., `broker-backend.onrender.com`)

**Environment Variables for Backend:**

```
DEBUG=False
SECRET_KEY=<generate strong random string>
DATABASE_URL=<paste PostgreSQL connection string>
REDIS_URL=<your existing Redis URL>
GROQ_API_KEY=<your API key>
SERPAPI_API_KEY=<your API key>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong password>
ADMIN_EMAIL=admin@yoursite.com
PYTHONUNBUFFERED=1
PYTHON_VERSION=3.12.4
```

#### Step 4: Deploy Frontend
- [ ] Go to Render → New → Static Site
- [ ] Select your GitHub repo
- [ ] Name: `broker-frontend`
- [ ] Branch: main
- [ ] Build Command: `cd frontend && npm install && npm run build`
- [ ] Publish Directory: `frontend/dist`
- [ ] Click "Advanced"
- [ ] Add Environment Variable:
  ```
  VITE_API_URL=https://broker-backend.onrender.com
  ```
- [ ] Click Create
- [ ] Wait 3-5 minutes
- [ ] Copy the URL (e.g., `broker-frontend.onrender.com`)

#### Step 5: Update CORS (Backend)
- [ ] Go back to broker-backend service
- [ ] Click Environment tab
- [ ] Add: `FRONTEND_URL=https://broker-frontend.onrender.com`
- [ ] Click "Manual Deploy" → "Deploy latest commit"
- [ ] Wait for redeploy

### 6. Deploy Celery Worker (AUTOMATIC via render.yaml) ⚠️

**✨ NEW: Celery now runs via Render Cron Job!**

The `render.yaml` file includes an automatic cron job for Celery tasks. No manual setup needed!

**What this means:**
- ✅ Celery tasks run automatically every 15 minutes
- ✅ More reliable than GitHub Actions
- ✅ No need for Background Worker service
- ✅ Runs on Render infrastructure (not GitHub)

**Just deploy using render.yaml (see below) and it's automatically configured!**

---

### 7. Deploy Using render.yaml (RECOMMENDED - Automatic Everything)

This is the **fastest and easiest way**. It sets up everything automatically:

```bash
# 1. Make sure render.yaml is in your repo root
# 2. Commit changes
git add . && git commit -m "Deploy with render.yaml" && git push

# 3. Go to Render Dashboard
# 4. Click "New +" → "Web Service"
# 5. Select your GitHub repo
# 6. Scroll down → "Infrastructure as Code"
# 7. Click "Use render.yaml" 
# 8. Select render.yaml file
# 9. Click "Create"
```

Render will automatically create:
- ✅ PostgreSQL Database (broker-db)
- ✅ Django Backend (broker-backend) with persistent disk storage
- ✅ React Frontend (broker-frontend)
- ✅ Celery Worker Cron Job (broker-celery-worker) - runs every 15 minutes

**That's it! No manual steps needed.**

For detailed info on cron jobs and data persistence, see [RENDER_CRON_AND_PERSISTENCE.md](RENDER_CRON_AND_PERSISTENCE.md)

### 7. Test Your App
- [ ] Open `https://broker-frontend.onrender.com` in browser
- [ ] Try selecting a locality (should trigger AI analysis)
- [ ] Try creating a chat
- [ ] Check messages work
- [ ] Open admin: `https://broker-backend.onrender.com/admin/`

---

## ✅ Verify Deployment

After deployment, verify everything is working:

### Check Backend
```bash
curl https://broker-backend.onrender.com/api/localities/
# Should return JSON data (may be empty on first deploy)
```

### Check Celery Tasks
1. Go to Render Dashboard
2. Click **broker-celery-worker** service
3. Check **Events** tab - should show scheduled runs every 15 minutes
4. Check **Logs** tab - should show task processing

Example successful log:
```
worker: Ready to accept tasks
properties.tasks.enrich_locality_pipeline received
properties.tasks.enrich_locality_pipeline succeeded
```

### Verify Data Persistence
The `render.yaml` setup includes:
- ✅ PostgreSQL database (persists data)
- ✅ Mounted disk storage on backend (5GB for files/logs)
- ✅ Automatic Redis backup (via REDIS_URL)

Data will survive Render restarts and service updates.

---

## 📊 Data Persistence Overview

| Component | Persistence | Details |
|-----------|-------------|---------|
| PostgreSQL | ✅ Persistent | Primary data storage, automatic backups |
| Disk Storage | ✅ Persistent | 5GB mounted to backend (/var/data) |
| Redis | ✅ Persistent | Managed service (external), encrypted |
| Celery Tasks | ✅ Persistent | Queued tasks stored in Redis |
| Session Data | ✅ Persistent | Stored in PostgreSQL |

**Bottom line:** All data persists across restarts. No data loss.

See [RENDER_CRON_AND_PERSISTENCE.md](RENDER_CRON_AND_PERSISTENCE.md) for more details.

---

## 🔧 Useful Links

| Link | Purpose |
|------|---------|
| https://render.com/docs | Render Documentation |
| https://broker-backend.onrender.com/admin/ | Admin Panel |
| https://broker-frontend.onrender.com | Your Live App |

---

## ⚠️ Troubleshooting

### Backend shows "503 Service Unavailable"
→ Check the Logs tab in Render  
→ Look for Python errors  
→ Common issues: missing environment variable, database migration failed

### Frontend shows blank page / 404
→ Check browser console (F12)  
→ Look for API errors  
→ Verify `VITE_API_URL` is correct in environment  
→ Try hard refresh (Ctrl+Shift+R)

### Chat/API not working
→ Go to Django admin  
→ Check if Chat table exists (it should after migration)  
→ Verify backend has correct `DATABASE_URL`  
→ Verify frontend `VITE_API_URL` has no trailing slash

### Images not loading
→ In production, you need cloud storage (S3)  
→ For now, use database/API for storing image references

---

## 💾 After Deployment

1. **Create Admin User**: 
   - In Render, go to broker-backend → Shell
   - Run: `python backend/core/manage.py createsuperuser`
   - Follow prompts

2. **Monitor**: Check Render dashboard for errors/performance

3. **Backup**: Render PostgreSQL has automatic backups

4. **Custom Domain**: Go to service settings → add domain

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Django Docs: https://docs.djangoproject.com
- React/Vite: https://vitejs.dev

Good luck with your deployment! 🎉
