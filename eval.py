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
        top: 20px;
        right: 20px;
        z-index: 999;
        background: rgba(255, 255, 255, 0.9);
        padding: 8px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .nav-container button {
        margin-left: 10px;
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

# Database Functions
def check_teacher_login(email, password):
    try:
        db = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cur = db.cursor()
        cur.execute("SELECT * FROM teacher WHERE mail = %s AND password = %s", (email, password))
        return cur.fetchone() is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if 'cur' in locals(): cur.close()
        if 'db' in locals(): db.close()

def check_student_login(email, password):
    try:
        db = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE email = %s AND password = %s", (email, password))
        return cur.fetchone() is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if 'cur' in locals(): cur.close()
        if 'db' in locals(): db.close()

def register_student(name, email, password):
    try:
        db = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cur = db.cursor()
        cur.execute("INSERT INTO students (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, password))
        db.commit()
        return True
    except Exception as e:
        st.error(f"Registration error: {e}")
        return False
    finally:
        if 'cur' in locals(): cur.close()
        if 'db' in locals(): db.close()

# Main Application
def main():
    # Navigation Buttons
    st.markdown("""
    <div class="nav-container">
        <button onclick="window.location.href='#home'">🏠 Home</button>
        <button onclick="window.location.href='#login'">🔑 Login</button>
        <button onclick="window.location.href='#signup'">📝 Signup</button>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)  # Adjust the number of <br> tags as needed
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

        # Login Page
        elif st.session_state.active_tab == "Login":
            st.markdown("<h1>User Login</h1>", unsafe_allow_html=True)
            with st.form("login_form"):
                login_type = st.radio("Login as:", ["Teacher", "Student"], horizontal=True)
                email = st.text_input("Email:")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    if login_type == "Teacher":
                        if check_teacher_login(email, password):
                            st.session_state.logged_in = True
                            st.session_state.user_role = "teacher"
                            st.session_state.active_tab = "Home"
                            st.experimental_rerun()
                        else:
                            st.error("Invalid teacher credentials")
                    else:
                        if check_student_login(email, password):
                            st.session_state.logged_in = True
                            st.session_state.user_role = "student"
                            st.session_state.active_tab = "Home"
                            st.experimental_rerun()
                        else:
                            st.error("Invalid student credentials")

        # Signup Page
        elif st.session_state.active_tab == "Signup":
            st.markdown("<h1>Student Registration</h1>", unsafe_allow_html=True)
            with st.form("signup_form"):
                name = st.text_input("Full Name:")
                email = st.text_input("Email:")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Create Account")
                
                if submitted:
                    if register_student(name, email, password):
                        st.success("Registration successful! Please login.")
                        st.session_state.active_tab = "Login"
                        st.experimental_rerun()
                    else:
                        st.error("Registration failed. Please try again.")

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
