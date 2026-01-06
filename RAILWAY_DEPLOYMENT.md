# 🚂 Railway Deployment Guide

Complete step-by-step guide to deploy your Printing Price Predictor to Railway.

## 📋 Prerequisites

- [ ] GitHub account
- [ ] Railway account (sign up at [railway.app](https://railway.app))
- [ ] Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))
- [ ] Git installed locally

## 🎯 Deployment Strategy

We'll deploy both frontend and backend as separate services in one Railway project.

---

## 📦 Method 1: Deploy via GitHub (Recommended)

### Step 1: Prepare Your Repository

```bash
# Navigate to project directory
cd printing-price-predictor

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI Printing Price Predictor"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. If first time: Click **"Configure GitHub App"** and authorize Railway
5. Select your repository

### Step 3: Deploy Backend Service

Railway will automatically detect the backend:

1. **Verify Detection**:
   - Railway should detect the Dockerfile
   - If not, click service → Settings → Set Root Directory to `backend`

2. **Configure Environment Variables**:
   - Click on the backend service
   - Go to **Variables** tab
   - Click **"+ New Variable"**
   - Add: `ANTHROPIC_API_KEY` = `your_anthropic_api_key_here`
   - Railway automatically sets `PORT`

3. **Deploy**:
   - Click **"Deploy"**
   - Wait for build to complete (~2-3 minutes)

4. **Generate Domain**:
   - Go to **Settings** tab
   - Scroll to **Networking**
   - Click **"Generate Domain"**
   - Copy the URL (e.g., `https://printing-backend-production.up.railway.app`)

### Step 4: Deploy Frontend Service

1. **Add New Service**:
   - Click **"+ New"** in your project
   - Select **"GitHub Repo"**
   - Choose the same repository

2. **Configure Frontend**:
   - Click the new service → **Settings**
   - Set **Root Directory**: `frontend`
   - Set **Build Command**: `npm install && npm run build`
   - Set **Start Command**: `npx serve -s build -l $PORT`

3. **Add Environment Variable**:
   - Go to **Variables** tab
   - Add: `REACT_APP_API_URL` = `your_backend_url_from_step3`
   - Example: `https://printing-backend-production.up.railway.app`

4. **Deploy**:
   - Railway will auto-deploy
   - Wait for build (~3-5 minutes)

5. **Generate Domain**:
   - Settings → Networking → Generate Domain
   - Your app is live! 🎉

---

## 📦 Method 2: Deploy via Railway CLI

### Install Railway CLI

```bash
# macOS/Linux
brew install railway

# Windows (using Scoop)
scoop install railway

# Or using npm
npm install -g @railway/cli
```

### Deploy Backend

```bash
cd backend

# Login to Railway
railway login

# Initialize new project
railway init

# Link to your Railway project
railway link

# Add environment variable
railway variables set ANTHROPIC_API_KEY=your_key_here

# Deploy
railway up

# Get the URL
railway domain
```

### Deploy Frontend

```bash
cd ../frontend

# Create new service
railway init

# Add environment variable
railway variables set REACT_APP_API_URL=your_backend_url

# Deploy
railway up

# Get the URL
railway domain
```

---

## 🔧 Configuration Details

### Backend Configuration

**File**: `backend/railway.json`
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Environment Variables

#### Backend Variables:
| Variable | Value | Required |
|----------|-------|----------|
| `ANTHROPIC_API_KEY` | Your Claude API key | Optional* |
| `PORT` | Auto-set by Railway | Auto |

*Optional: App works without it, but uses rule-based pricing only

#### Frontend Variables:
| Variable | Value | Required |
|----------|-------|----------|
| `REACT_APP_API_URL` | Backend Railway URL | Yes |

---

## 🧪 Testing Your Deployment

### Test Backend

```bash
# Health check
curl https://your-backend.railway.app/health

# Get available options
curl https://your-backend.railway.app/options

# Calculate estimate
curl -X POST https://your-backend.railway.app/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_type": "glossy",
    "paper_size": "A4",
    "color_type": "color",
    "quantity": 100,
    "sides": "single",
    "binding": "none",
    "lamination": "none",
    "turnaround": "standard"
  }'
```

### Test Frontend

1. Visit your frontend URL in browser
2. Fill out the form
3. Click "Calculate Price"
4. Verify results display correctly

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Backend won't start
```bash
# Check logs
railway logs

# Common fixes:
# 1. Verify ANTHROPIC_API_KEY is set
# 2. Check Dockerfile is in backend directory
# 3. Ensure requirements.txt has all dependencies
```

**Problem**: Port binding error
- Railway sets `PORT` automatically
- Ensure your code uses `os.getenv("PORT", 8000)`

### Frontend Issues

**Problem**: Can't connect to backend
```bash
# Verify environment variable
railway variables

# Should show:
# REACT_APP_API_URL=https://your-backend.railway.app

# If missing, add it:
railway variables set REACT_APP_API_URL=https://your-backend.railway.app
```

**Problem**: Build fails
- Check Node version compatibility
- Verify package.json is in frontend directory
- Check build logs in Railway dashboard

### CORS Issues

If frontend can't connect due to CORS:

Edit `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.railway.app",
        "http://localhost:3000"  # for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔄 Updating Your Deployment

### Auto-Deploy (GitHub)

Every push to `main` branch auto-deploys:

```bash
git add .
git commit -m "Update pricing logic"
git push origin main
```

Railway will automatically rebuild and redeploy both services.

### Manual Deploy (CLI)

```bash
# In backend or frontend directory
railway up
```

---

## 💰 Pricing & Limits

### Railway Free Tier

- ✅ $5 free credits/month
- ✅ 512MB RAM per service
- ✅ Shared CPU
- ✅ 1GB disk
- ✅ Unlimited bandwidth

**Estimated costs for this app**: ~$2-3/month

### Anthropic API Costs

- Claude API: Pay-as-you-go
- ~$0.003 per estimate (with AI)
- Free tier: $5 credit on signup

---

## 📊 Monitoring

### View Logs

```bash
# Via CLI
railway logs

# Or in dashboard:
# Project → Service → Deployments → View Logs
```

### Metrics

Railway dashboard shows:
- CPU usage
- Memory usage
- Request count
- Response times

---

## 🔒 Security Best Practices

1. **Never commit API keys**
   ```bash
   # Check .gitignore includes:
   .env
   .env.local
   ```

2. **Use environment variables**
   - Store all secrets in Railway Variables
   - Access via `os.getenv()`

3. **Enable CORS properly**
   - Only allow your frontend domain
   - Remove `"*"` for production

4. **Add rate limiting** (for production):
   ```python
   # In backend/main.py
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/estimate")
   @limiter.limit("10/minute")
   async def estimate_price(job: PrintJob):
       ...
   ```

---

## 🚀 Production Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Environment variables set
- [ ] Custom domain configured (optional)
- [ ] SSL/HTTPS enabled (automatic on Railway)
- [ ] CORS configured for production
- [ ] Error monitoring setup
- [ ] Database added (if needed)
- [ ] Backups configured (if using database)

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic API Docs](https://docs.anthropic.com/)

---

## 🆘 Need Help?

1. Check Railway logs: `railway logs`
2. Join [Railway Discord](https://discord.gg/railway)
3. Check [Railway Status](https://railway.statuspage.io/)
4. Review error messages in deployment logs

---

**Deployment complete!** 🎉

Your AI-powered printing price calculator is now live and ready to serve quotes!
