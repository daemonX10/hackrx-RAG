import asyncio
import aiofiles
import httpx
from typing import List, Optional, Tuple
from io import BytesIO
import PyPDF2
from docx import Document
import re
from models.schemas import DocumentChunk, DocumentType

class DocumentProcessor:
    """Handles document parsing and text extraction"""
    
    async def process_document(self, document_url: str) -> Tuple[List[DocumentChunk], DocumentType]:
        """Main entry point for document processing"""
        try:
            # Download document
            content, doc_type = await self._download_document(document_url)
            
            # Extract text based on document type
            if doc_type == DocumentType.PDF:
                text_chunks = await self._process_pdf(content)
            elif doc_type == DocumentType.DOCX:
                text_chunks = await self._process_docx(content)
            else:
                text_chunks = await self._process_text(content.decode('utf-8'))
            
            return text_chunks, doc_type
            
        except Exception as e:
            raise Exception(f"Document processing failed: {str(e)}")
    
    async def _download_document(self, url: str) -> Tuple[bytes, DocumentType]:
        """Download document from URL and determine type"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            
            content = response.content
            content_type = response.headers.get('content-type', '').lower()
            
            # Determine document type
            if 'pdf' in content_type or url.lower().endswith('.pdf'):
                doc_type = DocumentType.PDF
            elif 'wordprocessingml' in content_type or url.lower().endswith('.docx'):
                doc_type = DocumentType.DOCX
            elif 'text' in content_type or url.lower().endswith('.txt'):
                doc_type = DocumentType.TEXT
            else:
                # Try to detect from content
                if content.startswith(b'%PDF'):
                    doc_type = DocumentType.PDF
                elif b'PK' in content[:10]:  # ZIP signature for DOCX
                    doc_type = DocumentType.DOCX
                else:
                    doc_type = DocumentType.TEXT
            
            return content, doc_type
    
    async def _process_pdf(self, content: bytes) -> List[DocumentChunk]:
        """Extract text from PDF content"""
        chunks = []
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    # Split text into chunks
                    page_chunks = self._create_text_chunks(text, page_num + 1)
                    chunks.extend(page_chunks)
            
            return chunks
        except Exception as e:
            raise Exception(f"PDF processing error: {str(e)}")
    
    async def _process_docx(self, content: bytes) -> List[DocumentChunk]:
        """Extract text from DOCX content"""
        chunks = []
        try:
            docx_file = BytesIO(content)
            doc = Document(docx_file)
            
            full_text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    full_text.append(paragraph.text)
            
            text = '\n'.join(full_text)
            chunks = self._create_text_chunks(text)
            
            return chunks
        except Exception as e:
            raise Exception(f"DOCX processing error: {str(e)}")
    
    async def _process_text(self, content: str) -> List[DocumentChunk]:
        """Process plain text content"""
        return self._create_text_chunks(content)
    
    def _create_text_chunks(self, text: str, page_number: Optional[int] = None) -> List[DocumentChunk]:
        """Split text into manageable chunks"""
        from config import settings
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        chunks = []
        chunk_size = settings.MAX_CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        
        # Split by sentences to maintain context
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                # Create chunk
                chunk = DocumentChunk(
                    content=current_chunk.strip(),
                    page_number=page_number,
                    chunk_index=chunk_index,
                    metadata={"word_count": len(current_chunk.split())}
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Start new chunk with overlap
                words = current_chunk.split()
                if len(words) > overlap // 10:  # Approximate word overlap
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
            chunk = DocumentChunk(
                content=current_chunk.strip(),
                page_number=page_number,
                chunk_index=chunk_index,
                metadata={"word_count": len(current_chunk.split())}
            )
            chunks.append(chunk)
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:\-\(\)\[\]{}"\']', ' ', text)
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)
        
        return text.strip()
