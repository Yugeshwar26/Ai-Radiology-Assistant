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
    st.divider()
    st.info("Industrial-grade screening tool using Gemini 2.5 Flash for diagnostic assistance.")
    st.markdown("---")
    st.markdown("### Developed by:")
    st.markdown("**Yugeshwar P.**")
    st.markdown("**Visvesh M.**")
    st.markdown("**Matheshwaran S.**")
    st.markdown("CSE Students")

# 4. Main Dashboard UI
st.title("🩺 AI Radiology Assistant")
st.markdown(f"### Currently Analyzing: {scan_type}")
st.divider()

# Upload Box
uploaded_file = st.file_uploader(f"Upload {scan_type} Image (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Two-column layout
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("📷 Uploaded Scan")
        # RGB CONVERSION FIX: Crucial for avoiding 'unsupported mode' errors
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, use_container_width=True, caption=f"Patient {scan_type}")
        
    with col2:
        st.subheader("📝 AI-Generated Analysis")
        
        if st.button(f"Generate {scan_type} Report", type="primary", use_container_width=True):
            with st.spinner("AI is analyzing anatomical features..."):
                try:
                    # UPDATED EXPERT DUAL-MODE PROMPT WITH FORCED EXACT DIAGNOSIS
                    system_prompt = f"""
                    You are a Senior Radiologist specializing in {scan_type}. Analyze the uploaded image with high precision.

                    CRITICAL INSTRUCTION: 
                    You MUST start your response with a clear, bolded diagnosis. Based on the image, output EXACTLY one of these two lines first:
                    **DIAGNOSIS: PNEUMONIA DETECTED** OR 
                    **DIAGNOSIS: NORMAL**

                    After the diagnosis, provide the response in TWO distinct sections:

                    ### SECTION 1: PROFESSIONAL MEDICAL REPORT
                    - Clinical Indication: Preliminary screening and triage.
                    - Technical Findings: Provide a detailed anatomical analysis (e.g., look for opacities, fluid, or clear lungs).
                    - Impression: Provide a definitive diagnostic conclusion based on observed evidence.

                    ---
                    ### SECTION 2: PATIENT-FRIENDLY SUMMARY (SIMPLE ENGLISH)
                    Translate the findings into simple English for a non-medical person:
                    - Use a friendly, reassuring tone.
                    - Explain terms (e.g., use 'cloudy areas' instead of 'opacities').
                    - List 3 clear 'Next Steps' (e.g., 'Consult your primary physician').

                    **Disclaimer:** This is an AI-generated preliminary analysis and MUST be validated by a qualified doctor before treatment.
                    """
                    
                    # Using Gemini 2.5 Flash for the fastest, most accurate results on the free tier
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[system_prompt, img]
                    )
                    
                    st.success("Analysis Complete!")
                    st.markdown(response.text)
                    
                    # Download Button for the Report
                    st.download_button(
                        label="💾 Download Full Report",
                        data=response.text,
                        file_name=f"{scan_type}_Analysis.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"❌ System Error: {str(e)}")
