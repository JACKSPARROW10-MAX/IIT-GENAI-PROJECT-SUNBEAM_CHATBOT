import streamlit as st
from datetime import datetime
import sys
import os
import time

# Ensure Project Root is in path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from RAG_Model.Agent_response import agent_response

# --- Page Configuration ---
st.set_page_config(
    page_title="Sunbeam AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatFloatingInputContainer {
        padding-bottom: 20px;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #e3f2fd;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
    }
    .sidebar .sidebar-content {
        background-color: #1a237e;
        color: white;
    }
    h1 {
        color: #1a237e;
        font-weight: 700;
    }
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'user_name' not in st.session_state:
    st.session_state.user_name = 'Guest'

# --- Helper Functions ---
def clear_chat():
    if st.session_state.messages:
        # Save to history before clearing
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        preview = st.session_state.messages[0]['content'][:40] + "..."
        st.session_state.chat_history.append({"time": timestamp, "preview": preview, "msgs": st.session_state.messages.copy()})
    st.session_state.messages = []

def get_language_prompt(lang):
    if lang == "Hindi": return "\n\nPlease provide the response in Hindi."
    if lang == "Marathi": return "\n\nPlease provide the response in Marathi."
    return ""

# --- Sidebar ---
with st.sidebar:
    st.image(os.path.join(os.path.dirname(__file__), "chatbot_img.jpg"), width='stretch')
    st.title("Settings")
    
    st.session_state.user_name = st.text_input("Profile Name", value=st.session_state.user_name)
    st.session_state.language = st.selectbox("Preferred Language", ["English", "Hindi", "Marathi"])
    
    st.divider()
    
    if st.button("🗑️ Clear Current Chat", width='stretch'):
        clear_chat()
        st.rerun()
        
    st.subheader("Previous Chats")
    if not st.session_state.chat_history:
        st.caption("No history yet.")
    else:
        for i, hist in enumerate(reversed(st.session_state.chat_history)):
            if st.button(f"📜 {hist['preview']}", key=f"hist_{i}", width='stretch'):
                st.session_state.messages = hist['msgs']
                st.rerun()

# --- Main UI ---
st.title("🤖 Sunbeam AI Assistant")
st.caption(f"Welcome back, **{st.session_state.user_name}**! How can I help you today?")

# Quick Action Chips
cols = st.columns(4)
topics = [
    ("🏢 About Sunbeam", "Tell me about Sunbeam Institute?"),
    ("🎓 Courses", "What modular courses are available?"),
    ("💼 Internships", "Tell me about internship fees and batches"),
    ("📍 Location", "Where is Sunbeam Institute located?")
]

for col, (label, query) in zip(cols, topics):
    if col.button(label, width='stretch'):
        st.session_state.messages.append({"role": "user", "content": query})
        # Trigger response generation logic below

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input & Logic
if prompt := st.chat_input("Type your question here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Searching Sunbeam knowledge base..."):
            # Construct final query with language preference
            full_query = prompt + get_language_prompt(st.session_state.language)
            
            # Call the RAG Agent
            response = agent_response(full_query)
            
            # Simulate streaming for premium feel
            placeholder = st.empty()
            full_response = ""
            for chunk in response.split(' '):
                full_response += chunk + ' '
                time.sleep(0.02)
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            
    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

# Bottom spacer
st.markdown("<div style='margin-bottom: 100px;'></div>", unsafe_allow_html=True)