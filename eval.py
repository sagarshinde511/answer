import streamlit as st
import mysql.connector
import os

host = "82.180.143.66"
user = "u263681140_students"
passwd = "testStudents@123"
db_name = "u263681140_students"

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

col1, col2 = st.columns(2)

with col1:
    st.image("nlp2.jpg", use_column_width=True)  

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

with col2:
    st.markdown("<h2 style='font-size: 30px;'>Login System</h2>", unsafe_allow_html=True)

    if not st.session_state.logged_in:
        login_type = st.selectbox("Login as:", ["Teacher", "Student"])

        with st.form("login_form"):
            email = st.text_input("Email:")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if login_type == "Teacher":
                    if check_teacher_login(email, password):
                        st.session_state.logged_in = True
                        st.session_state.user_role = "teacher"
                        st.success("Welcome, Teacher!")
                        #os.system("streamlit run C:\\Users\\DELL\\Desktop\\AI\\pdfEval.py")
                    else:
                        st.error("Incorrect email or password for Teacher. Please try again.")
                elif login_type == "Student":
                    if check_student_login(email, password):
                        st.session_state.logged_in = True
                        st.session_state.user_role = "student"
                        st.success("Welcome, Student!")
                    else:
                        st.error("Incorrect email or password for Student. Please try again.")
    else:
        st.success(f"Already logged in as {st.session_state.user_role}")
