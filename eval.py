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
<div class="nav-container">
    <button onclick="window.location.href='?tab=home'">🏠 Home</button>
    <button onclick="window.location.href='?tab=login'">🔑 Login</button>
    <button onclick="window.location.href='?tab=signup'">📝 Signup</button>
</div>
""", unsafe_allow_html=True)

# Main Application
def main():
    # Handle query parameters
    params = st.query_params()
    initial_tab = params.get("tab", ["home"])[0]
    
    # Session State Management
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = initial_tab
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

    # Update tab from query parameters
    if params.get("tab"):
        st.session_state.active_tab = params["tab"][0]

    # Main Content Container
    with st.container():
        st.markdown('<div class="landing-container">', unsafe_allow_html=True)
        
        # Home Page
        if st.session_state.active_tab == "home":
            st.markdown("<h1>Subjective Answers Evaluation System</h1>", unsafe_allow_html=True)
            st.markdown("---")
            
            if st.session_state.logged_in:
                st.success(f"Welcome back, {st.session_state.user_role}!")
                if st.session_state.user_role == "teacher":
                    st.write("Teacher Dashboard Content")
                else:
                    st.write("Student Dashboard Content")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.image("https://cdn.pixabay.com/photo/2018/06/27/07/45/college-student-3500990_1280.jpg", 
                            use_container_width=True)
                with col2:
                    st.markdown("""
                    <div style='padding: 2rem;'>
                        <h3 style='color: #9333ea;'>Welcome to Smart Evaluation System</h3>
                        <p style='font-size: 16px;'>
                            Revolutionize your answer evaluation process with AI-powered assessment 
                            and comprehensive analytics for both teachers and students.
                        </p>
                        <ul style='color: #4f46e5;'>
                            <li>Instant Answer Scoring</li>
                            <li>Detailed Feedback</li>
                            <li>Progress Tracking</li>
                            <li>AI-Powered Insights</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Login Page
        elif st.session_state.active_tab == "login":
            st.markdown("<h1>Login</h1>", unsafe_allow_html=True)
            st.markdown("---")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    try:
                        conn = mysql.connector.connect(
                            host=host,
                            user=user,
                            passwd=passwd,
                            database=db_name
                        )
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT * FROM users WHERE username = %s AND password = %s",
                            (username, password)
                        )
                        user_data = cursor.fetchone()
                        
                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.user_role = user_data[3]  # Assuming role is in 4th column
                            st.experimental_set_query_params(tab="home")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    
                    except Exception as e:
                        st.error(f"Database error: {str(e)}")
        
        # Signup Page
        elif st.session_state.active_tab == "signup":
            st.markdown("<h1>Sign Up</h1>", unsafe_allow_html=True)
            st.markdown("---")
            
            with st.form("signup_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type="password")
                user_role = st.selectbox("Role", ["student", "teacher"])
                submit = st.form_submit_button("Create Account")
                
                if submit:
                    try:
                        conn = mysql.connector.connect(
                            host=host,
                            user=user,
                            passwd=passwd,
                            database=db_name
                        )
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                            (new_username, new_password, user_role)
                        )
                        conn.commit()
                        st.success("Account created successfully! Please login.")
                        st.experimental_set_query_params(tab="login")
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error creating account: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
