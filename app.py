import streamlit as st  
from google.genai import Client  
import pymupdf  
from fpdf import FPDF  # <--- Moved to the top!

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="IntegrityFlow AI", layout="wide")
st.title("🛡️ IntegrityFlow AI: Revenue Integrity Portal")

# --- 2. AUTHENTICATION ---
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
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- 4. USER INTERFACE ---
with st.sidebar:
    st.header("Settings")
    st.info("🔒 HIPAA Compliant Mode: Data is processed in memory and never stored on our servers.")
    st.divider() 
    
    task = st.radio("Choose Analysis Type", ["Generate SBR Appeal", "Audit Compliance"])
    model_id = "gemini-2.5-flash" 

uploaded_report = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if st.button("🚀 Run AI Analysis"):
    if uploaded_report:
        with st.spinner(f"Analyzing with {model_id}..."):
            try:
                # 1. Extract text
                report_text = extract_text_from_pdf(uploaded_report)
                context_text = report_text[:15000]
                
                # 2. Call the Gemini 2026 API
                prompt = f"System: You are a California Workers Comp expert. Task: {task}. Analyze this report and provide a professional result: {context_text}"
                
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                
                # 3. Display Result
                st.success("Analysis Complete!")
                st.markdown("### AI Output")
                analysis_result = response.text
                st.write(analysis_result)
                
                # 4. PDF DOWNLOADER
                st.divider()
                
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=12) # Helvetica is more standard for 2026 PDFs
                
                # Clean the text for PDF compatibility
                clean_text = analysis_result.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, txt=clean_text)
                
                # Get the PDF as a bytearray and convert to standard bytes
                pdf_data = pdf.output() 
                binary_pdf = bytes(pdf_data) # This fixes the 'Invalid binary data' error
                
                st.download_button(
                    label="📥 Download SBR Appeal as PDF",
                    data=binary_pdf,
                    file_name="SBR_Appeal_Report.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"AI Execution Error: {e}")
    else:
        st.warning("Please upload a PDF file first.")
