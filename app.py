import streamlit as st
import openai
import os

# Set page title
st.title("Customizable ChatGPT App with User Templates")

# Load OpenAI API Key securely from environment variables or Streamlit secrets
openai.api_key = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", "your-api-key-here"))

# Upload template file (TXT)
uploaded_file = st.file_uploader("Upload a Template File (TXT)", type=["txt"])

# Read template text if file is uploaded
template_text = ""
if uploaded_file:
    template_text = uploaded_file.read().decode("utf-8")
    st.text_area("Template Preview", template_text, height=200)

# User input field
user_input = st.text_area("Enter your input:")

# Generate response button
if st.button("Generate Response"):
    if uploaded_file:
        # Replace {input} placeholder in template
        prompt = template_text.replace("{input}", user_input)
    else:
        prompt = user_input

    # Send the modified prompt to ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # Display the response
    st.write(response["choices"][0]["message"]["content"])
