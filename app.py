import streamlit as st  # Fixes the NameError
from google.genai import Client  # Modern 2026 SDK import
import pymupdf 

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="IntegrityFlow AI", layout="wide")
st.title("🛡️ IntegrityFlow AI: Revenue Integrity Portal")

# --- 2. AUTHENTICATION ---
# We use the Streamlit Secrets vault for safety
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = Client(api_key=api_key)
    else:
        st.error("API Key not found in Streamlit Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# --- 3. HELPER FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    """Extracts text from uploaded PDF using PyMuPDF."""
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- 4. USER INTERFACE ---
with st.sidebar:
    st.header("Settings")
    task = st.radio("Choose Analysis Type", ["Generate SBR Appeal", "Audit Compliance"])
    # 2026 Stable Model ID
    model_id = "gemini-2.5-flash" 

uploaded_report = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if st.button("🚀 Run AI Analysis"):
    if uploaded_report:
        with st.spinner(f"Analyzing with {model_id}..."):
            try:
                # 1. Extract text
                report_text = extract_text_from_pdf(uploaded_report)
                
                # 2. Limit text to avoid token overflow (approx 15k chars)
                context_text = report_text[:15000]
                
                # 3. Call the Gemini 2026 API
                prompt = f"System: You are a California Workers Comp expert. Task: {task}. Analyze this report and provide a professional result: {context_text}"
                
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                
                # 4. Display Result
                st.success("Analysis Complete!")
                st.markdown("### AI Output")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"AI Execution Error: {e}")
    else:
        st.warning("Please upload a PDF file first.")
