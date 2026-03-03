import io
import os
from typing import Any, Dict, Optional
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from forensics.forensic_tools import calculate_file_hashes, get_file_type, analyze_file_metadata

# Load environment variables at the very top
load_dotenv()

# Initialize Session State
if 'audit_triggered' not in st.session_state:
    st.session_state.audit_triggered = False
if 'file_results' not in st.session_state:
    st.session_state.file_results = {}
if 'ai_insights' not in st.session_state:
    st.session_state.ai_insights = ""
if 'threat_level' not in st.session_state:
    st.session_state.threat_level = "CLEAN"
if 'integrity_score' not in st.session_state:
    st.session_state.integrity_score = "100%"
if 'messages' not in st.session_state:
    st.session_state.messages = []

# THEME AND STYLING
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Main Page Config
st.set_page_config(page_title="Axiom Forge Truth OS", layout="wide")

# Inject Custom CSS
local_css("styles.css")

def get_direct_ai_insights(file_data: Any, file_metadata: Optional[Dict] = None) -> str:
    """Get AI insights with safe decode for the prompt."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return "API Key Missing."
    
    client = Groq(api_key=api_key)
    
    if isinstance(file_data, (bytes, bytearray)):
        clean_text = file_data.decode('utf-8', errors='ignore')[:5000]
    else:
        clean_text = str(file_data)[:5000]

    # Build prompt with metadata if available
    prompt = f"Analyze this forensic data for anomalies:\n\nFile Content:\n{clean_text}\n\n"
    
    if file_metadata:
        prompt += f"File Metadata:\n"
        prompt += f"- Size: {file_metadata.get('size', 'Unknown')} bytes\n"
        prompt += f"- MIME Type: {file_metadata.get('type', {}).get('mime_type', 'Unknown')}\n"
        prompt += f"- Description: {file_metadata.get('type', {}).get('description', 'Unknown')}\n"
        prompt += f"- MD5: {file_metadata.get('hashes', {}).get('md5', 'Unknown')}\n"
        prompt += f"- SHA256: {file_metadata.get('hashes', {}).get('sha256', 'Unknown')}\n"

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a forensic expert AI."}, {"role": "user", "content": prompt}],
        temperature=0.3
    )
    return completion.choices[0].message.content

def main():
    # Sidebar - Case Investigator
    st.sidebar.title("Evidence Lock")
    st.sidebar.markdown("---")
    
    operator_id = st.sidebar.text_input('OPERATOR ID', type='password', placeholder="Enter access code")
    
    # API Status
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        st.sidebar.success("GROQ CORE: ONLINE")
    else:
        st.sidebar.error("GROQ CORE: OFFLINE")
    
    # Authentication check
    if not operator_id:
        st.markdown("""
        <div style='text-align: center; padding: 100px;'>
            <h1 style='color: #00D1FF;'>ACCESS RESTRICTED</h1>
            <p style='color: #8B949E;'>PLEASE ENTER OPERATOR CREDENTIALS IN THE SIDEBAR</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.sidebar.success(f"OPERATOR: {operator_id}")
    st.sidebar.markdown("---")
    
    # Sidebar Upload
    uploaded_file = st.sidebar.file_uploader("UPLOAD EVIDENCE", type=["csv", "pdf"])
    
    # Evidence Locker Section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Evidence Locker")
    
    if uploaded_file:
        # Create a temporary file to analyze
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Analyze file metadata
            file_metadata = analyze_file_metadata(tmp_file_path)
            
            if file_metadata:
                with st.sidebar.expander(f"📁 {uploaded_file.name}", expanded=True):
                    st.markdown(f"**Size:** {file_metadata['size']} bytes")
                    st.markdown(f"**Hash (MD5):** {file_metadata['hashes']['md5']}")
                    st.markdown(f"**Hash (SHA256):** {file_metadata['hashes']['sha256']}")
                    st.markdown(f"**Verified Mimetype:** {file_metadata['type']['mime_type']}")
                    st.markdown(f"**Description:** {file_metadata['type']['description']}")
            else:
                st.sidebar.error("Failed to analyze file metadata")
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
    
    # Audit Button
    st.sidebar.markdown("---")
    if st.sidebar.button("RUN FORENSIC AUDIT", use_container_width=True):
        if uploaded_file:
            st.session_state.audit_triggered = True
            file_content = bytes(uploaded_file.getvalue())
            
            # Analyze file metadata
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            try:
                file_metadata = analyze_file_metadata(tmp_file_path)
                hashes = file_metadata['hashes'] if file_metadata else calculate_file_hashes(file_content)
                file_type = file_metadata['type'] if file_metadata else get_file_type(file_content)
                
                st.session_state.file_results = {
                    'hashes': hashes,
                    'file_type': file_type,
                    'name': uploaded_file.name,
                    'content': file_content,
                    'metadata': file_metadata
                }
                
                with st.spinner("AUDITING EVIDENCE..."):
                    try:
                        insights = get_direct_ai_insights(file_content, file_metadata)
                        st.session_state.ai_insights = insights
                        if any(word in insights.lower() for word in ['malicious', 'breach', 'tampered', 'anomaly']):
                            st.session_state.threat_level = "CRITICAL"
                            st.session_state.integrity_score = "40%"
                        else:
                            st.session_state.threat_level = "CLEAN"
                            st.session_state.integrity_score = "100%"
                    except Exception as e:
                        st.session_state.ai_insights = f"AUDIT ERROR: {str(e)}"
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
        else:
            st.sidebar.warning("UPLOAD EVIDENCE BEFORE AUDIT")

    # Main Content Area
    st.markdown('<h1 class="main-title">Axiom Forge Truth OS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Direct Forensic Analysis & Neural Verification</p>', unsafe_allow_html=True)
    st.markdown('<div class="title-divider"></div>', unsafe_allow_html=True)
    
    # Top Row Metrics
    m_col1, m_col2, m_col3 = st.columns(3)
    file_count = "1" if uploaded_file else "0"
        
    with m_col1:
        st.metric("EVIDENCE SCANNED", file_count)
    with m_col2:
        st.metric("THREAT LEVEL", st.session_state.threat_level)
    with m_col3:
        st.metric("SYSTEM INTEGRITY", st.session_state.integrity_score)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Audit Results
    if st.session_state.audit_triggered and st.session_state.file_results:
        res = st.session_state.file_results
        
        with st.container():
            st.subheader("METADATA & INTEGRITY REPORT")
            c1, c2, c3 = st.columns(3)
            with c1: st.info(f"FILE TYPE: {res['file_type']['description']}")
            with c2: st.info(f"MD5: {res['hashes']['md5'][:16]}...")
            with c3: st.info(f"SHA-256: {res['hashes']['sha256'][:24]}...")
            
        if st.session_state.ai_insights:
            st.subheader("AI FORENSIC INSIGHTS")
            st.markdown(st.session_state.ai_insights)
            
    # Chat Interface at the bottom
    st.markdown("---")
    st.subheader("Ask the Forensic AI")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Analyze findings or ask about the evidence..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = "I am ready to analyze the evidence once the audit is complete."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    main()
