# 🚀 AllFence Deployment Guide

Complete guide to deploy AllFence to production using Neon (PostgreSQL) + Render (Backend) + Vercel (Frontend).

## 📋 Prerequisites

- GitHub account
- Neon account (free): https://neon.tech
- Render account (free): https://render.com  
- Vercel account (free): https://vercel.com

---

## 🗄️ Step 1: Set Up Neon PostgreSQL Database

### 1.1 Create Neon Account & Project

1. Go to https://neon.tech
2. Sign up with GitHub (recommended)
3. Click "Create a project"
4. Choose a project name: `allfence`
5. Select region closest to you
6. Click "Create project"

### 1.2 Get Connection String

1. In your Neon dashboard, click on your project
2. Go to "Connection Details"
3. Copy the **Connection string** (looks like):
   ```
   postgresql://username:password@ep-cool-name-123456.region.aws.neon.tech/allfence
   ```
4. Save this - you'll need it for Render

### 1.3 (Optional) Migrate Data from SQLite

If you want to migrate your existing data:

```bash
# Export SQLite data
python backend/scripts/export_data.py

# Import to PostgreSQL (after setting DATABASE_URL)
export DATABASE_URL="your-neon-connection-string"
python backend/scripts/import_data.py
```

---

## 🖥️ Step 2: Deploy Backend to Render

### 2.1 Push Code to GitHub

```bash
cd /Users/quentingeoffroy/Desktop/info_202_allfence

# Add all changes
git add .

# Commit
git commit -m "Prepare for production deployment"

# Push to GitHub
git push origin main
```

### 2.2 Create Render Web Service

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `quentinbkk/allfence`
4. Configure the service:
   - **Name**: `allfence-api`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn app:app`
   - **Instance Type**: `Free`

### 2.3 Set Environment Variables in Render

Click "Advanced" → "Add Environment Variable" and add:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.13.3` |
| `FLASK_ENV` | `production` |
| `DEBUG` | `False` |
| `SECRET_KEY` | `[Generate a random 32-char string]` |
| `JWT_SECRET_KEY` | `[Generate a random 32-char string]` |
| `DATABASE_URL` | `[Your Neon connection string]` |
| `CORS_ORIGINS` | `https://allfence.vercel.app` (update after deploying frontend) |

**Generate random strings:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.4 Deploy

1. Click "Create Web Service"
2. Wait 5-10 minutes for deployment
3. Your API will be available at: `https://allfence-api.onrender.com`
4. Test it: `https://allfence-api.onrender.com/api/health`

**Important:** Free tier services spin down after inactivity. First request may take 30-50 seconds.

---

## 🌐 Step 3: Deploy Frontend to Vercel

### 3.1 Update Frontend Environment

1. Create production environment file:

```bash
cd allfence-frontend
cp .env.example .env.production
```

2. Edit `.env.production`:
```env
VITE_API_URL=https://allfence-api.onrender.com/api
```

3. Commit the change:
```bash
git add .env.production
git commit -m "Add production environment config"
git push origin main
```

### 3.2 Deploy to Vercel

#### Option A: Using Vercel Dashboard (Recommended)

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository: `quentinbkk/allfence`
4. Configure project:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `allfence-frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://allfence-api.onrender.com/api`
6. Click "Deploy"
7. Wait 2-3 minutes
8. Your app will be live at: `https://allfence.vercel.app` (or similar)

#### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd allfence-frontend
vercel --prod
```

---

## 🔄 Step 4: Update CORS Settings

After frontend is deployed:

1. Go to your Render dashboard
2. Select your `allfence-api` service
3. Go to "Environment"
4. Update `CORS_ORIGINS` to your Vercel URL:
   ```
   CORS_ORIGINS=https://your-app-name.vercel.app
   ```
5. Click "Save Changes"
6. Wait for redeployment

---

## ✅ Step 5: Initialize Production Database

### 5.1 Create Initial Data

Option 1 - Via API (if you have authentication set up):
```bash
curl -X POST https://allfence-api.onrender.com/api/admin/initialize
```

Option 2 - Connect directly to Neon and run migrations:
```bash
# Set your Neon connection string
export DATABASE_URL="your-neon-connection-string"

# Run database initialization
cd backend
python -c "from src.database import init_db; init_db()"
```

### 5.2 (Optional) Create Admin User

```bash
cd backend
python scripts/create_admin.py
```

### 5.3 (Optional) Simulate Season Data

```bash
cd backend
python scripts/simulate_season.py
```

---

## 🧪 Step 6: Test Your Deployment

### Backend API Tests

```bash
# Health check
curl https://allfence-api.onrender.com/api/health

# Get fencers
curl https://allfence-api.onrender.com/api/fencers?limit=5

# Get rankings
curl "https://allfence-api.onrender.com/api/rankings?bracket=Senior"
```

### Frontend Tests

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Check all pages:
   - Home page loads
   - Tournaments page shows data
   - Fencers page shows data
   - Rankings page shows data
   - Rankings Progress chart loads
3. Test navigation
4. Test filtering and search

---

## 🔧 Troubleshooting

### Backend Issues

**"Application failed to start"**
- Check Render logs: Dashboard → Service → Logs
- Verify all environment variables are set
- Ensure DATABASE_URL is correct

**"Database connection failed"**
- Verify Neon database is running
- Check DATABASE_URL format (should start with `postgresql://`)
- Ensure Neon project isn't suspended

**"CORS errors in browser"**
- Update CORS_ORIGINS in Render to match your Vercel URL
- Clear browser cache
- Check browser console for exact error

### Frontend Issues

**"Failed to load data"**
- Verify VITE_API_URL points to correct backend URL
- Check browser console for errors
- Test API endpoint directly in browser

**"Build failed"**
- Check Vercel build logs
- Ensure all dependencies in package.json
- Verify TypeScript has no errors

### Database Issues

**"Table doesn't exist"**
- Run init_db() to create tables
- Check Neon dashboard → Tables

**"Slow queries"**
- Free tier has connection limits
- Consider adding indexes
- Upgrade to paid tier if needed

---

## 📊 Monitoring

### Render
- Dashboard → Your Service → Metrics
- View CPU, Memory, Response times
- Check logs for errors

### Vercel  
- Dashboard → Your Project → Analytics
- View page views, errors
- Check deployment logs

### Neon
- Dashboard → Your Project → Monitoring
- View database connections
- Check query performance

---

## 🔐 Security Checklist

Before sharing publicly:

- [ ] Change all SECRET_KEY and JWT_SECRET_KEY values
- [ ] Set CORS_ORIGINS to specific domain (not `*`)
- [ ] Set DEBUG to False in production
- [ ] Review API endpoints for sensitive data
- [ ] Test authentication flows
- [ ] Add rate limiting (optional)
- [ ] Enable HTTPS (automatic on Vercel/Render)
- [ ] Review error messages (don't expose internals)

---

## 💰 Cost Breakdown

**Current Setup (All Free Tier):**
- Neon: $0/month (0.5GB database, 3GB transfer)
- Render: $0/month (750 hours, sleeps after inactivity)
- Vercel: $0/month (100GB bandwidth)

**Total: $0/month** 🎉

**Limitations:**
- Backend spins down after 15 min inactivity (cold start delay)
- Database limited to 0.5GB
- No custom domains without verification

---

## 🚀 Next Steps

Once deployed, you can:

1. **Add Custom Domain**
   - Vercel: Settings → Domains
   - Cost: Free with Vercel

2. **Monitor Usage**
   - Check Render/Vercel/Neon dashboards
   - Set up alerts

3. **Optimize Performance**
   - Add caching
   - Optimize database queries
   - Consider CDN for static assets

4. **Scale as Needed**
   - Upgrade Render to keep backend always on ($7/month)
   - Upgrade Neon for more storage ($19/month)
   - Vercel Pro for team features ($20/month)

---

## 🆘 Getting Help

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Neon Docs**: https://neon.tech/docs
- **GitHub Issues**: Create issue in your repo

---

**🎉 Congratulations!** Your AllFence application is now live and accessible worldwide!

Share your link:
- Frontend: `https://your-app.vercel.app`
- API: `https://allfence-api.onrender.com/api`
