from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai
import pandas as pd
from sql import init_db

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === Streamlit File Uploader ===
st.sidebar.markdown("### 📂 Upload Student.db")
uploaded_file = st.sidebar.file_uploader("Upload your Student.db file", type=["db"])

# Save uploaded database to a temporary path
db_path = "student.db"  # Default path
if uploaded_file is not None:
    with open("uploaded_student.db", "wb") as f:
        f.write(uploaded_file.read())
    db_path = "uploaded_student.db"
    st.sidebar.success("✅ Database uploaded successfully!")
else:
    init_db()  # Only create fresh DB if no file is uploaded

# Function to get Gemini response
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        full_prompt = f"{prompt[0]}\n\nQuestion: {question}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return None

# Function to execute SQL query
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"SQL Error: {str(e)}")
        return []

# Prompt template (unchanged)
prompt = ["""Your original prompt here..."""]  # Keep your original Gemini prompt

# === Streamlit UI ===

st.set_page_config(
    page_title="SQL Query Generator using Gemini",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="auto"
)

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
            st.success("SQL query generated successfully!")

            st.markdown("### 📄 Generated SQL Query")
            st.code(response, language="sql")

            try:
                rows = read_sql_query(response, db_path)

                st.markdown("### 📊 Query Results")
                if rows:
                    df = pd.DataFrame(rows)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No results found for the given query.")
            except Exception as e:
                st.error(f"❌ Error executing SQL query:\n{e}")

            # 📥 Download current DB
            with open(db_path, "rb") as f:
                st.download_button(
                    label="📥 Download Current Database",
                    data=f,
                    file_name=os.path.basename(db_path),
                    mime="application/octet-stream"
                )
        else:
            st.error("Failed to generate SQL. Please try again.")
