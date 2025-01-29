import streamlit as st
import mysql.connector
from streamlit_option_menu import option_menu

# Custom CSS for multicolor design
st.markdown("""
<style>
    [data-testid=stAppViewContainer] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
    }
    
    .landing-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 2rem auto;
        max-width: 1200px;
    }
    
    .nav-tabs {
        position: absolute;
        top: 20px;
        right: 20px;
    }
    
    .stButton button {
        background: linear-gradient(45deg, #4f46e5, #9333ea);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        margin: 0 0.5rem;
    }
    
    .stButton button:hover {
        opacity: 0.9;
        color: white;
    }
</style>
""", unsafe_allow_html=True)
def check_teacher_login(email, password):
    try:
        db = mysql.connector.connect(host=host, user=user, password=passwd, database=db_name)
        cur = db.cursor()
        cur.execute("SELECT * FROM teacher WHERE mail = %s AND password = %s", (email, password))
        return cur.fetchone() is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        cur.close()
        db.close()

def check_student_login(email, password):
    try:
        db = mysql.connector.connect(host=host, user=user, password=passwd, database=db_name)
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE email = %s AND password = %s", (email, password))
        return cur.fetchone() is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        cur.close()
        db.close()

st.title("Subjective Answers Evaluation Login Page")

def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Home"

    # Navigation tabs
    with st.container():
        cols = st.columns([4, 1, 1, 1])
        with cols[1]:
            if st.button("🏠 Home"):
                st.session_state.active_tab = "Home"
        with cols[2]:
            if st.button("🔑 Login"):
                st.session_state.active_tab = "Login"
        with cols[3]:
            if st.button("📝 Signup"):
                st.session_state.active_tab = "Signup"

    # Main content container
    with st.container():
        st.markdown('<div class="landing-container">', unsafe_allow_html=True)
        
        if st.session_state.active_tab == "Home":
            st.markdown("<h1 style='color: #4f46e5; text-align: center;'>Subjective Answers Evaluation</h1>", 
                       unsafe_allow_html=True)
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.image("https://cdn.pixabay.com/photo/2018/06/27/07/45/college-student-3500990_1280.jpg", 
                        use_column_width=True)
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

        elif st.session_state.active_tab == "Login":
            st.markdown("<h2 style='color: #4f46e5; text-align: center;'>User Login</h2>", 
                       unsafe_allow_html=True)
            with st.form("login_form"):
                login_type = st.radio("Login as:", ["Teacher", "Student"], horizontal=True)
                email = st.text_input("Email:")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    # Add your login logic here
                    st.success("Login logic would go here")

        elif st.session_state.active_tab == "Signup":
            st.markdown("<h2 style='color: #4f46e5; text-align: center;'>Create Account</h2>", 
                       unsafe_allow_html=True)
            with st.form("signup_form"):
                name = st.text_input("Full Name:")
                email = st.text_input("Email:")
                password = st.text_input("Password", type="password")
                user_type = st.selectbox("Account Type:", ["Student", "Teacher"])
                submitted = st.form_submit_button("Create Account")
                
                if submitted:
                    # Add your signup logic here
                    st.success("Signup logic would go here")

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
