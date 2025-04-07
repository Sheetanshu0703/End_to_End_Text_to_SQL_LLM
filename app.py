import streamlit as st
from dotenv import load_dotenv
import os
import sqlite3
import google.generativeai as genai
import pandas as pd
from sql import init_db  # Make sure this function exists and creates a default database

# === Page Configuration ===
st.set_page_config(
    page_title="SQL Query Generator using Gemini",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="auto"
)

# === Load Environment Variables ===
load_dotenv()

# === Configure Gemini API ===
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === Sidebar File Uploader ===
st.sidebar.markdown("### 📂 Upload Student.db")
uploaded_file = st.sidebar.file_uploader("Upload your Student.db file", type=["db"])

# === Save uploaded database or create default ===
db_path = "student.db"
if uploaded_file is not None:
    with open("uploaded_student.db", "wb") as f:
        f.write(uploaded_file.read())
    db_path = "uploaded_student.db"
    st.sidebar.success("✅ Database uploaded successfully!")
else:
    init_db()

# === Gemini Query Function ===
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        full_prompt = f"{prompt[0]}\n\nQuestion: {question}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return None

# === SQL Execution Function ===
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        conn.commit()
        conn.close()
        return rows, columns
    except Exception as e:
        st.error(f"SQL Error: {str(e)}")
        return [], []

# === Prompt Template ===
prompt = ["""
You are an expert in converting English questions into SQL queries.

The SQL database has the table named STUDENT with the following columns:
- ID (Integer)
- NAME (Text)
- AGE (Integer)
- GENDER (Text)
- CLASS (Text)
- SECTION (Text)
- ROLL_NO (Text)
- MARKS (Integer)
- EMAIL (Text)
- PHONE (Text)
- ADDRESS (Text)
- ADMISSION_DATE (Date)
- ATTENDANCE_PCT (Float)
- SCHOLARSHIP (Boolean)

Generate precise SQL queries for the following kinds of questions:

Example 1 -  How many students are enrolled in the database?  
=> SELECT COUNT(*) FROM STUDENT;

Example 2 - Show all students in the 'Data Science' class.  
=> SELECT * FROM STUDENT WHERE CLASS = 'Data Science';

Example 3 -  List all students with marks above 85.  
=> SELECT * FROM STUDENT WHERE MARKS > 85;

Example 4 -  Show the names and emails of female students in section B.  
=> SELECT NAME, EMAIL FROM STUDENT WHERE GENDER = 'Female' AND SECTION = 'B';

Example 5 -  Who are the scholarship holders in the AI & ML class?  
=> SELECT NAME FROM STUDENT WHERE CLASS = 'AI & ML' AND SCHOLARSHIP = TRUE;

Example 6 -  List students with attendance below 75%.  
=> SELECT * FROM STUDENT WHERE ATTENDANCE_PCT < 75;

Example 7 -  Get all students admitted after 1st Jan 2022.  
=> SELECT * FROM STUDENT WHERE ADMISSION_DATE > '2022-01-01';

Example 8 -  Find students aged between 20 and 22.  
=> SELECT * FROM STUDENT WHERE AGE BETWEEN 20 AND 22;

Example 9 -  List students whose name starts with 'A'.  
=> SELECT * FROM STUDENT WHERE NAME LIKE 'A%';

Example 10 - Show the top 5 students with the highest marks.  
=> SELECT * FROM STUDENT ORDER BY MARKS DESC LIMIT 5;

Example 11 - Count how many students are in each class.  
=> SELECT CLASS, COUNT(*) FROM STUDENT GROUP BY CLASS;

Example 12 - Find students from 'Delhi' who scored above 90.  
=> SELECT * FROM STUDENT WHERE ADDRESS = 'Delhi' AND MARKS > 90;

Note:  
- Only return the raw SQL query.  
- Do not include backticks (
) or the word "sql" in the response.  
- Keep the query clean, concise, and syntactically correct.
"""]

# === UI ===
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>🔍 Gemini SQL Query Assistant</h1>
    <p style='text-align: center; font-size: 18px;'>Ask any question in plain English and get the corresponding SQL query + results.</p>
""", unsafe_allow_html=True)

st.markdown("### 📝 Enter your question in English")
question = st.text_input("Example: How many students scored above 85?", key="input")

if st.button("🚀 Generate SQL & Run"):
    if question.strip() == "":
        st.warning("Please enter a question to generate SQL.")
    else:
        with st.spinner("Generating SQL query using Gemini..."):
            response = get_gemini_response(question, prompt)

        if response:
            st.success("✅ SQL query generated successfully!")

            st.markdown("### 📄 Generated SQL Query")
            st.code(response, language="sql")

            rows, columns = read_sql_query(response, db_path)

            st.markdown("### 📊 Query Results")
            if rows:
                df = pd.DataFrame(rows, columns=columns)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No results found for the given query.")

            # === Download Section ===
            st.markdown("### 📥 Download Options")
            download_format = st.selectbox("Choose file format:", ["SQLite (.sqlite)", "Raw DB (.db)", "CSV (.csv)"])

            if download_format == "CSV (.csv)":
                try:
                    conn = sqlite3.connect(db_path)
                    df_all = pd.read_sql_query("SELECT * FROM STUDENT", conn)
                    conn.close()

                    csv_data = df_all.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV of STUDENT Table",
                        data=csv_data,
                        file_name="student_data.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"❌ Error generating CSV: {e}")
            else:
                extension = "sqlite" if download_format == "SQLite (.sqlite)" else "db"
                filename = f"student.{extension}"
                with open(db_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Download Database as {extension}",
                        data=f,
                        file_name=filename,
                        mime="application/octet-stream"
                    )
        else:
            st.error("❌ Failed to generate SQL. Please try again.")
