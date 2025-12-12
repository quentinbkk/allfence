# Quick Deployment Guide - SQLite Version

This guide deploys your AllFence app with SQLite (no PostgreSQL needed).

## What You're Deploying

- **Backend**: Flask API + SQLite database on Render (free tier)
- **Frontend**: React app on Vercel (free tier)
- **Cost**: $0/month

---

## Step 1: Prepare Your Code

### 1. Commit and push to GitHub

```bash
cd /Users/quentingeoffroy/Desktop/info_202_allfence

# Add all files
git add .

# Commit
git commit -m "Ready for deployment with SQLite"

# Push to GitHub
git push origin main
```

---

## Step 2: Deploy Backend to Render

### 1. Create Render account
- Go to https://render.com
- Sign up with GitHub

### 2. Create new Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repository: `quentinbkk/allfence`
- Configure:
  - **Name**: `allfence-api`
  - **Branch**: `main`
  - **Root Directory**: (leave empty)
  - **Runtime**: `Python 3`
  - **Build Command**: `cd backend && pip install -r requirements.txt`
  - **Start Command**: `cd backend && gunicorn app:app`
  - **Instance Type**: `Free`

### 3. Add Persistent Disk (IMPORTANT for SQLite)
- Scroll to "Disks" section
- Click "Add Disk"
  - **Name**: `allfence-data`
  - **Mount Path**: `/opt/render/project/src/backend/data`
  - **Size**: `1 GB`

### 4. Set Environment Variables
Click "Environment" and add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | (Click "Generate" button) |
| `JWT_SECRET_KEY` | (Click "Generate" button) |
| `DEBUG` | `False` |
| `FLASK_ENV` | `production` |
| `CORS_ORIGINS` | `https://allfence.vercel.app` _(update after Vercel deployment)_ |

### 5. Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Copy your backend URL: `https://allfence-api.onrender.com`

### 6. Upload Database (One-time setup)
After first deployment:
- Go to your service dashboard
- Click "Shell" tab
- Upload your database file: `backend/data/database/fencing_management.db`
  - Or SSH in and copy it manually
  - The disk persists across deployments

**Alternative**: Let the app create a fresh database:
```bash
# In Render shell
cd backend
python -c "from src.database import init_db; init_db(); print('Database initialized')"
python scripts/load_realistic_data.py  # Load your data
```

---

## Step 3: Deploy Frontend to Vercel

### 1. Create Vercel account
- Go to https://vercel.com
- Sign up with GitHub

### 2. Import Project
- Click "Add New..." → "Project"
- Import `quentinbkk/allfence`
- Configure:
  - **Framework Preset**: `Vite`
  - **Root Directory**: `allfence-frontend`
  - **Build Command**: `npm run build`
  - **Output Directory**: `dist`

### 3. Set Environment Variable
- Go to "Environment Variables"
- Add:
  - **Key**: `VITE_API_URL`
  - **Value**: `https://allfence-api.onrender.com/api`

### 4. Deploy
- Click "Deploy"
- Wait 2-3 minutes
- Copy your frontend URL: `https://allfence.vercel.app`

---

## Step 4: Update CORS

Go back to Render:
1. Open your `allfence-api` service
2. Go to "Environment"
3. Update `CORS_ORIGINS` to your actual Vercel URL
4. Click "Save Changes" (triggers redeploy)

---

## Step 5: Test Your Deployment

### Backend Health Check
```bash
curl https://allfence-api.onrender.com/api/health
```
Should return: `{"status": "healthy"}`

### Frontend
1. Visit your Vercel URL
2. Navigate through pages:
   - Home page loads
   - Fencers list displays
   - Tournaments show up
   - Rankings work

### Test Login
- Username: `admin`
- Password: (whatever you set locally)

---

## Troubleshooting

### Backend Issues

**"Application failed to respond"**
- Check Render logs: Dashboard → Logs
- Verify build completed successfully
- Check disk is mounted: `ls -la /opt/render/project/src/backend/data`

**"No database file"**
- Upload your SQLite database to the persistent disk
- Or initialize fresh: Run `init_db()` in Render shell

**"CORS errors"**
- Verify `CORS_ORIGINS` matches your Vercel URL exactly
- No trailing slash
- Include `https://`

### Frontend Issues

**"API calls failing"**
- Check `VITE_API_URL` environment variable
- Must end with `/api`
- Browser console shows actual errors

**"Page not found"**
- Vercel automatically handles routing for SPA
- If issues, check build logs

---

## Updating Your App

### Backend Updates
```bash
git add backend/
git commit -m "Update backend"
git push origin main
```
Render auto-deploys on push!

### Frontend Updates
```bash
git add allfence-frontend/
git commit -m "Update frontend"
git push origin main
```
Vercel auto-deploys on push!

### Database Updates
- SQLite file persists on the disk
- Manual updates: Use Render Shell to run scripts
- Schema changes: Create migration scripts

---

## Free Tier Limits

**Render Free Tier:**
- 750 hours/month (always-on)
- Spins down after 15 min inactivity
- First request after spin-down takes ~30 seconds
- 1 GB disk storage

**Vercel Free Tier:**
- Unlimited deployments
- 100 GB bandwidth/month
- Always-on (no spin-down)

**Total Cost: $0/month** 🎉

---

## Next Steps (Optional)

1. **Custom Domain**: Add your domain on Vercel (free SSL)
2. **Monitoring**: Use Render and Vercel dashboards
3. **Backups**: Download SQLite file periodically from Render disk
4. **Analytics**: Add Google Analytics to frontend
5. **CDN**: Vercel has built-in CDN

---

## Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **SQLite Docs**: https://www.sqlite.org/docs.html

Your app is now live! 🚀
