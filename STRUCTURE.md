# 🏗️ Project Structure

```
hackrx-solution/
├── 📁 models/                     # Pydantic data models
│   ├── __init__.py
│   └── schemas.py                # Request/Response models
│
├── 📁 services/                   # Core business logic
│   ├── __init__.py
│   ├── document_processor.py     # PDF/DOCX processing
│   ├── embedding_service.py      # FAISS vector search
│   ├── llm_service.py            # Gemini LLM integration
│   └── query_service.py          # Main orchestration
│
├── 📁 utils/                      # Utility functions
│   ├── __init__.py
│   └── text_processing.py        # Text processing helpers
│
├── 📄 main.py                     # FastAPI application
├── 📄 config.py                   # Configuration settings
├── 📄 requirements.txt            # Python dependencies
├── 📄 .env.example               # Environment template
├── 📄 README.md                   # Project documentation
├── 📄 DEPLOYMENT.md              # Deployment guide
├── 📄 test_api.py                # API testing suite
├── 📄 start.bat                  # Windows startup script
└── 📄 start.sh                   # Linux/Mac startup script
```

## 🔧 Key Components

### 1. **Document Processor** (`services/document_processor.py`)
- Downloads documents from URLs
- Extracts text from PDF, DOCX files
- Splits text into semantic chunks
- Handles multiple document formats

### 2. **Embedding Service** (`services/embedding_service.py`)
- Creates semantic embeddings using SentenceTransformers
- Builds FAISS index for fast similarity search
- Performs semantic retrieval of relevant chunks
- Optimized for speed and accuracy

### 3. **LLM Service** (`services/llm_service.py`)
- Integrates with Google Gemini API
- Generates contextual answers with reasoning
- Provides explainable decision rationale
- Optimized for token efficiency

### 4. **Query Service** (`services/query_service.py`)
- Orchestrates the complete workflow
- Handles multiple questions concurrently
- Provides detailed analytics and metrics
- Manages error handling and fallbacks

### 5. **FastAPI Application** (`main.py`)
- RESTful API endpoints
- Async request handling
- Comprehensive error handling
- Health monitoring and status checks

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API info |
| `/health` | GET | Health check and service status |
| `/api/v1/hackrx/run` | POST | Main query processing endpoint |
| `/api/v1/hackrx/run/detailed` | POST | Detailed responses with analytics |
| `/api/v1/analyze-document` | POST | Document structure analysis |
| `/api/v1/summarize-document` | POST | Document summarization |

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your GEMINI_API_KEY
   ```

2. **Run Server**
   ```bash
   python main.py
   # or use start.bat (Windows) / start.sh (Linux/Mac)
   ```

3. **Test API**
   ```bash
   python test_api.py
   ```

## 📊 Evaluation Criteria Coverage

✅ **Accuracy**: Semantic search + LLM reasoning  
✅ **Token Efficiency**: Optimized prompts and chunking  
✅ **Latency**: Async processing and concurrent handling  
✅ **Reusability**: Modular architecture with clear separation  
✅ **Explainability**: Detailed reasoning and clause traceability  

## 🏆 HackRx 6.0 Ready!

This solution is designed specifically for the HackRx 6.0 requirements:
- Processes insurance, legal, HR, and compliance documents
- Handles PDF, DOCX, and email formats
- Uses embeddings for semantic search (FAISS)
- Implements clause retrieval and matching
- Provides explainable decision rationale
- Returns structured JSON responses
- Optimized for accuracy and performance
