import streamlit as st
import mysql.connector

# Database Configuration
host = "82.180.143.66"
user = "u263681140_students"
passwd = "testStudents@123"
db_name = "u263681140_students"

# Custom CSS Styling
st.markdown("""
<style>
[data-testid=stAppViewContainer] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
    min-height: 100vh;
}
.landing-container {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    margin: 2rem auto;
    max-width: 1200px;
}
.nav-container {
    position: fixed;
    top: 60px;
    right: 10px;
    z-index: 999;
    background: transparent !important;
    padding: 8px;
    border-radius: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    max-width: 500px;
}
.nav-container button {
    border: none;
    background: linear-gradient(45deg, #4f46e5, #9333ea);
    color: white !important;
    border-radius: 5px;
    padding: 8px 16px;
    transition: all 0.3s ease;
}
.nav-container button:hover {
    opacity: 0.9;
    transform: scale(1.05);
}
.stMarkdown h1 {
    color: #4f46e5 !important;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Navigation Buttons with JavaScript handling
st.markdown("""
st.sidebar.button("🏠 Home", on_click=lambda: setattr(st.session_state, "active_tab", "home"))
st.sidebar.button("🔑 Login", on_click=lambda: setattr(st.session_state, "active_tab", "login"))
st.sidebar.button("📝 Signup", on_click=lambda: setattr(st.session_state, "active_tab", "signup"))
""", unsafe_allow_html=True)

# Main Application
def main():
    # Initialize session state variables
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "home"

    # Navigation Logic
    tab = st.session_state.active_tab

    # Main Content
    with st.container():
        st.markdown('<div class="landing-container">', unsafe_allow_html=True)

        if tab == "home":
            st.markdown("<h1>Subjective Answers Evaluation System</h1>", unsafe_allow_html=True)

        elif tab == "login":
            st.markdown("<h1>Login</h1>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    # Database login validation here...
                    st.session_state.logged_in = True
                    st.session_state.active_tab = "home"  # Redirect to home
                    st.rerun()  # Force a refresh to reflect login state

        elif tab == "signup":
            st.markdown("<h1>Sign Up</h1>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
