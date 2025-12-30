import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Sunbeam Bot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Prevent page scrolling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
        max-height: 100vh;
        overflow: hidden;
    }
    
    /* Simple background */
    .stApp {
        background: #f0f9ff;
        overflow: hidden;
    }
    
    /* Title styling */
    .main-title {
        color: #0369a1;
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    /* Topic buttons */
    div[data-testid="column"] > div > div > button {
        background: #e0f2fe !important;
        color: #0369a1 !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        font-weight: 500 !important;
        width: 100% !important;
    }
    
    div[data-testid="column"] > div > div > button:hover {
        background: #bae6fd !important;
        transform: translateY(-2px);
    }
    
    /* Chat messages container - FIXED HEIGHT */
    .messages-container {
        height: calc(100vh - 350px);
        overflow-y: auto;
        padding: 1rem;
        background: white;
        border: 2px solid #bae6fd;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    /* Scrollbar for messages */
    .messages-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .messages-container::-webkit-scrollbar-track {
        background: #f0f9ff;
        border-radius: 10px;
    }
    
    .messages-container::-webkit-scrollbar-thumb {
        background: #38bdf8;
        border-radius: 10px;
    }
    
    .messages-container::-webkit-scrollbar-thumb:hover {
        background: #0ea5e9;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background: #e0f2fe;
        border: 2px solid #38bdf8;
        color: #0c4a6e;
        margin-left: 2rem;
    }
    
    .bot-message {
        background: white;
        border: 2px solid #bae6fd;
        color: #0c4a6e;
        margin-right: 2rem;
    }
    

    
    /* Mode buttons */
    .stButton > button {
        background: white !important;
        color: #0369a1 !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background: #e0f2fe !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #f0f9ff;
    }
    
    /* Make all sidebar elements same width */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        height: 45px !important;
        font-size: 0.95rem !important;
        padding: 0.5rem !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stTextInput {
        font-size: 0.9rem !important;
    }
    
    /* History items uniform size */
    section[data-testid="stSidebar"] div[data-testid="column"] {
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'chat_mode' not in st.session_state:
    st.session_state.chat_mode = 'text'

if 'current_input' not in st.session_state:
    st.session_state.current_input = ""

if 'language' not in st.session_state:
    st.session_state.language = 'English'

if 'profile_name' not in st.session_state:
    st.session_state.profile_name = 'User'

if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

if 'visible_messages' not in st.session_state:
    st.session_state.visible_messages = 5

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
            st.session_state.visible_messages = len(session['messages'])
            break

def new_chat():
    """Start a new chat session"""
    save_to_history()
    st.session_state.messages = []
    st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.visible_messages = 5

def load_more_messages():
    """Load more previous messages"""
    st.session_state.visible_messages += 5

def set_topic_question(question):
    st.session_state.current_input = question

def get_rag_response(user_message):
    """
    Placeholder for RAG model integration
    """
    return f"This is a placeholder response. Integrate your RAG model here to process: '{user_message}'"

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.language = st.selectbox(
            "🌐 Lang",
            ["EN", "ES", "FR", "DE", "HI", "MR"],
            index=["EN", "ES", "FR", "DE", "HI", "MR"].index("EN")
        )
    with col2:
        st.session_state.profile_name = st.text_input("👤 Name", value=st.session_state.profile_name, max_chars=15)
    
    st.markdown("<hr style='margin: 1rem 0; border: 1px solid #bae6fd;'>", unsafe_allow_html=True)
    
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
    
    st.markdown("<hr style='margin: 1rem 0; border: 1px solid #bae6fd;'>", unsafe_allow_html=True)
    
    st.markdown("### 📝 History")
    
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
st.markdown('<h1 class="main-title">🤖 Sunbeam Bot</h1>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Topics section
st.markdown("<h3 style='color: #0369a1; margin-bottom: 1rem;'>Quick Topics</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

topic_questions = {
    "📈 Finance": "Can you help me understand financial planning and investment strategies?",
    "💪 Fitness": "What are some effective fitness routines for beginners?",
    "📅 Coaching": "How can I improve my time management and productivity?",
    "🏢 Business": "What are the key elements of starting a successful business?"
}

topics = list(topic_questions.keys())

with col1:
    if st.button(topics[0], key="topic_0", use_container_width=True):
        set_topic_question(topic_questions[topics[0]])

with col2:
    if st.button(topics[1], key="topic_1", use_container_width=True):
        set_topic_question(topic_questions[topics[1]])

with col3:
    if st.button(topics[2], key="topic_2", use_container_width=True):
        set_topic_question(topic_questions[topics[2]])

with col4:
    if st.button(topics[3], key="topic_3", use_container_width=True):
        set_topic_question(topic_questions[topics[3]])

# Chat interface
if st.session_state.chat_mode == 'text':
    # Load more button
    if len(st.session_state.messages) > st.session_state.visible_messages:
        if st.button("⬆️ Load Previous Messages", use_container_width=True):
            load_more_messages()
            st.rerun()
    for msg in st.session_state.messages[-3:]:
        st.markdown(f'<div class="history-item">{msg["content"][:40]}...</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # st.markdown("""
    # <div class="sidebar-card">
    #     <button class="btn-sidebar">↗️ Share chat</button>
    #     <button class="btn-sidebar">🆕 New Chat</button>
    # </div>
    # <div class="sidebar-card">
    #     <div class="sidebar-title">🌍 Select Language</div>
    # """, unsafe_allow_html=True)
    
    # st.selectbox("", ["English", "हिंदी", "मराठी"], key="lang")
   # Replace your language section with this EXACT code:

    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title" style="margin-bottom: 4px !important;">🌍 Select Language</div>
    """, unsafe_allow_html=True)

    st.selectbox("", ["🇮🇳 English", "🇮🇳 हिन्दी", "🇮🇳 मराठी"], key="lang")

    st.markdown("</div>", unsafe_allow_html=True)



    
    st.markdown("""
     </div>
    <div class="sidebar-card" style="text-align: center;">
        <div class="sidebar-title" style="justify-content: center;">📞 Call</div>
        <button class="call-btn">📱</button>
        <div style="color: #007BFF; font-weight: 600; font-size: 10px;">+91 7768960392</div>
    </div>
    """, unsafe_allow_html=True)

    
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style='text-align: center; color: #0369a1; padding: 2rem;'>
            <h3>👋 Hello! I'm Sunbeam Bot</h3>
            <p>How can I assist you today? Choose a topic above or type your question below.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        start_index = max(0, len(st.session_state.messages) - st.session_state.visible_messages)
        visible_msgs = st.session_state.messages[start_index:]
        
        for message in visible_msgs:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message"><strong>🤖 Sunbeam Bot:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-scroll to bottom
    st.markdown("""
    <script>
        const element = document.getElementById('messages-scroll');
        if (element) {
            element.scrollTop = element.scrollHeight;
        }
    </script>
    """, unsafe_allow_html=True)

else:  # Voice mode
    st.markdown("<h3 style='color: #0369a1; text-align: center; margin: 2rem 0;'>🎤 Voice Chat Mode</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center;'>
            <div style='width: 200px; height: 200px; margin: 0 auto; 
                 background: linear-gradient(135deg, #7dd3fc 0%, #a78bfa 50%, #06b6d4 100%);
                 border-radius: 50%; display: flex; align-items: center; justify-content: center;
                 box-shadow: 0 0 30px rgba(56, 189, 248, 0.5);'>
                <div style='width: 180px; height: 180px; background: white;
                     border-radius: 50%; display: flex; align-items: center; justify-content: center;'>
                    <div style='width: 160px; height: 160px; 
                         background: linear-gradient(135deg, #34d399 0%, #06b6d4 100%);
                         border-radius: 50%;'></div>
                </div>
            </div>
            <p style='color: #0369a1; margin-top: 1.5rem; font-weight: 500;'>Click the microphone to start speaking</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.button("✏️ Notes", use_container_width=True)
    with col2:
        if st.button("🎤 Record", use_container_width=True, type="primary"):
            st.info("Voice recording integration point")
    with col3:
        st.button("📄 Transcript", use_container_width=True)

# FIXED INPUT BAR - Using st.chat_input
user_input = st.chat_input("Type your message and press Enter...")

if user_input:
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    bot_response = get_rag_response(user_input)
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": bot_response,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    st.session_state.visible_messages = 5
    save_to_history()
    st.session_state.current_input = ""
    st.rerun()