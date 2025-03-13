import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import pandas as pd
import time
import json
import openai
from werkzeug.utils import secure_filename

import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

response = client.responses.create(
    model="gpt-4o",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)

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
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to download and save file from URL
@st.cache_data
def download_file(file_url):
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        filename = secure_filename(file_url.split("/")[-1])

        if not allowed_file(filename):
            return None, "File type not allowed"

        file_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return file_path, f"File '{filename}' uploaded successfully!"
    except requests.exceptions.RequestException as e:
        return None, f"Failed to fetch file: {str(e)}"

# Streamlit UI for Document Upload
st.title("Document Upload via URL")
st.write("Enter a document URL below to download and save it.")

file_url = st.text_input("Enter file URL", "")

if st.button("Upload Document"):
    if file_url:
        file_path, message = download_file(file_url)
        if file_path:
            st.success(message)
            with open(file_path, "rb") as file:
                st.download_button("Download File", file, file_name=file_path.split("/")[-1])
        else:
            st.error(message)
    else:
        st.warning("Please enter a valid URL.")
