import streamlit as st
import google.generativeai as genai
import pymupdf 

st.set_page_config(page_title="IntegrityFlow AI", layout="wide")
st.title("🛡️ IntegrityFlow AI: Revenue Integrity Portal")

# AUTHENTICATION
api_key = ""
genai.configure(api_key=api_key)

# --- 1. MODEL FINDER (The Magic Fix) ---
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # We prioritize Gemini 3, then 2, then 1.5
    target_model = next((m for m in available_models if "gemini-3-flash" in m), 
                   next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0]))
    st.sidebar.success(f"Using Model: {target_model}")
except Exception as e:
    st.error(f"Could not list models: {e}")
    target_model = "gemini-1.5-flash" # Fallback

# --- 2. UI & LOGIC ---
uploaded_report = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if st.button("🚀 Run AI Analysis"):
    if uploaded_report:
        with st.spinner("Analyzing..."):
            try:
                doc = pymupdf.open(stream=uploaded_report.read(), filetype="pdf")
                raw_text = "".join([page.get_text() for page in doc])[:10000]
                
                model = genai.GenerativeModel(target_model)
                response = model.generate_content(f"Analyze this CA Workers Comp report: {raw_text}")
                
                st.markdown("### Analysis Result")
                st.write(response.text)
            except Exception as e:
                st.error(f"AI Error: {str(e)}")
