# Postman Testing Guide for HackRx RAG API 🚀

## Quick Setup

### 1. Start Your Local Server
```bash
# Make sure you're in the project directory
cd "d:\hackathons\hackrx-bajaj\phase 1\hackrx-solution"

# Activate virtual environment
.venv\Scripts\activate

# Start the server
python main.py
```

Your API will be running at: `http://localhost:8000`

### 2. Import Postman Collection

I'll create a Postman collection file that you can import directly into Postman.

## Manual Postman Setup

### Collection Structure
Create a new collection called "HackRx RAG API" with these requests:

## 1. Health Check Request

**Method**: `GET`  
**URL**: `http://localhost:8000/health`  
**Headers**: None required

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "dependencies": {
    "gemini_api": "connected",
    "embedding_service": "ready",
    "document_processor": "ready"
  }
}
```

## 2. Basic Query Request

**Method**: `POST`  
**URL**: `http://localhost:8000/hackrx/run`  
**Headers**:
- `Content-Type: application/json`

**Body** (raw JSON):
```json
{
  "query": "What is this insurance policy about?"
}
```

**Expected Response**:
```json
{
  "answer": "Based on the document analysis...",
  "confidence": 0.85,
  "source_chunks": ["relevant excerpts..."],
  "processing_time": 1.23,
  "metadata": {
    "chunks_found": 5,
    "model_used": "gemini-pro",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
  }
}
```

## 3. Query with Document URL

**Method**: `POST`  
**URL**: `http://localhost:8000/hackrx/run`  
**Headers**:
- `Content-Type: application/json`

**Body** (raw JSON):
```json
{
  "query": "What is the waiting period for cataract treatment?",
  "document_url": "https://example.com/policy.pdf"
}
```

## 4. Specific HackRx Test Queries

### Test Case 1: Cataract Waiting Period
**Body**:
```json
{
  "query": "What is the waiting period for cataract surgery?"
}
```

### Test Case 2: Hospital Definition
**Body**:
```json
{
  "query": "How is a hospital defined in this policy?"
}
```

### Test Case 3: Coverage Details
**Body**:
```json
{
  "query": "What medical expenses are covered under this policy?"
}
```

### Test Case 4: Premium Calculation
**Body**:
```json
{
  "query": "How is the premium calculated for this insurance policy?"
}
```

### Test Case 5: Exclusions
**Body**:
```json
{
  "query": "What are the exclusions in this insurance policy?"
}
```

## 5. Interactive API Documentation Test

**Method**: `GET`  
**URL**: `http://localhost:8000/docs`  
**Headers**: None

This will open the Swagger UI in your browser for interactive testing.

## Environment Variables for Postman

Create a Postman Environment called "HackRx Local" with these variables:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` |
| `api_version` | `v1` | `v1` |

Then use `{{base_url}}` in your requests instead of hardcoding the URL.

## Testing Scenarios

### Scenario 1: Basic Functionality Test
1. Run Health Check → Should return 200 OK
2. Run Basic Query → Should return answer with confidence score
3. Check response time < 3 seconds

### Scenario 2: Performance Test
1. Run the same query multiple times
2. Check if response times improve (caching effect)
3. Monitor memory usage

### Scenario 3: Error Handling Test
**Invalid Query Test**:
```json
{
  "query": ""
}
```
Expected: 400 Bad Request with validation error

**Missing Query Test**:
```json
{
  "document_url": "https://example.com/doc.pdf"
}
```
Expected: 400 Bad Request with missing field error

### Scenario 4: HackRx Benchmark Test
Run all 5 specific test queries and verify:
- All return 200 OK
- Confidence scores > 0.7
- Answers are relevant and detailed
- Processing time < 3 seconds each

## Advanced Postman Features

### Pre-request Scripts
Add this to your collection's Pre-request Script:
```javascript
// Set timestamp
pm.environment.set("timestamp", new Date().toISOString());

// Log request details
console.log("Testing endpoint:", pm.request.url);
console.log("Query:", JSON.stringify(pm.request.body.raw));
```

### Test Scripts
Add this to your requests' Test tab:
```javascript
// Basic response validation
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response time is less than 3000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(3000);
});

// For /hackrx/run endpoint
if (pm.request.url.toString().includes('/hackrx/run')) {
    pm.test("Response has required fields", function () {
        const jsonData = pm.response.json();
        pm.expect(jsonData).to.have.property('answer');
        pm.expect(jsonData).to.have.property('confidence');
        pm.expect(jsonData).to.have.property('processing_time');
    });
    
    pm.test("Confidence score is valid", function () {
        const jsonData = pm.response.json();
        pm.expect(jsonData.confidence).to.be.within(0, 1);
    });
}

// Log response for debugging
console.log("Response:", pm.response.json());
```

## Load Testing with Postman

### Collection Runner Setup
1. Create a Collection Runner
2. Select "HackRx RAG API" collection
3. Set iterations: 10
4. Set delay: 1000ms
5. Run to test load handling

### Monitor Results
- Check for any failed requests
- Monitor average response times
- Look for memory leaks or performance degradation

## Troubleshooting

### Common Issues

**1. Connection Refused**
- Make sure your server is running: `python main.py`
- Check the correct port (8000)
- Verify no firewall blocking

**2. 500 Internal Server Error**
- Check server logs in terminal
- Verify GOOGLE_API_KEY is set in .env file
- Check if all dependencies are installed

**3. Slow Response Times**
- First query is always slower (model loading)
- Subsequent queries should be faster
- Large documents take more time to process

**4. Empty or Poor Responses**
- Check if document is properly loaded
- Try more specific queries
- Verify document content is text-readable

### Debug Mode Testing
Run server in debug mode:
```bash
# Set environment variable
$env:LOG_LEVEL="DEBUG"
python main.py
```

This will show detailed logs for debugging API issues.

## Production Testing

When testing deployed versions, replace `localhost:8000` with your production URL:

- **Railway**: `https://your-app.railway.app`
- **Render**: `https://your-app.render.com`
- **Heroku**: `https://your-app.herokuapp.com`

## Next Steps

1. **Import the Postman collection** (see file below)
2. **Run health check** to verify server is working
3. **Test basic query** to ensure API functionality
4. **Run HackRx benchmark queries** to verify competition readiness
5. **Perform load testing** to check scalability

---

Happy testing! 🧪 Your HackRx RAG API is ready for comprehensive testing with Postman.
