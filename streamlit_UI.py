"""
Streamlit UI for AI Chat Assistant
This module handles all UI-related functionality and uses ChatService for core logic
"""

import streamlit as st
import time
from chatService import ChatService, MultiChatService

# Configure the Streamlit page - this sets up the basic appearance
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make the UI more attractive
st.markdown("""
<style>
    /* Main chat container styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    
    /* Human message styling - right aligned with blue theme */
    .chat-message.user {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        margin-left: 2rem;
    }
    
    /* AI message styling - left aligned with green theme */
    .chat-message.assistant {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
        margin-right: 2rem;
    }
    
    /* Message header with role and timestamp */
    .message-header {
        font-weight: bold;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    
    /* Message content styling */
    .message-content {
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e0e0e0;
        padding: 12px 20px;
        font-size: 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2196f3;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
    }
    
    /* Send button styling */
    .stButton > button {
        border-radius: 25px;
        height: 50px;
        background-color: #4caf50;
        color: white;
        border: none;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
    }
    
    /* Service selector styling */
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
</style>
""", unsafe_allow_html=True)

class StreamlitChatUI:
    """
    Streamlit UI handler for chat functionality.
    This class manages all UI interactions and delegates core logic to ChatService.
    """
    
    def __init__(self):
        """Initialize the Streamlit UI."""
        self.initialize_session_state()
        self.setup_services()
    
    def initialize_session_state(self):
        """Initialize session state variables if they don't exist."""
        if "multi_chat_service" not in st.session_state:
            st.session_state.multi_chat_service = MultiChatService()
        
        if "openai_api_key" not in st.session_state:
            st.session_state.openai_api_key = ""
        
        if "active_service_name" not in st.session_state:
            st.session_state.active_service_name = "Science & Math Assistant"
        
        if "processing" not in st.session_state:
            st.session_state.processing = False
    
    def setup_services(self):
        """Set up different chat services."""
        multi_service = st.session_state.multi_chat_service
        
        # Science & Math Assistant (current service)
        if "Science & Math Assistant" not in multi_service.get_service_names():
            science_service = ChatService(st.session_state.openai_api_key)
            multi_service.add_service("Science & Math Assistant", science_service)
        
        # You can add more services here in the future
        # Example:
        # if "General Assistant" not in multi_service.get_service_names():
        #     general_service = ChatService(st.session_state.openai_api_key)
        #     general_service.system_prompt = "You are a helpful general AI assistant..."
        #     multi_service.add_service("General Assistant", general_service)
        
        # Set active service
        multi_service.set_active_service(st.session_state.active_service_name)
    
    def display_chat_message(self, role: str, content: str, timestamp: str):
        """
        Display a single chat message with proper styling.
        
        Args:
            role (str): Either 'user' or 'assistant'
            content (str): The message content
            timestamp (str): When the message was sent
        """
        if role == "user":
            role_display = "You"
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 0.75rem; 
                        margin-bottom: 1rem; margin-left: 30rem; border-left: 5px solid #2196f3;">
                <div style="font-weight: bold; font-size: 0.9rem; margin-bottom: 0.5rem; opacity: 0.8;">
                    {role_display} • {timestamp}
                </div>
                <div style="font-size: 1rem; line-height: 1.5;">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            role_display = "AI Assistant"
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 0.75rem; 
                        margin-bottom: 1rem; margin-right: 2rem; border-left: 5px solid #4caf50;">
                <div style="font-weight: bold; font-size: 0.9rem; margin-bottom: 0.5rem; opacity: 0.8;">
                    {role_display} • {timestamp}
                </div>
                <div style="font-size: 1rem; line-height: 1.5;">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with configuration options."""
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # Service selection
            multi_service = st.session_state.multi_chat_service
            service_names = multi_service.get_service_names()
            
            if len(service_names) > 1:
                selected_service = st.selectbox(
                    "Choose AI Service",
                    service_names,
                    index=service_names.index(st.session_state.active_service_name) 
                          if st.session_state.active_service_name in service_names else 0
                )
                
                if selected_service != st.session_state.active_service_name:
                    st.session_state.active_service_name = selected_service
                    multi_service.set_active_service(selected_service)
                    st.rerun()
            
            # API Key input
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.openai_api_key,
                help="Enter your OpenAI API key. You can get one from https://platform.openai.com/api-keys"
            )
            
            # Update API key for all services
            if api_key != st.session_state.openai_api_key:
                st.session_state.openai_api_key = api_key
                for service in multi_service.services.values():
                    service.set_api_key(api_key)
            
            # Display API key status
            if api_key:
                st.success("✅ API Key configured")
            else:
                st.warning("⚠️ Please enter your OpenAI API Key")
            
            st.markdown("---")
            
            # Chat controls
            st.header("💬 Chat Controls")
            active_service = multi_service.get_active_service()
            
            if active_service:
                # Clear chat button
                if st.button("🗑️ Clear Chat History", use_container_width=True):
                    active_service.clear_conversation()
                    st.rerun()
                
                # Display conversation statistics
                stats = active_service.get_conversation_stats()
                st.info(f"💬 Total messages: {stats['total_messages']}")
                st.info(f"👤 Your messages: {stats['user_messages']}")
                st.info(f"🤖 AI responses: {stats['assistant_messages']}")
                
                # Export conversation
                if stats['total_messages'] > 0:
                    if st.button("📥 Export Conversation", use_container_width=True):
                        conversation_text = active_service.export_conversation()
                        st.download_button(
                            label="💾 Download as Text",
                            data=conversation_text,
                            file_name=f"chat_export_{st.session_state.active_service_name.lower().replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
    
    def render_chat_area(self):
        """Render the main chat area."""
        multi_service = st.session_state.multi_chat_service
        active_service = multi_service.get_active_service()
        
        if not active_service:
            st.error("❌ No active chat service available.")
            return
        
        st.header(f"💬 Chat - {st.session_state.active_service_name}")
        
        # Display existing chat messages in a scrollable container
        chat_container = st.container(height=400)
        
        messages = active_service.get_messages()
        
        if messages:
            with chat_container:
                for message in messages:
                    self.display_chat_message(
                        message["role"],
                        message["content"],
                        message.get("timestamp", "Unknown time")
                    )
        else:
            with chat_container:
                st.info("👋 Welcome! Start a conversation by typing a message below.")
    
    def render_input_area(self):
        """Render the input area for user messages."""
        multi_service = st.session_state.multi_chat_service
        active_service = multi_service.get_active_service()
        
        if not active_service:
            return
        
        st.markdown("---")
        
        # Use a form to handle input and submission properly
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                user_input = st.text_input(
                    "Type your message here...",
                    placeholder="Ask me anything about science or math!",
                    label_visibility="collapsed"
                )
            
            with col2:
                send_button = st.form_submit_button("📤 Send", use_container_width=True)
        
        # Process user input when form is submitted
        if send_button and user_input.strip():
            if not active_service.validate_api_key():
                st.error("❌ Please enter your OpenAI API key in the sidebar first.")
                return
            
            # Show processing toast
            st.toast("🤖 AI is thinking...", icon="🔄")
            
            # Process the conversation turn
            try:
                user_msg, ai_msg, success = active_service.process_conversation_turn(user_input)
                
                if success:
                    st.toast("Science/Math answer ready! 🧠", icon="✅")
                else:
                    st.toast("❌ Error processing message", icon="❌")
                
                # Small delay for user experience
                time.sleep(0.5)
                
                # Refresh to show new messages
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
        
        elif send_button and not user_input.strip():
            st.warning("⚠️ Please enter a message before sending.")
    
    def run(self):
        """Run the main Streamlit application."""
        # Update services with current API key
        self.setup_services()
        
        # Main title
        st.title("🤖 AI Chat Assistant")
        st.markdown("---")
        
        # Render different sections
        self.render_sidebar()
        self.render_chat_area()
        self.render_input_area()


def main():
    """Main application entry point."""
    # Create and run the UI
    ui = StreamlitChatUI()
    ui.run()


# Run the application
if __name__ == "__main__":
    main()