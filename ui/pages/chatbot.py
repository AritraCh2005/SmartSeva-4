"""
Main chatbot page with enhanced UUID-based chat management
"""
import streamlit as st
from ui.components.sidebar import render_sidebar
from ui.components.chat_interface import render_chat_messages, render_chat_input
from core.memory_manager import memory_manager
from services.chat_service import chat_service
from utils.logger import get_logger

logger = get_logger(__name__)

def _initialize_session_state():
    """Initialize session state variables for enhanced chat system."""
    # Initialize current chat tracking
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
        logger.info("Initialized current_chat_id to None")
    
    # Initialize messages for current chat
    if "current_chat_messages" not in st.session_state:
        st.session_state.current_chat_messages = []
        logger.info("Initialized current_chat_messages")
    
    # Initialize new chat creation state
    if "pending_new_chat" not in st.session_state:
        st.session_state.pending_new_chat = True
        logger.info("Initialized pending_new_chat state")
    
    # Initialize chat management states
    if "show_delete_confirmation" not in st.session_state:
        st.session_state.show_delete_confirmation = None
    
    if "memory_loaded_for_chat" not in st.session_state:
        st.session_state.memory_loaded_for_chat = None
    
    if "is_new_chat" not in st.session_state:
        st.session_state.is_new_chat = False
    
    # Initialize chat history cache
    if "chat_history_cache" not in st.session_state:
        st.session_state.chat_history_cache = {}
    
    logger.info("Session state initialized for enhanced chat system.")

def _handle_chat_switching():
    """Handle switching between chats and memory management."""
    current_chat_id = st.session_state.get("current_chat_id")
    
    if current_chat_id:
        # Check if we need to load memory for this chat
        if st.session_state.get("memory_loaded_for_chat") != current_chat_id:
            # Get chat messages
            chat_messages = chat_service.get_chat_messages(current_chat_id)
            
            # Load messages into memory for this specific chat
            if memory_manager.load_chat_messages_from_history(current_chat_id, chat_messages):
                st.session_state.memory_loaded_for_chat = current_chat_id
                logger.info(f"Loaded memory for chat {current_chat_id}")
            else:
                logger.warning(f"Failed to load memory for chat {current_chat_id}")
            
            # Update session messages
            st.session_state.current_chat_messages = chat_messages

def show_chatbot_page():
    """Main chatbot page with enhanced memory management and error handling."""
    
    # Initialize session state
    _initialize_session_state()
    
    # Handle chat switching and memory management
    _handle_chat_switching()
    
    # Increment page load counter
    st.session_state.page_load_count = st.session_state.get("page_load_count", 0) + 1
    
    # Check RAG engine health periodically
    if st.session_state.get("page_load_count", 0) % 15 == 0:
        try:
            from core.rag_engine import rag_engine
            status = rag_engine.get_chain_status()
            if not status.get("chain_available") or not status.get("vector_store_available"):
                logger.warning(f"RAG system health check failed: {status}")
        except Exception as e:
            logger.error(f"Error checking RAG system health: {e}")
    
    # Render sidebar
    render_sidebar()
    
    # Render main chat interface
    render_chat_messages()
    render_chat_input()

