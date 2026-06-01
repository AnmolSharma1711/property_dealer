# Quick Reference: Render Cron & Persistence

## 🚀 TL;DR - Quick Facts

| Question | Answer |
|----------|--------|
| **Where do Celery tasks run?** | Render Cron Job (`broker-celery-worker`) every 15 min |
| **Do I need GitHub Actions?** | ❌ No - deprecated |
| **Where is my data stored?** | PostgreSQL database + 5GB mounted disk |
| **Will my data be lost on restart?** | ❌ No - everything persists |
| **How do I deploy?** | Use `render.yaml` - one-click setup |
| **Do I need a Background Worker?** | ❌ No - cron job handles it |

---

## 🔍 Monitor Celery Tasks

**Location:** Render Dashboard → `broker-celery-worker`

```
Events Tab     → See when tasks are scheduled
Logs Tab       → View task output (should see task names)
Metrics Tab    → CPU/Memory usage
```

**Expected logs:**
```
worker: Ready to accept tasks
properties.tasks.enrich_locality_pipeline received
properties.tasks.enrich_locality_pipeline succeeded
```

---

## 📊 Check Data Persistence

### Test 1: Database Connection
```bash
# SSH into backend service (Render Dashboard → Shell)
python manage.py shell
>>> from django.db import connection
>>> print(connection.settings_dict['ENGINE'])
# Should print: django.db.backends.postgresql
```

### Test 2: Data Survives Restart
```bash
# 1. Add a test property via admin
# 2. Go to broker-backend service → "Manual Deploy"
# 3. Wait for redeploy (5-10 minutes)
# 4. Check admin - property should still exist ✓
```

### Test 3: Disk Storage
```bash
# SSH into backend
df -h /var/data
# Should show ~5GB mounted storage
```

---

## 🐛 Troubleshooting

### Issue: Cron Job Not Running

**Check 1:** Is service active?
- Dashboard → `broker-celery-worker` → Status should be "Active"

**Check 2:** Check logs
- Logs should show: `worker: Ready to accept tasks`
- If not, check environment variables section

**Check 3:** Verify schedule syntax
- Must be valid cron: `"*/15 * * * *"` (every 15 min)
- Edit `render.yaml` if needed, then push to redeploy

### Issue: Data Disappearing

**Check 1:** Which database?
```bash
echo $DATABASE_URL
# Must contain 'postgres' not 'sqlite'
```

**Check 2:** Is persistent disk mounted?
```bash
mount | grep /var/data
# Should show: /var/data mounted
```

**Check 3:** Disk full?
```bash
df -h /var/data
# If 100%, delete old files or increase sizeGB in render.yaml
```

### Issue: Tasks Failing with "Module Not Found"

**Solution:**
1. Check `backend/requirements.txt` has all dependencies
2. Rebuild cron service in Render
3. Check logs for which module is missing

### Issue: Database Connection Error

**Check 1:** DATABASE_URL set?
```bash
echo $DATABASE_URL
# Must be set and valid
```

**Check 2:** PostgreSQL service running?
- Dashboard → `broker-db` → Status should be "Available"

**Check 3:** Wrong user/password?
- Check environment variables in broker-celery-worker
- Must match broker-backend exactly

---

## ⚙️ Configuration Changes

### Change Cron Schedule

**File:** `render.yaml`, line ~72

```yaml
schedule: "*/15 * * * *"  # Every 15 minutes
```

**Common values:**
- `"*/5 * * * *"` = Every 5 minutes
- `"*/15 * * * *"` = Every 15 minutes (default)
- `"0 * * * *"` = Every hour
- `"0 0 * * *"` = Daily at midnight

**Apply change:**
```bash
git add render.yaml
git commit -m "Update cron schedule"
git push
# Render redeploys automatically
```

### Increase Disk Storage

**File:** `render.yaml`, line ~55

```yaml
disks:
  - name: broker-data
    mountPath: /var/data
    sizeGB: 5  # Change this number
```

**Apply change:**
```bash
git add render.yaml
git commit -m "Increase storage to 10GB"
git push
# Render redeploys, disk size increases
```

### Add Environment Variable

**File:** `render.yaml`, cron service section

```yaml
envVars:
  - key: NEW_VAR
    value: new_value
```

**Apply change:**
```bash
git add render.yaml
git commit -m "Add environment variable"
git push
```

---

## 📈 Performance Tips

### Task Queue Backing Up?

**Increase concurrency:**
In `render.yaml`, change:
```yaml
startCommand: cd backend/core && celery -A core worker -l info --concurrency=2 -t 300
# Changed concurrency from 1 to 2
```

**Run more frequently:**
```yaml
schedule: "*/5 * * * *"  # Every 5 minutes instead of 15
```

### Want Faster Task Completion?

**Option 1:** Add a Background Worker (in addition to cron)
- More expensive but continuous processing
- Not recommended for most cases

**Option 2:** Increase timeout:
```yaml
startCommand: cd backend/core && celery -A core worker -l info --concurrency=1 -t 600
# Changed -t 300 to -t 600 (10 minutes)
```

---

## 🔐 Security

### Database Backups

**Automatic:** Render backs up PostgreSQL daily

**Manual backup:**
1. Dashboard → `broker-db` → Settings
2. Click "Create Backup"
3. Download when ready

### Secrets Management

**Don't commit secrets to git:**
```bash
# ❌ Wrong
DEBUG=False
SECRET_KEY=actual-secret-here

# ✅ Right - use Render environment variables
DEBUG=${DEBUG}
SECRET_KEY=${SECRET_KEY}
```

**Set in Render Dashboard:**
- Backend service → Environment tab
- Add/edit variables there, not in code

---

## 📞 Getting Help

### Check Logs First
- 90% of issues are in the logs
- Dashboard → Service → Logs tab

### Common Error Patterns

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Missing in requirements.txt |
| `OperationalError: No such table` | Migration failed, run manually |
| `Connection refused` | Redis/DB credentials wrong |
| `Task timeout` | Increase `-t` value in startCommand |
| `Disk full` | Increase sizeGB in render.yaml |

### Reset Everything

If all else fails:
```bash
# 1. Delete all services in Render Dashboard
# 2. Push latest code to GitHub
# 3. Re-deploy with render.yaml
# 4. Takes ~20 minutes but clean slate
```

---

## ✅ Deployment Checklist

- [ ] `render.yaml` committed to GitHub
- [ ] All environment variables set in Render
- [ ] PostgreSQL database created
- [ ] Backend, Frontend, Cron deployed
- [ ] Cron logs show task runs
- [ ] Data persists after restart test
- [ ] Admin panel accessible
- [ ] Frontend loads successfully
- [ ] API calls working

---

**Questions?** See [RENDER_CRON_AND_PERSISTENCE.md](RENDER_CRON_AND_PERSISTENCE.md) for full guide.
