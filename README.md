# 🖨️ AI-Powered Printing Price Predictor

A full-stack web application that uses AI (Claude) to predict printing job prices based on specifications like paper type, quantity, color, binding, and more.

## 🌟 Features

- **AI-Powered Pricing**: Uses Claude AI for intelligent price estimation
- **Rule-Based Fallback**: Robust pricing even without API key
- **Volume Discounts**: Automatic discounts for bulk orders
- **Comprehensive Options**: Paper types, sizes, binding, lamination, rush orders
- **Real-time Estimates**: Instant price calculations
- **Responsive Design**: Works on desktop and mobile
- **Professional UI**: Clean, modern interface

## 🏗️ Architecture

- **Frontend**: React.js with modern CSS
- **Backend**: FastAPI (Python) with async support
- **AI**: Anthropic Claude API for intelligent pricing
- **Deployment**: Railway (with Dockerfile)

## 📁 Project Structure

```
printing-price-predictor/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Docker configuration
│   └── railway.json        # Railway deployment config
├── frontend/
│   ├── src/
│   │   ├── App.js          # React main component
│   │   ├── App.css         # Styling
│   │   └── index.js        # Entry point
│   ├── public/
│   │   └── index.html      # HTML template
│   └── package.json        # Node dependencies
└── .env.example            # Environment variables template
```

## 🚀 Deployment to Railway

### Prerequisites

1. [Railway Account](https://railway.app) (free tier available)
2. [Anthropic API Key](https://console.anthropic.com/) (optional, but recommended for AI features)
3. Git installed on your machine

### Step 1: Prepare Your Repository

```bash
# Initialize git if not already done
cd printing-price-predictor
git init
git add .
git commit -m "Initial commit"

# Push to GitHub (or GitLab/Bitbucket)
git remote add origin <your-repo-url>
git push -u origin main
```

### Step 2: Deploy Backend to Railway

1. **Log in to Railway**: Go to [railway.app](https://railway.app)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account if not already connected
   - Select your repository

3. **Configure Backend Service**:
   - Railway will auto-detect the Dockerfile
   - Click on the service → Settings
   - Set Root Directory: `backend`
   - Add environment variable:
     - `ANTHROPIC_API_KEY`: Your Claude API key
   - Deploy!

4. **Get Backend URL**:
   - Go to Settings → Generate Domain
   - Copy the URL (e.g., `https://your-app.railway.app`)

### Step 3: Deploy Frontend to Railway

1. **Add Frontend Service**:
   - In your Railway project, click "+ New"
   - Select "GitHub Repo"
   - Choose the same repository

2. **Configure Frontend**:
   - Settings → Root Directory: `frontend`
   - Add environment variable:
     - `REACT_APP_API_URL`: Your backend URL from Step 2
   - Settings → Build Command: `npm install && npm run build`
   - Settings → Start Command: `npx serve -s build -l $PORT`

3. **Generate Domain**:
   - Settings → Generate Domain
   - Your app is now live!

### Alternative: Deploy Separately

#### Backend Only on Railway:

```bash
cd backend
railway login
railway init
railway up

# Set environment variables
railway variables set ANTHROPIC_API_KEY=your_key_here
```

#### Frontend on Vercel/Netlify:

1. Push frontend to separate repo or use monorepo
2. Deploy to [Vercel](https://vercel.com) or [Netlify](https://netlify.com)
3. Set `REACT_APP_API_URL` environment variable to your Railway backend URL

## 🛠️ Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export ANTHROPIC_API_KEY=your_key_here  # On Windows: set ANTHROPIC_API_KEY=your_key_here

# Run server
python main.py
# Server runs at http://localhost:8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Run development server
npm start
# App runs at http://localhost:3000
```

## 🧪 Testing the API

### Test Backend Endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Get options
curl http://localhost:8000/options

# Calculate estimate
curl -X POST http://localhost:8000/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_type": "glossy",
    "paper_size": "A4",
    "color_type": "color",
    "quantity": 500,
    "sides": "double",
    "binding": "spiral",
    "lamination": "none",
    "turnaround": "express"
  }'
```

## 📊 Pricing Logic

### Base Pricing:
- **Standard Paper**: $0.05/sheet
- **Glossy Paper**: $0.12/sheet
- **Matte Paper**: $0.10/sheet
- **Cardstock**: $0.20/sheet

### Multipliers:
- **Color Printing**: 2.5x base price
- **Double-sided**: 1.6x base price
- **Express Delivery**: 1.5x
- **Same Day**: 2.0x

### Volume Discounts:
- 100-499 sheets: 5% off
- 500-999 sheets: 10% off
- 1000+ sheets: 15% off

### Additional Costs:
- **Staple Binding**: $0.50
- **Spiral Binding**: $3.00
- **Perfect Binding**: $5.00
- **Lamination**: $1.50/sheet

## 🔑 Environment Variables

### Backend (`.env`):
```env
ANTHROPIC_API_KEY=sk-ant-...  # Optional, but enables AI pricing
PORT=8000                      # Server port (Railway sets this automatically)
```

### Frontend (`.env`):
```env
REACT_APP_API_URL=https://your-backend.railway.app
```

## 🎨 Customization

### Modify Pricing Rules:

Edit `backend/main.py` in the `BASE_PRICES` dictionary:

```python
BASE_PRICES = {
    "paper_type": {
        "premium": 0.25,  # Add new paper types
        # ...
    }
}
```

### Add New Options:

1. Update `BASE_PRICES` in `backend/main.py`
2. Add to `get_options()` endpoint
3. Update frontend form in `frontend/src/App.js`

### Styling:

Customize colors in `frontend/src/App.css`:

```css
/* Change primary color */
background: linear-gradient(135deg, #your-color 0%, #your-color-2 100%);
```

## 🔒 Security Notes

- Never commit API keys to Git
- Use environment variables for sensitive data
- Enable CORS only for your frontend domain in production
- Implement rate limiting for production use
- Add authentication if needed

## 📈 Scaling Considerations

### For Production:

1. **Database**: Add PostgreSQL for quote history
   ```bash
   railway add postgresql
   ```

2. **Caching**: Implement Redis for common calculations

3. **Rate Limiting**: Add rate limiting middleware

4. **Authentication**: Add user accounts if needed

5. **Analytics**: Track quote requests and conversions

## 🐛 Troubleshooting

### Backend won't start on Railway:
- Check logs: `railway logs`
- Verify environment variables are set
- Ensure Dockerfile is in correct location

### Frontend can't connect to backend:
- Verify `REACT_APP_API_URL` is set correctly
- Check CORS settings in backend
- Ensure backend is deployed and running

### AI pricing not working:
- Verify `ANTHROPIC_API_KEY` is set
- Check API key is valid
- App will fall back to rule-based pricing

## 📝 API Documentation

Once deployed, visit:
- API Docs: `https://your-backend.railway.app/docs`
- Alternative Docs: `https://your-backend.railway.app/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use for commercial projects!

## 🆘 Support

- Check Railway logs: `railway logs`
- Review FastAPI logs in Railway dashboard
- Test API endpoints using `/docs` interface

## 🎯 Next Steps

1. ✅ Deploy to Railway
2. 🔄 Add database for quote history
3. 👤 Implement user authentication
4. 📧 Add email quote functionality
5. 📊 Build admin dashboard
6. 💳 Integrate payment processing
7. 📱 Create mobile app version

---

Built with ❤️ using FastAPI, React, and Claude AI
