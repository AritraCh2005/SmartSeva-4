"""
Vector database operations page
"""
import streamlit as st
from core.vector_operations import vector_db_operations
from utils.logger import get_logger
from ui.styles.vectordb_page import apply_vector_operations_styling

import streamlit as st

import streamlit as st

def apply_vector_operations_styling():
    st.markdown("""
    <style>
    /* Main page title (h1) - Crimson red */
    .stApp h1 {
        color: #b30000 !important;
    }

    /* Subheadings (h2 - h4) - Deep blue */
    .stApp h2, .stApp h3, .stApp h4 {
        color: #003366 !important;
    }

    /* Paragraphs and normal text - dark gray */
    .stApp p, .stApp li, .stApp span, .stApp div {
        color: #222222 !important;
    }

    /* Metric label (like "Total Documents") - Purple */
    .stMetric label {
        color: #6a0dad !important;
    }

    /* Markdown horizontal rule line */
    hr {
        border-color: #888 !important;
    }
    </style>
    """, unsafe_allow_html=True)



logger = get_logger(__name__)

def show_vector_operations_page():
    """Main vector operations page."""
     # Apply custom CSS styling
    apply_vector_operations_styling()
    if st.button("← Back to Chat", type="secondary"):
        st.session_state.current_page = "chat"
        st.rerun()
    st.title("🗄️ Vector Database Operations")
    st.markdown("---")
    
    # Display current stats
    _display_vector_store_stats()
    
    st.markdown("---")
    
    # Create tabs for different operations
    tab1, tab2 = st.tabs(["📄 Add Documents", "📋 List Documents"])
    
    with tab1:
        _show_add_documents_tab()
    
    with tab2:
        _show_list_documents_tab()
    

def _display_vector_store_stats():
    """Display vector store statistics."""
    st.subheader("📊 Vector Store Statistics")
    
    with st.spinner("Loading vector store statistics..."):
        stats = vector_db_operations.get_document_stats()
    
    if stats["available"]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Total Documents", 
                value=stats["total_documents"],
                help="Number of unique PDF documents in the vector store"
            )
        
        with col2:
            # Status indicator
            if stats["total_documents"] > 0:
                st.success("✅ Vector store is operational")
            else:
                st.info("ℹ️ Vector store is ready")
    else:
        # Check if it was just recreated (empty but available)
        if stats.get("total_documents", 0) == 0 and stats.get("available", False):
            st.info("ℹ️ Vector store is empty but ready to receive documents")
        else:
            st.error("❌ Vector store is not available or accessible")
            if "error" in stats:
                st.error(f"Error: {stats['error']}")

def _show_add_documents_tab():
    """Show add documents tab."""
    st.subheader("📄 Add New Documents")
    st.markdown("Upload PDF documents to add them to the vector store for RAG processing.")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files to upload",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files to add to the vector store"
    )
    
    if uploaded_files:
        st.info(f"Selected {len(uploaded_files)} file(s) for upload")
        
        # Display selected files
        for file in uploaded_files:
            st.write(f"📄 {file.name} ({file.size / 1024:.1f} KB)")
        
        # Add documents button
        if st.button("🚀 Add Documents to Vector Store", type="primary", use_container_width=True):
            _process_document_uploads(uploaded_files)

def _process_document_uploads(uploaded_files):
    """Process document uploads with enhanced progress tracking."""
    
    # Create a container for the progress display
    progress_container = st.container()
    
    with progress_container:
        st.markdown("### 🔄 Processing Documents")
        
        # Overall progress
        overall_progress = st.progress(0)
        overall_status = st.empty()
        
        # Individual file processing status
        file_status_container = st.container()
    
    results = []
    
    with st.spinner("Initializing document processing..."):
        # Small delay for better UX
        import time
        time.sleep(0.5)
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Update overall status
        overall_status.text(f"Processing file {i+1} of {len(uploaded_files)}: {uploaded_file.name}")
        overall_progress.progress(i / len(uploaded_files))
        
        # Show individual file processing with spinner
        with file_status_container:
            with st.spinner(f"📄 Processing {uploaded_file.name}..."):
                # Process the file
                result = vector_db_operations.add_pdf_to_vectorstore(uploaded_file, uploaded_file.name)
                results.append({
                    "filename": uploaded_file.name,
                    "result": result
                })
                
                # Show immediate feedback for this file
                if result["success"]:
                    st.success(f"✅ {uploaded_file.name}: Successfully processed")
                else:
                    st.error(f"❌ {uploaded_file.name}: {result['message']}")
    
    # Complete the progress
    overall_progress.progress(1.0)
    overall_status.text("🎉 All files processed!")
    
    # Display final results summary
    with progress_container:
        st.markdown("---")
        st.subheader("📊 Final Results")
        
        success_count = sum(1 for item in results if item["result"]["success"])
        
        if success_count == len(uploaded_files):
            st.success(f"🎉 Successfully processed all {len(uploaded_files)} files!")
        elif success_count > 0:
            st.info(f"✅ Successfully processed {success_count} out of {len(uploaded_files)} files.")
        else:
            st.error(f"❌ Failed to process any files. Please check the error messages above.")
        
        if success_count > 0:
            st.balloons()

def _show_list_documents_tab():
    """Show list documents tab."""
    st.subheader("📋 Document List")
    st.markdown("View all documents currently stored in the vector database.")

    # Display deletion status message if available
    if "deletion_status" in st.session_state:
        status = st.session_state.deletion_status
        if status["success"]:
            st.success(status["message"])
        else:
            st.error(status["message"])
        del st.session_state.deletion_status
    
    # Add a search bar
    search_query = st.text_input("Search documents by name:", placeholder="Enter a document name to search...")

    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh List"):
            st.rerun()
    
    # Load documents
    with st.spinner("Loading documents..."):
        documents = vector_db_operations.list_documents()
    
    if not documents:
        st.info("📭 No documents found in the vector store.")
        st.markdown("💡 **Tip:** Use the 'Add Documents' tab to upload PDF files.")
        return

    # Filter documents based on search query
    if search_query:
        search_query_lower = search_query.lower()
        filtered_docs = []
        for doc in documents:
            # Search both the original filename and display name (without .pdf)
            display_name = doc.replace('.pdf', '') if doc.endswith('.pdf') else doc
            if search_query_lower in doc.lower() or search_query_lower in display_name.lower():
                filtered_docs.append(doc)
        documents = filtered_docs

    # Display document count
    if documents:
        st.success(f"Found {len(documents)} document(s) matching your search.")
    else:
        st.warning("No documents found matching your search criteria.")
    
    # Display documents in a nice format
    st.markdown("### 📚 Available Documents")
    
    for i, doc in enumerate(documents, 1):
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            # Remove .pdf extension for display
            display_name = doc.replace('.pdf', '') if doc.endswith('.pdf') else doc
            
            with col1:
                st.markdown(f"**{i}.** 📄 `{display_name}`")
            
            with col2:
                # Add a quick delete button
                if st.button("🗑️", key=f"quick_delete_{i}", help=f"Delete {display_name}"):
                    st.session_state[f"confirm_delete_{doc}"] = True
                    st.rerun()
            
            # Show confirmation dialog if delete was clicked
            if st.session_state.get(f"confirm_delete_{doc}", False):
                st.warning(f"⚠️ Confirm deletion of '{display_name}'?")
                col_yes, col_no = st.columns(2)
                
                with col_yes:
                    if st.button("✅ Yes", key=f"yes_{i}"):
                        result = vector_db_operations.delete_document_by_filename(doc)
                        if result["success"]:
                            st.session_state.deletion_status = {"success": True, "message": f"✅ Successfully deleted {display_name}."}
                        else:
                            st.session_state.deletion_status = {"success": False, "message": f"❌ Failed to delete {display_name}: {result.get('message', 'Unknown error')}"}
                        
                        del st.session_state[f"confirm_delete_{doc}"]
                        st.rerun()
                
                with col_no:
                    if st.button("❌ No", key=f"no_{i}"):
                        del st.session_state[f"confirm_delete_{doc}"]
                        st.rerun()
            
            st.markdown("---")

