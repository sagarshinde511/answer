import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF

host = "82.180.143.66"
user = "u263681140_students"
passwd = "testStudents@123"
db_name = "u263681140_students"

def evaluate_answers(correct_answers, student_answers):
            # Logout button

    vectorizer = TfidfVectorizer()
    marks_obtained = []
    
    for index, row in student_answers.iterrows():
        question_id = row['Question']  # Extract the question ID
        student_answer = row['Answers']  # Extract the student's answer

        # Find the correct answer for this question
        correct_answer_row = correct_answers[correct_answers['Question'] == question_id]
        if correct_answer_row.empty:
            marks_obtained.append(0)  # Assign 0 if no correct answer is found
            continue
        
        correct_answer = correct_answer_row['Answer'].values[0]  # Get correct answer text
        max_marks = correct_answer_row['Marks'].values[0]  # Get full marks for this question
        
        # Combine correct and student answer for vectorization
        combined_text = [correct_answer, student_answer]
        
        # Convert both answers into vector form
        vectors = vectorizer.fit_transform(combined_text)
        
        # Compute cosine similarity (ranges from 0 to 1)
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        # Assign marks based on similarity
        if similarity > 0.9:
            assigned_marks = max_marks
        elif similarity > 0.75:
            assigned_marks = max_marks * 0.9
        elif similarity > 0.5:
            assigned_marks = max_marks * 0.75
        elif similarity > 0.3:
            assigned_marks = max_marks * 0.5
        else:
            assigned_marks = max_marks * similarity  # Proportional marks

        marks_obtained.append(int(np.ceil(assigned_marks)))  # Round up
    
    # Add marks to student answers DataFrame
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
        cur.close()
        db.close()

def teacher_dashboard():
    if st.button("🔴 Logout"):
        st.session_state.page = "login"
        st.session_state.logged_in = False
        st.rerun()  # Reload the page

    """Displays the teacher's evaluation dashboard after login."""
    st.title("📊 Teacher Dashboard - Student Answer Evaluation")

    # File uploaders
    correct_file = st.file_uploader("Upload Correct Answers CSV", type=["csv"])
    student_file = st.file_uploader("Upload Student Answers CSV", type=["csv"])
    
    if correct_file and student_file:
        correct_answers = pd.read_csv(correct_file)
        student_answers = pd.read_csv(student_file)
        
        # Process evaluation
        results = evaluate_answers(correct_answers, student_answers)
        total_marks_obtained = results['Marks_Obtained'].sum()
        total_max_marks = correct_answers['Marks'].sum()
        
        # Display results
        st.subheader("🔹 Student Results:")
        st.dataframe(results[['Question', 'Answers', 'Marks_Obtained']])
        
        st.markdown(f"**🎯 Total Marks Obtained: {total_marks_obtained} / {total_max_marks}**")
        
        # Option to download results as CSV
        csv = results.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results (CSV)", data=csv, file_name="evaluated_results.csv", mime="text/csv")
        
        # Logout button
        if st.button("🔴 Logout"):
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.rerun()  # Reload the page

def login_page():
    st.title("🔑 Subjective Answers Evaluation Login Page")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("nlp2.jpg", use_container_width=True)

    with col2:
        st.markdown("<h2 style='font-size: 30px;'>Login System</h2>", unsafe_allow_html=True)

        login_type = st.selectbox("Login as:", ["Teacher", "Student"])

        with st.form("login_form"):
            email = st.text_input("Email:")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if login_type == "Teacher":
                    if check_teacher_login(email, password):
                        st.session_state.page = "dashboard"
                        st.session_state.logged_in = True
                        st.success("✅ Login successful! Redirecting to dashboard...")
                        st.rerun()  # Refresh the page
                    else:
                        st.error("❌ Incorrect email or password for Teacher. Please try again.")
                else:
                    st.error("🚫 Only teacher login is implemented for now.")

# -------------------- MAIN APP LOGIC --------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "dashboard":
    teacher_dashboard()
