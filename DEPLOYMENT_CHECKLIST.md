# 🚀 Deployment Checklist for HackRx 6.0

## ✅ Files Ready for Deployment

- [x] `Dockerfile` - Container configuration
- [x] `render.yaml` - Render deployment config  
- [x] `requirements.txt` - Python dependencies
- [x] `main.py` - FastAPI application with PORT support
- [x] `.dockerignore` - Excludes unnecessary files
- [x] All service modules in `services/`, `models/`, `utils/`

## 🎯 Quick Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for HackRx deployment"
git push origin main
```

### 2. Deploy on Render
1. Go to https://dashboard.render.com/
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Select "Deploy from render.yaml" 
5. Set environment variable: `GEMINI_API_KEY` = `AIzaSyCcwA-BcilFRsLVXzpNWMFASzDJzNL7_6w`
6. Click "Deploy"

### 3. Test Your Deployment
```bash
# Update URL in test_deployed.py, then run:
python test_deployed.py https://your-app-name.onrender.com
```

### 4. Submit to HackRx
Submit this URL: `https://your-app-name.onrender.com/api/v1/hackrx/run`

## 📋 Environment Variables Needed

| Variable | Value | Required |
|----------|-------|----------|
| `GEMINI_API_KEY` | `AIzaSyCcwA-BcilFRsLVXzpNWMFASzDJzNL7_6w` | ✅ Yes |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Optional |
| `PORT` | Auto-set by Render | Auto |

## 🎯 Expected Endpoints After Deployment

- **Health**: `GET https://your-app.onrender.com/health`
- **Main**: `POST https://your-app.onrender.com/api/v1/hackrx/run`
- **Detailed**: `POST https://your-app.onrender.com/api/v1/hackrx/run/detailed`  
- **Docs**: `GET https://your-app.onrender.com/docs`

## ⚠️ Important Notes

- First request after deploy may take 30-60 seconds (cold start)
- Free tier sleeps after 15 minutes of inactivity
- All tests passed locally - ready for evaluation! ✅

## 🆘 If Deployment Fails

1. Check Render logs in dashboard
2. Verify GEMINI_API_KEY is set correctly
3. Ensure GitHub repo has all files
4. Contact support if needed

**Your HackRx 6.0 solution is ready for deployment! 🎉**
