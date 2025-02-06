import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF
import re
import fitz  # PyMuPDF for reading PDFs
import re
from rapidfuzz import fuzz

# Database configuration
host = "82.180.143.66"
user = "u263681140_students"
passwd = "testStudents@123"
db_name = "u263681140_students"
# Function to check admin credentials
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=passwd,
    database=db_name,
    #pool_name=None  # Disabling connection pooling
)
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
# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# Function to extract roll number
def extract_roll_number(text):
    match = re.search(r'Roll Number:\s*(\d+)', text)
    return match.group(1) if match else "Unknown"

# Function to extract questions and answers
def extract_questions_answers(pdf_text):
    lines = pdf_text.split("\n")
    questions, answers = [], []
    current_question, current_answer = None, ""

    for line in lines:
        line = line.strip()
        if line.startswith("Q "):
            if current_question:
                questions.append(current_question)
                answers.append(current_answer.strip())
            current_question = line
            current_answer = ""
        elif current_question:
            current_answer += " " + line

    if current_question:
        questions.append(current_question)
        answers.append(current_answer.strip())
    return questions, answers

# Function to extract question number
def extract_question_number(question):
    match = re.search(r'Q\s?\d+', question)
    if match:
        q_number = match.group(0).replace(" ", "")
        question_text = re.sub(r'Q\s?\d+', '', question).strip()
        return q_number, question_text
    return None, question

# Function to clean answers
def clean_answer_column(answer):
    return str(answer).replace('Answer: ', '').strip() if answer else ""

# Function to calculate similarity
def calculate_similarity(answer1, answer2):
    return fuzz.ratio(str(answer1), str(answer2)) if answer1 and answer2 else 0

# Function to assign marks
def assign_marks(similarity, total_marks):
    if similarity >= 90:
        return total_marks
    elif similarity >= 70:
        return total_marks * 0.75
    elif similarity >= 50:
        return total_marks * 0.50
    else:
        return 0

def evaluate_answers():
    
    st.title("📄 Automated Answer Sheet Grading")
    st.sidebar.header("📂 Upload Files")
    
    correct_answers_file = st.sidebar.file_uploader("📌 Upload Correct Answers (Excel)", type=["xlsx"])
    student_pdf = st.sidebar.file_uploader("📌 Upload Student Answer Sheet (PDF)", type=["pdf"])
    
    if correct_answers_file and student_pdf:
        try:
            # Load correct answers
            correct_answers = pd.read_excel(correct_answers_file)
            
            # Process student answers
            pdf_text = extract_text_from_pdf(student_pdf)
            questions, answers = extract_questions_answers(pdf_text)
            roll_number = extract_roll_number(pdf_text)
            
            student_answers = pd.DataFrame({'Question': questions, 'Answers': answers})
            student_answers[['No', 'Question']] = student_answers['Question'].apply(lambda x: pd.Series(extract_question_number(x)))
            student_answers['Answers'] = student_answers['Answers'].apply(clean_answer_column)
    
            # Ensure 'No' column exists in correct answers
            if 'No' not in correct_answers.columns:
                st.error("❌ The uploaded correct answers file is missing a 'No' column.")
            else:
                # Merge and compute similarity
                df_merged = pd.merge(student_answers, correct_answers, on='No', suffixes=('_student', '_correct'), how="inner")
    
                # Handle missing columns gracefully
                if "Answers_student" not in df_merged.columns:
                    df_merged.rename(columns={"Answers": "Answers_student"}, inplace=True)
    
                df_merged['Similarity (%)'] = df_merged.apply(
                    lambda row: calculate_similarity(row.get('Answers_student', ''), row.get('Answers_correct', '')),
                    axis=1
                )
                df_merged['Assigned Marks'] = df_merged.apply(
                    lambda row: assign_marks(row['Similarity (%)'], row['Marks']),
                    axis=1
                )
    
                # Compute total marks
                total_marks_obtained = df_merged['Assigned Marks'].sum()
                total_possible_marks = correct_answers['Marks'].sum()
    
                # Display results
                st.subheader(f"📌 Roll Number: {roll_number}")
                st.write(f"### ✅ Total Marks: {total_marks_obtained:.2f} / {total_possible_marks:.2f}")
    
                # Ensure only available columns are displayed
                columns_to_display = ['No', 'Question', 'Answers_student', 'Similarity (%)', 'Assigned Marks']
                available_columns = [col for col in columns_to_display if col in df_merged.columns]
                st.dataframe(df_merged[available_columns])
    
                # Save and download results
                output_file = "graded_answers.csv"
                df_merged.to_csv(output_file, index=False)
                st.download_button("⬇️ Download Results", data=open(output_file, "rb"), file_name="graded_answers.csv", mime="text/csv")
        
        except Exception as e:
            st.error(f"🚨 Error processing files: {e}")
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
    evaluate_answers()    
    if st.button("🔴 Logout"):
        st.session_state.update({"page": "login", "logged_in": False})
        st.rerun()
    

def fetch_student_info(email):

    """Fetch student information from database using email"""
    conn = None
    cursor = None
    try:
        # Use existing database configuration
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT name, enrolment, email, mobile, branch FROM students WHERE email = %s", 
            (email,)
        )
        return cursor.fetchone()
    except Exception as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
def adminDashboard():
    #st.title("👑 Administrator Dashboard")

    # Horizontal radio buttons for navigation
    selected_option = st.radio(
        "Select Data to View:",
        ["Result Details", "Teacher Details", "Student Details"],
        horizontal=True,
        key="admin_view"
    )

    if selected_option == "Result Details":
        st.subheader("📊 Result Records")
        result_data =0
        #result_data = fetch_data("results")  # Assuming you have a 'results' table
        if result_data:
            df = pd.DataFrame(result_data)
            st.dataframe(df)
        else:
            st.warning("No result data found in the database.")

    elif selected_option == "Teacher Details":
        st.subheader("👩🏫 Teacher Records")
        teacher_data = fetch_data("teacher")
        if teacher_data:
            df = pd.DataFrame(teacher_data)
            st.dataframe(df)
        else:
            st.warning("No teacher data found in the database.")

    elif selected_option == "Student Details":
        st.subheader("📚 Student Records")
        student_data = fetch_data("students")
        if student_data:
            df = pd.DataFrame(student_data)
            st.dataframe(df)
        else:
            st.warning("No student data found in the database.")

def admin_dashboard():
    st.title("👑 Admin Dashboard")
    adminDashboard()
    if st.button("🔴 Logout"):
        st.session_state.update({"page": "login", "logged_in": False})
        st.rerun()

    #st.write("Admin functionality for answer evaluation")
def HomePage():
    st.image("background.jpg", use_container_width=True, caption="Automated Answer Evaluation System")
    background_image_url = "https://www.freepik.com/free-vector/abstract-blue-circle-black-background-technology_34386132.htm#fromView=keyword&page=1&position=12&uuid=dc1355a0-023d-44c3-987d-ba1e0a8270b6&new_detail=true&query=Dark+Website+Background"  # Update with your image URL
 
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
                global global_var
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
                    elif login_type == "Student":
                        if check_student_login(email, password):
                            st.session_state["email"] = email 
                            st.session_state.update({"page": "student_dash", "role": "student"})
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
    #login_page()
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "teacher_dash":
        teacher_dashboard()
    elif st.session_state.get("page") == "student_dash":
        st.header("Student Dashboard")
        email = st.session_state.get("email")
        #st.write("Well Come:", email)
        student_info = fetch_student_info(email)
        if student_info:
            st.subheader("Student Dashboard")
            
            # Create radio buttons for navigation
            selected_tab = st.radio("Select View", ["Profile", "Marks"], horizontal=True)
            
            if selected_tab == "Profile":
                # Convert student info to DataFrame and display in table format
                profile_df = pd.DataFrame([{
                    "Name": student_info['name'],
                    "Enrolment": student_info['enrolment'],
                    "Email": student_info['email'],
                    "Mobile": student_info['mobile'],
                    "Branch": student_info['branch']
                }])
                
                st.write("### Student Profile")
                st.dataframe(profile_df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Name": "Student Name",
                                "Enrolment": "Enrollment Number"
                            })
                
            else:
                st.write("### Marks Information")
                st.info("Marks details will be displayed here once available")
            if st.button("🔴 Logout"):
                st.session_state.update({"page": "login", "logged_in": False})
                st.rerun()

        else:
            st.error("Student information not found")
    elif st.session_state.page == "admin_dash":
        admin_dashboard()
