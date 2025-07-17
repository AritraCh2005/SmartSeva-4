"""
Enhanced Memory management for conversation history with chat isolation
"""
import uuid
import time
from typing import Dict, List, Optional, Any
from langchain.memory import ConversationBufferWindowMemory
from config.settings import MEMORY_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class ChatMemoryManager:
    """Enhanced memory manager with chat isolation and UUID-based chat IDs."""
    
    def __init__(self):
        # Dictionary to store memory instances for each chat
        self.chat_memories: Dict[str, ConversationBufferWindowMemory] = {}
        self.current_chat_id: Optional[str] = None
        self.max_memory_size = MEMORY_CONFIG.get("window_size", 10)
        self.return_messages = MEMORY_CONFIG.get("return_messages", True)
        logger.info("Enhanced Chat Memory Manager initialized.")
    
    def create_new_chat_memory(self, chat_id: str) -> str:
        """Create a new memory instance for a chat with UUID."""
        if not chat_id:
            chat_id = str(uuid.uuid4())
        
        # Create fresh memory instance for this chat
        self.chat_memories[chat_id] = ConversationBufferWindowMemory(
            k=self.max_memory_size,
            return_messages=self.return_messages
        )
        
        logger.info(f"Created new memory instance for chat: {chat_id}")
        return chat_id
    
    def switch_to_chat(self, chat_id: str) -> bool:
        """Switch to a specific chat's memory context."""
        try:
            if chat_id not in self.chat_memories:
                # Create new memory if chat doesn't exist
                self.create_new_chat_memory(chat_id)
            
            self.current_chat_id = chat_id
            logger.info(f"Switched to chat memory: {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error switching to chat {chat_id}: {e}")
            return False
    
    def get_current_memory(self) -> Optional[ConversationBufferWindowMemory]:
        """Get the current active chat's memory."""
        if self.current_chat_id and self.current_chat_id in self.chat_memories:
            return self.chat_memories[self.current_chat_id]
        return None
    
    def save_context(self, input_data: Dict, output_data: Dict) -> bool:
        """Save conversation context to current chat's memory."""
        try:
            current_memory = self.get_current_memory()
            if not current_memory:
                logger.warning("No active chat memory found. Cannot save context.")
                return False
                
            current_memory.save_context(input_data, output_data)
            logger.info(f"Context saved to chat {self.current_chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving context to memory: {e}")
            return False
    
    def load_memory_variables(self) -> Dict:
        """Load memory variables from current chat."""
        try:
            current_memory = self.get_current_memory()
            if not current_memory:
                logger.warning("No active chat memory found. Returning empty history.")
                return {"history": []}
                
            memory_vars = current_memory.load_memory_variables({})
            logger.debug(f"Loaded memory variables for chat {self.current_chat_id}")
            return memory_vars
            
        except Exception as e:
            logger.error(f"Error loading memory variables: {e}")
            return {"history": []}
    
    def clear_current_chat_memory(self) -> bool:
        """Clear only the current chat's memory."""
        try:
            current_memory = self.get_current_memory()
            if not current_memory:
                logger.warning("No active chat memory to clear.")
                return False
                
            current_memory.clear()
            logger.info(f"Cleared memory for chat {self.current_chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing current chat memory: {e}")
            return False
    
    def delete_chat_memory(self, chat_id: str) -> bool:
        """Completely delete a chat's memory."""
        try:
            if chat_id in self.chat_memories:
                del self.chat_memories[chat_id]
                
                # If we're deleting the current chat, reset current_chat_id
                if self.current_chat_id == chat_id:
                    self.current_chat_id = None
                    
                logger.info(f"Deleted memory for chat {chat_id}")
                return True
            else:
                logger.warning(f"Chat {chat_id} memory not found for deletion.")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting chat memory {chat_id}: {e}")
            return False
    
    def load_chat_messages_from_history(self, chat_id: str, chat_messages: List[Dict]) -> bool:
        """Load chat messages into a specific chat's memory from saved history with enhanced error handling."""
        try:
            # Switch to the target chat
            if not self.switch_to_chat(chat_id):
                logger.error(f"Failed to switch to chat {chat_id}")
                return False
            
            # Clear existing memory for this chat
            if not self.clear_current_chat_memory():
                logger.warning(f"Failed to clear memory for chat {chat_id}, proceeding anyway")
            
            if not chat_messages:
                logger.info(f"No messages to load for chat {chat_id}")
                return True
            
            # Enhanced message loading with better error handling
            message_pairs = []
            successful_pairs = 0
            
            for i in range(0, len(chat_messages) - 1, 2):
                try:
                    if i + 1 < len(chat_messages):
                        user_msg = chat_messages[i]
                        assistant_msg = chat_messages[i + 1]
                        
                        # Validate message structure
                        if (isinstance(user_msg, dict) and isinstance(assistant_msg, dict) and
                            user_msg.get("role") == "user" and 
                            assistant_msg.get("role") == "Virtual Assistant" and
                            user_msg.get("content") and assistant_msg.get("content")):
                            
                            message_pairs.append((user_msg["content"], assistant_msg["content"]))
                            successful_pairs += 1
                        else:
                            logger.warning(f"Invalid message pair at index {i} for chat {chat_id}")
                            
                except Exception as e:
                    logger.warning(f"Error processing message pair at index {i}: {e}")
                    continue
            
            # Load recent pairs within memory window to maintain context
            # Take the most recent messages that fit in memory window
            max_pairs = max(1, self.max_memory_size // 2)  # Ensure at least 1 pair
            recent_pairs = message_pairs[-max_pairs:] if len(message_pairs) > max_pairs else message_pairs
            
            # Load pairs into memory with error handling
            loaded_pairs = 0
            for user_content, assistant_content in recent_pairs:
                try:
                    if self.save_context({"input": user_content}, {"output": assistant_content}):
                        loaded_pairs += 1
                    else:
                        logger.warning(f"Failed to save context pair to memory for chat {chat_id}")
                except Exception as e:
                    logger.error(f"Error loading message pair into memory: {e}")
                    continue
            
            logger.info(f"Successfully loaded {loaded_pairs}/{len(recent_pairs)} conversation pairs into memory for chat {chat_id}")
            return loaded_pairs > 0
            
        except Exception as e:
            logger.error(f"Error loading chat messages to memory for chat {chat_id}: {e}")
            return False
    
    def get_chat_memory_summary(self, chat_id: str) -> Dict:
        """Get summary of a specific chat's memory."""
        try:
            if chat_id not in self.chat_memories:
                return {"exists": False, "message_count": 0}
            
            memory = self.chat_memories[chat_id]
            history = memory.load_memory_variables({}).get("history", [])
            
            return {
                "exists": True,
                "message_count": len(history),
                "is_current": chat_id == self.current_chat_id
            }
            
        except Exception as e:
            logger.error(f"Error getting memory summary for chat {chat_id}: {e}")
            return {"exists": False, "message_count": 0, "error": str(e)}
    
    def get_all_active_chats(self) -> List[str]:
        """Get list of all chat IDs that have active memory."""
        return list(self.chat_memories.keys())

# Global enhanced memory manager instance
memory_manager = ChatMemoryManager()