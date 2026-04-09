import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Set page config for a wider, cleaner layout
st.set_page_config(page_title="AI Interview Coach", page_icon="🤖", layout="centered")

st.title("🤖 AI Interview Coach")

# --- SIDEBAR: Settings ---
st.sidebar.header("Interview Settings")
role = st.sidebar.text_input("Role", "Data Scientist")
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

# Stop execution if API key is missing
if not API_KEY:
    st.error("⚠️ GOOGLE_API_KEY not found. Please ensure it is set in your .env file.")
    st.stop()

# --- HELPER FUNCTION ---
def ask_gemini(prompt):
    # Updated to the newer, actively supported model (Gemini 2.5 Flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status() # Catches HTTP errors (like 404 or 403)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# --- MAIN UI: Step 1 ---
st.markdown("### Step 1: Generate Questions")
user_topic = st.text_input("Enter a topic (e.g., Machine Learning, SQL, Python):")

if st.button("Generate Questions", type="primary"):
    if not user_topic.strip():
        st.warning("Please enter a topic first.")
    else:
        with st.spinner(f"Generating {difficulty} questions for {role}..."):
            prompt = f"Generate 3 {difficulty} level interview questions for a {role} role focusing on the topic: {user_topic}."
            res = ask_gemini(prompt)

            if "error" in res:
                st.error(f"API Error: {res['error']}")
            else:
                try:
                    text = res['candidates'][0]['content']['parts'][0]['text']
                    st.info(text)
                except KeyError:
                    st.error("Unexpected response from API.")
                    st.json(res)

st.divider()

# --- MAIN UI: Step 2 ---
st.markdown("### Step 2: Evaluate Your Answer")
question_to_answer = st.text_area("Paste the question you are answering:")
user_answer = st.text_area("Enter your answer here:", height=150)

if st.button("Evaluate Answer", type="primary"):
    if not question_to_answer.strip() or not user_answer.strip():
        st.warning("Please provide both the question and your answer.")
    else:
        with st.spinner("Evaluating your response..."):
            prompt = f"""
            Act as an expert interviewer. Evaluate this answer for a {role} position.
            
            Question: {question_to_answer}
            Candidate's Answer: {user_answer}
            
            Please provide:
            1. A score out of 10.
            2. Constructive feedback (what was good, what was missing).
            3. An example of a strong, complete answer.
            """
            
            res = ask_gemini(prompt)

            if "error" in res:
                st.error(f"API Error: {res['error']}")
            else:
                try:
                    text = res['candidates'][0]['content']['parts'][0]['text']
                    st.success(text)
                except KeyError:
                    st.error("Unexpected response from API.")
                    st.json(res)