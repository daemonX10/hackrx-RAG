import re
import hashlib
from typing import List, Dict, Any
from urllib.parse import urlparse

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.,!?;:\-\(\)\[\]{}"\']', ' ', text)
    # Fix spacing around punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)
    
    return text.strip()

def extract_domain_keywords(text: str, domain: str = "insurance") -> List[str]:
    """Extract domain-specific keywords from text"""
    domain_patterns = {
        "insurance": [
            r'\b(?:policy|coverage|premium|claim|benefit|deductible|copay)\b',
            r'\b(?:waiting period|grace period|renewal|exclusion)\b',
            r'\b(?:insured|insurer|policyholder|beneficiary)\b'
        ],
        "legal": [
            r'\b(?:contract|agreement|clause|provision|liability)\b',
            r'\b(?:terms|conditions|obligations|rights|duties)\b',
            r'\b(?:breach|compliance|violation|penalty)\b'
        ],
        "hr": [
            r'\b(?:employee|employer|employment|salary|benefits)\b',
            r'\b(?:leave|vacation|sick|medical|dental)\b',
            r'\b(?:performance|evaluation|promotion|termination)\b'
        ]
    }
    
    keywords = []
    patterns = domain_patterns.get(domain, domain_patterns["insurance"])
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend([match.lower() for match in matches])
    
    # Remove duplicates and return
    return list(set(keywords))

def create_document_hash(content: str) -> str:
    """Create a hash for document content for caching"""
    return hashlib.md5(content.encode()).hexdigest()

def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def split_text_smartly(text: str, max_chunk_size: int, overlap: int = 100) -> List[str]:
    """Split text into chunks while preserving sentence boundaries"""
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    
    for sentence in sentences:
        # Check if adding this sentence would exceed chunk size
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap
            words = current_chunk.split()
            if len(words) > overlap // 10:
                overlap_text = ' '.join(words[-(overlap // 10):])
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def calculate_similarity_score(query_embedding, doc_embedding) -> float:
    """Calculate cosine similarity between embeddings"""
    try:
        import numpy as np
        
        # Normalize embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norm = doc_embedding / np.linalg.norm(doc_embedding)
        
        # Calculate cosine similarity
        similarity = np.dot(query_norm, doc_norm)
        
        return float(similarity)
    except:
        return 0.0

def format_processing_time(seconds: float) -> str:
    """Format processing time in human-readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

def extract_numbers_and_dates(text: str) -> Dict[str, List[str]]:
    """Extract numbers and dates from text"""
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    dates = re.findall(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b', text, re.IGNORECASE)
    
    return {
        "numbers": numbers,
        "dates": dates
    }

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
