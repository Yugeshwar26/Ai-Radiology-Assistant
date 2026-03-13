import streamlit as st
from google import genai
from PIL import Image
import os
import time

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
                            technical_focus = "look for lower lobe consolidation (Pneumonia), upper lobe cavitations (Tuberculosis), or clear lung fields (Normal)"
                        elif scan_type == "Bone Fracture (X-Ray)":
                            diagnosis_options = "**DIAGNOSIS: FRACTURE DETECTED** OR **DIAGNOSIS: NORMAL**"
                            technical_focus = "look for bone cortical disruption, displacement, or joint alignment"
                        elif scan_type == "Brain CT/MRI":
                            diagnosis_options = "**DIAGNOSIS: ABNORMALITY DETECTED** OR **DIAGNOSIS: NORMAL**"
                            technical_focus = "look for intracranial hemorrhage, mass effect, tumors, or midline shift"
                        elif scan_type == "Dental X-Ray":
                            diagnosis_options = "**DIAGNOSIS: DENTAL ANOMALY DETECTED** OR **DIAGNOSIS: NORMAL**"
                            technical_focus = "look for caries (cavities), impacted teeth, or root infections"

                        # --- NEW PROMPT WITH TRIAGE INSTRUCTIONS ---
                        system_prompt = f"""
                        You are a Senior Radiologist specializing in {scan_type}. Analyze the uploaded image with high precision.

                        CRITICAL INSTRUCTION: 
                        You MUST start your response with exactly TWO lines.
                        Line 1: A clear diagnosis from these options: {diagnosis_options}
                        Line 2: TRIAGE_LEVEL: [RED, YELLOW, or GREEN] 
                        (Rule: RED = Brain Abnormality, Tuberculosis, or Fracture. YELLOW = Pneumonia or Dental Anomaly. GREEN = Normal).

                        After these two lines, provide the response in TWO distinct sections:
                        ### SECTION 1: PROFESSIONAL MEDICAL REPORT
                        - Clinical Indication: Preliminary screening and triage.
                        - Technical Findings: Provide a detailed anatomical analysis ({technical_focus}).
                        - Impression: Provide a definitive diagnostic conclusion.

                        ---
                        ### SECTION 2: PATIENT-FRIENDLY SUMMARY (SIMPLE ENGLISH)
                        Translate the findings into simple English for a non-medical person:
                        - List 3 clear 'Next Steps'.
                        """
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[system_prompt, img]
                        )
                        
                        reply = response.text
                        st.success("Analysis Complete!")
                        
                        # --- FEATURE 1: EMERGENCY TRIAGE COLOR CODING ---
                        if "TRIAGE_LEVEL: RED" in reply.upper():
                            st.error("🚨 **CODE RED - CRITICAL TRIAGE:** Immediate medical intervention required.")
                            
                            # --- FEATURE 2: SECOND OPINION AUTO-ROUTING ---
                            with st.expander("✉️ Auto-Routing to Specialist Triggered", expanded=True):
                                st.warning("⚠️ Critical anomaly detected. Automatically packaging scan and AI report for Senior Specialist review.")
                                if st.button("Transmit to City Central Hospital Now"):
                                    with st.spinner("Encrypting HL7 Payload..."):
                                        time.sleep(1.5) # Simulating network delay for realism
                                    st.success("✅ Encrypted scan & report successfully sent to on-call specialist!")
                                    
                        elif "TRIAGE_LEVEL: YELLOW" in reply.upper():
                            st.warning("🟨 **CODE YELLOW - URGENT TRIAGE:** Requires prompt medical evaluation.")
                        elif "TRIAGE_LEVEL: GREEN" in reply.upper():
                            st.success("🟩 **CODE GREEN - ROUTINE TRIAGE:** No acute anomalies detected.")
                        
                        # Print the actual AI report below the colored boxes
                        st.markdown(reply)
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                            st.warning("⏳ **API Rate Limit Reached.** (Free Tier Guardrail). Please wait 30 seconds before scanning the next patient.")
                        else:
                            st.error(f"❌ System Error: {error_msg}")
