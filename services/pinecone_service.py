import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import hashlib
import json
from config import settings
from models.schemas import DocumentChunk, ClauseMatch

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("⚠️  Pinecone not available, falling back to FAISS only")

class PineconeService:
    """Handles Pinecone vector database operations for persistent document storage"""
    
    def __init__(self):
        self.pc = None
        self.index = None
        self.is_initialized = False
        self.local_docs_namespace = "local_docs"
        self.user_docs_namespace = "user_docs"
    
    async def initialize(self):
        """Initialize Pinecone connection"""
        if self.is_initialized:
            return
        
        if not PINECONE_AVAILABLE:
            print("⚠️  Pinecone package not available, falling back to FAISS")
            return
        
        if not settings.PINECONE_API_KEY:
            print("⚠️  Pinecone API key not provided, falling back to FAISS")
            return
        
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Use the provided endpoint directly if available
            if settings.PINECONE_ENDPOINT:
                print(f"Using Pinecone endpoint: {settings.PINECONE_ENDPOINT}")
                # Connect directly to the index using the endpoint
                self.index = self.pc.Index(
                    name=settings.PINECONE_INDEX_NAME,
                    host=settings.PINECONE_ENDPOINT
                )
            else:
                # Fallback: Check if index exists, create if not
                if settings.PINECONE_INDEX_NAME not in [index.name for index in self.pc.list_indexes()]:
                    print(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
                    self.pc.create_index(
                        name=settings.PINECONE_INDEX_NAME,
                        dimension=settings.EMBEDDING_DIMENSION,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region=settings.PINECONE_ENVIRONMENT
                        )
                    )
                    # Wait for index to be ready
                    await asyncio.sleep(5)
                
                # Connect to index
                self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            
            self.is_initialized = True
            print("✅ Pinecone initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Pinecone: {e}")
            print("⚠️  Falling back to FAISS for vector storage")
    
    def _generate_doc_hash(self, file_path: str) -> str:
        """Generate a hash for document to check if it's already processed"""
        if file_path.startswith(('http://', 'https://')):
            return hashlib.md5(file_path.encode()).hexdigest()
        else:
            # For local files, use file path + modification time
            try:
                stat = os.stat(file_path)
                content = f"{file_path}:{stat.st_mtime}"
                return hashlib.md5(content.encode()).hexdigest()
            except:
                return hashlib.md5(file_path.encode()).hexdigest()
    
    async def is_document_indexed(self, document_path: str, is_local: bool = False) -> bool:
        """Check if document is already indexed in Pinecone"""
        if not self.is_initialized:
            return False
        
        try:
            doc_hash = self._generate_doc_hash(document_path)
            namespace = self.local_docs_namespace if is_local else self.user_docs_namespace
            
            # Check if any vectors exist with this document hash
            query_result = self.index.query(
                vector=[0.0] * settings.EMBEDDING_DIMENSION,
                filter={"doc_hash": doc_hash},
                namespace=namespace,
                top_k=1,
                include_metadata=True
            )
            
            return len(query_result.matches) > 0
            
        except Exception as e:
            print(f"Error checking document index status: {e}")
            return False
    
    async def store_document_chunks(self, chunks: List[DocumentChunk], document_path: str, is_local: bool = False):
        """Store document chunks in Pinecone"""
        if not self.is_initialized:
            return
        
        try:
            doc_hash = self._generate_doc_hash(document_path)
            namespace = self.local_docs_namespace if is_local else self.user_docs_namespace
            
            # Prepare vectors for upsert
            vectors = []
            for i, chunk in enumerate(chunks):
                vector_id = f"{doc_hash}_{i}"
                metadata = {
                    "doc_hash": doc_hash,
                    "document_path": document_path,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "is_local": is_local,
                    **chunk.metadata
                }
                
                # Assuming chunks already have embeddings, if not we'll need to generate them
                if hasattr(chunk, 'embedding') and chunk.embedding is not None:
                    vectors.append({
                        "id": vector_id,
                        "values": chunk.embedding,
                        "metadata": metadata
                    })
            
            if vectors:
                # Upsert in batches
                batch_size = 100
                for i in range(0, len(vectors), batch_size):
                    batch = vectors[i:i + batch_size]
                    self.index.upsert(vectors=batch, namespace=namespace)
                
                print(f"✅ Stored {len(vectors)} chunks in Pinecone namespace '{namespace}'")
            
        except Exception as e:
            print(f"Error storing chunks in Pinecone: {e}")
    
    async def search_similar_chunks(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        prefer_user_docs: bool = True
    ) -> List[ClauseMatch]:
        """Search for similar chunks in Pinecone with priority for user documents"""
        if not self.is_initialized:
            return []
        
        try:
            results = []
            
            if prefer_user_docs:
                # First search in user documents (higher priority)
                user_results = self.index.query(
                    vector=query_embedding,
                    namespace=self.user_docs_namespace,
                    top_k=top_k,
                    include_metadata=True
                )
                
                for match in user_results.matches:
                    results.append(ClauseMatch(
                        content=match.metadata.get("content", ""),
                        similarity_score=float(match.score),
                        page_number=match.metadata.get("page_number"),
                        chunk_index=match.metadata.get("chunk_index", 0),
                        metadata={
                            **match.metadata,
                            "source_priority": "user_document",
                            "source_type": "external"
                        }
                    ))
                
                # If we don't have enough results, search local docs
                if len(results) < top_k:
                    remaining_k = top_k - len(results)
                    local_results = self.index.query(
                        vector=query_embedding,
                        namespace=self.local_docs_namespace,
                        top_k=remaining_k,
                        include_metadata=True
                    )
                    
                    for match in local_results.matches:
                        results.append(ClauseMatch(
                            content=match.metadata.get("content", ""),
                            similarity_score=float(match.score) * 0.8,  # Lower priority for local docs
                            page_number=match.metadata.get("page_number"),
                            chunk_index=match.metadata.get("chunk_index", 0),
                            metadata={
                                **match.metadata,
                                "source_priority": "local_document",
                                "source_type": "local"
                            }
                        ))
            else:
                # Search both namespaces equally
                for namespace in [self.user_docs_namespace, self.local_docs_namespace]:
                    results_ns = self.index.query(
                        vector=query_embedding,
                        namespace=namespace,
                        top_k=top_k // 2,
                        include_metadata=True
                    )
                    
                    for match in results_ns.matches:
                        priority_multiplier = 1.0 if namespace == self.user_docs_namespace else 0.8
                        results.append(ClauseMatch(
                            content=match.metadata.get("content", ""),
                            similarity_score=float(match.score) * priority_multiplier,
                            page_number=match.metadata.get("page_number"),
                            chunk_index=match.metadata.get("chunk_index", 0),
                            metadata={
                                **match.metadata,
                                "source_priority": "user_document" if namespace == self.user_docs_namespace else "local_document",
                                "source_type": "external" if namespace == self.user_docs_namespace else "local"
                            }
                        ))
            
            # Sort by similarity score (already accounts for priority)
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"Error searching Pinecone: {e}")
            return []
    
    async def clear_user_documents(self):
        """Clear all user-uploaded documents from Pinecone"""
        if not self.is_initialized:
            return
        
        try:
            self.index.delete(delete_all=True, namespace=self.user_docs_namespace)
            print("✅ Cleared all user documents from Pinecone")
        except Exception as e:
            print(f"Error clearing user documents: {e}")
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index"""
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "status": "initialized",
                "total_vectors": stats.total_vector_count,
                "namespaces": {
                    "local_docs": stats.namespaces.get(self.local_docs_namespace, {}).get('vector_count', 0),
                    "user_docs": stats.namespaces.get(self.user_docs_namespace, {}).get('vector_count', 0)
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
