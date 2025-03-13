import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import pandas as pd
import time
import json
import openai
from werkzeug.utils import secure_filename

# Configure OpenAI API Key
def configure_openai():
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""

    api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password", value=st.session_state.api_key)

    if api_key:
        st.session_state.api_key = api_key  # Save it in session_state
        openai.api_key = api_key
        return True
    return False

# Function to chat with OpenAI
def chat_with_recruiter_agent(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful recruiting assistant for a team of recruiters."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Recruiter Agent Tab
def recruiter_agent_tab():
    st.title("Recruiter Agent")

    if not configure_openai():
        st.warning("Please enter your OpenAI API key in the sidebar to continue.")
        return

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask your recruiting question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            response = chat_with_recruiter_agent(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Configure upload folder
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists

# Function to check allowed file types
def
