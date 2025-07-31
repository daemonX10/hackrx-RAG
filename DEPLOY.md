# 🚀 HackRx 6.0 - Quick Deployment Guide

## Deploy to Render (Recommended)

### Option 1: Deploy via GitHub (Recommended)
1. Push your code to GitHub repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: `Docker` (uses Dockerfile)
6. Add environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `EMBEDDING_MODEL`: `all-MiniLM-L6-v2`
7. Click "Deploy"

### Option 2: Deploy with render.yaml
1. Push code with `render.yaml` file to GitHub
2. In Render, select "Deploy from render.yaml"
3. Set your GEMINI_API_KEY in environment variables
4. Deploy!

## Your API Endpoints

Once deployed, your API will be available at:
- **Base URL**: `https://your-app-name.onrender.com`
- **Health Check**: `GET /health`
- **Main Endpoint**: `POST /api/v1/hackrx/run`
- **Detailed Endpoint**: `POST /api/v1/hackrx/run/detailed`
- **Document Analysis**: `POST /api/v1/analyze-document`
- **API Docs**: `GET /docs`

## Testing Your Deployment

Update the `BASE_URL` in `test_api.py`:
```python
BASE_URL = "https://your-app-name.onrender.com"
```

Then run: `python test_api.py`

## Submission

Submit this URL to HackRx dashboard:
```
https://your-app-name.onrender.com/api/v1/hackrx/run
```

## Environment Variables Required

- `GEMINI_API_KEY`: Your Google Gemini API key (from your .env file)
- `PORT`: Automatically set by Render
- `EMBEDDING_MODEL`: all-MiniLM-L6-v2 (optional, has default)

## Notes

- Free tier: 750 hours/month, sleeps after 15min of inactivity
- First request after sleep may take 30-60 seconds to wake up
- Perfect for hackathon evaluation!

## Troubleshooting

If deployment fails:
1. Check logs in Render dashboard
2. Ensure GEMINI_API_KEY is set
3. Verify requirements.txt has all dependencies
4. Check Dockerfile builds locally: `docker build -t hackrx .`
