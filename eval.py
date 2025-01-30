import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF
import re

# Database configuration
host = "82.180.143.66"
user = "u263681140_students"
passwd = "testStudents@123"
db_name = "u263681140_students"
# Function to check admin credentials

# Function to connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host= "82.180.143.66",
        user="u263681140_students",
        password="testStudents@123",
        database="u263681140_students"
    )

# Function to fetch data from a table
def fetch_data(table_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        st.error(f"Database error: {e}")
        return []
def check_admin_login(email, password):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admin WHERE mail = %s AND password = %s",
            (email, password)
        )
        return cursor.fetchone() is not None
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
def adminLogin():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if st.session_state["page"] == "login":
        with st.form("admin_form"):
            st.subheader("🧑💼 Administrator Login")
            email = st.text_input("Admin Email")
            password = st.text_input("Admin Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if check_admin_login(email, password):
                    st.session_state.update({"page": "admin_dash", "role": "admin"})
                    st.success("Admin login successful!")
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")

    elif st.session_state["page"] == "admin_dash":
        st.title("Administrator Dashboard")

        # Horizontal radio buttons
        selected_option = st.radio(
            "Select Data to View:",
            ["Students", "Teachers","Check Marks"],
            horizontal=True,
            key="admin_view"
        )

        if selected_option == "Students":
            st.subheader("📚 Student Records")
            student_data = fetch_data("students")
            if student_data:
                df = pd.DataFrame(student_data)
                st.dataframe(df)
            else:
                st.warning("No student data found in the database.")

        elif selected_option == "Teachers":
            st.subheader("👩🏫 Teacher Records")
            teacher_data = fetch_data("teacher")
            if teacher_data:
                df = pd.DataFrame(teacher_data)
                st.dataframe(df)
            else:
                st.warning("No teacher data found in the database.")

        # Add logout button at bottom
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.session_state["page"] = "login"
            st.rerun()

def RegisterUser():
    branches = [
        "Computer Science", 
        "Mechanical Engineering", 
        "Electrical Engineering", 
        "Civil Engineering", 
        "Electronics and Communication", 
        "Information Technology",
        "Chemical Engineering", 
        "Aerospace Engineering"
    ]
    st.title("Registration Form")

    registration_type = st.selectbox("Select Registration Type", ["Teacher", "Student"])

    with st.form("registration_form"):
        if registration_type == "Teacher":
            name = st.text_input("Name")
            mail = st.text_input("Email")
            mobile = st.text_input("Mobile Number")
            password = st.text_input("Password", type="password")
            branch = st.selectbox("Branch", branches)  
            submitted = st.form_submit_button("Register")

            if submitted:
                if name and mail and mobile and password and branch:
                    if not is_valid_email(mail):
                        st.warning("Please enter a valid email address!")
                    elif not is_valid_mobile(mobile):
                        st.warning("Mobile number must be 10 digits!")
                    else:
                        insert_teacher(name, mail, mobile, password, branch)
                else:
                    st.warning("Please fill all the fields!")
        
        elif registration_type == "Student":
            name = st.text_input("Name")
            enrolment = st.text_input("Enrolment Number")
            mail = st.text_input("Email")
            mobile = st.text_input("Mobile Number")
            password = st.text_input("Password", type="password")
            branch = st.selectbox("Branch", branches) 
            submitted = st.form_submit_button("Register")

            if submitted:
                if name and enrolment and mail and mobile and password and branch:
                    if not is_valid_email(mail):
                        st.warning("Please enter a valid email address!")
                    elif not is_valid_mobile(mobile):
                        st.warning("Mobile number must be 10 digits!")
                    else:
                        insert_student(name, enrolment, mail, mobile, password, branch)
                else:
                    st.warning("Please fill all the fields!")

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_mobile(mobile):
    pattern = r'^\d{10}$'
    return re.match(pattern, mobile) is not None
def teacher_email_exists(mail):
    db, cur = None, None
    try:
        db = mysql.connector.connect(host=host, user=user, password=passwd, database=db_name)
        cur = db.cursor()
        cur.execute("SELECT * FROM teacher WHERE mail = %s", (mail,))
        return cur.fetchone() is not None
    finally:
        if cur:
            cur.close()
        if db:
            db.close()

def student_exists(mail, enrolment):
    db, cur = None, None
    try:
        db = mysql.connector.connect(host=host, user=user, password=passwd, database=db_name)
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE email = %s OR enrolment = %s", (mail, enrolment))
        return cur.fetchone() is not None
    finally:
        if cur:
            cur.close()
        if db:
            db.close()
def insert_teacher(name, mail, mobile, password, branch):
    db, cur = None, None
    try:
        if teacher_email_exists(mail):
            st.warning("Email already exists for another teacher!")
            return

        db = mysql.connector.connect(host=host, user=user, password=passwd, database=db_name)
        cur = db.cursor()

        insert_query = '''INSERT INTO teacher (name, mail, mobile, password, branch) 
                          VALUES (%s, %s, %s, %s, %s);'''
        cur.execute(insert_query, (name, mail, mobile, password, branch))
        db.commit()
        st.success("Teacher registered successfully!")

    except Exception as e:
        st.error(f"Error: {e}")

    finally:
        if cur:
            cur.close()
        if db:
            db.close()

def insert_student(name, enrolment, mail, mobile, password, branch):
    db, cur = None, None
    try:
        if student_exists(mail, enrolment):
            st.warning("Email or enrolment number already exists for another student!")
            return

        db = mysql.connector.connect(host=host, user=user, password=passwd, database=db_name)
        cur = db.cursor()

        insert_query = '''INSERT INTO students (name, enrolment, email, mobile, password, branch) 
                          VALUES (%s, %s, %s, %s, %s, %s);'''
        cur.execute(insert_query, (name, enrolment, mail, mobile, password, branch))
        db.commit()
        st.success("Student registered successfully!")

    except Exception as e:
        st.error(f"Error: {e}")

    finally:
        if cur:
            cur.close()
        if db:
            db.close()
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
def HomePage():
   #st.set_page_config(page_title="Automated Answer Evaluation System", page_icon="📊", layout="wide")

    # Background Image (adjust the path if necessary)
    # Set up page configuration
    #st.set_page_config(page_title="Automated Answer Evaluation System", page_icon="📊", layout="centered")

    # Background Image (adjust the path if necessary)
    background_image_url = "https://img.freepik.com/free-vector/abstract-blue-light-pipe-speed-zoom-black-background-technology_1142-9530.jpg?t=st=1738266296~exp=1738269896~hmac=5f29687d125f52e232bf6d7288aaa389fce4717d2ba4512c5467d82949fd2a5d&w=996"  # Update with your image URL
 
    # Simple HTML to add background image and style
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url({background_image_url});
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
        }}
        .header {{
            text-align: center;
            color: white;
            font-size: 40px;
            padding: 50px;
        }}
        .subtitle {{
            text-align: center;
            color: white;
            font-size: 20px;
            margin-bottom: 20px;
        }}
        .cta-button {{
            display: block;
            margin: 0 auto;
            padding: 15px 30px;
            background-color: #FF5722;
            color: white;
            font-size: 18px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
        .cta-button:hover {{
            background-color: #E64A19;
        }}
        .section {{
            margin-top: 30px;
            padding: 20px;
            text-align: center;
        }}
        .features {{
            display: flex;
            justify-content: space-around;
        }}
        .feature {{
            background-color: rgba(255, 255, 255, 0.7);
            padding: 20px;
            border-radius: 10px;
            width: 22%;
            text-align: center;
        }}
        </style>
        """, unsafe_allow_html=True
    )

    # Main Content
    st.markdown('<div class="header">Automated Answer Evaluation System</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Efficient, Automated Answer Evaluation at Your Fingertips</div>', unsafe_allow_html=True)

    # Call to Action button
    if st.button('Get Started', key='get_started', help='Start using the system now'):
        st.write("Redirecting to the system setup... (You can replace this with an actual link)")

    # Features Section
    st.markdown('<div class="section"><h3>Key Features</h3></div>', unsafe_allow_html=True)

    # Using simple flex layout to arrange features
    features = [
        ("⚡", "Instant Grading", "Automated, real-time evaluation of answers."),
        ("✏️", "Customizable Rubrics", "Define grading criteria tailored to your needs."),
        ("🧠", "AI-Powered", "Deep learning algorithms for precise evaluation."),
        ("💬", "Detailed Feedback", "Personalized feedback for each student.")
    ]

    st.markdown('<div class="features">', unsafe_allow_html=True)
    for icon, title, description in features:
        st.markdown(f"""
        <div class="feature">
            <div>{icon}</div>
            <div><b>{title}</b></div>
            <div>{description}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; font-size: 14px; color: white;">
            &copy; 2025 Automated Answer Evaluation System. All Rights Reserved.
        </div>
    """, unsafe_allow_html=True)

# -------------------- MAIN PAGE TABS --------------------
def login_page():
    st.title("📚 Automated Answer Evaluation System")
    tab1, tab2, tab3, tab4 = st.tabs(["Home","Login", "Signup", "Admin Login"])
    with tab1:
            HomePage()
    
    with tab2:
        col1, col2 = st.columns([2, 3])
        with col1:
            # Display the image
            st.markdown("<br><br><br>", unsafe_allow_html=True)
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

    with tab3:
        RegisterUser()
    with tab4:
        #st.header("Administrator Login")
        adminLogin()
# -------------------- APP FLOW CONTROL --------------------
if "page" not in st.session_state:
    st.session_state.update({
        "page": "login",
        "logged_in": False,
        "role": None
    })
if(__name__ == "__main__"):
    login_page()
