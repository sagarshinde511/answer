import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF

# Database configuration
host = "82.180.143.66"
user = "u263681140_students"
passwd = "testStudents@123"
db_name = "u263681140_students"

# -------------------- HELPER FUNCTIONS --------------------
def evaluate_answers(correct_answers, student_answers):
    vectorizer = TfidfVectorizer()
    marks_obtained = []
    
    for index, row in student_answers.iterrows():
        question_id = row['Question']
        student_answer = row['Answers']

        correct_answer_row = correct_answers[correct_answers['Question'] == question_id]
        if correct_answer_row.empty:
            marks_obtained.append(0)
            continue
        
        correct_answer = correct_answer_row['Answer'].values[0]
        max_marks = correct_answer_row['Marks'].values[0]
        
        combined_text = [correct_answer, student_answer]
        vectors = vectorizer.fit_transform(combined_text)
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        if similarity > 0.9:
            assigned_marks = max_marks
        elif similarity > 0.75:
            assigned_marks = max_marks * 0.9
        elif similarity > 0.5:
            assigned_marks = max_marks * 0.75
        elif similarity > 0.3:
            assigned_marks = max_marks * 0.5
        else:
            assigned_marks = max_marks * similarity

        marks_obtained.append(int(np.ceil(assigned_marks)))
    
    student_answers['Marks_Obtained'] = marks_obtained
    return student_answers

# -------------------- AUTHENTICATION FUNCTIONS --------------------
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
        if 'db' in locals(): db.close()

def check_admin_login(email, password):
    try:
        db = mysql.connector.connect(host=host, user=user, password=passwd, database=db_name)
        cur = db.cursor()
        cur.execute("SELECT * FROM admin WHERE mail = %s AND password = %s", (email, password))
        return cur.fetchone() is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if 'db' in locals(): db.close()

def signup_user(name, email, password, role):
    try:
        db = mysql.connector.connect(host=host, user=user, password=passwd, database=db_name)
        cur = db.cursor()
        table = "teacher" if role == "Teacher" else "student"
        
        # Check existing user
        cur.execute(f"SELECT * FROM {table} WHERE mail = %s", (email,))
        if cur.fetchone():
            return False
            
        # Insert new user
        cur.execute(f"INSERT INTO {table} (name, mail, password) VALUES (%s, %s, %s)", 
                   (name, email, password))
        db.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False
    finally:
        if 'db' in locals(): db.close()

# -------------------- DASHBOARDS --------------------
def teacher_dashboard():
    st.title("📊 Teacher Dashboard")
    if st.button("🔴 Logout"):
        st.session_state.update({"page": "login", "logged_in": False})
        st.rerun()

    correct_file = st.file_uploader("Upload Correct Answers CSV", type=["csv"])
    student_file = st.file_uploader("Upload Student Answers CSV", type=["csv"])
    
    if correct_file and student_file:
        correct_answers = pd.read_csv(correct_file)
        student_answers = pd.read_csv(student_file)
        
        results = evaluate_answers(correct_answers, student_answers)
        total_marks = results['Marks_Obtained'].sum()
        max_marks = correct_answers['Marks'].sum()
        
        st.subheader("Evaluation Results")
        st.dataframe(results[['Question', 'Answers', 'Marks_Obtained']])
        st.markdown(f"**Total Marks: {total_marks}/{max_marks}**")
        
        csv = results.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results", csv, "results.csv", "text/csv")

def admin_dashboard():
    st.title("👑 Admin Dashboard")
    if st.button("🔴 Logout"):
        st.session_state.update({"page": "login", "logged_in": False})
        st.rerun()

    st.write("Admin functionality for answer evaluation")
    # Add admin-specific features here

# -------------------- MAIN PAGE TABS --------------------
def login_page():
    st.title("📚 Automated Answer Evaluation System")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Signup", "Admin Login"])
    
    with tab1:
        col1, col2 = st.columns([2, 3])
        
        with col1:
            # Display the image
            st.image("nlp2.jpg", use_container_width=True, caption="Automated Answer Evaluation System")
        
        with col2:
            st.header("User Login")
            login_type = st.selectbox("Select Role", ["Teacher", "Student"], key="login_role")
            
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if login_type == "Teacher":
                        if check_teacher_login(email, password):
                            st.session_state.update({"page": "teacher_dash", "role": "teacher"})
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    else:
                        st.warning("Student login not implemented yet")

    with tab2:
        st.header("New User Signup")
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Select Role", ["Teacher", "Student"])
            submit = st.form_submit_button("Create Account")
            
            if submit:
                if signup_user(name, email, password, role):
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Error creating account or email already exists")

    with tab3:
        st.header("Administrator Login")
        with st.form("admin_form"):
            email = st.text_input("Admin Email")
            password = st.text_input("Admin Password", type="password")
            submit = st.form_submit_button("Admin Login")
            
            if submit:
                if check_admin_login(email, password):
                    st.session_state.update({"page": "admin_dash", "role": "admin"})
                    st.success("Admin login successful!")
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")

# -------------------- APP FLOW CONTROL --------------------
if "page" not in st.session_state:
    st.session_state.update({
        "page": "login",
        "logged_in": False,
        "role": None
    })

if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "teacher_dash":
    teacher_dashboard()
elif st.session_state.page == "admin_dash":
    admin_dashboard()
