import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_V1_PREFIX = "/api/v1"
    PROJECT_NAME = "HackRx 6.0 - Intelligent Query-Retrieval System"
    VERSION = "1.0.0"
    
    # LLM Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = "gemini-1.5-flash"
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION = 384
    
    # Document Processing
    MAX_CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_TOKENS_PER_REQUEST = 30000
    
    # FAISS Configuration
    FAISS_INDEX_PATH = "data/faiss_index"
    
    # Cache Configuration
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # 1 hour
    
    # Performance
    MAX_CONCURRENT_REQUESTS = 10
    REQUEST_TIMEOUT = 30

settings = Settings()
