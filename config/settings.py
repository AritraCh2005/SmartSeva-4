"""
Configuration settings for BSK Assistant
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Configuration
PAGE_CONFIG = {
    "page_title": "SmartSeva",
    "page_icon": "🏛️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Model Configuration
MODEL_CONFIG = {
    "embedding_model": "text-embedding-3-small",
    "chat_model": "gpt-4o-mini-2024-07-18",
    "temperature": 0.3,
    "streaming": True
}

# Vector Store Configuration
VECTOR_STORE_CONFIG = {
    "db_path": "data/chroma_db",
    "search_type": "mmr",
    "k": 4,
    "fetch_k":8 ,
    "lambda_mult": 0.8
}

# Memory Configuration
MEMORY_CONFIG = {
    "window_size": 6,
    "return_messages": True,
}

# File Paths
CHAT_HISTORY_FILE = "data/chat_history.json"
LOG_FILE = "logs/rag_chatbot.log"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Prompt Template
SYSTEM_PROMPT = """
You are a helpful assistant designed to provide clear, reliable, and up-to-date information about Indian government services.

Your responsibilities:
- Answer user queries in a simple and natural way.
- Provide accurate information about government schemes and services, including eligibility criteria, required documents, application procedures, and processing times.
- Only respond when you have verified and accurate information. If the information is not available or unclear, politely say so.
- Do not guess, assume, or generate information. Never make up responses.
- Do not answer questions unrelated to Indian government services.
"""

