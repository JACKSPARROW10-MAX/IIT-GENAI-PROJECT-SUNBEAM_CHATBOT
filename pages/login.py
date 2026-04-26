import streamlit as st

st.set_page_config(
    page_title="Sunbeam Login",
    page_icon="🤖",
    layout="centered"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

VALID_USERNAME = "admin"
VALID_PASSWORD = "sejal143"
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

.login-box {
    max-width: 380px;
    margin: auto;
    padding: 30px;
    border-radius: 12px;
    background-color: #ffffff;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
}

button[kind="primary"] {
    background-color: #2c5364 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="login-box">', unsafe_allow_html=True)

st.title("Sunbeam Chatbot")
st.subheader("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login", use_container_width=True):
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        st.session_state.logged_in = True
        st.success("Login successful ")
        st.switch_page("main.py")

    else:
        st.error("Invalid username or password")

st.markdown("</div>", unsafe_allow_html=True)
