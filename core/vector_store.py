"""
Vector store management
"""
import os
from langchain_chroma import Chroma
from models.embeddings import get_embeddings
from config.settings import VECTOR_STORE_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class VectorStoreManager:
    """Manages vector store operations."""
    
    def __init__(self):
        self.embeddings = get_embeddings()
        self.vector_store = None
        self.retriever = None
        self._load_vector_store()
    
    def _load_vector_store(self):
        """Load vector store from disk or create new one if not exists."""
        try:
            db_path = VECTOR_STORE_CONFIG["db_path"]
            if os.path.exists(db_path):
                self.vector_store = Chroma(
                    persist_directory=db_path,
                    embedding_function=self.embeddings
                )
                logger.info("Vector store loaded successfully.")
            else:
                logger.warning("Vector store directory not found. Creating new vector store...")
                self._create_new_vector_store()
            self._create_retriever()
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
    
    def _create_new_vector_store(self):
        """Create a new empty vector store."""
        try:
            db_path = VECTOR_STORE_CONFIG["db_path"]
            # Ensure the parent directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Create a new empty Chroma vector store
            self.vector_store = Chroma(
                persist_directory=db_path,
                embedding_function=self.embeddings
            )
            logger.info("New vector store created successfully.")
        except Exception as e:
            logger.error(f"Failed to create new vector store: {e}")
            raise

    def _create_retriever(self):
        """Create retriever from vector store."""
        if not self.vector_store:
            logger.error("Vector store not available for retriever creation.")
            return
        
        try:
            self.retriever = self.vector_store.as_retriever(
                search_type=VECTOR_STORE_CONFIG["search_type"],
                search_kwargs={
                    "k": VECTOR_STORE_CONFIG["k"],
                    "fetch_k": VECTOR_STORE_CONFIG["fetch_k"],
                    "lambda_mult": VECTOR_STORE_CONFIG["lambda_mult"]
                }
            )
            logger.info("Retriever created successfully.")
        except Exception as e:
            logger.error(f"Failed to create retriever: {e}")
    
    def get_retriever(self):
        """Get retriever instance."""
        return self.retriever
    
    def reinitialize_vector_store(self):
        """Reinitialize the vector store - useful when it becomes unavailable."""
        try:
            logger.info("Attempting to reinitialize vector store...")
            self._load_vector_store()
            return self.is_available()
        except Exception as e:
            logger.error(f"Failed to reinitialize vector store: {e}")
            return False

    def is_available(self):
        """Check if vector store is available."""
        return self.vector_store is not None

# Global vector store instance
vector_store_manager = VectorStoreManager()