# %%
import os 
import openai 
from openai import OpenAI
import random
import streamlit as st
import requests
from dotenv import load_dotenv

# %%
st.sidebar.title("InterviewIQ  🧠")
st.sidebar.markdown("---")
st.sidebar.write("Developed to help you land your dream job.")


# %%
st.success("Welcome to InterviewIQ; Congrats on reaching the interview stage!", icon="✅")

# %%
# 1. SIDEBAR KEY INPUT 

# %%
st.title("Settings")
user_key = st.text_input("Enter your OpenAI API Key", type="password")
st.info("Don't have one? Get it at platform.openai.com")



# %%
# Update your client initialization
if user_key:
    client = OpenAI(api_key=user_key)
else:
    st.warning("Please enter an API key in the sidebar to start.")
    st.stop() # This prevents the rest of the app from running


# %%
load_dotenv(override=True)

# %%
openai_api_key = os.getenv("openai_api_key")

# %%
openai_api_key = os.getenv("openai_api_key")

# %%
client =OpenAI(
    base_url="https://openrouter.ai/api/v1",
     api_key=openai_api_key,
    
)

# %%
# 1. SETUP: Initialize OpenAI and Page Config

# %%
client = OpenAI(api_key=os.getenv("openai_api_key")) 

# %%
st.set_page_config(page_title="InterviewIQ", page_icon="🧠")

# %%
# 2. LOGIC FUNCTIONS 

# %%
def generate_questions(role, num_questions=3):
    prompt = f"Generate {num_questions} technical interview questions for {role}. Format as a numbered list."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    text = response.choices[0].message.content
    
    # Your parsing logic to convert text to a list
    questions = []
    for line in text.split("\n"):
        line = line.strip()
        if line and line[0].isdigit():
            parts = line.split(".", 1)
            if len(parts) > 1:
                questions.append(parts[1].strip())
    return questions

def score_answer(role, question, user_answer):
    prompt = f"""
    You are an interview coach.
    Role: {role}
    Question: {question}
    User Answer: {user_answer}
    
    1. Score the answer from 1 to 10.
    2. Give detailed feedback.
    3. Provide an ideal answer.
    4. Start your response with 'RESULT: PASS' if score is 7+ or 'RESULT: FAIL' if lower.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content



# %%
    # Your parsing logic to convert text to a list

# %%
# 3. SESSION STATE: The "Memory" of the App

# %%
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
    st.session_state.questions = []
    st.session_state.current_index = 0
    st.session_state.score_history = []
    st.session_state.total_points = 0


# %%
st.sidebar.warning(f"DEBUG:{len(st.session_state.questions)}questions load")

# %%
# 4. UI: THE INTERVIEW SCREENS

# %%
st.title("InterviewIQ AI 🧠")

# SCREEN A: Setup (The 'Input' part of your code)
if not st.session_state.interview_started:
    st.write("Welcome! Let's prepare you for your next job.")
    role_input = st.text_input("Enter the job role you are interviewing for:", placeholder="e.g. Data Scientist")
    num_q = st.slider("Number of questions", 1, 5, 3)
    
    if st.button("Start Interview"):
        if role_input:
            with st.spinner("Preparing your interview questions..."):
                st.session_state.questions = generate_questions(role_input, num_q)
                st.session_state.role = role_input
                st.session_state.interview_started = True
                st.rerun()
        else:
            st.warning("Please enter a job role.")

# SCREEN B: The Interview Loop
elif st.session_state.current_index < len(st.session_state.questions):
    # Progress bar at the top
    progress = st.session_state.current_index / len(st.session_state.questions)
    st.progress(progress)
    
    current_q = st.session_state.questions[st.session_state.current_index]
    
    st.subheader(f"Question {st.session_state.current_index + 1}")
    st.info(current_q)
    
    user_ans = st.text_area("Your Response:", height=150, key=f"q_{st.session_state.current_index}")

    if st.button("Submit Answer"):
        with st.spinner("AI is evaluating..."):
            feedback = score_answer(st.session_state.role, current_q, user_ans)
            
            # Record points if they passed
            if "RESULT: PASS" in feedback.upper():
                st.session_state.total_points += 1
            
            # Save history
            st.session_state.score_history.append({
                "question": current_q,
                "feedback": feedback
            })
            
            st.session_state.current_index += 1
            st.rerun()

# SCREEN C: Results & Feedback (The final print statements)
else:
    st.balloons()
    st.success(f"Interview Complete! Your Final Score: {st.session_state.total_points}/{len(st.session_state.questions)}")
    
    st.header("Detailed Feedback Report")
    for item in st.session_state.score_history:
        with st.expander(f"Review: {item['question']}"):
            st.write(item['feedback'])
    
    if st.button("Start New Interview"):
        # Reset everything
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

st.success("You nailed it!", icon="✅")




