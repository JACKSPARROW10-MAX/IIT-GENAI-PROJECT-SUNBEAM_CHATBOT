import streamlit as st
from datetime import datetime
import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
from RAG_Model.Agent_response import agent_response

# Page configuration
st.set_page_config(
    page_title="Sunbeam Bot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'chat_mode' not in st.session_state:
    st.session_state.chat_mode = 'text'

if 'language' not in st.session_state:
    st.session_state.language = 'English'

if 'profile_name' not in st.session_state:
    st.session_state.profile_name = 'User'

if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

if 'process_query' not in st.session_state:
    st.session_state.process_query = None

# Functions
def save_to_history():
    """Save current chat session to history"""
    if st.session_state.messages:
        session_data = {
            'id': st.session_state.current_session_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'messages': st.session_state.messages.copy(),
            'preview': st.session_state.messages[0]['content'][:50] + "..." if st.session_state.messages else "Empty chat"
        }
        if not any(h['id'] == session_data['id'] for h in st.session_state.chat_history):
            st.session_state.chat_history.insert(0, session_data)

def load_from_history(session_id):
    """Load a chat session from history"""
    for session in st.session_state.chat_history:
        if session['id'] == session_id:
            st.session_state.messages = session['messages'].copy()
            st.session_state.current_session_id = session_id
            break

def new_chat():
    """Start a new chat session"""
    save_to_history()
    st.session_state.messages = []
    st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

def process_topic_query(query):
    """Process a topic query"""
    st.session_state.process_query = query

def get_language_instruction(language):
    """Get language instruction for the query"""
    if language == "Hindi":
        return " Answer in Hindi language."
    elif language == "Marathi":
        return " Answer in Marathi language."
    else:
        return ""

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.language = st.selectbox(
            "🌍 Language",
            ["English", "Hindi", "Marathi"],
            index=0
        )
    with col2:
        st.session_state.profile_name = st.text_input("👤 Name", value=st.session_state.profile_name, max_chars=15)
    
    st.divider()
    
    st.markdown("### 💬 Chat Mode")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Text", use_container_width=True, type="primary" if st.session_state.chat_mode == 'text' else "secondary"):
            st.session_state.chat_mode = 'text'
            st.rerun()
    with col2:
        if st.button("🎤 Voice", use_container_width=True, type="primary" if st.session_state.chat_mode == 'voice' else "secondary"):
            st.session_state.chat_mode = 'voice'
            st.rerun()
    
    st.divider()
    
    st.markdown("### 📜 History")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_chat()
        st.rerun()
    
    if st.session_state.chat_history:
        for idx, session in enumerate(st.session_state.chat_history):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    f"{session['preview'][:20]}...",
                    key=f"hist_{idx}",
                    use_container_width=True
                ):
                    load_from_history(session['id'])
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                    st.session_state.chat_history.pop(idx)
                    st.rerun()
            st.caption(f"🕒 {session['timestamp']}")
    else:
        st.info("No history yet")

# Main content
st.title("🤖 Sunbeam Bot")

# Topics section
st.markdown("### Quick Topics")

col1, col2, col3 = st.columns(3)

topic_questions = {
    "📚 About Us": "Tell me About Sunbeam?",
    "💼 Internship": "info of internships which has fees 4000 show in table format",
    "📖 Course": "List A Course Title and Price"
}

topics = list(topic_questions.keys())

with col1:
    if st.button(topics[0], key="topic_0", use_container_width=True):
        process_topic_query(topic_questions[topics[0]])

with col2:
    if st.button(topics[1], key="topic_1", use_container_width=True):
        process_topic_query(topic_questions[topics[1]])

with col3:
    if st.button(topics[2], key="topic_2", use_container_width=True):
        process_topic_query(topic_questions[topics[2]])

st.divider()

# Chat interface
if st.session_state.chat_mode == 'text':
    # Display messages
    if len(st.session_state.messages) == 0:
        st.info("👋 Hello! I'm Sunbeam Bot. How can I assist you today? Choose a topic above or type your question below.")
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Process topic query if set
    if st.session_state.process_query:
        query = st.session_state.process_query
        st.session_state.process_query = None
        
        # Add user message (without language instruction)
        st.session_state.messages.append({
            "role": "user", 
            "content": query,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        with st.chat_message("user"):
            st.write(query)
        
        # Get bot response with language instruction
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Add language instruction to query for LLM
                llm_query = query + get_language_instruction(st.session_state.language)
                bot_response =agent_response(llm_query)
                st.write(bot_response)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": bot_response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        save_to_history()
        st.rerun()
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message (without language instruction)
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get bot response with language instruction
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Add language instruction to query for LLM
                llm_query = user_input + get_language_instruction(st.session_state.language)
                bot_response = agent_response(llm_query)
                st.write(bot_response)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": bot_response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        save_to_history()
        st.rerun()

else:  # Voice mode
    st.markdown("### 🎤 Voice Chat Mode")
    st.info("Voice recording feature coming soon!")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.button("✏️ Notes", use_container_width=True)
    with col2:
        if st.button("🎤 Record", use_container_width=True, type="primary"):
            st.info("Voice recording integration point")
    with col3:
        st.button("📄 Transcript", use_container_width=True)