import streamlit as st
import google.generativeai as genai
import pymupdf 

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="IntegrityFlow AI", layout="wide")
st.title("🛡️ IntegrityFlow AI: Revenue Integrity Portal")

# --- 2. AUTHENTICATION ---
# Hardcoding for this 1-minute test to ensure it works
api_key = "AIzaSyBNFBoY039R_jaBtmEMgbXjRSjJsurL25k"
genai.configure(api_key=api_key)

# --- 3. HELPER FUNCTIONS ---
def extract_text(uploaded_file):
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

# --- 4. UI ---
task = st.sidebar.radio("Task", ["Generate SBR Appeal", "Audit Report"])
uploaded_report = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if st.button("🚀 Run AI Analysis"):
    if uploaded_report:
        with st.spinner("Processing with Gemini..."):
            try:
                raw_text = extract_text(uploaded_report)[:8000] # Limit for speed
                
                # FIXED: Using the specific model path that works with the API
                model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                
                prompt = f"System: You are a CA Workers Comp Expert. Task: {task}. Analyze this: {raw_text}"
                
                response = model.generate_content(prompt)
                
                st.success("Analysis Complete!")
                st.markdown("### AI Analysis Result")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"AI Error: {str(e)}")
                st.info("Try switching the task in the sidebar and clicking run again.")
    else:
        st.error("Please upload a PDF first.")
