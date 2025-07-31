# HackRx 6.0 - Setup and Deployment Guide

## Quick Setup (5 minutes)

### 1. Clone and Setup
```bash
cd hackrx-solution
pip install -r requirements.txt
```

### 2. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 3. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file and add your Gemini API key
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Run the Server
```bash
python main.py
```

Your API will be available at: `http://localhost:8000`

### 5. Test Your API
```bash
python test_api.py
```

## Deployment Options

### Option 1: Local Development
- Use the setup above
- Perfect for testing and development

### Option 2: Cloud Deployment (Railway/Render)

#### Railway.app (Recommended)
1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Add environment variables in Railway dashboard:
   - `GEMINI_API_KEY=your_key`
4. Deploy automatically

#### Render.com
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Add environment variables
5. Deploy

### Option 3: Replit (Quick Demo)
1. Fork the project to Replit
2. Add `GEMINI_API_KEY` to Secrets
3. Run the project

## Webhook URL Format

For hackathon submission, your webhook URL should be:
```
https://your-domain.com/api/v1/hackrx/run
```

Examples:
- Local: `http://localhost:8000/api/v1/hackrx/run`
- Railway: `https://your-app.railway.app/api/v1/hackrx/run`
- Render: `https://your-app.onrender.com/api/v1/hackrx/run`

## API Documentation

Once running, visit:
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Gemini API Errors**
   - Check your API key is correct
   - Ensure you have credits/quota
   - Verify API key has proper permissions

3. **Memory Issues**
   - Reduce `MAX_CHUNK_SIZE` in config
   - Use smaller embedding models
   - Increase server memory if on cloud

4. **Timeout Issues**
   - Increase `REQUEST_TIMEOUT` in config
   - Use smaller documents for testing
   - Check internet connection

### Performance Tuning

1. **For Better Speed**
   - Use smaller embedding models
   - Reduce chunk overlap
   - Enable caching

2. **For Better Accuracy**
   - Increase chunk overlap
   - Use larger context windows
   - Fine-tune similarity thresholds

## Monitoring

Check these endpoints for system health:
- `/health` - Service status
- `/` - Basic info
- `/docs` - API documentation

## Support

If you encounter issues:
1. Check the console logs
2. Test with the provided test script
3. Verify all environment variables are set
4. Ensure all dependencies are installed

Good luck with your HackRx 6.0 submission! 🚀
