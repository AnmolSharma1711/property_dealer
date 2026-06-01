# Render Deployment: Correct Steps for render.yaml

## ⭐ Updated Method (Works Now)

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Add render.yaml for infrastructure as code"
git push origin main
```

### Step 2: Connect Render Blueprint

On Render Dashboard:

1. Click **"New +"** button
2. Select **"Blueprint"** (this is the Infrastructure as Code option)
3. Click **"Public GitHub repository"**
4. Paste your GitHub repo URL:
   ```
   https://github.com/yourusername/your-repo
   ```
5. Click **"Connect"**
6. Select the branch (default: `main`)
7. Render will automatically:
   - Read your `render.yaml` file
   - Show a preview of all services to be created
   - List: PostgreSQL DB, Backend, Frontend, Celery Cron Worker
8. Review the preview and click **"Deploy"**
9. Wait 15-20 minutes for deployment

---

## Alternative: Manual Web Service → Auto-detect render.yaml

If you already created a Web Service:

1. Go to **Render Dashboard** → **New +** → **Web Service**
2. Select your GitHub repo
3. Fill in the basic info:
   - Name: `broker-backend` (or any name)
   - Branch: `main`
4. Scroll down - Render should **auto-detect** `render.yaml`
5. If it shows "Detected render.yaml", click **"Use render.yaml"**
6. Click **"Create"**

---

## Why "Infrastructure as Code" Section Doesn't Appear

The UI changed:
- ❌ Old: "Infrastructure as Code" dropdown on Web Service
- ✅ New: **"Blueprint"** service type (separate from Web Service)

**Blueprints = Infrastructure as Code on new Render UI**

---

## Verify It's Using render.yaml

After deployment:

1. Go to Render Dashboard
2. Look for these services:
   - ✅ `broker-db` (PostgreSQL)
   - ✅ `broker-backend` (Web)
   - ✅ `broker-frontend` (Web)
   - ✅ `broker-celery-worker` (Cron)

If all 4 services exist, it successfully deployed from `render.yaml` ✓

---

## If Blueprint Isn't Working

Try this workaround:

1. Delete the render.yaml (temporarily)
2. Create services manually:
   - PostgreSQL database
   - Backend web service
   - Frontend static site
   - Cron job (Background Worker type)
3. Manually add all environment variables
4. Test to ensure it works

Then re-add render.yaml for future deployments.

---

## render.yaml Compatibility

- ✅ Render officially supports render.yaml
- ✅ Works with public repos on GitHub
- ✅ Automatically creates all defined services

**Official Docs:** https://render.com/docs/infrastructure-as-code

---

## Next Steps

1. **Try Blueprint approach:**
   ```
   Render Dashboard → New + → Blueprint
   → Connect your GitHub repo
   → Deploy from render.yaml
   ```

2. **If that doesn't work:**
   - Create services manually (Postgres, Backend, Frontend, Cron)
   - Test everything works
   - Then refine render.yaml for next deployment

Let me know if you see the Blueprint option or if you need manual setup steps!
