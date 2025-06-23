# Railway Deployment Guide for Digital Bulletin Board

## 🚀 Deploy to Railway (Recommended)

Railway offers free hosting for Python applications with easy GitHub integration.

### Step 1: Prepare for Deployment

1. **Create a Procfile** (Railway uses this to start your app):
```
web: python main.py
```

2. **Update main.py for production** (add to the bottom):
```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
```

3. **Create runtime.txt** (specify Python version):
```
python-3.11.0
```

### Step 2: Deploy to Railway

1. **Go to Railway.app** and sign up with GitHub
2. **Create New Project** → **Deploy from GitHub repo**
3. **Connect your repository**
4. **Railway will automatically**:
   - Detect it's a Python app
   - Install requirements.txt
   - Start your app using the Procfile

### Step 3: Configure Environment Variables

In Railway dashboard:
- Go to Variables tab
- Add any environment variables you need
- Your encrypted config files will be included automatically

### Step 4: Custom Domain (Optional)

Railway provides:
- Free subdomain: `yourapp.railway.app`
- Custom domain support (paid plans)

## 🔧 Production Configuration

Add these to your main.py for production:

```python
import os

# Production settings
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
PORT = int(os.environ.get("PORT", 8000))

# Update uvicorn.run call
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=PORT, 
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )
```

## ⚡ Alternative: Render.com

1. Connect GitHub repo to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python main.py`
4. Deploy automatically on git push

## 🌍 Alternative: Heroku

1. Install Heroku CLI
2. Create Procfile: `web: python main.py`
3. `heroku create yourapp`
4. `git push heroku main`

## 🔒 Security for Production

1. **Environment Variables**: Store secrets as environment variables
2. **HTTPS**: All platforms provide HTTPS automatically
3. **Database**: Your encrypted local database works on all platforms
4. **Monitoring**: Enable logging and monitoring

## 💡 Tips

- **Free Tiers**: Railway, Render, and Heroku offer free tiers
- **Performance**: Railway and Render generally faster than Heroku free tier
- **Scaling**: All platforms support easy scaling
- **Custom Domains**: Available on paid plans

Railway is recommended because:
- ✅ Simple GitHub integration
- ✅ Generous free tier
- ✅ Fast deployments
- ✅ Great for Python apps
- ✅ No credit card required for free tier
