import streamlit as st
import google.generativeai as genai
import pymupdf 
import re

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="IntegrityFlow AI", layout="wide")
st.title("🛡️ IntegrityFlow AI: Revenue Integrity Portal")

# --- 2. AUTHENTICATION ---
# Ensure your Secret key in Streamlit is named GEMINI_API_KEY
try:
    api_key = st.secrets["AIzaSyBNFBoY039R_jaBtmEMgbXjRSjJsurL25k"]
    genai.configure(api_key=api_key)
except:
    st.error("API Key not found. Please check Streamlit Secrets.")

# --- 3. HELPER FUNCTIONS ---
def extract_text(uploaded_file):
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

# --- 4. UI ---
task = st.sidebar.radio("Task", ["Generate SBR Appeal", "Audit Report"])
uploaded_report = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if st.button("🚀 Run AI Analysis"):
    if uploaded_report:
        with st.spinner("Processing..."):
            raw_text = extract_text(uploaded_report)[:10000] # Limit text for speed
            
            # Use the most stable model: gemini-1.5-pro or flash
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Analyze this CA Workers Comp report for {task} and MTUS compliance: {raw_text}"
            
            try:
                response = model.generate_content(prompt)
                st.success("Analysis Complete!")
                st.write(response.text)
            except Exception as e:
                st.error(f"AI Error: {str(e)}")
    else:
        st.error("Please upload a PDF first.")
