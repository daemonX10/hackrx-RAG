import asyncio
import time
from typing import List, Dict, Any
from services.document_processor import DocumentProcessor
from services.embedding_service import EmbeddingService
from services.llm_service import LLMService
from models.schemas import QueryRequest, QueryResponse, AnswerResponse

class QueryService:
    """Main service that orchestrates document processing, embedding search, and LLM answering"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize all services"""
        if self.is_initialized:
            return
        
        await asyncio.gather(
            self.embedding_service.initialize(),
            self.llm_service.initialize()
        )
        self.is_initialized = True
    
    async def process_query(self, request: QueryRequest, include_detailed: bool = False) -> QueryResponse:
        """Main entry point for processing queries"""
        start_time = time.time()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Step 1: Process document
            print(f"Processing document: {request.documents}")
            chunks, doc_type = await self.document_processor.process_document(request.documents)
            print(f"Extracted {len(chunks)} chunks from {doc_type} document")
            
            # Step 2: Build embeddings index
            print("Building embeddings index...")
            await self.embedding_service.build_index(chunks)
            
            # Step 3: Process each question
            print(f"Processing {len(request.questions)} questions...")
            answers = []
            detailed_responses = []
            total_tokens = 0
            
            # Process questions with some concurrency but limit to avoid rate limits
            semaphore = asyncio.Semaphore(3)  # Max 3 concurrent questions
            
            async def process_single_question(question: str) -> tuple:
                async with semaphore:
                    return await self._answer_single_question(question)
            
            # Execute questions
            tasks = [process_single_question(q) for q in request.questions]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Handle failed question
                    answer = f"Error processing question: {str(result)}"
                    detailed_response = AnswerResponse(
                        question=request.questions[i],
                        answer=answer,
                        confidence_score=0.0,
                        reasoning="Error occurred during processing",
                        relevant_clauses=[],
                        token_usage={}
                    )
                else:
                    answer, detailed_response = result
                
                answers.append(answer)
                if include_detailed:
                    detailed_responses.append(detailed_response)
                
                # Sum up token usage
                if detailed_response.token_usage:
                    total_tokens += sum(detailed_response.token_usage.values())
            
            processing_time = time.time() - start_time
            
            # Create response
            response = QueryResponse(
                answers=answers,
                processing_time=processing_time,
                total_tokens_used=total_tokens
            )
            
            if include_detailed:
                response.detailed_responses = detailed_responses
            
            return response
            
        except Exception as e:
            # Return error response
            error_answers = [f"Error: {str(e)}" for _ in request.questions]
            return QueryResponse(
                answers=error_answers,
                processing_time=time.time() - start_time
            )
    
    async def _answer_single_question(self, question: str) -> tuple:
        """Process a single question and return answer + detailed response"""
        try:
            # Step 1: Enhanced context retrieval with multiple strategies
            
            # Get relevant chunks using semantic search
            relevant_chunks = await self.embedding_service.search_similar_chunks(question, top_k=8)
            
            # Get broader context for better understanding
            extended_context = await self.embedding_service.get_relevant_context(question, top_k=5)
            
            # Create comprehensive context combining multiple approaches
            comprehensive_context = self._create_comprehensive_context(question, relevant_chunks, extended_context)
            
            # Step 2: Use enhanced LLM prompt to generate answer
            detailed_response = await self.llm_service.answer_question(question, comprehensive_context, relevant_chunks)
            
            return detailed_response.answer, detailed_response
            
        except Exception as e:
            error_response = AnswerResponse(
                question=question,
                answer=f"Error processing question: {str(e)}",
                confidence_score=0.0,
                reasoning="Error occurred during question processing",
                relevant_clauses=[],
                token_usage={}
            )
            return error_response.answer, error_response
    
    def _create_comprehensive_context(self, question: str, relevant_chunks: List, extended_context: str) -> str:
        """Create comprehensive context for better LLM reasoning"""
        
        # Analyze question to determine what type of information to prioritize
        question_lower = question.lower()
        
        # Start with extended context
        context_parts = [extended_context]
        
        # Add specific relevant chunks with clear separation
        if relevant_chunks:
            context_parts.append("\n" + "="*50)
            context_parts.append("MOST RELEVANT DOCUMENT SECTIONS:")
            context_parts.append("="*50)
            
            for i, chunk in enumerate(relevant_chunks[:5]):
                context_parts.append(f"\nSECTION {i+1} (Relevance: {chunk.similarity_score:.3f}):")
                context_parts.append(f"{chunk.content}")
                if chunk.page_number:
                    context_parts.append(f"[Page: {chunk.page_number}]")
        
        # Add keyword-based context enhancement
        if any(word in question_lower for word in ["period", "time", "days", "months", "years"]):
            context_parts.append("\n" + "="*30)
            context_parts.append("TIME-RELATED INFORMATION FOCUS")
            context_parts.append("="*30)
            
        elif any(word in question_lower for word in ["define", "definition", "what is", "means"]):
            context_parts.append("\n" + "="*30)
            context_parts.append("DEFINITION AND EXPLANATION FOCUS")
            context_parts.append("="*30)
            
        elif any(word in question_lower for word in ["limit", "sub-limit", "cap", "maximum"]):
            context_parts.append("\n" + "="*30)
            context_parts.append("LIMITS AND RESTRICTIONS FOCUS")
            context_parts.append("="*30)
        
        return "\n".join(context_parts)
    
    async def analyze_document_structure(self, document_url: str) -> Dict[str, Any]:
        """Analyze document structure and extract metadata"""
        try:
            chunks, doc_type = await self.document_processor.process_document(document_url)
            
            # Basic analysis
            total_words = sum(len(chunk.content.split()) for chunk in chunks)
            pages = set(chunk.page_number for chunk in chunks if chunk.page_number)
            
            # Extract key terms using LLM
            sample_text = " ".join([chunk.content for chunk in chunks[:3]])  # First 3 chunks
            key_clauses = await self.llm_service.extract_key_clauses(sample_text)
            
            return {
                "document_type": doc_type.value,
                "total_chunks": len(chunks),
                "total_words": total_words,
                "total_pages": len(pages) if pages else None,
                "key_clauses": key_clauses,
                "average_chunk_size": total_words // len(chunks) if chunks else 0
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_document_summary(self, document_url: str, max_length: int = 500) -> str:
        """Generate a summary of the document"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            chunks, _ = await self.document_processor.process_document(document_url)
            
            # Get first few chunks for summary
            sample_text = " ".join([chunk.content for chunk in chunks[:5]])
            
            # Create summary prompt
            prompt = f"""Provide a concise summary of this document (max {max_length} characters):

{sample_text[:2000]}

Focus on:
- Document type and purpose
- Key coverage areas or topics
- Important terms and conditions
- Main benefits or provisions"""

            response = await self.llm_service.model.generate_content(prompt)
            summary = response.text[:max_length]
            
            return summary
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
