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

def generate_pdf(results, total_marks_obtained, total_max_marks):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Student Evaluation Report", ln=True, align='C')
    pdf.ln(10)
    
    for index, row in results.iterrows():
        pdf.cell(200, 10, txt=f"Q{row['Question']}: {row['Marks_Obtained']} marks", ln=True)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Marks Obtained: {total_marks_obtained} / {total_max_marks}", ln=True)
    
    pdf_output = "evaluation_results.pdf"
    pdf.output(pdf_output)
    return pdf_output

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

def main():
    # Streamlit UI
    st.title("📊 Student Answer Evaluation System")
    
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
        
        # Option to download results as PDF
        if st.button("📥 Download Results (PDF)"):
            pdf_file = generate_pdf(results, total_marks_obtained, total_max_marks)
            with open(pdf_file, "rb") as f:
                st.download_button("📥 Download PDF", f, file_name="evaluation_results.pdf", mime="application/pdf")

st.title("Subjective Answers Evaluation Login Page")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<br>", unsafe_allow_html=True)  # Add a <br> tag before the image
    st.image("nlp2.jpg", use_container_width=True)

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
                        st.session_state.clear()  # Reset session state data (clear page)
                        st.success("Welcome, Teacher!")
                        main()  # Show teacher dashboard
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
