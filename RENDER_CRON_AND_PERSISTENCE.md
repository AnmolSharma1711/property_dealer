# Render Cron Job & Data Persistence Setup

This guide explains how to use Render's native Cron Job service for Celery tasks and ensure data persists across restarts.

## What Changed?

✅ **Old Setup** (Not Recommended):
- Used GitHub Actions to run Celery tasks
- Required GitHub Secrets configuration
- Less reliable, more complex

✅ **New Setup** (Recommended):
- Uses Render's native Cron Job service
- Automatic scheduling on Render infrastructure
- Built-in data persistence
- No GitHub Secrets needed

---

## Why This is Better

| Feature | GitHub Actions | Render Cron |
|---------|---|---|
| Reliability | ⚠️ Dependent on GitHub | ✅ Native Render |
| Configuration | 🔧 Requires GitHub Secrets | ✅ Simple YAML |
| Cost | 💰 Uses GitHub Actions minutes | ✅ Included in Render |
| Data Persistence | ⚠️ Manual setup | ✅ Automatic |
| Maintenance | 🔧 Multiple config files | ✅ Single render.yaml |

---

## Setup Steps

### 1. Deploy Using render.yaml (Automatic)

The `render.yaml` file now includes a cron service. When you deploy using this file:

```bash
# Push your changes
git add .
git commit -m "Switch to Render cron jobs"
git push origin main
```

### 2. Connect render.yaml to Render

On Render Dashboard:
1. Click **New +** → **Web Service**
2. Select your GitHub repo
3. Scroll down and find **"Infrastructure as Code"** section
4. Click **"Use render.yaml"**
5. Select `render.yaml` from the dropdown
6. Click **"Create"**

Render will automatically create:
- ✅ PostgreSQL Database (broker-db)
- ✅ Django Backend (broker-backend)
- ✅ React Frontend (broker-frontend)  
- ✅ **Celery Worker Cron Job (broker-celery-worker)** ← NEW

### 3. Verify Cron Job is Running

After deployment:

1. Go to Render Dashboard
2. Click **"broker-celery-worker"** service
3. Check **Events** tab - should show scheduled runs every 15 minutes
4. Check **Logs** tab - should show task processing output

Example log output:
```
[2024-06-01 10:00:00] worker: Ready to accept tasks
[2024-06-01 10:00:05] properties.tasks.enrich_locality_pipeline[...] received
[2024-06-01 10:00:10] properties.tasks.enrich_locality_pipeline[...] succeeded
```

### 4. Adjust Cron Schedule (Optional)

To change how often tasks run, edit `render.yaml`:

```yaml
- type: cron
  name: broker-celery-worker
  schedule: "*/15 * * * *"  # Change this line
```

Common schedules:
- `"*/5 * * * *"` - Every 5 minutes
- `"*/15 * * * *"` - Every 15 minutes (default)
- `"0 * * * *"` - Every hour
- `"0 0 * * *"` - Daily at midnight

---

## Data Persistence

### The Problem

On Render, services restart occasionally:
- Updates/patches
- Resource scaling
- Manual restarts

Without proper configuration, data is **lost**.

### The Solution

The new `render.yaml` includes **three layers of persistence**:

#### 1️⃣ PostgreSQL Database (Primary)

```yaml
- type: pserv
  name: broker-db
  plan: starter  # Free tier includes 256MB
```

**This is your primary data store.** All properties, users, and core data is here.

✅ **Automatically persisted** - PostgreSQL handles this
✅ **Encrypted** by Render
✅ **Backed up** automatically

**To verify:**
1. Go to Render Dashboard
2. Click **broker-db** service
3. Check **Connections** tab - confirms database is running
4. All data in Django models persists here

#### 2️⃣ Mounted Disk Storage

```yaml
disks:
  - name: broker-data
    mountPath: /var/data
    sizeGB: 5  # Adjust if needed
```

This is mounted to the **broker-backend** service.

**Use cases:**
- Debug logs (currently written to files)
- Uploaded media files
- Cache data that survives restarts

**Upgrading storage:**
Edit `render.yaml`:
```yaml
disks:
  - name: broker-data
    mountPath: /var/data
    sizeGB: 50  # Increased to 50GB
```

Then redeploy.

#### 3️⃣ Redis Session Storage

The REDIS_URL you set in environment variables persists sessions and task queue data.

---

## Database Connection Verification

### Check if PostgreSQL is Being Used

On Render, verify the database configuration:

```bash
# SSH into backend service
# Run this command:
python manage.py shell

>>> from django.db import connection
>>> print(connection.settings_dict['ENGINE'])
# Should print: django.db.backends.postgresql
```

### Manual Database Backup

To backup your data on Render:

1. Go to Render Dashboard
2. Click **broker-db**
3. Click **Settings** tab
4. Scroll to **Backups**
5. Click **"Create Backup"**

This creates a backup you can download.

---

## Troubleshooting

### Celery Tasks Not Running

**Check 1: Is cron job scheduled?**
```bash
# Check Render dashboard logs for:
"worker: Ready to accept tasks"
```

**Check 2: Are environment variables set?**
1. Go to **broker-celery-worker** service
2. Click **Environment** tab
3. Verify all variables are present:
   - DATABASE_URL ✓
   - REDIS_URL ✓
   - GROQ_API_KEY ✓
   - SERPAPI_API_KEY ✓

**Check 3: Is Redis connection working?**
```bash
# SSH into backend
redis-cli -u $REDIS_URL ping
# Should return: PONG
```

### Data Still Being Lost

**Step 1: Verify PostgreSQL is active**
```bash
python manage.py dbshell
# Should connect successfully
```

**Step 2: Check disk space**
```bash
df -h /var/data
# Verify it's not full
```

**Step 3: Increase storage if needed**
Edit render.yaml and increase `sizeGB` value

**Step 4: Force redeploy**
```bash
git add render.yaml
git commit -m "Fix data persistence"
git push origin main
# Render will redeploy with new configuration
```

### Cron Job Timeout

If tasks take longer than 25 minutes, increase timeout:

Edit `startCommand` in render.yaml:
```yaml
startCommand: cd backend/core && celery -A core worker -l info --concurrency=1 -t 600
# Changed -t 300 to -t 600 (10 minutes)
```

---

## Cleanup: Delete GitHub Actions

The old GitHub Actions workflow is now deprecated. To clean up:

```bash
# Option 1: Delete the workflow file
rm .github/workflows/celery-worker.yml
git add .
git commit -m "Remove deprecated GitHub Actions workflow"
git push origin main

# Option 2: Keep it as backup (commented out)
# Already done - see .github/workflows/celery-worker.yml
```

You can safely delete GitHub Secrets related to this workflow:
1. Go to GitHub Repo → Settings → Secrets
2. Remove: `DATABASE_URL`, `REDIS_URL`, `GROQ_API_KEY`, `SERPAPI_API_KEY`, `SECRET_KEY`
3. These are now configured in Render

---

## Monitor Your Setup

### View Cron Job Metrics

Render Dashboard → **broker-celery-worker**:
- **Events** - See when tasks run
- **Logs** - See task output
- **Metrics** - CPU/Memory usage

### Set Up Alerts (Optional)

1. Go to Render → Account → Notifications
2. Enable email alerts for:
   - Service failures
   - Disk running out of space
   - Database issues

### Sample Monitoring Commands

```bash
# Connect to Redis to check task queue
redis-cli -u $REDIS_URL
KEYS "celery*"
LLEN "celery"  # Number of queued tasks

# Connect to PostgreSQL
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM properties_property;"
```

---

## Summary

✅ **You now have:**
1. Reliable Celery task scheduling via Render Cron
2. Persistent PostgreSQL database
3. Mounted disk storage for files
4. Automatic backups
5. No GitHub Actions complexity

🚀 **Next steps:**
1. Deploy using render.yaml
2. Monitor the cron job in Render dashboard
3. Verify no data is lost on restart
4. Delete GitHub Actions workflow files

**Questions?** Check Render documentation: https://render.com/docs
