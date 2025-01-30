import streamlit as st
import mysql.connector

# Database Configuration
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "passwd": "testStudents@123",
    "database": "u263681140_students"
}

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
    max-width: 900px;
}
.stMarkdown h1 {
    color: #4f46e5 !important;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# Sidebar Navigation
st.sidebar.title("Navigation")
if st.sidebar.button("🏠 Home"):
    st.session_state.active_tab = "home"
if st.sidebar.button("🔑 Login"):
    st.session_state.active_tab = "login"
if st.sidebar.button("📝 Signup"):
    st.session_state.active_tab = "signup"
if st.session_state.logged_in and st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.active_tab = "home"
    st.rerun()

# Main Application
def main():
    tab = st.session_state.active_tab

    with st.container():
        st.markdown('<div class="landing-container">', unsafe_allow_html=True)

        # Home Page
        if tab == "home":
            st.markdown("<h1>Subjective Answers Evaluation System</h1>", unsafe_allow_html=True)
            st.markdown("---")

            if st.session_state.logged_in:
                st.success(f"Welcome back, {st.session_state.user_role}!")
                if st.session_state.user_role == "teacher":
                    st.write("📚 Teacher Dashboard")
                else:
                    st.write("📖 Student Dashboard")
            else:
                st.image("https://cdn.pixabay.com/photo/2018/06/27/07/45/college-student-3500990_1280.jpg", use_column_width=True)
                st.markdown("""
                ### Welcome to Smart Evaluation System  
                Revolutionize your answer evaluation process with **AI-powered assessment** and **comprehensive analytics** for both teachers and students.
                - ✅ Instant Answer Scoring  
                - ✅ Detailed Feedback  
                - ✅ Progress Tracking  
                - ✅ AI-Powered Insights  
                """)

        # Login Page
        elif tab == "login":
            st.markdown("<h1>🔑 Login</h1>", unsafe_allow_html=True)
            st.markdown("---")

            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    try:
                        conn = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT * FROM users WHERE username = %s AND password = %s",
                            (username, password)
                        )
                        user_data = cursor.fetchone()

                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.user_role = user_data[3]
                            st.session_state.active_tab = "home"
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")

                    except Exception as e:
                        st.error(f"Database error: {str(e)}")
                    finally:
                        cursor.close()
                        conn.close()

        # Signup Page
        elif tab == "signup":
            st.markdown("<h1>📝 Sign Up</h1>", unsafe_allow_html=True)
            st.markdown("---")

            with st.form("signup_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type="password")
                user_role = st.selectbox("Role", ["student", "teacher"])
                submit = st.form_submit_button("Create Account")

                if submit:
                    try:
                        conn = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                            (new_username, new_password, user_role)
                        )
                        conn.commit()
                        st.success("✅ Account created successfully! Please login.")
                        st.session_state.active_tab = "login"
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error creating account: {str(e)}")
                    finally:
                        cursor.close()
                        conn.close()

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
