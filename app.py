import streamlit as st
from google import genai
import pymupdf  # PyMuPDF
import re

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="IntegrityFlow AI | Revenue Recovery", layout="wide")
st.title("🛡️ IntegrityFlow AI: Revenue Integrity Portal")
st.markdown("### California Workers' Comp - SBR & Audit Engine (2026 Compliance)")

# --- 2. AUTHENTICATION (SI-GEMINI BRAIN) ---
# This pulls the key from your Streamlit Secrets (Step 4 in my previous message)
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# --- 3. HELPER FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    """Extracts text from uploaded PDF bytes."""
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def scrub_phi(text):
    """Basic anonymization to protect your career and the clinic."""
    text = re.sub(r'(Patient|Name|Claimant):\s*[A-Z][a-z]+\s[A-Z][a-z]+', r'\1: [ANONYMIZED]', text)
    text = re.sub(r'\d{3}-\d{2}-\d{4}', '[SSN-REDACTED]', text)
    return text

# --- 4. THE UI / SIDEBAR ---
with st.sidebar:
    st.header("Select Task")
    task = st.radio("What do you want to do?", 
                    ["Generate SBR Appeal", "Contract Audit (Underpayments)", "Clinical Documentation Audit"])

# --- 5. MAIN PROCESSING LOGIC ---
uploaded_report = st.file_uploader("Upload Medical Report (PDF)", type="pdf")
uploaded_eor = st.file_uploader("Upload EOR/Denial (PDF) - Optional", type="pdf")

if st.button("🚀 Run AI Analysis"):
    if uploaded_report:
        with st.spinner("Analyzing against 2026 MTUS Guidelines..."):
            # Process text
            report_text = scrub_phi(extract_text_from_pdf(uploaded_report))
            eor_text = scrub_phi(extract_text_from_pdf(uploaded_eor)) if uploaded_eor else "No EOR provided."

            # Define the Prompt based on the task
            system_prompt = f"""
            You are a CA Workers' Comp Expert. Task: {task}.
            Using the provided Medical Report and EOR, perform the following:
            1. If SBR: Write a formal appeal letter citing 2026 MTUS rules.
            2. If Audit: Identify missing functional goals or underpayments.
            3. Always provide 'The Fix': The exact sentence the doctor should add.
            
            Medical Report: {report_text}
            EOR/Denial: {eor_text}
            """

            # Call Gemini
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_prompt
            )

            # Display Results
            st.success("Analysis Complete!")
            st.text_area("Final Output (Copy & Paste to Letterhead)", value=response.text, height=500)
    else:
        st.error("Please upload at least a Medical Report to begin.")

st.info("Note: This AI tool is for administrative support. Final review must be performed by a qualified professional.")
