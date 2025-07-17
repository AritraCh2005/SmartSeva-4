"""
Enhanced Chat service for managing chat operations with UUID-based chat IDs
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from config.settings import CHAT_HISTORY_FILE
from utils.logger import get_logger

logger = get_logger(__name__)

class ChatService:
    """Service for managing chat operations with UUID-based IDs."""
    
    def __init__(self):
        self.chat_file = CHAT_HISTORY_FILE
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists."""
        data_dir = os.path.dirname(self.chat_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def load_chat_history(self) -> Dict[str, Any]:
        """Load chat history from JSON file."""
        try:
            if os.path.exists(self.chat_file):
                with open(self.chat_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"Error loading chat history: {e}")
            return {}
    
    def save_chat_history(self, chat_data: Dict[str, Any]) -> bool:
        """Save chat history to JSON file."""
        try:
            with open(self.chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            return False
    
    def create_new_chat(self, custom_id: Optional[str] = None) -> str:
        """Create a new chat session with UUID."""
        try:
            chat_data = self.load_chat_history()
            
            # Generate UUID-based chat ID
            new_chat_id = custom_id if custom_id else str(uuid.uuid4())
            
            # Ensure uniqueness
            while new_chat_id in chat_data:
                new_chat_id = str(uuid.uuid4())
            
            chat_data[new_chat_id] = {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "title": "New Chat",
                "messages": [],
                "fresh_context": True,
                "message_count": 0
            }
            
            self.save_chat_history(chat_data)
            logger.info(f"Created new chat with UUID: {new_chat_id}")
            return new_chat_id
            
        except Exception as e:
            logger.error(f"Error creating new chat: {e}")
            return str(uuid.uuid4())  # Return a UUID even if save fails
    
    def get_chat_by_id(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chat by its ID."""
        try:
            chat_data = self.load_chat_history()
            return chat_data.get(chat_id)
        except Exception as e:
            logger.error(f"Error getting chat {chat_id}: {e}")
            return None
    
    def update_chat_title(self, chat_id: str, first_message: str) -> bool:
        """Update chat title based on first user message."""
        try:
            chat_data = self.load_chat_history()
            if chat_id in chat_data:
                # Create a more meaningful title from first message
                title = first_message.strip()
                if len(title) > 30:
                    title = title[:27] + "..."
                
                chat_data[chat_id]["title"] = title
                chat_data[chat_id]["updated_at"] = datetime.now().isoformat()
                
                self.save_chat_history(chat_data)
                logger.info(f"Updated chat {chat_id} title: {title}")
                return True
            else:
                logger.warning(f"Chat {chat_id} not found for title update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating chat title for {chat_id}: {e}")
            return False
    
    def save_message_to_chat(self, chat_id: str, role: str, content: str) -> bool:
        """Save a message to the specified chat."""
        try:
            chat_data = self.load_chat_history()
            if chat_id in chat_data:
                # Use sequential message number instead of UUID for simplicity
                next_seq = len(chat_data[chat_id]["messages"]) + 1
                message = {
                    "seq": next_seq,  # Sequential number instead of UUID
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                
                chat_data[chat_id]["messages"].append(message)
                chat_data[chat_id]["message_count"] = len(chat_data[chat_id]["messages"])
                chat_data[chat_id]["updated_at"] = datetime.now().isoformat()
                
                self.save_chat_history(chat_data)
                logger.info(f"Saved message to chat {chat_id}")
                return True
            else:
                logger.warning(f"Chat {chat_id} not found for message save")
                return False
                
        except Exception as e:
            logger.error(f"Error saving message to chat {chat_id}: {e}")
            return False
    
    def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages from a specific chat."""
        try:
            chat_data = self.load_chat_history()
            if chat_id in chat_data:
                return chat_data[chat_id].get("messages", [])
            else:
                logger.warning(f"Chat {chat_id} not found")
                return []
                
        except Exception as e:
            logger.error(f"Error getting messages for chat {chat_id}: {e}")
            return []
    
    def delete_chat(self, chat_id: str) -> bool:
        """Delete a specific chat from history."""
        try:
            chat_data = self.load_chat_history()
            if chat_id in chat_data:
                del chat_data[chat_id]
                self.save_chat_history(chat_data)
                logger.info(f"Deleted chat {chat_id}")
                return True
            else:
                logger.warning(f"Chat {chat_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {e}")
            return False
    
    def get_all_chats(self) -> Dict[str, Any]:
        """Get all chats, sorted by last updated."""
        try:
            chat_data = self.load_chat_history()
            
            # Sort by updated_at timestamp (most recent first)
            sorted_chats = dict(sorted(
                chat_data.items(),
                key=lambda x: x[1].get("updated_at", x[1].get("created_at", "")),
                reverse=True
            ))
            
            return sorted_chats
            
        except Exception as e:
            logger.error(f"Error getting all chats: {e}")
            return {}
    
    def get_chat_summary(self, chat_id: str) -> Dict[str, Any]:
        """Get summary information about a chat."""
        try:
            chat_data = self.load_chat_history()
            if chat_id in chat_data:
                chat = chat_data[chat_id]
                return {
                    "id": chat_id,
                    "title": chat.get("title", "Untitled Chat"),
                    "created_at": chat.get("created_at"),
                    "updated_at": chat.get("updated_at"),
                    "message_count": chat.get("message_count", len(chat.get("messages", []))),
                    "has_messages": len(chat.get("messages", [])) > 0
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting chat summary for {chat_id}: {e}")
            return {}
    
    def cleanup_empty_chats(self) -> int:
        """Remove chats that have no messages."""
        try:
            chat_data = self.load_chat_history()
            empty_chats = []
            
            for chat_id, chat_info in chat_data.items():
                if len(chat_info.get("messages", [])) == 0:
                    empty_chats.append(chat_id)
            
            for chat_id in empty_chats:
                del chat_data[chat_id]
            
            if empty_chats:
                self.save_chat_history(chat_data)
                logger.info(f"Cleaned up {len(empty_chats)} empty chats")
            
            return len(empty_chats)
            
        except Exception as e:
            logger.error(f"Error during chat cleanup: {e}")
            return 0

# Global enhanced chat service instance
chat_service = ChatService()