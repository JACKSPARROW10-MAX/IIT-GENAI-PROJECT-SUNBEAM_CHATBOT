import streamlit as st

st.set_page_config(
    page_title="Sunbeam Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Navigate based on login status
if st.session_state.logged_in:
    st.switch_page("pages/Sunbeam_Chatbot.py")
else:
    st.switch_page("pages/login.py")
