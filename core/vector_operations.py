"""
Vector database operations for managing documents in ChromaDB
"""
import os
import tempfile
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from core.vector_store import vector_store_manager
from utils.logger import get_logger
import re
logger = get_logger(__name__)

class VectorDBOperations:
    """Handles vector database CRUD operations."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=300,
            length_function=len,
            add_start_index=True
        )
        logger.info("VectorDBOperations initialized.")

    def list_documents(self) -> List[str]:
        """
        List all unique document filenames in the vector store.
        
        Returns:
            List of filenames
        """
        try:
            if not vector_store_manager.is_available():
                logger.warning("Vector store not available for listing documents. Attempting to reinitialize...")
                if not vector_store_manager.reinitialize_vector_store():
                    logger.error("Could not reinitialize vector store.")
                    return []
            
            collection = vector_store_manager.vector_store._collection
            
            # Get all documents with metadata
            results = collection.get(include=["metadatas"])
            
            # Extract unique filenames from metadata
            filenames = set()
            for metadata in results["metadatas"]:
                if metadata and "filename" in metadata:
                    filenames.add(metadata["filename"])
            
            return sorted(list(filenames))
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
        
    @staticmethod
    def clean_pdf_text(text: str) -> str:
        """
        Cleans up whitespace and line breaks from text extracted from a PDF.
        
        - Replaces multiple newlines and spaces with a single space to join broken lines.
        - Consolidates multiple spaces into a single space.
        - Removes leading/trailing whitespace.
        """
        # Replace newlines that are not preceded by a punctuation mark, effectively joining sentences.
        text = re.sub(r'(?<![.\-:])\s*\n\s*', ' ', text)
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def add_pdf_to_vectorstore(self, uploaded_file, filename: str) -> Dict:
        """
        Add a PDF file to the vector store.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            filename: Name of the file
            
        Returns:
            Dict with operation status and details
        """
        try:
            # Check if vector store is available, try to reinitialize if not
            if not vector_store_manager.is_available():
                logger.warning("Vector store not available. Attempting to reinitialize...")
                if not vector_store_manager.reinitialize_vector_store():
                    return {
                        "success": False,
                        "message": "Vector store is not available and could not be reinitialized. Please check the database connection.",
                        "chunks_added": 0
                    }
            
            # Check if document already exists
            existing_docs = self.list_documents()
            if filename in existing_docs:
                return {
                    "success": False,
                    "message": f"Document '{filename}' already exists in the vector store. Please delete it first or use a different name.",
                    "chunks_added": 0
                }
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name
            
            try:
                # Load PDF using PyMuPDFLoader
                from langchain_community.document_loaders import PyMuPDFLoader
                loader = PyMuPDFLoader(temp_file_path)
                docs = loader.load()

                # ... (error checking for empty docs) ...

                # Merge all pages into a single text string
                full_text = "\n".join([doc.page_content for doc in docs])

                # CLEAN THE EXTRACTED TEXT
                cleaned_text = self.clean_pdf_text(full_text)
                
                # ... (error checking for empty cleaned_text) ...

                # Create a single document for splitting, now using the cleaned text
                merged_doc = Document(
                    page_content=cleaned_text, # <--- USE THE CLEANED TEXT HERE
                    metadata={"source": filename, "filename": filename}
                )

                # Split into chunks
                chunks = self.text_splitter.split_documents([merged_doc])
                
                if not chunks:
                    return {
                        "success": False,
                        "message": "Failed to create chunks from the document.",
                        "chunks_added": 0
                    }
                
                # Create IDs for each chunk
                chunk_ids = [f"{filename}_{i+1}" for i in range(len(chunks))]
                
                # Update metadata to ensure filename is stored
                for chunk in chunks:
                    chunk.metadata["filename"] = filename
                    chunk.metadata["source"] = filename
                
                # Add chunks to vector store
                vector_store_manager.vector_store.add_documents(chunks, ids=chunk_ids)
                
                logger.info(f"Successfully added {len(chunks)} chunks for {filename}")
                
                return {
                    "success": True,
                    "message": f"Successfully added '{filename}' to vector store.",
                    "chunks_added": len(chunks)
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error adding PDF to vector store: {e}")
            return {
                "success": False,
                "message": f"Error processing PDF: {str(e)}",
                "chunks_added": 0
        }

    
    
    def delete_document_by_filename(self, filename: str) -> Dict:
        """
        Delete all chunks of a document from the vector store using its filename.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            Dict with operation status and details
        """
        try:
            if not vector_store_manager.is_available():
                return {
                    "success": False,
                    "message": "Vector store is not available.",
                    "chunks_deleted": 0
                }
            
            collection = vector_store_manager.vector_store._collection
            
            # Query collection to find all chunks with matching filename in metadata
            results = collection.get(where={"filename": filename})
            
            if results["ids"]:
                # Delete the chunks
                vector_store_manager.vector_store.delete(ids=results["ids"])
                
                chunks_count = len(results["ids"])
                logger.info(f"Deleted {chunks_count} chunks for filename: {filename}")
                
                return {
                    "success": True,
                    "message": f"Successfully deleted '{filename}' and all its {chunks_count} chunks.",
                    "chunks_deleted": chunks_count
                }
            else:
                return {
                    "success": False,
                    "message": f"No document found with filename: '{filename}'",
                    "chunks_deleted": 0
                }
                
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return {
                "success": False,
                "message": f"Error deleting document: {str(e)}",
                "chunks_deleted": 0
            }
    
    
    
    def get_document_stats(self) -> Dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dict with vector store statistics
        """
        try:
            if not vector_store_manager.is_available():
                logger.warning("Vector store not available. Attempting to reinitialize...")
                if vector_store_manager.reinitialize_vector_store():
                    logger.info("Vector store reinitialized successfully.")
                else:
                    return {
                        "total_documents": 0,
                        "total_chunks": 0,
                        "available": False,
                        "error": "Vector store unavailable and could not be reinitialized"
                    }
            
            collection = vector_store_manager.vector_store._collection
            results = collection.get(include=["metadatas"])
            
            # Count unique documents
            filenames = set()
            for metadata in results["metadatas"]:
                if metadata and "filename" in metadata:
                    filenames.add(metadata["filename"])
            
            return {
                "total_documents": len(filenames),
                "total_chunks": len(results["metadatas"]),
                "available": True
            }
            
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "available": False,
                "error": str(e)
            }
    

# Global vector operations instance
vector_db_operations = VectorDBOperations()