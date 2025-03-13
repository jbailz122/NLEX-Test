import streamlit as st
import re
import spacy
from jinja2 import Template

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Streamlit App
st.title("📝 Template Filler with Unstructured Data")

# Upload template file
st.sidebar.header("1️⃣ Upload Template File")
template_file = st.sidebar.file_uploader("Upload a text template", type=["txt"])

# Input unstructured text
st.sidebar.header("2️⃣ Enter Unstructured Text")
unstructured_text = st.sidebar.text_area("Paste your unstructured text here")

# Function to extract key details
def extract_data(text):
    """Extracts names, dates, and amounts using NLP."""
    doc = nlp(text)
    
    extracted_data = {
        "name": None,
        "date": None,
        "amount": None
    }

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            extracted_data["name"] = ent.text
        elif ent.label_ == "DATE":
            extracted_data["date"] = ent.text
        elif ent.label_ == "MONEY":
            extracted_data["amount"] = ent.text

    # Fallback regex for amount
    amount_match = re.search(r"\$\d+(?:,\d{3})*(?:\.\d{2})?", text)
    if amount_match and extracted_data["amount"] is None:
        extracted_data["amount"] = amount_match.group()

    return extracted_data

# Process and render template
if template_file and unstructured_text:
    # Read the template
    template_text = template_file.read().decode("utf-8")
    template = Template(template_text)

    # Extract data from unstructured text
    extracted_info = extract_data(unstructured_text)

    # Render template
    filled_template = template.render(extracted_info)

    st.header("📄 Filled Template Output")
    st.text_area("Generated Document", filled_template, height=300)

    # Download button
    st.download_button(
        label="📥 Download Document",
        data=filled_template,
        file_name="filled_document.txt",
        mime="text/plain"
    )
