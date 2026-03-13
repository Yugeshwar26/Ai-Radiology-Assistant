import streamlit as st
from google import genai
from PIL import Image
import os

# 1. Page Configuration
st.set_page_config(page_title="AI Radiology Assistant", page_icon="🩺", layout="wide")

# Custom CSS for Industrial UI
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #0066cc;
        color: white;
        border-radius: 6px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease 0s;
    }
    div.stButton > button:first-child:hover {
        background-color: #005bb5;
        transform: translateY(-2px);
    }
    .stFileUploader {
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

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
    st.markdown("- **Yugeshwar P.**")
    st.markdown("- **Visvesh M.**")
    st.markdown("- **Matheshwaran S.**")
    st.markdown("*CSE Students, Kamaraj College of Engineering & Technology*")

# 4. Main Dashboard UI
st.title("🩺 AI Radiology Assistant")
st.markdown("*A collaborative GenAI co-pilot designed to bring clarity to complex medical imaging.*")
st.markdown(f"**Currently Analyzing:** `{scan_type}` &nbsp; | &nbsp; **System Status:** 🟢 Online")
st.divider()

# Upload Box
uploaded_file = st.file_uploader(f"Upload {scan_type} Image (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        with st.container(border=True):
            st.subheader("📷 Uploaded Scan")
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, use_container_width=True, caption=f"Patient {scan_type}")
        
    with col2:
        with st.container(border=True):
            st.subheader("📝 AI-Generated Analysis")
            
            if st.button(f"🔍 Analyze Scan & Generate Report", use_container_width=True):
                with st.spinner(f"AI is analyzing {scan_type} features..."):
                    try:
                        # --- DYNAMIC DIAGNOSIS LOGIC ---
                        if scan_type == "Chest X-Ray":
                            diagnosis_options = "**DIAGNOSIS: PNEUMONIA DETECTED** OR **DIAGNOSIS: TUBERCULOSIS DETECTED** OR **DIAGNOSIS: NORMAL**"
                            technical_focus = "look for lower lobe consolidation/opacities (Pneumonia), upper lobe cavitations and infiltrates (Tuberculosis), or clear lung fields (Normal)"
                        elif scan_type == "Bone Fracture (X-Ray)":
                            diagnosis_options = "**DIAGNOSIS: FRACTURE DETECTED** OR **DIAGNOSIS: NORMAL**"
                            technical_focus = "look for bone cortical disruption, displacement, or joint alignment"
                        elif scan_type == "Brain CT/MRI":
                            diagnosis_options = "**DIAGNOSIS: ABNORMALITY DETECTED** OR **DIAGNOSIS: NORMAL**"
                            technical_focus = "look for intracranial hemorrhage, mass effect, tumors, or midline shift"
                        elif scan_type == "Dental X-Ray":
                            diagnosis_options = "**DIAGNOSIS: DENTAL ANOMALY DETECTED** OR **DIAGNOSIS: NORMAL**"
                            technical_focus = "look for caries (cavities), impacted teeth, or root infections"
                        else:
                            diagnosis_options = "**DIAGNOSIS: ANOMALY DETECTED** OR **DIAGNOSIS: NORMAL**"
                            technical_focus = "provide a detailed structural analysis"

                        # --- THE DYNAMIC PROMPT ---
                        system_prompt = f"""
                        You are a Senior Radiologist specializing in {scan_type}. Analyze the uploaded image with high precision.

                        CRITICAL INSTRUCTION: 
                        You MUST start your response with a clear, bolded diagnosis. Based on the image, output EXACTLY one of these lines first:
                        {diagnosis_options}

                        After the diagnosis, provide the response in TWO distinct sections:

                        ### SECTION 1: PROFESSIONAL MEDICAL REPORT
                        - Clinical Indication: Preliminary screening and triage.
                        - Technical Findings: Provide a detailed anatomical analysis ({technical_focus}).
                        - Impression: Provide a definitive diagnostic conclusion based on observed evidence.

                        ---
                        ### SECTION 2: PATIENT-FRIENDLY SUMMARY (SIMPLE ENGLISH)
                        Translate the findings into simple English for a non-medical person:
                        - Use a friendly, reassuring tone.
                        - Explain complex medical terms simply.
                        - List 3 clear 'Next Steps' (e.g., 'Consult your primary physician').

                        **Disclaimer:** This is an AI-generated preliminary analysis and MUST be validated by a qualified doctor before treatment.
                        """
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[system_prompt, img]
                        )
                        
                        st.success("Analysis Complete!")
                        st.markdown(response.text)
                        
                        st.download_button(
                            label="💾 Download Full Report",
                            data=response.text,
                            file_name=f"{scan_type.replace('/', '_')}_Analysis.txt",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ System Error: {str(e)}")
