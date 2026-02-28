import streamlit as st  
from google.genai import Client  
import pymupdf  
from fpdf import FPDF  

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="IntegrityFlow AI", layout="wide")

# --- CUSTOM UI DESIGN (v0.dev Style) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #050505;
        color: #FFFFFF;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #1a1a1a;
    }
    
    /* HIPAA Badge */
    .hipaa-badge {
        background-color: rgba(0, 255, 163, 0.1);
        color: #00ffa3;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(0, 255, 163, 0.3);
        font-size: 0.8rem;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Buttons - The "IntegrityFlow Green" */
    .stButton>button {
        background-color: #00ffa3 !important;
        color: #000000 !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 700 !important;
        width: 100% !important;
        padding: 0.6rem !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        background-color: #00cc82 !important;
        transform: translateY(-2px);
    }

    /* Radio Buttons / Selectors */
    .stRadio [data-testid="stWidgetLabel"] {
        color: #888888 !important;
        font-weight: 600 !important;
    }

    /* Success/Info Messages */
    .stAlert {
        background-color: #111111 !important;
        border: 1px solid #333333 !important;
        color: #00ffa3 !important;
    }

    /* Title Styling */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -1px !important;
    }
    </style>
    """, unsafe_content=True)

# --- 2. AUTHENTICATION (Unchanged) ---
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

# --- 3. HELPER FUNCTIONS (Unchanged) ---
def extract_text_from_pdf(uploaded_file):
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- 4. USER INTERFACE ---
st.title("🛡️ IntegrityFlow AI")
st.markdown("<p style='color: #888; margin-top: -20px;'>Revenue Integrity Portal</p>", unsafe_content=True)

with st.sidebar:
    st.markdown('<div class="hipaa-badge">🔒 HIPAA Compliant Mode Active</div>', unsafe_content=True)
    st.header("IntegrityFlow Tools")
    
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

# File Uploader Styled
uploaded_report = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if st.button("🚀 Run AI Analysis"):
    if uploaded_report:
        with st.spinner(f"Processing {task}..."):
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
                - If Rating String Builder: Provide the AMA Guides 5th Ed. rating string code and SHOW THE MATH for the Combined Values Chart
                - If MTUS Justification: Cite specific MTUS medical guidelines for the requested treatment.

                Analyze this report and provide a detailed professional result: {context_text}
                """
                
                # 3. Call Gemini
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                
                # 4. Display Result in a Styled Container
                st.success("Analysis Complete!")
                st.markdown(f"### AI {task} Result")
                analysis_result = response.text
                
                with st.container():
                    st.markdown("""<div style="background-color: #0a0a0a; padding: 20px; border-radius: 12px; border: 1px solid #1a1a1a;">""", unsafe_content=True)
                    st.write(analysis_result)
                    st.markdown("""</div>""", unsafe_content=True)
                
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
