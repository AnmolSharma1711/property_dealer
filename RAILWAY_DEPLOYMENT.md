# Deploy to Railway.app (No Card Required)

Railway is a modern deployment platform similar to Render but simpler and without payment requirements for free tier.

## 🚀 Quick Start Deployment

### Step 1: Sign Up on Railway

1. Go to **https://railway.app**
2. Click **"Start Project"**
3. Sign up with **GitHub** (recommended)
4. Authorize Railway to access your GitHub

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub"**
3. Select your repository: `AnmolSharma1711/property_dealer`
4. Select `main` branch

### Step 3: Configure Services

Railway will auto-detect services. Configure each:

#### PostgreSQL (Database)
1. Click **"Add"** → **"PostgreSQL"**
2. Name: `postgres`
3. Plan: Free tier ✓
4. Click **"Deploy"**

#### Backend (Django)
1. Click **"Add"** → **"GitHub Repo"**
2. Select your repo
3. Set these environment variables:
   ```
   DEBUG=False
   SECRET_KEY=<generate strong random string>
   PYTHONUNBUFFERED=1
   PYTHON_VERSION=3.12
   REDIS_URL=<your Redis URL>
   GROQ_API_KEY=<your API key>
   SERPAPI_API_KEY=<your API key>
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=<strong password>
   ADMIN_EMAIL=admin@example.com
   ```
4. **Build Command:**
   ```
   pip install -r backend/requirements.txt && cd backend/core && python manage.py migrate && python manage.py collectstatic --noinput && python create_admin.py
   ```
5. **Start Command:**
   ```
   cd backend/core && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2
   ```
6. **Root Directory:** `backend/core`
7. Click **"Deploy"**

#### Frontend (React)
1. Click **"Add"** → **"GitHub Repo"**
2. Select your repo
3. Set environment variables:
   ```
   VITE_API_URL=https://backend-production.up.railway.app/api
   ```
   (Replace with actual backend URL after deployment)
4. **Build Command:**
   ```
   cd frontend && npm install && npm run build
   ```
5. **Start Command:**
   ```
   cd frontend && npm run preview
   ```
6. **Root Directory:** `frontend`
7. Click **"Deploy"**

#### Celery Worker (Background Tasks)
1. Click **"Add"** → **"GitHub Repo"**
2. Select your repo
3. Set SAME environment variables as backend
4. **Build Command:**
   ```
   pip install -r backend/requirements.txt
   ```
5. **Start Command:**
   ```
   cd backend/core && celery -A core worker -l info --concurrency=1 -t 300
   ```
6. **Root Directory:** `backend/core`
7. Click **"Deploy"**

### Step 4: Connect Services

Railway uses environment variables to connect services:

1. **Backend needs PostgreSQL:**
   - Railway automatically sets `DATABASE_URL`
   - Add to backend environment: `DATABASE_URL=${{Postgres.DATABASE_URL}}`

2. **Frontend needs Backend URL:**
   - Get Backend URL from Railway dashboard
   - Add to frontend: `VITE_API_URL=https://your-backend-url/api`

3. **Celery needs same database:**
   - Add same `DATABASE_URL` as backend

### Step 5: Verify Deployment

Check each service:

**Backend:**
- Open the service URL from Railway dashboard
- Should show Django running (might be blank but no errors)
- Check admin: `/admin/` endpoint

**Frontend:**
- Open the service URL
- Should show React app

**Database:**
- Open PostgreSQL service
- Should show "Connected" status

**Celery:**
- Open service logs
- Should show: `worker: Ready to accept tasks`

---

## 📊 Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| Free Tier | ✅ $5/month credit | ❌ Requires card |
| Setup | ✅ Simpler | Complex |
| GitHub | ✅ Direct connect | ✅ Direct connect |
| Database | ✅ Included | ✅ Included |
| Cron Jobs | ✅ Supported | ✅ Supported |
| Data Persistence | ✅ PostgreSQL | ✅ PostgreSQL |

---

## 🔧 Local Development Testing Before Deploy

Before pushing to Railway, test locally:

```bash
# Activate venv
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Test backend
cd backend/core
python manage.py runserver

# In another terminal, test frontend
cd frontend
npm install
npm run dev
```

If both run locally without errors, they'll work on Railway!

---

## 📝 Environment Variables Needed

Collect these before deployment:

```
DEBUG=False
SECRET_KEY=your-secret-key
PYTHONUNBUFFERED=1
PYTHON_VERSION=3.12
REDIS_URL=your-redis-url
GROQ_API_KEY=your-groq-key
SERPAPI_API_KEY=your-serpapi-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=strong-password
ADMIN_EMAIL=admin@example.com
```

Get values from your local `.env` file:
```bash
cat backend/.env
```

---

## 🐛 Troubleshooting

### Build Fails - "requirements.txt not found"
- Make sure `buildCommand` has correct path:
  ```
  pip install -r backend/requirements.txt
  ```

### Database Connection Error
- Check `DATABASE_URL` is set in backend and celery-worker
- Railway sets this automatically but you may need to reference it

### Frontend Can't Connect to Backend
- Make sure `VITE_API_URL` is set in frontend
- Use the backend URL from Railway dashboard
- Format: `https://your-backend-name.up.railway.app/api`

### Celery Not Processing Tasks
- Check logs: Railway → celery-worker → Logs
- Verify `REDIS_URL` is set correctly
- Check database connection: `DATABASE_URL`

### Static Files Not Serving
- Django collectstatic runs in build command
- Should be in `backend/core/staticfiles/`

---

## 📊 Persistent Data

Railway includes:
- ✅ PostgreSQL database (persists data)
- ✅ File system for each service (doesn't persist across redeploys)
- ✅ Redis (external service, you provide URL)

All your property data stays in PostgreSQL, so it's safe!

---

## 🎯 Next Steps After Deployment

1. **Test the application:**
   - Open frontend URL
   - Try adding a property
   - Check admin panel

2. **Monitor logs:**
   - Railway → Each Service → Logs
   - Look for errors

3. **Add custom domain (optional):**
   - Railway → Domain → Add custom domain
   - Configure DNS at your registrar

4. **Enable auto-redeploy:**
   - Railway → Service → Deployments → Enable auto-deploy

---

## 💡 Tips

- Railway redeploys on every GitHub push to `main` branch
- Check logs in real-time on Railway dashboard
- Free tier includes 5GB bandwidth/month
- Can add paid plan later if needed (no card required initially)

Good luck! 🚀
