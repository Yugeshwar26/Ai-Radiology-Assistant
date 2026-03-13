import streamlit as st
from google import genai
from PIL import Image
import os

# 1. Page Configuration
st.set_page_config(page_title="AI Radiology Assistant", page_icon="🩺", layout="wide")

# 2. Secure API Key Loading
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key is missing! Please configure it in Streamlit Secrets.")
    st.stop()

# Initialize the Gemini Client
client = genai.Client(api_key=API_KEY)

# 3. Sidebar - Settings & Info
with st.sidebar:
    st.title("Settings")
    scan_type = st.selectbox(
        "Select Type of Radiology Scan",
        ["Chest X-Ray", "Bone Fracture (X-Ray)", "Brain CT/MRI", "Dental X-Ray"]
    )
    st.info("This tool uses GenAI to assist in preliminary screening. It is not a final diagnosis.")

# 4. Main Dashboard UI
st.title("🩺 AI Radiology Assistant (GenAI)")
st.markdown(f"### Currently Analyzing: {scan_type}")
st.divider()

# Upload Box
uploaded_file = st.file_uploader(f"Upload {scan_type} Image (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Two-column layout
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("📷 Uploaded Scan")
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, use_container_width=True, caption=f"Patient {scan_type}")
        
    with col2:
        st.subheader("📝 AI-Generated Analysis")
        
        if st.button(f"Generate {scan_type} Report", type="primary", use_container_width=True):
            with st.spinner("Analyzing image..."):
                try:
                    # UPDATED DUAL-MODE PROMPT
                    system_prompt = f"""
                    You are an expert radiologist. Analyze this {scan_type} and provide a response with TWO distinct sections:

                    ### SECTION 1: PROFESSIONAL MEDICAL REPORT
                    Provide a formal, structured medical report including:
                    - Clinical Indication
                    - Technical Findings (detailed anatomical analysis)
                    - Impression (Diagnostic conclusion)

                    ---
                    ### SECTION 2: PATIENT-FRIENDLY SUMMARY (SIMPLE ENGLISH)
                    Translate the findings above into simple, everyday English for a person with no medical knowledge:
                    - Use a friendly and reassuring tone.
                    - Explain complex terms (e.g., instead of 'opacity', use 'cloudy area').
                    - Provide 3 clear 'Next Steps' for the patient.

                    **Disclaimer:** This is an AI-generated preliminary analysis and MUST be validated by a qualified doctor.
                    """
                    
                    # Call Gemini 2.5 Flash
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[system_prompt, img]
                    )
                    
                    st.success("Report Generated Successfully!")
                    st.markdown(response.text)
                    
                    # Download Button for the Report
                    st.download_button(
                        label="Download Report as Text",
                        data=response.text,
                        file_name=f"{scan_type}_Report.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"❌ System Error: {str(e)}")
