import numpy as np
import faiss
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import os
import pickle
from models.schemas import DocumentChunk, ClauseMatch
from services.pinecone_service import PineconeService

class EmbeddingService:
    """Handles document embeddings and semantic search using FAISS and Pinecone"""
    
    def __init__(self):
        self.model = None
        self.index = None
        self.chunks = []
        self.is_initialized = False
        self.pinecone_service = PineconeService()
    
    async def initialize(self):
        """Initialize the embedding model, FAISS index, and Pinecone"""
        if self.is_initialized:
            return
        
        from config import settings
        
        try:
            # Load embedding model
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Initialize FAISS index (as fallback)
            self.index = faiss.IndexFlatIP(settings.EMBEDDING_DIMENSION)  # Inner Product for cosine similarity
            
            # Initialize Pinecone service
            await self.pinecone_service.initialize()
            
            self.is_initialized = True
            
        except Exception as e:
            raise Exception(f"Failed to initialize embedding service: {str(e)}")
    
    async def create_embeddings(self, chunks: List[DocumentChunk]) -> np.ndarray:
        """Create embeddings for document chunks and attach them to chunks"""
        if not self.is_initialized:
            await self.initialize()
        
        # Extract text content
        texts = [chunk.content for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=False, normalize_embeddings=True)
        
        # Attach embeddings to chunks for Pinecone storage
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i].tolist()
        
        return embeddings
    
    async def build_index(self, chunks: List[DocumentChunk], document_path: str = "", is_local: bool = False) -> None:
        """Build index from document chunks with Pinecone priority"""
        if not self.is_initialized:
            await self.initialize()
        
        # Check if document is already in Pinecone (for local docs)
        if is_local and await self.pinecone_service.is_document_indexed(document_path, is_local=True):
            print(f"✅ Local document already indexed in Pinecone: {document_path}")
            return
        
        # Store chunks for FAISS fallback
        self.chunks = chunks
        
        # Create embeddings
        embeddings = await self.create_embeddings(chunks)
        
        # Store in Pinecone if available
        if self.pinecone_service.is_initialized:
            await self.pinecone_service.store_document_chunks(chunks, document_path, is_local)
        
        # Also add to FAISS as fallback
        if hasattr(self, 'index') and self.index is not None:
            self.index.add(embeddings.astype('float32'))
        
        print(f"Built index with {len(chunks)} chunks {'(cached in Pinecone)' if self.pinecone_service.is_initialized else '(FAISS only)'}")
    
    async def search_similar_chunks(self, query: str, top_k: int = 5, prefer_user_docs: bool = True) -> List[ClauseMatch]:
        """Search for similar document chunks with priority for user documents"""
        if not self.is_initialized:
            await self.initialize()
        
        # Try Pinecone first (with priority system)
        if self.pinecone_service.is_initialized:
            query_embedding = self.model.encode([query], convert_to_tensor=False, normalize_embeddings=True)
            results = await self.pinecone_service.search_similar_chunks(
                query_embedding[0].tolist(), 
                top_k=top_k, 
                prefer_user_docs=prefer_user_docs
            )
            if results:
                return results
        
        # Fallback to FAISS
        if hasattr(self, 'index') and self.index is not None and self.index.ntotal > 0:
            query_embedding = self.model.encode([query], convert_to_tensor=False, normalize_embeddings=True)
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            matches = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    match = ClauseMatch(
                        content=chunk.content,
                        similarity_score=float(score),
                        page_number=chunk.page_number,
                        chunk_index=chunk.chunk_index,
                        metadata={
                            **chunk.metadata,
                            "source_priority": "fallback_faiss",
                            "source_type": "faiss"
                        }
                    )
                    matches.append(match)
            return matches
        
        return []
    
    async def get_relevant_context(self, query: str, top_k: int = 3) -> str:
        """Get relevant context for a query as a single string"""
        matches = await self.search_similar_chunks(query, top_k)
        
        if not matches:
            return ""
        
        # Combine top matches into context
        context_parts = []
        for i, match in enumerate(matches):
            context_parts.append(f"[Context {i+1}] {match.content}")
        
        return "\n\n".join(context_parts)
    
    def save_index(self, path: str) -> None:
        """Save FAISS index and chunks to disk"""
        if not self.is_initialized or self.index.ntotal == 0:
            return
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}.faiss")
        
        # Save chunks
        with open(f"{path}.chunks", 'wb') as f:
            pickle.dump(self.chunks, f)
    
    def load_index(self, path: str) -> bool:
        """Load FAISS index and chunks from disk"""
        try:
            if not self.is_initialized:
                return False
            
            # Load FAISS index
            if os.path.exists(f"{path}.faiss"):
                self.index = faiss.read_index(f"{path}.faiss")
            
            # Load chunks
            if os.path.exists(f"{path}.chunks"):
                with open(f"{path}.chunks", 'rb') as f:
                    self.chunks = pickle.load(f)
            
            return True
        except Exception:
            return False
    
    def clear_index(self):
        """Clear the current index and chunks"""
        if self.is_initialized:
            from config import settings
            self.index = faiss.IndexFlatIP(settings.EMBEDDING_DIMENSION)
            self.chunks = []
