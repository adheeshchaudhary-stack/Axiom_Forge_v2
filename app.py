import io
import os
from typing import Any
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from forensics.forensic_tools import calculate_file_hashes, get_file_type

# Load environment variables at the very top
load_dotenv()

# THEME AND STYLING
st.markdown("""
<style>
    .stApp { background-color: #EFEEE3 !important; }
    [data-testid="stAppViewContainer"] { background-color: #EFEEE3 !important; }
    .stButton>button { border-radius: 99px; background-color: #1937AD; color: white; }
    .metric-card { background-color: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

def get_direct_ai_insights(file_data: Any, dataset_label: str) -> str:
    """Get AI insights with safe decode for the prompt."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return "API Key Missing."
    
    client = Groq(api_key=api_key)
    
    # Safe decode for prompt - ensure we get a string
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
    """Get verification status from AI analysis."""
    if not ai_text: return "SYSTEM STABLE", "badge-stable"
    ai_lower = ai_text.lower()
    if any(word in ai_lower for word in ['malicious', 'breach', 'tampered', 'anomaly']):
        return "BREACH DETECTED", "badge-breach"
    return "SYSTEM STABLE", "badge-stable"

def main():
    st.title("🔐 Truth OS - Forensic Analysis Suite")
    
    # Sidebar Login
    st.sidebar.header("🔐 System Access")
    operator_id = st.sidebar.text_input('Operator ID', type='password', placeholder="Enter access code")
    
    # API Status Indicator
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        st.sidebar.success("API Key Loaded ✓")
    else:
        st.sidebar.error("API Key Not Found ✗")
    
    # Authentication check
    if not operator_id:
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2>🔒 ACCESS RESTRICTED</h2>
            <p>Please enter your Operator ID in the sidebar to access the system</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.sidebar.success(f"Welcome, Operator {operator_id}")
    st.sidebar.divider()
    
    # Main content area
    uploaded_file = st.sidebar.file_uploader("Upload Evidence", type=["csv", "pdf"])
    
    # Metric Tiles
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Integrity", "100%", delta="Secure")
    with col2:
        st.metric("Files Scanned", "0", delta="Active")
    with col3:
        st.metric("Anomalies", "0", delta="Clean")
    
    st.divider()
    
    if uploaded_file:
        # Immediate casting to bytes (Step 4 requirement)
        file_content = bytes(uploaded_file.getvalue())
        
        # Forensic Analysis
        st.subheader("🛠️ Forensic Metadata & Integrity")
        hashes = calculate_file_hashes(file_content)
        file_type = get_file_type(file_content, uploaded_file.name)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**File Type:** {file_type}")
        with col2:
            st.info(f"**MD5:** {hashes['md5'][:16]}...")
        with col3:
            st.info(f"**SHA-256:** {hashes['sha256'][:24]}...")
        
        # Data Table for CSV files
        if uploaded_file.name.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(file_content))
                
                st.subheader("📊 Raw Data Analysis")
                st.dataframe(df, use_container_width=True)
                
                # Line Chart for visual analytics
                if 'Amount' in df.columns:
                    st.subheader("📈 Amount Distribution")
                    st.line_chart(df['Amount'])
                elif len(df.columns) > 0:
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        st.subheader(f"📈 {numeric_cols[0]} Distribution")
                        st.line_chart(df[numeric_cols[0]])
                
            except Exception as e:
                st.warning(f"Could not parse CSV data: {str(e)}")
        
        # AI Analysis Block
        st.subheader("🤖 AI Forensic Analysis")
        if st.button("Run Forensic AI Analysis"):
            with st.spinner("Analyzing evidence..."):
                try:
                    insights = get_direct_ai_insights(file_content, uploaded_file.name)
                    status, css = get_verification_status(insights)
                    
                    if status == "BREACH DETECTED":
                        st.error(f"🚨 **{status}**")
                    else:
                        st.success(f"✅ **{status}**")
                    
                    st.markdown("### Analysis Results:")
                    st.markdown(insights)
                    
                except Exception as e:
                    st.error(f"Analysis Failed: {str(e)}")

if __name__ == '__main__':
    main()