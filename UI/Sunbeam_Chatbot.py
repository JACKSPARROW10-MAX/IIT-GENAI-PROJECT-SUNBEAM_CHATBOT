import streamlit as st
import time

st.set_page_config(page_title="Sunbeam AI Chat", page_icon="☀️", layout="wide")

# ==================== COMPACT SUNBEAM DESIGN - NO WHITE SPACE ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
* { font-family: 'Roboto', sans-serif !important; margin: 0; padding: 0; box-sizing: border-box; }

.main { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); }

/* COMPACT HEADER - 60px */
.header-main {
    background: linear-gradient(90deg, #007BFF 0%, #0056B3 100%);
    height: 60px;
    padding: 0 30px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 10px rgba(0,123,255,0.2);
}

.logo {
    font-size: 24px;
    font-weight: 700;
    color: white;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* COMPACT NAV - 50px SINGLE TABS */
.nav-bar {
    background: white;
    height: 50px;
    padding: 0 30px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.08);
}

.nav-item {
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 14px;
    cursor: pointer;
    color: #495057;
    transition: all 0.2s;
}

.nav-item:hover, .nav-item.active {
    background: #007BFF;
    color: white;
}

/* TIGHT CONTENT - 20px padding */
.content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px 30px 20px;
}

/* COMPACT HERO - 24px padding */
.hero {
    background: white;
    border-radius: 12px;
    padding: 24px 30px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border-top: 4px solid #007BFF;
    display: flex;
    gap: 30px;
}

.hero-text {
    flex: 1;
}

.hero h1 {
    font-size: 28px;
    font-weight: 700;
    color: #1a1a2a;
    margin-bottom: 8px;
}

.hero p {
    font-size: 16px;
    color: #6c757d;
    margin: 0;
}

/* COMPACT STATS */
.stats-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border-top: 4px solid #007BFF;
    height: fit-content;
}


.message {
    display: flex;
    gap: 12px;
    max-width: 75%;
}

.message.user {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.bubble {
    padding: 12px 20px;
    border-radius: 20px;
    font-size: 14px;
    line-height: 1.4;
}

.bubble.user {
    background: linear-gradient(135deg, #007BFF, #0056B3);
    color: white;
}

.bubble.bot {
    background: white;
    border: 1px solid #e9ecef;
    color: #495057;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* INPUT - 90px */
.input-area {
    height: 90px;
    padding: 20px;
    background: white;
    border-top: 1px solid #e9ecef;
    display: flex;
    align-items: center;
    gap: 12px;
}

.input-controls {
    display: flex;
    gap: 8px;
}

.btn-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 1px solid #dee2e6;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.2s;
}

.btn-circle:hover {
    border-color: #007BFF;
    background: #007BFF;
    color: white;
}

.chat-input input {
    flex: 1;
    height: 44px;
    border: 1px solid #e9ecef;
    border-radius: 22px;
    padding: 0 20px;
    font-size: 14px;
}

/* COMPACT SIDEBAR - 280px */
section[data-testid="stSidebar"] {
    width: 280px !important;
    background: linear-gradient(180deg, #007BFF 0%, #0056B3 100%);
    padding: 20px 20px 20px;
}

.sidebar-card {
    background: rgba(255,255,255,0.95);
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.sidebar-title {
    font-size: 16px;
    font-weight: 600;
    color: #007BFF;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #cce7ff;
    display: flex;
    align-items: center;
    gap: 8px;
}

.history-item {
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 13px;
    cursor: pointer;
    border-left: 3px solid #cce7ff;
}

.btn-sidebar {
    width: 100%;
    height: 40px;
    background: linear-gradient(135deg, #007BFF, #0056B3);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    margin-bottom: 8px;
    cursor: pointer;
}

.call-btn {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    border: none;
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 8px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(40,167,69,0.3);
}

.typing {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: white;
    border-radius: 20px 20px 20px 6px;
    border: 1px solid #e9ecef;
}

.dot-typing {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #007BFF;
    animation: bounce 1.4s infinite;
}

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}
</style>
""", unsafe_allow_html=True)

# ==================== COMPACT HEADER + SINGLE NAV ====================
st.markdown("""
<div class="header-main">
    <div class="logo">☀️ SUNBEAM AI</div>
</div>
""", unsafe_allow_html=True)

# ==================== TIGHT CONTENT ====================
st.markdown('<div class="content">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    # ==================== COMPACT CHAT ====================
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    st.markdown('<div class="messages">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.markdown('<div style="color: #6c757d; text-align: center; padding: 40px 0; font-size: 14px;">👋 Start chatting about PG programs...</div>', unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        msg_class = "message user" if msg["role"] == "user" else "message"
        st.markdown(f"""
        <div class="{msg_class}">
            <div class="bubble {'user' if msg['role'] == 'user' else 'bot'}">
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    chatcol1, chatcol2 = st.columns([3, 1])
    with chatcol1:
        prompt = st.chat_input("Ask about PGCP-AC, fees, admissions...")

    with chatcol2:
        st.markdown("""
        <div class="input-area">
            <div class="input-controls">
                <button class="btn-circle" title="Voice">🎤</button>
                <button class="btn-circle" title="File">📎</button>
            </div>
        """, unsafe_allow_html=True)
    
    
    
    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==================== COMPACT SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">🌐 Navigation</div>
        <div class="nav-item active" style="padding: 12px 16px; margin-bottom: 4px; font-size: 13px;">🏠 Home</div>
        <div class="nav-item" style="padding: 12px 16px; margin-bottom: 4px; font-size: 13px;">📚 Programs</div>
        <div class="nav-item" style="padding: 12px 16px; margin-bottom: 4px; font-size: 13px;">📅 Admissions</div>
        <div class="nav-item" style="padding: 12px 16px; margin-bottom: 4px; font-size: 13px;">👥 Placements</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">📜 History</div>
    """, unsafe_allow_html=True)
    
    if st.button("Clear", key="clear"):
        st.session_state.messages = []
        st.rerun()
    
    for msg in st.session_state.messages[-3:]:
        st.markdown(f'<div class="history-item">{msg["content"][:40]}...</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-card">
        <button class="btn-sidebar">↗️ Share chat</button>
        <button class="btn-sidebar">🆕 New Chat</button>
    </div>
    <div class="sidebar-card">
        <div class="sidebar-title">🌍 Select Language</div>
    """, unsafe_allow_html=True)
    
    st.selectbox("", ["English", "हिंदी", "मराठी"], key="lang")
    
    st.markdown("""
     </div>
    <div class="sidebar-card" style="text-align: center;">
        <div class="sidebar-title" style="justify-content: center;">📞 Call</div>
        <button class="call-btn">📱</button>
        <div style="color: #007BFF; font-weight: 600; font-size: 10px;">+91 7768960392</div>
    </div>
    """, unsafe_allow_html=True)

# ==================== CHAT LOGIC ====================
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()
    
    with st.empty():
        st.markdown("""
        <div class="message">
            <div class="bubble bot typing">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div class="dot-typing"></div>
                    <div class="dot-typing"></div>
                    <div class="dot-typing"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
    
    response = f"✅ **AI Response** for '{prompt}'"
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
