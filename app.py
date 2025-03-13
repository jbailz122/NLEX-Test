import streamlit as st
import re
import spacy
from jinja2 import Template

# Add OpenAI configuration
def configure_openai():
    api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")
    if api_key:
        openai.api_key = api_key
        return True
    return False

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
    # Chat interface
    st.subheader("Chat with Recruiter Agent")
