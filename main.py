from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from config import settings
from models.schemas import QueryRequest, QueryResponse, ErrorResponse
from services.query_service import QueryService

# Global service instance
query_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    global query_service
    
    # Startup
    print("🚀 Starting HackRx 6.0 Intelligent Query-Retrieval System...")
    query_service = QueryService()
    
    try:
        await query_service.initialize()
        print("✅ All services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🔄 Shutting down services...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LLM-Powered Intelligent Query-Retrieval System for HackRx 6.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_query_service() -> QueryService:
    """Dependency to get query service instance"""
    if query_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return query_service

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "HackRx 6.0 - Intelligent Query-Retrieval System",
        "version": settings.VERSION,
        "status": "running",
        "endpoints": {
            "main": "/api/v1/hackrx/run",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global query_service
    
    services_status = {
        "query_service": query_service is not None,
        "embedding_service": query_service.embedding_service.is_initialized if query_service else False,
        "llm_service": query_service.llm_service.is_initialized if query_service else False
    }
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": services_status
    }
    
    if not all(services_status.values()):
        health_status["status"] = "degraded"
    
    return health_status

@app.post(f"{settings.API_V1_PREFIX}/hackrx/run", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    service: QueryService = Depends(get_query_service)
):
    """
    Main endpoint for processing document queries
    
    This endpoint:
    1. Downloads and processes documents (PDF, DOCX, etc.)
    2. Creates semantic embeddings using FAISS
    3. Performs similarity search for relevant chunks
    4. Uses LLM (Gemini) to generate contextual answers
    5. Returns structured JSON responses
    """
    try:
        # Validate request
        if not request.documents:
            raise HTTPException(status_code=400, detail="Document URL is required")
        
        if not request.questions:
            raise HTTPException(status_code=400, detail="At least one question is required")
        
        # Process the query
        result = await service.process_query(request, include_detailed=False)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.post(f"{settings.API_V1_PREFIX}/hackrx/run/detailed", response_model=QueryResponse)
async def process_query_detailed(
    request: QueryRequest,
    service: QueryService = Depends(get_query_service)
):
    """
    Extended endpoint that returns detailed responses including:
    - Confidence scores
    - Reasoning explanations
    - Relevant document clauses
    - Token usage statistics
    """
    try:
        result = await service.process_query(request, include_detailed=True)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post(f"{settings.API_V1_PREFIX}/analyze-document")
async def analyze_document(
    document_url: str,
    service: QueryService = Depends(get_query_service)
):
    """
    Analyze document structure and extract metadata
    """
    try:
        analysis = await service.analyze_document_structure(document_url)
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {str(e)}"
        )

@app.post(f"{settings.API_V1_PREFIX}/summarize-document")
async def summarize_document(
    document_url: str,
    max_length: int = 500,
    service: QueryService = Depends(get_query_service)
):
    """
    Generate a summary of the document
    """
    try:
        summary = await service.get_document_summary(document_url, max_length)
        return {"summary": summary}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document summarization failed: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message=str(exc),
            details={"path": str(request.url)}
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting {settings.PROJECT_NAME}")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔗 Main Endpoint: http://localhost:{port}{settings.API_V1_PREFIX}/hackrx/run")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
