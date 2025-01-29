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
[data-testid=stAppViewContainer] {{
        background-image: url("background.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }}
    
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
        box-shadow: None
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        max-width: 500px;  /* Added max-width for wrapping */
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

# Navigation Buttons
st.markdown("""
<div class="nav-container">
    <button onclick="window.location.href='#home'">🏠 Home</button>
    <button onclick="window.location.href='#login'">🔑 Login</button>
    <button onclick="window.location.href='#signup'">📝 Signup</button>
</div>
""", unsafe_allow_html=True)

# Main Application
def main():
    # Session State Management
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Home"

    # Main Content Container
    with st.container():
        st.markdown('<div class="landing-container">', unsafe_allow_html=True)
        
        # Home Page
        if st.session_state.active_tab == "Home":
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
                    st.markdown("<br><br>", unsafe_allow_html=True)  # Adjust the number of <br> tags as needed
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
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
