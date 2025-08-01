import streamlit as st
from chatbot import ConfidenceChatbot
from models import UserMessage
from dotenv import load_dotenv
from datetime import datetime
import logging
from typing import List, Dict, Any
import uuid
import json

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_MESSAGE_LENGTH = 500
DEFAULT_CONFIDENCE_LEVEL = 5

# Page config
st.set_page_config(
    page_title="ConfidenceAI - Your Personal Confidence Coach",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_custom_css() -> str:
    """Load and return custom CSS styles with dark mode support"""
    return """
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .chat-message {
            padding: 1.2rem;
            border-radius: 12px;
            margin: 1rem 0;
            animation: fadeIn 0.6s ease-out;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .user-message {
            background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            border-left: 4px solid #2196f3;
            color: #333;
        }
        .bot-message {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left: 4px solid #9c27b0;
            color: #333;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        }
        .quick-action-btn {
            width: 100%;
            margin: 0.3rem 0;
            padding: 0.5rem;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .error-message {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        @media (prefers-color-scheme: dark) {
            .main-header {
                background: linear-gradient(135deg, #4e5bb4 0%, #5a3f7f 100%);
                color: #e0e0e0;
            }
            .chat-message {
                box-shadow: 0 2px 10px rgba(255,255,255,0.1);
            }
            .user-message {
                background: linear-gradient(135deg, #2a3b5b 0%, #3b2a5b 100%);
                color: #e0e0e0;
                border-left: 4px solid #42a5f5;
            }
            .bot-message {
                background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
                color: #e0e0e0;
                border-left: 4px solid #ce93d8;
            }
            .metric-card {
                background: #2d2d2d;
                color: #e0e0e0;
            }
            .error-message {
                background-color: #5c2d2d;
                border-left: 4px solid #f44336;
                color: #e0e0e0;
            }
            .chat-message div[style*="color: #666"] {
                color: #b0b0b0 !important;
            }
            .chat-message strong {
                color: #e0e0e0;
            }
        }
    </style>
    """

def initialize_session_state():
    """Initialize all session state variables"""
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = ConfidenceChatbot()
            if 'messages' not in st.session_state:
                st.session_state.messages = []
            existing_contents = {msg['content'] for msg in st.session_state.messages}
            for msg in st.session_state.chatbot.session.messages:
                if msg['content'] not in existing_contents:
                    iso_timestamp = msg["timestamp"]
                    display_timestamp = datetime.fromisoformat(iso_timestamp).strftime("%H:%M")
                    st.session_state.messages.append({
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": display_timestamp,
                        "confidence_level": msg.get("confidence_level", DEFAULT_CONFIDENCE_LEVEL),
                        "matched_keywords": msg.get("matched_keywords", [])
                    })
                    existing_contents.add(msg['content'])
            st.session_state.confidence_history = [msg.get("confidence_level", DEFAULT_CONFIDENCE_LEVEL) for msg in st.session_state.messages if msg["role"] == "assistant"]
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {str(e)}")
            st.error("Failed to initialize ConfidenceAI. Ensure GEMINI_API_KEY is set correctly.")
            return False
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'confidence_history' not in st.session_state:
        st.session_state.confidence_history = []
    
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    
    if 'daily_goals' not in st.session_state:
        st.session_state.daily_goals = []
    
    return True

def validate_user_input(text: str) -> tuple[bool, str]:
    """Validate user input"""
    if not text or not text.strip():
        return False, "Please enter a message"
    
    if len(text) > MAX_MESSAGE_LENGTH:
        return False, f"Message too long. Please keep it under {MAX_MESSAGE_LENGTH} characters."
    
    inappropriate_words = ['spam', 'test123', 'asdf']
    if any(word in text.lower() for word in inappropriate_words):
        return False, "Please enter a meaningful message"
    
    return True, ""

def render_sidebar():
    """Render the enhanced sidebar with analytics dashboard"""
    with st.sidebar:
        st.markdown("### 🎯 Your Confidence Dashboard")
        
        try:
            session_data = st.session_state.chatbot.get_session_summary()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Messages",
                    session_data.get("total_messages", len(st.session_state.messages)),
                    delta=None if len(st.session_state.messages) == 0 else "+1"
                )
            with col2:
                avg_confidence = session_data.get("average_confidence", DEFAULT_CONFIDENCE_LEVEL)
                st.metric(
                    "Avg Confidence",
                    f"{avg_confidence:.1f}/10",
                    delta=f"+{avg_confidence - DEFAULT_CONFIDENCE_LEVEL:.1f}" if avg_confidence > DEFAULT_CONFIDENCE_LEVEL else None
                )
            
            if 'session_start_time' in st.session_state:
                duration = datetime.now() - st.session_state.session_start_time
                minutes = int(duration.total_seconds() / 60)
                st.metric("Session Time", f"{minutes} min")
            
            if st.session_state.confidence_history:
                st.markdown("**Confidence Trend**")
                st.line_chart(
                    st.session_state.confidence_history,
                    height=200,
                    use_container_width=True
                )
            else:
                st.info("Start chatting to see your confidence progress!")
            
            st.markdown("---")
            
            st.markdown("### 📜 Past Sessions")
            try:
                if st.button("🔎 View History"):
                    history = st.session_state.messages
                    if history:
                        for msg in history:
                            st.markdown(f"**{msg['role'].capitalize()}** ({msg['timestamp']}): {msg['content'][:100]}...")
                    else:
                        st.info("No past sessions found.")
                if st.button("📥 Download Session"):
                    session_data = st.session_state.chatbot.export_session()
                    session_data["daily_goals"] = st.session_state.daily_goals
                    st.download_button(
                        label="Download Chat Session",
                        data=json.dumps(session_data, indent=2),
                        file_name=f"confidence_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            except Exception as e:
                logger.error(f"Error loading history or downloading session: {str(e)}")
                st.error("Failed to load past sessions or export data.")
        
        except Exception as e:
            logger.error(f"Error rendering session data: {str(e)}")
            st.warning("Unable to load session analytics.")
        
        st.markdown("---")
        
        st.markdown("### ⚡ Instant Confidence Boosters")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💪 Affirmation", key="affirmation", help="Get a daily affirmation"):
                affirmations = [
                    "You are capable of amazing things!",
                    "Every challenge is an opportunity to grow!",
                    "Your potential is limitless!",
                    "You have everything you need to succeed!",
                    "Progress, not perfection, is the goal!"
                ]
                import random
                st.success(random.choice(affirmations))
                st.balloons()
        
        with col2:
            st.markdown("**🎯 Set Goal**")
            with st.form(key="goal_form"):
                goal_input = st.text_input("What's your goal for today?", key="goal_input")
                submit_button = st.form_submit_button("Save Goal")
                if submit_button and goal_input:
                    try:
                        goal_data = {
                            "id": str(uuid.uuid4()),
                            "user_id": "test_user",
                            "goal": goal_input.strip(),
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "completed": False
                        }
                        st.session_state.daily_goals.append(goal_data)
                        st.success("Goal added! You've got this! 🌟")
                    except Exception as e:
                        logger.error(f"Failed to save goal: {str(e)}")
                        st.error("Failed to save goal. Please try again.")
        
        if st.session_state.daily_goals:
            st.markdown("### 📋 Today's Goals")
            for i, goal in enumerate(st.session_state.daily_goals[-3:]):
                completed = st.checkbox(goal['goal'], value=goal['completed'], key=f"goal_{i}_{uuid.uuid4()}")
                if completed != goal['completed']:
                    goal['completed'] = completed
                    st.success("🎉 Goal status updated!")
        
        st.markdown("---")
        
        with st.expander("🚀 About ConfidenceAI"):
            st.markdown("""
            **Advanced Features:**
            - 🧠 AI-Powered Coaching
            - 📊 Real-Time Analytics
            - 🎯 Personalized Goal Setting
            - 💡 Dynamic Confidence Tips
            - 🔗 Tool Calling
            - 🧠 Agentic Behavior
            - 📜 Explainable AI
            - 💾 Exportable Session Data
            - 🔒 Privacy-First Design
            
            **Tech Stack:**
            - Streamlit + Python
            - Advanced Prompt Engineering
            - Pydantic Validation
            - Lightweight Analytics
            
            [⭐ Star on GitHub](https://github.com/walethewave/Confidence-Coach)
            """)

import html

def render_chat_message(message: Dict[str, Any], message_index: int):
    """Render individual chat message with explainable AI"""
    try:
        timestamp = message.get("timestamp", datetime.now().strftime("%H:%M"))
        try:
            timestamp = datetime.fromisoformat(timestamp).strftime("%H:%M")
        except ValueError:
            pass

        content = html.escape(message["content"])

        if message["role"] == "user":
            html_block = f"""
<div class="chat-message user-message">
    <strong>🙋‍♀️ You:</strong> <span>{content}</span>
    <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">{timestamp}</div>
</div>
"""
        else:
            html_block = f"""
<div class="chat-message bot-message">
    <strong>🤖 ConfidenceAI:</strong> <span>{content}</span>
    <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">{timestamp}</div>
</div>
"""
        st.markdown(html_block, unsafe_allow_html=True)

        if message["role"] == "assistant":
            col1, col2 = st.columns(2)
            with col1:
                if "tips" in message and message["tips"]:
                    with st.expander("💡 Confidence Tips", expanded=False):
                        for i, tip in enumerate(message["tips"], 1):
                            st.markdown(f"**{i}.** {tip}")
            with col2:
                if "next_steps" in message and message["next_steps"]:
                    with st.expander("🎯 Next Steps", expanded=False):
                        for i, step in enumerate(message["next_steps"], 1):
                            st.markdown(f"**{i}.** {step}")
                with st.expander("📊 Confidence Analysis", expanded=True):
                    confidence_level = message.get("confidence_level", DEFAULT_CONFIDENCE_LEVEL)
                    st.markdown(f"**Confidence Score:** {confidence_level}/10")
                    st.progress(confidence_level / 10)
                    if "matched_keywords" in message and message["matched_keywords"]:
                        st.markdown(f"**Reasoning:** Confidence rated {confidence_level} due to words: {', '.join(message['matched_keywords'])}")
                    else:
                        st.markdown("**Reasoning:** Default confidence level applied.")

    except Exception as e:
        logger.error(f"Error rendering message {message_index}: {str(e)}")
        st.error("Error displaying message")

def process_user_input(user_input: str) -> bool:
    """Process user input and generate response"""
    try:
        is_valid, error_message = validate_user_input(user_input)
        if not is_valid:
            st.error(error_message)
            return False

        existing_contents = {msg['content'] for msg in st.session_state.messages}
        if user_input not in existing_contents:
            user_message = UserMessage(content=user_input)
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": user_message.timestamp
            })
        
        with st.spinner("🤖 ConfidenceAI is crafting your personalized response..."):
            response = st.session_state.chatbot.generate_response(user_message)
            
            confidence_level = getattr(response, 'confidence_level', DEFAULT_CONFIDENCE_LEVEL)
            if user_input not in existing_contents:
                st.session_state.confidence_history.append(confidence_level)
            
            bot_message = {
                "role": "assistant",
                "content": response.response,
                "tips": getattr(response, 'confidence_tips', []),
                "next_steps": getattr(response, 'next_steps', []),
                "confidence_level": confidence_level,
                "matched_keywords": getattr(response, 'matched_keywords', []),
                "timestamp": response.timestamp
            }
            if response.response not in existing_contents:
                st.session_state.messages.append(bot_message)
            
            return True
            
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
        st.error("Sorry, I encountered an error processing your message. Please try again.")
        return False

def main():
    """Main application function"""
    st.markdown(load_custom_css(), unsafe_allow_html=True)
    
    if not initialize_session_state():
        return
    
    st.markdown("""
    <div class="main-header">
        <h1>🌟 ConfidenceAI - Your Personal Confidence Coach</h1>
        <p>Empowering you to unlock your full potential through advanced AI coaching</p>
        <div style="margin-top: 1rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0 0.2rem;">
                🧠 AI-Powered
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0 0.2rem;">
                📊 Progress Tracking
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0 0.2rem;">
                🎯 Personalized
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    render_sidebar()
    
    st.markdown("### 💬 Chat with ConfidenceAI")
    st.markdown("*Share your thoughts, challenges, or goals. I'm here to help build your confidence!*")
    
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            render_chat_message(message, i)
    
    user_input = st.chat_input(
        "Share what's on your mind... I'm here to help build your confidence! 🌟",
        max_chars=MAX_MESSAGE_LENGTH
    )
    
    if user_input:
        if process_user_input(user_input):
            st.rerun()
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔒 Privacy First**")
        st.caption("Your conversations are secure and private")
    
    with col2:
        st.markdown("**⚡ Real-time Coaching**")
        st.caption("Instant personalized guidance")
    
    with col3:
        st.markdown("**📈 Track Progress**")
        st.caption("Visualize your confidence journey")
    
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>Built with ❤️ using Streamlit, Advanced AI & Modern Web Technologies</p>
        <p><em>Your confidence journey starts with a single conversation</em> 🌟</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"App failed: {str(e)}")
        st.error("Application failed to start. Ensure GEMINI_API_KEY is set correctly.")