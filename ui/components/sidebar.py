"""
Enhanced Sidebar components for UUID-based chat interface
"""
import streamlit as st
from services.chat_service import chat_service
from core.memory_manager import memory_manager
from utils.logger import get_logger
from ui.styles.sidebar import apply_sidebar_styles

logger = get_logger(__name__)

def render_sidebar():
    """Render the sidebar with enhanced chat management and navigation."""
    # Apply sidebar styles
    apply_sidebar_styles()
    
    with st.sidebar:
        # BSK Assistant Header
        st.markdown("""
        <div class="sidebar-header">
            🏛️ SmartSeva Assistant
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation Section
        _render_navigation_section()
        
        st.markdown("---")
        
        # Chat Management Section (only show in chat mode)
        if st.session_state.get('current_page', 'chat') == 'chat':
            _render_chat_management_section()
        
        st.markdown("---")
        
        # About section
        _render_about_section()

def _render_navigation_section():
    """Render navigation section."""
    st.subheader("🧭 Navigation")
    
    current_page = st.session_state.get('current_page', 'chat')
    
    # Chat Page Button
    # if current_page == 'chat':
    #     st.button("💬 Chat Assistant", use_container_width=True, disabled=True)
    # else:
    #     if st.button("💬 Chat Assistant", use_container_width=True):
    #         st.session_state.current_page = 'chat'
    #         st.rerun()
    
    # Vector Operations Button
    if current_page == 'vector_ops':
        st.button("🗄️ Vector Database", use_container_width=True, disabled=True)
    else:
        if st.button("🗄️ Vector Database", use_container_width=True):
            st.session_state.current_page = 'vector_ops'
            st.rerun()

def _render_chat_management_section():
    """Render clean chat management section."""
    st.subheader("💬 Chat History")
    
    # New Chat button
    if st.button("✨ New Chat", use_container_width=True, type="primary"):
        _handle_new_chat()
    
    st.markdown("---")
    
    # Display chat history
    _render_chat_history()
    
    # Delete confirmation dialog
    _render_delete_confirmation()

def _handle_new_chat():
    """Handle new chat creation with enhanced memory management."""
    try:
        # Clear current chat memory if exists
        current_chat_id = st.session_state.get('current_chat_id')
        if current_chat_id:
            memory_manager.clear_current_chat_memory()
            logger.info(f"Cleared memory for previous chat {current_chat_id}")
        
        # Reset to pending state
        st.session_state.pending_new_chat = True
        st.session_state.current_chat_id = None
        st.session_state.current_chat_messages = []
        st.session_state.show_delete_confirmation = None
        st.session_state.memory_loaded_for_chat = None
        st.session_state.is_new_chat = False
        
        logger.info("Initiated new chat creation")
        st.rerun()
        
    except Exception as e:
        logger.error(f"Error handling new chat: {e}")
        st.error("Failed to create new chat. Please try again.")

def _render_chat_history():
    """Render clean chat history list."""
    try:
        all_chats = chat_service.get_all_chats()
        
        if all_chats:
            # Limit display to recent chats for performance
            display_limit = 20
            chat_items = list(all_chats.items())[:display_limit]
            
            for chat_id, chat_info in chat_items:
                chat_title = chat_info.get("title", "Untitled Chat")
                
                # Truncate title if too long
                display_title = chat_title if len(chat_title) <= 30 else chat_title[:27] + "..."
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Check if this is the current chat
                    is_current = chat_id == st.session_state.get('current_chat_id')
                    
                    if is_current:
                        # Current chat - show with different style
                        st.button(
                            f"🔸 {display_title}",
                            use_container_width=True,
                            disabled=True
                        )
                    else:
                        # Other chats - clickable
                        if st.button(
                            f"💬 {display_title}",
                            key=f"chat_{chat_id}",
                            use_container_width=True
                        ):
                            _load_chat(chat_id, chat_info)
                
                with col2:
                    # Only show delete button for non-current chats
                    if not is_current:
                        if st.button(
                            "🗑️",
                            key=f"delete_{chat_id}",
                            help="Delete chat"
                        ):
                            st.session_state.show_delete_confirmation = chat_id
                            st.rerun()
                            
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; color: #666;">
                <small>No chat history yet.<br>Create your first chat!</small>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        logger.error(f"Error rendering chat history: {e}")
        st.error("Failed to load chat history")

def _load_chat(chat_id, chat_info):
    """Load a specific chat with enhanced memory management."""
    try:
        # Clear current memory before switching
        current_chat_id = st.session_state.get('current_chat_id')
        if current_chat_id and current_chat_id != chat_id:
            memory_manager.clear_current_chat_memory()
            logger.info(f"Cleared memory for previous chat {current_chat_id}")
        
        # Set new chat as current
        st.session_state.current_chat_id = chat_id
        st.session_state.current_chat_messages = chat_info.get("messages", [])
        st.session_state.is_new_chat = False
        st.session_state.pending_new_chat = False
        st.session_state.show_delete_confirmation = None
        
        # Load chat messages into memory
        chat_messages = chat_service.get_chat_messages(chat_id)
        if memory_manager.load_chat_messages_from_history(chat_id, chat_messages):
            st.session_state.memory_loaded_for_chat = chat_id
            logger.info(f"Successfully loaded chat {chat_id[:8]}... with {len(chat_messages)} messages")
        else:
            logger.warning(f"Failed to load memory for chat {chat_id}")
            st.session_state.memory_loaded_for_chat = None
        
        st.rerun()
        
    except Exception as e:
        logger.error(f"Error loading chat {chat_id}: {e}")
        st.error("Failed to load chat. Please try again.")

def _render_delete_confirmation():
    """Render clean delete confirmation dialog."""
    chat_to_delete = st.session_state.get('show_delete_confirmation')
    
    if chat_to_delete:
        # Get chat info for confirmation
        chat_summary = chat_service.get_chat_summary(chat_to_delete)
        chat_title = chat_summary.get('title', 'Untitled Chat') if chat_summary else 'Unknown Chat'
        
        st.markdown("---")
        st.markdown(f"""
        <div style="background: #ff4b4b; padding: 1rem; border-radius: 8px; 
                    border-left: 4px solid #d63031; margin: 1rem 0; color: white;">
            <strong>⚠️ Delete Chat</strong><br>
            Are you sure you want to delete "<strong>{chat_title}</strong>"?<br>
            <small>This action cannot be undone!</small>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Delete", key="confirm_delete", type="secondary"):
                _handle_chat_deletion(chat_to_delete)
        
        with col2:
            if st.button("❌ Cancel", key="cancel_delete"):
                st.session_state.show_delete_confirmation = None
                st.rerun()

def _handle_chat_deletion(chat_id):
    """Handle chat deletion with proper cleanup."""
    try:
        # Delete from memory first
        memory_manager.delete_chat_memory(chat_id)
        
        # Delete from persistent storage
        if chat_service.delete_chat(chat_id):
            # If we're deleting the current chat, reset to pending state
            if chat_id == st.session_state.get('current_chat_id'):
                st.session_state.current_chat_id = None
                st.session_state.current_chat_messages = []
                st.session_state.pending_new_chat = True
                st.session_state.memory_loaded_for_chat = None
                st.session_state.is_new_chat = False
            
            st.session_state.show_delete_confirmation = None
            st.success(f"Chat deleted successfully!")
            logger.info(f"Successfully deleted chat {chat_id}")
            st.rerun()
        else:
            st.error("Failed to delete chat from storage")
            
    except Exception as e:
        logger.error(f"Error deleting chat {chat_id}: {e}")
        st.error("Failed to delete chat. Please try again.")

def _render_about_section():
    """Render clean about section."""
    with st.expander("📋 About This Project", expanded=False):
        st.markdown("""
        **SmartSeva Assistant** is an AI-powered virtual assistant designed specifically for 
        for officials providing government services to the technologically underprivileged citizens. It provides intelligent 
        support for government services, queries, and administrative assistance. 
        
        **Features:**
        - 💬 **Chat Assistant**: Interactive RAG-powered chatbot with conversation memory
        - 🆔 **Unique Chat Sessions**: Each conversation has its own isolated memory
        - 🔄 **Context Awareness**: Follow-up questions and conversation continuity
        - 🗄️ **Vector Database**: Manage documents for knowledge base
        - 📄 **Document Processing**: Upload and process PDF documents
        - 🔍 **Smart Search**: Find relevant information quickly
        
        The system uses advanced RAG (Retrieval-Augmented Generation) technology 
        to deliver accurate, contextual responses based on official documentation taken from the official department websites.
        """)




