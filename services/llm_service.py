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
        """Create a structured prompt for question answering with enhanced contextual reasoning"""
        
        # Prepare relevant chunks with better context
        chunk_info = ""
        if relevant_chunks:
            chunk_info = "\n".join([
                f"RELEVANT SECTION {i+1} (Similarity: {chunk.similarity_score:.3f}):\n{chunk.content}\n"
                for i, chunk in enumerate(relevant_chunks[:5])  # Use top 5 chunks for better context
            ])
        
        # Analyze question type for better prompting
        question_lower = question.lower()
        question_type = "general"
        specific_instructions = ""
        
        if any(word in question_lower for word in ["grace period", "waiting period", "period"]):
            question_type = "time_period"
            specific_instructions = """
SPECIAL FOCUS: This question asks about time periods. Look for:
- Specific durations (days, months, years)
- Grace periods, waiting periods, or policy periods
- Time-based conditions or requirements
- Exact numerical values with units (e.g., "30 days", "36 months", "2 years")"""
        
        elif any(word in question_lower for word in ["define", "definition", "what is", "what does", "means"]):
            question_type = "definition"
            specific_instructions = """
SPECIAL FOCUS: This question asks for a definition. Look for:
- Formal definitions or explanations
- Detailed descriptions of terms or concepts
- Specific criteria or requirements that define something
- Complete explanations rather than partial mentions"""
        
        elif any(word in question_lower for word in ["cover", "coverage", "included", "benefit", "include", "scope"]):
            question_type = "coverage"
            specific_instructions = """
SPECIAL FOCUS: This question asks about coverage, benefits, or what's included. Look for:
- What is covered, included, or within scope
- Specific benefits, services, or features
- Coverage limits, conditions, or restrictions
- Eligibility criteria or requirements
- Services, products, or areas included"""
        
        elif any(word in question_lower for word in ["discount", "reduction", "deduction", "savings", "rebate"]):
            question_type = "discount"
            specific_instructions = """
SPECIAL FOCUS: This question asks about discounts, reductions, or savings. Look for:
- Discount percentages, amounts, or reductions
- Conditions for earning discounts or savings
- Maximum or minimum discount amounts
- Rebates, deductions, or cost savings
- Special offers or promotional reductions"""
        
        elif any(word in question_lower for word in ["limit", "cap", "maximum", "minimum", "threshold", "restriction"]):
            question_type = "limits"
            specific_instructions = """
SPECIAL FOCUS: This question asks about limits, caps, or restrictions. Look for:
- Maximum and minimum amounts, quantities, or values
- Caps, thresholds, or upper/lower bounds
- Restrictions, limitations, or constraints
- Specific numerical limits or ranges
- Conditions that impose limits or restrictions"""
        
        elif any(word in question_lower for word in ["process", "procedure", "step", "how to", "method"]):
            question_type = "process"
            specific_instructions = """
SPECIAL FOCUS: This question asks about processes or procedures. Look for:
- Step-by-step procedures or methods
- Process descriptions and workflows
- Instructions or guidelines
- Sequential actions or requirements
- How-to information and methodologies"""
        
        elif any(word in question_lower for word in ["requirement", "criteria", "condition", "eligible", "qualification"]):
            question_type = "requirements"
            specific_instructions = """
SPECIAL FOCUS: This question asks about requirements or criteria. Look for:
- Eligibility criteria and qualifications
- Required conditions or prerequisites
- Mandatory requirements or specifications
- Qualification standards or benchmarks
- Compliance requirements or conditions"""

        prompt = f"""You are an expert document analyst specialized in extracting and analyzing information from various types of documents. Your task is to provide precise, accurate answers based strictly on the provided document content.

DOCUMENT SOURCE: The analysis is based on the user-provided document. If no specific document was provided by the user, information comes from the available knowledge base.

QUESTION TYPE: {question_type.upper()}
QUESTION: {question}

{specific_instructions}

DOCUMENT CONTEXT (Document excerpt):
{context}

{chunk_info}

CRITICAL ANALYSIS INSTRUCTIONS:

1. QUESTION UNDERSTANDING:
   - Break down the question into key components
   - Identify exactly what information is being requested
   - Note any specific details needed (numbers, dates, conditions, policies, procedures)

2. DOCUMENT SEARCH STRATEGY:
   - Scan ALL provided context for relevant information
   - Look for exact matches and synonymous terms
   - Pay special attention to numbered sections, definitions, policy clauses, procedures, and key terms
   - Cross-reference information across different sections

3. ACCURACY REQUIREMENTS:
   - Use ONLY information explicitly stated in the document
   - Include specific numbers, percentages, time periods, names, dates exactly as written
   - Maintain original terminology and phrasing from the document
   - If information is implied but not explicitly stated, note this clearly

4. ANSWER COMPLETENESS:
   - Provide the main answer first
   - Include all relevant conditions, exceptions, qualifications, or procedures
   - Mention related information that adds context
   - State clearly if information is not found in the provided document

5. DOCUMENT CONTEXT AWARENESS:
   - If answering from user-provided document: Focus primarily on that document's content
   - If no user document provided: Use available knowledge base information
   - Always specify the source of your information when possible

RESPONSE FORMAT:
ANSWER: [Direct, complete answer with specific details from the document]

CONFIDENCE: [Score from 0.0 to 1.0 - Use 0.9+ only when information is explicitly stated, 0.7-0.8 for clear implications, 0.5-0.6 for partial information, 0.3-0.4 when information is unclear, 0.0-0.2 when not found]

REASONING: [Detailed explanation citing specific document sections, clause numbers, page references, or exact text that supports your answer. If answer not found, explain what you searched for and why it's not available.]

QUALITY CHECKLIST:
✓ Answer addresses the exact question asked
✓ All specific details (numbers, dates, conditions, names) are included
✓ Information is directly from the document text
✓ Confidence score reflects actual certainty
✓ Reasoning explains the evidence clearly
✓ Source of information is clear (user document vs knowledge base)

IMPORTANT: If the specific information requested is not clearly stated in the provided context, respond with "The provided document does not contain specific information about [topic]" and explain what related information IS available. Always prioritize the user's document content when available."""

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
