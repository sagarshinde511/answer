import streamlit as st
import mysql.connector
import re
import os

# Database configuration
host = "82.180.143.66"
user = "u263681140_students"
passwd = "testStudents@123"
db_name = "u263681140_students"

# -------------------- Helper Functions --------------------
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

def teacher_email_exists(mail):
    try:
        db = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cur = db.cursor()
        cur.execute("SELECT * FROM teacher WHERE mail = %s", (mail,))
        return cur.fetchone() is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if 'cur' in locals(): cur.close()
        if 'db' in locals(): db.close()

def student_exists(mail, enrolment):
    try:
        db = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE email = %s OR enrolment = %s", (mail, enrolment))
        return cur.fetchone() is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if 'cur' in locals(): cur.close()
        if 'db' in locals(): db.close()

def insert_teacher(name, mail, mobile, password, branch):
    try:
        if teacher_email_exists(mail):
            st.warning("Email already exists for another teacher!")
            return

        db = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cur = db.cursor()
        insert_query = '''INSERT INTO teacher (name, mail, mobile, password, branch) 
                          VALUES (%s, %s, %s, %s, %s)'''
        cur.execute(insert_query, (name, mail, mobile, password, branch))
        db.commit()
        st.success("Teacher registered successfully!")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'db' in locals(): db.close()

def insert_student(name, enrolment, mail, mobile, password, branch):
    try:
        if student_exists(mail, enrolment):
            st.warning("Email or enrolment number already exists!")
            return

        db = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cur = db.cursor()
        insert_query = '''INSERT INTO students (name, enrolment, email, mobile, password, branch) 
                          VALUES (%s, %s, %s, %s, %s, %s)'''
        cur.execute(insert_query, (name, enrolment, mail, mobile, password, branch))
        db.commit()
        st.success("Student registered successfully!")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'db' in locals(): db.close()

# -------------------- App Structure --------------------
st.set_page_config(page_title="Evaluation System", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

tab1, tab2, tab3 = st.tabs(["🏠 Home", "🔑 Login", "📝 Signup"])

with tab1:
    st.title("Subjective Answers Evaluation System")
    st.image("nlp2.jpg", use_column_width=True)
    st.markdown("""
    ## Welcome!
    - Teachers: Evaluate student answers
    - Students: View your results
    - New users: Register in Signup tab
    """)

with tab2:
    st.header("Login Portal")
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
                        st.error("Invalid Teacher credentials")
                else:
                    if check_student_login(email, password):
                        st.session_state.logged_in = True
                        st.session_state.user_role = "student"
                        st.success("Welcome, Student!")
                    else:
                        st.error("Invalid Student credentials")
    else:
        st.success(f"Logged in as {st.session_state.user_role.capitalize()}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.experimental_rerun()

with tab3:
    st.header("Registration Portal")
    reg_type = st.selectbox("Register as:", ["Teacher", "Student"])
    branches = [
        "Computer Science", "Mechanical Engineering",
        "Electrical Engineering", "Civil Engineering",
        "Electronics and Communication", "Information Technology",
        "Chemical Engineering", "Aerospace Engineering"
    ]
    
    with st.form("reg_form"):
        if reg_type == "Teacher":
            name = st.text_input("Full Name")
            mail = st.text_input("Email")
            mobile = st.text_input("Mobile")
            password = st.text_input("Password", type="password")
            branch = st.selectbox("Branch", branches)
            
            if st.form_submit_button("Register"):
                if all([name, mail, mobile, password]) and len(mobile) == 10 and mobile.isdigit():
                    insert_teacher(name, mail, mobile, password, branch)
                else:
                    st.warning("Please fill all fields correctly!")
        
        else:
            name = st.text_input("Full Name")
            enrol = st.text_input("Enrolment Number")
            mail = st.text_input("Email")
            mobile = st.text_input("Mobile")
            password = st.text_input("Password", type="password")
            branch = st.selectbox("Branch", branches)
            
            if st.form_submit_button("Register"):
                if all([name, enrol, mail, mobile, password]) and len(mobile) == 10 and mobile.isdigit():
                    insert_student(name, enrol, mail, mobile, password, branch)
                else:
                    st.warning("Please fill all fields correctly!")
