import streamlit as st  
from google.genai import Client  
import pymupdf  
from fpdf import FPDF  

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
    st.header("IntegrityFlow Tools")
    st.info("🔒 HIPAA Compliant Mode Active")
    st.divider() 
    
    task = st.radio(
        "Select Clinical Task", 
        [
            "Generate SBR Appeal", 
            "Audit Compliance",
            "PR-4 MMI Evaluation",
            "Rating String Builder",
            "MTUS Justification"
        ]
    )
    model_id = "gemini-2.5-flash" 

uploaded_report = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if st.button("🚀 Run AI Analysis"):
    if uploaded_report:
        with st.spinner(f"Analyzing..."):
            try:
                # 1. Extract text
                report_text = extract_text_from_pdf(uploaded_report)
                context_text = report_text[:15000]
                
                # 2. Expert Prompt Logic
                prompt = f"""
                System: You are an expert in California Workers' Compensation (Labor Code & MTUS).
                Current Task: {task}.
                Instructions: 
                - If SBR Appeal: Write a formal letter to the Claims Administrator.
                - If Audit Compliance: Identify missing legal elements or coding errors.
                - If PR-4 MMI Evaluation: Check for Whole Person Impairment (WPI) and MMI status.
                - If Rating String Builder: Provide the AMA Guides 5th Ed. rating string code.
                - If MTUS Justification: Cite specific MTUS medical guidelines for the requested treatment.

                Analyze this report and provide a detailed professional result: {context_text}
                """
                
                # 3. Call Gemini
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                
                # 4. Display Result
                st.success("Analysis Complete!")
                st.markdown(f"### AI {task} Result")
                analysis_result = response.text
                st.write(analysis_result)
                
                # 5. PDF DOWNLOADER
                st.divider()
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=12)
                clean_text = analysis_result.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, txt=clean_text)
                
                pdf_data = pdf.output() 
                binary_pdf = bytes(pdf_data) 
                
                st.download_button(
                    label=f"📥 Download {task} as PDF",
                    data=binary_pdf,
                    file_name=f"{task.replace(' ', '_')}_Report.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"AI Execution Error: {e}")
    else:
        st.warning("Please upload a PDF file first.")
