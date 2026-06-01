# Fixed: Deploy with render.yaml (Blueprint)

## ✅ What Was Fixed

The `render.yaml` blueprint had several validation errors. All are now fixed:

- ✅ Removed invalid `env:` fields (should be `envVars:`)
- ✅ Removed `disks:` from services (added manually after deployment)
- ✅ Fixed `staticSiteDir` → `staticPublishPath`
- ✅ Removed top-level `envVars:` block
- ✅ Added `repo:` and `branch:` to all services
- ✅ Simplified PostgreSQL service (no custom config)
- ✅ Used `sync: false` for external API keys

---

## 🚀 Deployment Steps

### Step 1: Update Your Repo URL in render.yaml

Edit `render.yaml` and replace all instances of:
```
https://github.com/yourusername/your-repo
```

With your actual GitHub URL:
```
https://github.com/YourUsername/your-repo
```

There are 3 services that need this:
- broker-backend
- broker-frontend
- broker-celery-worker

### Step 2: Push to GitHub

```bash
git add render.yaml
git commit -m "Fix render.yaml blueprint"
git push origin main
```

### Step 3: Deploy Blueprint on Render

1. Go to **Render Dashboard**
2. Click **"New +"** button
3. Click **"Blueprint"**
4. Click **"Public GitHub repository"**
5. Enter your repo URL: `https://github.com/YourUsername/your-repo`
6. Click **"Connect"**
7. Review the services (should show 4 with no errors):
   - ✅ broker-db (PostgreSQL)
   - ✅ broker-backend (Web Python)
   - ✅ broker-frontend (Web Node)
   - ✅ broker-celery-worker (Cron)
8. Click **"Deploy"**
9. **Wait 15-20 minutes** for deployment to complete

---

## ⚠️ After Deployment: Manual Setup Required

The blueprint creates the services, but you need to manually set environment variables and add disk storage.

### Step 1: Set Environment Variables

Go to Render Dashboard → **broker-backend** → **Environment**

Add these variables (get values from your `.env` file):

| Key | Value | Source |
|-----|-------|--------|
| `REDIS_URL` | `redis://...` | Your external Redis service |
| `GROQ_API_KEY` | Your API key | From your account |
| `SERPAPI_API_KEY` | Your API key | From your account |

Save changes. Backend will redeploy automatically.

### Step 2: Add Persistent Disk

Go to Render Dashboard → **broker-backend** → **Settings**

Scroll to **Disks** section:

1. Click **"Create Disk"**
2. Fill in:
   - **Disk name:** `broker-data`
   - **Mount path:** `/var/data`
   - **Size (GB):** `5`
3. Click **"Create"**
4. The service will restart (~2-3 minutes)

✅ Now data persists across restarts!

### Step 3: Verify Deployment

Check each service:

**PostgreSQL:**
- Dashboard → `broker-db` → Status should be "Available"

**Backend:**
- Dashboard → `broker-backend` → Status should be "Live"
- Open: `https://broker-backend.onrender.com/admin/`
- Should show Django admin login

**Frontend:**
- Dashboard → `broker-frontend` → Status should be "Live"
- Open: `https://broker-frontend.onrender.com/`
- Should show the React app

**Celery Cron Job:**
- Dashboard → `broker-celery-worker` → Status should be "Active"
- Check **Events** tab → Should show scheduled runs every 15 minutes
- Check **Logs** tab → Should show task execution

---

## 🐛 Troubleshooting

### Blueprint Shows Validation Errors

**If you see errors like:**
- `cannot unmarshal !!seq into file.Runtime`
- `field disks not found`
- `field envVars not found`

**Solution:**
1. Edit `render.yaml` locally
2. Make sure:
   - No `env:` fields (only `envVars:`)
   - No `disks:` section
   - No top-level `envVars:` block
   - All services have `repo:` and `branch:`
3. Save and push to GitHub
4. Retry blueprint deployment

### Services Won't Deploy

**Check 1:** Is repo URL correct?
```yaml
repo: https://github.com/YourActualUsername/your-repo
```

**Check 2:** Does branch exist?
```yaml
branch: main  # or your branch name
```

**Check 3:** Are dependencies installed?
- `backend/requirements.txt` exists?
- `frontend/package.json` exists?

### Environment Variables Not Working

**Problem:** Services deployed but show errors about missing API keys

**Solution:** Environment variables with `sync: false` must be set manually:

1. Go to each service → Environment tab
2. Add the variable
3. Save (service redeploys automatically)

---

## 📊 Final Architecture

After all steps:

```
┌─ PostgreSQL (broker-db) ──────┐
│  Persisted data storage       │
└──────────────────────────────┘
         ↓ CONNECTION
┌─ Backend (broker-backend) ────┐
│ + Disk mount (/var/data)      │
│ + Environment variables       │
│ + Environment variables       │ 
│ Runs: gunicorn + Django       │
└──────────────────────────────┘
    ↓                    ↓
Frontend              Cron Job
(React)          (Celery Worker)
                 Every 15 min
```

✅ **Result:** Full production setup with:
- Persistent database
- Persistent file storage
- Automatic task scheduling
- Zero data loss on restart

---

## 📝 Summary Checklist

- [ ] Updated GitHub repo URL in render.yaml (3 places)
- [ ] Pushed render.yaml to GitHub
- [ ] Deployed Blueprint on Render
- [ ] All 4 services show in dashboard
- [ ] Set REDIS_URL env var on backend
- [ ] Set GROQ_API_KEY env var on backend
- [ ] Set SERPAPI_API_KEY env var on backend
- [ ] Created persistent disk (broker-data) on backend
- [ ] Backend admin accessible
- [ ] Frontend loads successfully
- [ ] Celery cron job shows scheduled runs
