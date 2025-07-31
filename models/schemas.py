from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    EMAIL = "email"
    TEXT = "text"

class QueryRequest(BaseModel):
    documents: str = Field(..., description="URL or path to the document")
    questions: List[str] = Field(..., description="List of questions to answer")
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one question is required")
        return v

class DocumentChunk(BaseModel):
    content: str
    page_number: Optional[int] = None
    chunk_index: int
    metadata: Dict[str, Any] = {}

class ClauseMatch(BaseModel):
    content: str
    similarity_score: float
    page_number: Optional[int] = None
    chunk_index: int
    metadata: Dict[str, Any] = {}

class AnswerResponse(BaseModel):
    question: str
    answer: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    relevant_clauses: List[ClauseMatch]
    token_usage: Dict[str, int] = {}

class QueryResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers corresponding to input questions")
    detailed_responses: Optional[List[AnswerResponse]] = None
    processing_time: Optional[float] = None
    total_tokens_used: Optional[int] = None

class LegacyQueryRequest(BaseModel):
    """Backward-compatible request format for existing clients"""
    query: str = Field(..., description="The question to ask about the document")
    document_url: str = Field(..., description="URL to the document to analyze")

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
