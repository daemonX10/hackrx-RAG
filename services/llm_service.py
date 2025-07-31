import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import re
from models.schemas import AnswerResponse, ClauseMatch

class LLMService:
    """Handles LLM interactions using Google Gemini API"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the Gemini model"""
        if self.is_initialized:
            return
        
        from config import settings
        
        if not settings.GEMINI_API_KEY:
            raise Exception("GEMINI_API_KEY not found in environment variables")
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.is_initialized = True
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini model: {str(e)}")
    
    async def answer_question(self, question: str, context: str, relevant_chunks: List[ClauseMatch]) -> AnswerResponse:
        """Generate an answer for a question using context and relevant chunks"""
        if not self.is_initialized:
            await self.initialize()
        
        # Create the prompt
        prompt = self._create_answer_prompt(question, context, relevant_chunks)
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse the response
            answer_data = self._parse_llm_response(response.text)
            
            # Create structured response
            return AnswerResponse(
                question=question,
                answer=answer_data.get("answer", "Unable to determine answer from provided context."),
                confidence_score=answer_data.get("confidence_score", 0.5),
                reasoning=answer_data.get("reasoning", "Analysis based on provided document context."),
                relevant_clauses=relevant_chunks,
                token_usage={"input_tokens": len(prompt.split()), "output_tokens": len(response.text.split())}
            )
            
        except Exception as e:
            # Fallback response
            return AnswerResponse(
                question=question,
                answer=f"Error processing question: {str(e)}",
                confidence_score=0.0,
                reasoning="Error occurred during LLM processing",
                relevant_clauses=relevant_chunks,
                token_usage={}
            )
    
    def _create_answer_prompt(self, question: str, context: str, relevant_chunks: List[ClauseMatch]) -> str:
        """Create a structured prompt for question answering"""
        
        chunk_info = ""
        if relevant_chunks:
            chunk_info = "\n".join([
                f"- Chunk {i+1} (Score: {chunk.similarity_score:.3f}): {chunk.content[:200]}..."
                for i, chunk in enumerate(relevant_chunks[:3])
            ])
        
        prompt = f"""You are an expert document analyst specializing in insurance, legal, HR, and compliance domains. 
Your task is to answer questions based on the provided document context with high accuracy and explainability.

QUESTION: {question}

DOCUMENT CONTEXT:
{context}

RELEVANT DOCUMENT SECTIONS:
{chunk_info}

INSTRUCTIONS:
1. Analyze the question carefully and identify the key information needed
2. Search through the provided context for relevant information
3. Provide a precise, factual answer based ONLY on the information in the context
4. If the answer is not clearly stated in the context, say so explicitly
5. Include specific details like numbers, dates, conditions, or requirements when available
6. Provide reasoning for your answer citing specific parts of the document

RESPONSE FORMAT:
Please structure your response as follows:

ANSWER: [Your direct answer to the question]

CONFIDENCE: [A score from 0.0 to 1.0 indicating your confidence in the answer]

REASONING: [Detailed explanation of how you arrived at the answer, citing specific document sections]

Remember:
- Be precise and factual
- Only use information from the provided context
- If information is unclear or missing, state this explicitly
- Focus on insurance, legal, HR, and compliance terminology accuracy"""

        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the structured LLM response"""
        try:
            # Extract sections using regex
            answer_match = re.search(r'ANSWER:\s*(.*?)(?=\n\n|\nCONFIDENCE:|$)', response_text, re.DOTALL | re.IGNORECASE)
            confidence_match = re.search(r'CONFIDENCE:\s*([\d.]+)', response_text, re.IGNORECASE)
            reasoning_match = re.search(r'REASONING:\s*(.*?)(?=\n\n|$)', response_text, re.DOTALL | re.IGNORECASE)
            
            answer = answer_match.group(1).strip() if answer_match else response_text.strip()
            confidence = float(confidence_match.group(1)) if confidence_match else 0.7
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "Based on document analysis"
            
            # Ensure confidence is between 0 and 1
            confidence = max(0.0, min(1.0, confidence))
            
            return {
                "answer": answer,
                "confidence_score": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            return {
                "answer": response_text.strip(),
                "confidence_score": 0.5,
                "reasoning": f"Response parsing error: {str(e)}"
            }
    
    async def extract_key_clauses(self, text: str, domain_keywords: List[str] = None) -> List[str]:
        """Extract key clauses from document text"""
        if not self.is_initialized:
            await self.initialize()
        
        domain_keywords = domain_keywords or ["policy", "coverage", "premium", "claim", "benefit", "waiting period", "exclusion"]
        
        prompt = f"""Analyze the following document text and extract key clauses related to {', '.join(domain_keywords)}.

TEXT:
{text[:2000]}  # Limit text to avoid token limits

Extract the most important clauses, conditions, and policy details. Focus on:
- Coverage details and limits
- Waiting periods and conditions
- Premium and payment terms
- Benefits and exclusions
- Important definitions

Return only the key clauses, one per line."""

        try:
            response = self.model.generate_content(prompt)
            clauses = [line.strip() for line in response.text.split('\n') if line.strip()]
            return clauses[:10]  # Return top 10 clauses
        except Exception:
            return []
    
    async def evaluate_query_complexity(self, question: str) -> Dict[str, Any]:
        """Evaluate the complexity and domain of a question"""
        if not self.is_initialized:
            await self.initialize()
        
        prompt = f"""Analyze this question and provide complexity assessment:

QUESTION: {question}

Assess:
1. Complexity level (1-5 scale)
2. Domain type (insurance/legal/HR/compliance/other)
3. Required information type (factual/analytical/comparative)
4. Key terms to search for

Respond in JSON format:
{{
    "complexity": 1-5,
    "domain": "domain_type",
    "information_type": "type",
    "key_terms": ["term1", "term2"]
}}"""

        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception:
            return {
                "complexity": 3,
                "domain": "general",
                "information_type": "factual",
                "key_terms": question.split()[:5]
            }
