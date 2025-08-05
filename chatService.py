"""
Chat Service Module - Contains core logic for AI chat functionality
This module is separate from UI to allow for easy integration with different interfaces
"""

import openai
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class ChatService:
    """
    Core chat service that handles AI interactions and message management.
    This class is UI-agnostic and can be used with any interface.
    """
    
    def __init__(self, api_key: str = ""):
        """
        Initialize the chat service.
        
        Args:
            api_key (str): OpenAI API key
        """
        self.api_key = api_key
        self.messages: List[Dict[str, str]] = []
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the AI assistant.
        
        Returns:
            str: System prompt defining AI behavior
        """
        return """You are an educational AI assistant specialized in Science and Mathematics. 

IMPORTANT RESTRICTIONS:
- Only answer questions related to science (physics, chemistry, biology, earth science, etc.) and mathematics (algebra, calculus, geometry, statistics, etc.)
- Focus on educational content that helps with studying and learning
- Provide explanations, solve problems, clarify concepts, and offer study guidance
- If asked about non-science/math topics (jokes, entertainment, general chat, personal advice, etc.), politely decline and redirect to educational topics

RESPONSE FORMAT:
- Give clear, step-by-step explanations
- Include relevant formulas, theories, or principles when applicable
- Provide examples to illustrate concepts
- Suggest related topics for further study when helpful

If a question is not related to science or mathematics education, respond with: "I'm designed to help with science and mathematics questions for educational purposes. Please ask me about topics like physics, chemistry, biology, mathematics, or other scientific concepts that can help with your studies."
"""
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the OpenAI API key.
        
        Args:
            api_key (str): OpenAI API key
        """
        self.api_key = api_key
    
    def validate_api_key(self) -> bool:
        """
        Check if API key is set.
        
        Returns:
            bool: True if API key is set, False otherwise
        """
        return bool(self.api_key.strip())
    
    def add_user_message(self, content: str) -> Dict[str, str]:
        """
        Add a user message to the conversation history.
        
        Args:
            content (str): User message content
            
        Returns:
            Dict[str, str]: Message dictionary with metadata
        """
        message = {
            "role": "user",
            "content": content.strip(),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.messages.append(message)
        return message
    
    def add_assistant_message(self, content: str) -> Dict[str, str]:
        """
        Add an assistant message to the conversation history.
        
        Args:
            content (str): Assistant message content
            
        Returns:
            Dict[str, str]: Message dictionary with metadata
        """
        message = {
            "role": "assistant",
            "content": content.strip(),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.messages.append(message)
        return message
    
    def get_ai_response(self, user_message: str) -> Tuple[str, bool]:
        """
        Get response from OpenAI API for a user message.
        
        Args:
            user_message (str): The user's input message
            
        Returns:
            Tuple[str, bool]: (AI response or error message, success flag)
        """
        if not self.validate_api_key():
            return "❌ API key not configured.", False
        
        if not user_message.strip():
            return "❌ Empty message provided.", False
        
        try:
            # Set up the OpenAI client with the provided API key
            client = openai.OpenAI(api_key=self.api_key)
            
            # Prepare the conversation history for the API
            messages_for_api = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add the chat history to maintain context across the conversation
            for msg in self.messages:
                messages_for_api.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add the current user message
            messages_for_api.append({
                "role": "user",
                "content": user_message
            })
            
            # Make the API call to OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using GPT-3.5-turbo for cost efficiency
                messages=messages_for_api,
                max_tokens=10,  # Limit response length to control costs
                temperature=0.7,  # Controls randomness - 0.7 gives good balance
            )
            
            # Extract and return the AI's response
            return response.choices[0].message.content, True
            
        except openai.AuthenticationError:
            return "❌ Authentication failed. Please check your OpenAI API key.", False
        except openai.RateLimitError:
            return "❌ Rate limit exceeded. Please try again later.", False
        except openai.APIError as e:
            return f"❌ OpenAI API error: {str(e)}", False
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}", False
    
    def process_conversation_turn(self, user_input: str) -> Tuple[Dict[str, str], Dict[str, str], bool]:
        """
        Process a complete conversation turn (user input + AI response).
        
        Args:
            user_input (str): User's message
            
        Returns:
            Tuple[Dict[str, str], Dict[str, str], bool]: 
                (user_message_dict, ai_message_dict, success_flag)
        """
        # Add user message
        user_message = self.add_user_message(user_input)
        
        # Get AI response
        ai_response, success = self.get_ai_response(user_input)
        
        # Add AI response to history
        ai_message = self.add_assistant_message(ai_response)
        
        return user_message, ai_message, success
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get all messages in the conversation.
        
        Returns:
            List[Dict[str, str]]: List of all messages
        """
        return self.messages.copy()
    
    def clear_conversation(self) -> None:
        """
        Clear all messages from the conversation history.
        """
        self.messages = []
    
    def get_message_count(self) -> int:
        """
        Get the total number of messages in the conversation.
        
        Returns:
            int: Number of messages
        """
        return len(self.messages)
    
    def export_conversation(self) -> str:
        """
        Export the conversation as a formatted string.
        
        Returns:
            str: Formatted conversation text
        """
        if not self.messages:
            return "No conversation history."
        
        conversation_text = "=== Conversation Export ===\n\n"
        
        for message in self.messages:
            role = "You" if message["role"] == "user" else "AI Assistant"
            timestamp = message.get("timestamp", "Unknown time")
            content = message["content"]
            
            conversation_text += f"[{timestamp}] {role}:\n{content}\n\n"
        
        return conversation_text
    
    def get_conversation_stats(self) -> Dict[str, int]:
        """
        Get statistics about the current conversation.
        
        Returns:
            Dict[str, int]: Statistics including message counts by role
        """
        user_messages = sum(1 for msg in self.messages if msg["role"] == "user")
        assistant_messages = sum(1 for msg in self.messages if msg["role"] == "assistant")
        
        return {
            "total_messages": len(self.messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages
        }


class MultiChatService:
    """
    Manager for multiple chat services.
    This allows for different AI services or configurations.
    """
    
    def __init__(self):
        """Initialize the multi-chat service manager."""
        self.services: Dict[str, ChatService] = {}
        self.active_service: Optional[str] = None
    
    def add_service(self, name: str, service: ChatService) -> None:
        """
        Add a chat service.
        
        Args:
            name (str): Service name/identifier
            service (ChatService): Chat service instance
        """
        self.services[name] = service
        if self.active_service is None:
            self.active_service = name
    
    def set_active_service(self, name: str) -> bool:
        """
        Set the active chat service.
        
        Args:
            name (str): Service name
            
        Returns:
            bool: True if service exists and was set, False otherwise
        """
        if name in self.services:
            self.active_service = name
            return True
        return False
    
    def get_active_service(self) -> Optional[ChatService]:
        """
        Get the currently active chat service.
        
        Returns:
            Optional[ChatService]: Active service or None
        """
        if self.active_service and self.active_service in self.services:
            return self.services[self.active_service]
        return None
    
    def get_service_names(self) -> List[str]:
        """
        Get list of all service names.
        
        Returns:
            List[str]: List of service names
        """
        return list(self.services.keys())