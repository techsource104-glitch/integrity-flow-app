import streamlit as st
from google.genai import Client  # <--- Use this specific import
import pymupdf 

# ... (Page Config) ...

# --- 2. AUTHENTICATION ---
# The new 2026 SDK uses a Client object
api_key = "AIzaSyBNFBoY039R_jaBtmEMgbXjRSjJsurL25k"
client = Client(api_key=api_key)

# --- 3. HELPER FUNCTIONS ---
def extract_text(uploaded_file):
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

# --- 4. UI ---
task = st.sidebar.radio("Task", ["Generate SBR Appeal", "Audit Report"])
uploaded_report = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if st.button("🚀 Run AI Analysis"):
    if uploaded_report:
        with st.spinner("Analyzing with Gemini 3 Flash..."):
            try:
                raw_text = extract_text(uploaded_report)[:15000] # Gemini 3 handles more text!
                
                # FIXED: Use the 2026 stable model name
                # Options: 'gemini-2.5-flash' (Stable) or 'gemini-3-flash-preview' (Latest)
                model_id = 'gemini-2.5-flash' 
                
                prompt = f"System: You are a CA Workers Comp Expert. Task: {task}. Analyze this medical report: {raw_text}"
                
                # New SDK call format
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                
                st.success("Analysis Complete!")
                st.markdown("### AI Analysis Result")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"AI Error: {str(e)}")
                st.info("Tip: If gemini-2.5-flash fails, try changing the model_id to 'gemini-3-flash-preview'.")
    else:
        st.error("Please upload a PDF first.")
