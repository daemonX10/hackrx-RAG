# HackRx 6.0 - LLM-Powered Intelligent Query-Retrieval System

## Overview
This solution implements an intelligent document processing and query retrieval system using FastAPI, Pydantic, and Google Gemini API. It processes PDFs, DOCX, and email documents to answer contextual questions for insurance, legal, HR, and compliance domains.

## Features
- ✅ Document processing (PDF, DOCX, Email)
- ✅ Semantic search using FAISS embeddings
- ✅ LLM-powered query understanding with Gemini API
- ✅ Clause matching and retrieval
- ✅ Explainable decision rationale
- ✅ Structured JSON responses
- ✅ Token-efficient processing

## Architecture
```
Input Documents → Document Parser → Embedding Search → Clause Matching → Logic Evaluation → JSON Output
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 3. Run the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the API
The API will be available at `http://localhost:8000`

## API Endpoints

### POST /api/v1/hackrx/run
Process documents and answer questions.

**Request:**
```json
{
    "documents": "https://example.com/document.pdf",
    "questions": [
        "What is the grace period for premium payment?"
    ]
}
```

**Response:**
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment..."
    ]
}
```

## Project Structure
```
hackrx-solution/
├── main.py                 # FastAPI application
├── models/                 # Pydantic models
├── services/              # Core business logic
├── utils/                 # Utility functions
├── config.py              # Configuration
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Evaluation Criteria Coverage
- **Accuracy**: Semantic search + LLM reasoning
- **Token Efficiency**: Optimized prompts and chunking
- **Latency**: Async processing and caching
- **Reusability**: Modular architecture
- **Explainability**: Detailed decision rationale
