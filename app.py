import io
import os
from typing import Any
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from forensics.forensic_tools import calculate_file_hashes, extract_pdf_metadata, get_file_type

load_dotenv()

# THEME AND STYLING FIX
st.markdown("""
<style>
    .stApp { background-color: #EFEEE3 !important; }
    [data-testid="stAppViewContainer"] { background-color: #EFEEE3 !important; }
    .stButton>button { border-radius: 99px; background-color: #1937AD; color: white; }
</style>
""", unsafe_allow_html=True)

def get_direct_ai_insights(file_data: Any, dataset_label: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return "API Key Missing."
    client = Groq(api_key=api_key)
    
    # CRITICAL FIX: Ensure AI receives decoded string, not bytes/bytearray
    if isinstance(file_data, (bytes, bytearray)):
        clean_text = file_data.decode('utf-8', errors='ignore')[:5000]
    else:
        clean_text = str(file_data)[:5000]

    prompt = f"Analyze this forensic data for anomalies:\n\n{clean_text}"
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a forensic expert."}, {"role": "user", "content": prompt}],
        temperature=0.3
    )
    return completion.choices[0].message.content

def get_verification_status(ai_text: str) -> tuple[str, str]:
    if not ai_text: return "SYSTEM STABLE", "badge-stable"
    ai_lower = ai_text.lower()
    # Trigger ONLY on specific forensic indicators
    if any(word in ai_lower for word in ['malicious', 'breach', 'tampered', 'anomaly']):
        return "BREACH DETECTED", "badge-breach"
    return "SYSTEM STABLE", "badge-stable"

def main():
    st.title("Axiom Forge Truth OS")
    
    # API Status Indicator in Sidebar
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        st.sidebar.success("Key Loaded ✓")
    else:
        st.sidebar.error("Key Not Found ✗")
    
    uploaded_file = st.sidebar.file_uploader("Upload Evidence", type=["csv", "pdf"])

    if uploaded_file:
        # SANITIZE DATA IMMEDIATELY: Convert bytearray to bytes
        file_content = bytes(uploaded_file.getvalue())
        
        st.subheader("🛠️ Forensic Metadata & Integrity")
        hashes = calculate_file_hashes(file_content)
        st.code(f"MD5: {hashes['md5']}\nSHA-256: {hashes['sha256']}")

        if st.button("Run Forensic AI Analysis"):
            with st.spinner("Analyzing..."):
                try:
                    insights = get_direct_ai_insights(file_content, uploaded_file.name)
                    status, css = get_verification_status(insights)
                    if status == "BREACH DETECTED":
                        st.error(status)
                    else:
                        st.success(status)
                    st.markdown(insights)
                except Exception as e:
                    st.error(f"Analysis Failed: {str(e)}")

if __name__ == '__main__':
    main()