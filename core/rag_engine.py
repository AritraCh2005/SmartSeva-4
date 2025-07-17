"""
Enhanced RAG (Retrieval-Augmented Generation) engine with improved robustness
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from models.llm_models import get_chat_model
from core.vector_store import vector_store_manager
from core.memory_manager import memory_manager
from config.settings import SYSTEM_PROMPT, VECTOR_STORE_CONFIG
from utils.logger import get_logger
import time
from typing import List, Dict, Optional, Any

logger = get_logger(__name__)

class RAGEngine:
    """Enhanced RAG engine with improved error handling, context management, and memory integration."""
    
    def __init__(self):
        self.llm_model = get_chat_model()
        self.prompt_template = self._create_enhanced_prompt_template()
        self.chain = None
        self.retrieval_config = VECTOR_STORE_CONFIG
        self._initialize_chain()
    
    def _create_enhanced_prompt_template(self):
        """Create enhanced prompt template with better context handling."""
        return ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + """

            Important Guidelines:
            - Use the provided context from documents to answer questions accurately
            - If the context doesn't contain relevant information, clearly state that the information is not available in the knowledge base
            - Maintain conversation continuity by referencing previous messages when relevant
            - Always prioritize accuracy over completeness
            - For follow-up questions, consider the full conversation history to provide contextually appropriate responses"""),
            ("human", "use this Context from official given documents to answer queries:\n{context}"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "Current question: {input}")
        ])
    
    def _get_enhanced_context(self, documents: List, query: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """Improved context retrieval: sorts, filters, and limits documents by relevance."""
        try:
            if not documents:
                logger.info(f"No documents retrieved for query: {query}")
                return {
                    "context": "No specific service information found for this query. Please try rephrasing your question or contact a government helpline number.",
                    "sources": [],
                    "relevance_score": 0.0
                }

            logger.info(f"Processing {len(documents)} retrieved documents for chat {chat_id}")

            # Sort documents by relevance score (descending)
            sorted_docs = sorted(documents, key=lambda d: getattr(d, 'relevance_score', 0.5), reverse=True)

            # Filter documents above a relevance threshold
            relevance_threshold = 0.3
            filtered_docs = [doc for doc in sorted_docs if getattr(doc, 'relevance_score', 0.5) >= relevance_threshold]

            # Limit the number of documents to avoid prompt overflow
            max_docs = 5
            selected_docs = filtered_docs[:max_docs]

            context_parts = []
            sources = []
            total_relevance = 0

            for i, doc in enumerate(selected_docs, 1):
                metadata = getattr(doc, 'metadata', {})
                source = metadata.get('filename', f'Document {i}')
                page = metadata.get('page', 'Unknown')
                formatted_content = f"Source {i} (from {source}):\n{doc.page_content}"
                context_parts.append(formatted_content)
                sources.append({"source": source, "page": page})
                score = getattr(doc, 'relevance_score', 0.5)
                total_relevance += score

            avg_relevance = total_relevance / len(selected_docs) if selected_docs else 0

            return {
                "context": "\n\n".join(context_parts) if context_parts else "No highly relevant BSK service information found.",
                "sources": sources,
                "relevance_score": avg_relevance
            }

        except Exception as e:
            logger.error(f"Error in enhanced context retrieval: {e}")
            return {
                "context": "Error retrieving context. Please try again.",
                "sources": [],
                "relevance_score": 0.0
            }
    
    def _initialize_chain(self):
        """Initialize the RAG chain with robust error handling."""
        try:
            self.chain = self._create_enhanced_rag_chain()
            if self.chain:
                logger.info("Enhanced RAG chain initialized successfully")
            else:
                logger.warning("Failed to initialize RAG chain")
        except Exception as e:
            logger.error(f"Error during chain initialization: {e}")
            self.chain = None
    
    def _create_enhanced_rag_chain(self):
        """Create enhanced RAG chain with better error handling and context management."""
        try:
            # Check vector store availability
            if not vector_store_manager.is_available():
                logger.warning("Vector store unavailable. Attempting to reinitialize...")
                if not vector_store_manager.reinitialize_vector_store():
                    logger.error("Vector store still unavailable after reinitialization.")
                    return None
            
            # Get retriever with enhanced configuration
            retriever = vector_store_manager.get_retriever()
            if not retriever:
                logger.error("Failed to create retriever.")
                return None
            
            # Enhanced chain with better context handling
            def get_context_and_history(x):
                """Enhanced context and history retrieval."""
                query = x["input"]
                chat_id = x.get("chat_id")
                
                # Retrieve documents
                try:
                    documents = retriever.invoke(query)
                    context_info = self._get_enhanced_context(documents, query, chat_id)
                    
                    # Get memory for current chat
                    if chat_id:
                        memory_manager.switch_to_chat(chat_id)
                    
                    memory_vars = memory_manager.load_memory_variables()
                    
                    return {
                        "context": context_info["context"],
                        "history": memory_vars.get("history", []),
                        "input": query,
                        "sources": context_info["sources"],
                        "relevance_score": context_info["relevance_score"]
                    }
                    
                except Exception as e:
                    logger.error(f"Error in context and history retrieval: {e}")
                    return {
                        "context": "Error retrieving information. Please try again.",
                        "history": [],
                        "input": query,
                        "sources": [],
                        "relevance_score": 0.0
                    }
            
            # Create the enhanced chain
            chain = (
                RunnablePassthrough()
                | get_context_and_history
                | self.prompt_template
                | self.llm_model
                | StrOutputParser()
            )
            
            logger.info("Enhanced RAG chain created successfully.")
            return chain
            
        except Exception as e:
            logger.error(f"Failed to create enhanced RAG chain: {e}")
            return None
    
    def _validate_query(self, query: str) -> Dict[str, Any]:
        """Validate and preprocess query."""
        if not query or not query.strip():
            return {"valid": False, "reason": "Empty query"}
        
        if len(query.strip()) < 1:
            return {"valid": False, "reason": "Query too short"}
        
        if len(query) > 2000:
            return {"valid": False, "reason": "Query too long"}
        
        return {"valid": True, "processed_query": query.strip()}
    
    def _ensure_chain_availability(self) -> bool:
        """Ensure the RAG chain is available and functional."""
        if not self.chain:
            logger.info("Chain not available. Attempting to recreate...")
            self._initialize_chain()
        
        if not self.chain:
            logger.error("Failed to create or recreate chain")
            return False
        
        return True
    
    def process_query(self, query: str, chat_id: Optional[str] = None) -> Any:
        """Enhanced query processing with improved error handling and robustness."""
        start_time = time.time()
        logger.info(f"Processing query for chat {chat_id}: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        # Validate query
        validation_result = self._validate_query(query)
        if not validation_result["valid"]:
            error_msg = f"Invalid query: {validation_result['reason']}"
            logger.warning(error_msg)
            yield error_msg
            return
        
        processed_query = validation_result["processed_query"]
        
        # Ensure memory context is set
        if chat_id:
            if not memory_manager.switch_to_chat(chat_id):
                logger.warning(f"Failed to switch to chat {chat_id}, continuing with current context")
        
        # Ensure chain availability
        if not self._ensure_chain_availability():
            error_msg = "RAG system is currently unavailable. Please ensure documents are loaded and try again."
            logger.error(error_msg)
            yield error_msg
            return
        
        # Process query with enhanced error handling
        try:
            full_response = ""
            chunk_count = 0
            
            # Add chat_id to the input for enhanced context retrieval
            chain_input = {"input": processed_query, "chat_id": chat_id}
            for chunk in self.chain.stream(chain_input):
                if chunk:  # Ensure chunk is not empty
                    full_response += chunk
                    chunk_count += 1
                    yield chunk
                    
                    # Safety check for streaming timeout
                    if time.time() - start_time > 60:  # 60 second timeout
                        logger.warning("Query processing timeout reached")
                        break
            
            processing_time = time.time() - start_time
            logger.info(f"Query processed successfully in {processing_time:.2f}s with {chunk_count} chunks")
            
            # Enhanced context saving with better error handling
            if full_response.strip():
                save_success = memory_manager.save_context(
                    {"input": processed_query},
                    {"output": full_response}
                )
                
                if save_success:
                    logger.info(f"Context saved to chat {chat_id} memory")
                else:
                    logger.warning(f"Failed to save context to chat {chat_id} memory")
            else:
                logger.warning("Empty response generated, not saving to memory")
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error processing query after {processing_time:.2f}s: {str(e)}"
            logger.error(error_msg)
            
            # Try to provide a helpful error message
            if "rate limit" in str(e).lower():
                yield "Rate limit exceeded. Please wait a moment and try again."
            elif "timeout" in str(e).lower():
                yield "Request timed out. Please try with a shorter query."
            elif "context" in str(e).lower():
                yield "Context processing error. Please ensure documents are properly loaded."
            else:
                yield "An error occurred while processing your query. Please try again."
    
    def get_chain_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the RAG chain."""
        return {
            "chain_available": self.chain is not None,
            "vector_store_available": vector_store_manager.is_available(),
            "memory_manager_active": memory_manager.current_chat_id is not None,
            "active_chats": len(memory_manager.get_all_active_chats()),
            "retrieval_config": self.retrieval_config
        }
    
    def reinitialize(self) -> bool:
        """Reinitialize the entire RAG system."""
        try:
            logger.info("Reinitializing RAG engine...")
            
            # Reinitialize vector store
            if not vector_store_manager.reinitialize_vector_store():
                logger.error("Failed to reinitialize vector store")
                return False
            
            # Reinitialize chain
            self._initialize_chain()
            
            success = self.chain is not None
            logger.info(f"RAG engine reinitialization {'successful' if success else 'failed'}")
            return success
            
        except Exception as e:
            logger.error(f"Error during RAG engine reinitialization: {e}")
            return False

# Global enhanced RAG engine instance
rag_engine = RAGEngine()