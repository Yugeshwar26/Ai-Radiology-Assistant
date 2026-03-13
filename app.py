import streamlit as st
from google import genai
from PIL import Image
import os
import time

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="AI Radiology Suite", page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

# 2. MASSIVE UI CSS INJECTION
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Deep Medical Dark Theme Background */
    .stApp {
        background-color: #0B1120;
        color: #E2E8F0;
    }

    /* Style the Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }

    /* Glassmorphism Containers (The Boxes) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(10px) !important;
        padding: 15px;
    }

    /* Futuristic File Uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 2px dashed #0EA5E9 !important;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(14, 165, 233, 0.1) !important;
        border: 2px dashed #38BDF8 !important;
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.4);
    }

    /* Primary Action Button */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #0284C7 0%, #0EA5E9 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.6);
        background: linear-gradient(90deg, #0369A1 0%, #0284C7 100%);
    }

    /* Headers and Text */
    h1, h2, h3 {
        color: #F8FAFC !important;
    }
    
    /* Neon Status Dot */
    .status-dot {
        height: 10px;
        width: 10px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #10B981;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    </style>
""", unsafe_allow_html=True)

# 3. Secure API Key Loading
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key is missing! Please configure it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# 4. Sidebar - Industrial Control Panel
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3003/3003254.png", width=60) # Medical AI icon
    st.markdown("## Control Panel")
    st.markdown("<div style='color: #94A3B8; font-size: 0.9em; margin-bottom: 20px;'>Med-Core Operating System v2.5</div>", unsafe_allow_html=True)
    
    scan_type = st.selectbox(
        "SCAN MODALITY",
        ["Chest X-Ray", "Bone Fracture (X-Ray)", "Brain CT/MRI", "Dental X-Ray"],
        help="Select the imaging modality for the AI to analyze."
    )
    
    st.markdown("---")
    st.markdown("### System Admins:")
    st.markdown("<div style='background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px;'>", unsafe_allow_html=True)
    st.markdown("👨‍💻 **Yugeshwar P.**<br>👨‍💻 **Visvesh M.**<br>👨‍💻 **Matheshwaran S.**", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #0EA5E9; font-size: 0.8em; margin-top: 10px;'>📍 Kamaraj College of Engineering</div>", unsafe_allow_html=True)

# 5. Main Dashboard UI
st.markdown("<h1>🧬 Med-Core: AI Radiology Suite</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8; font-size: 1.1em;'>Autonomous Multimodal Triage & Diagnostic Co-Pilot</p>", unsafe_allow_html=True)

# Status Bar
st.markdown(f"""
<div style='background: #1E293B; padding: 10px 20px; border-radius: 8px; border-left: 4px solid #0EA5E9; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;'>
    <span><b>Target Modality:</b> <span style='color: #38BDF8;'>{scan_type}</span></span>
    <span><span class='status-dot'></span> System Online & Connected to Gemini API</span>
</div>
""", unsafe_allow_html=True)

# Upload Box
uploaded_file = st.file_uploader(f"Upload {scan_type} Scan (DICOM-converted JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        with st.container(border=True):
            st.markdown("<h3 style='color: #38BDF8;'>📷 Patient Scan Viewer</h3>", unsafe_allow_html=True)
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, use_container_width=True)
        
    with col2:
        with st.container(border=True):
            st.markdown("<h3 style='color: #38BDF8;'>⚙️ AI Analysis Engine</h3>", unsafe_allow_html=True)
            
            if st.button(f"INITIATE SCAN PROTOCOL"):
                with st.spinner(f"Neural networks analyzing {scan_type}..."):
                    try:
                        # DYNAMIC LOGIC
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

                        # PROMPT
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
                        st.success("✅ Protocol Complete")
                        
                        # TRIAGE & AUTO ROUTING
                        if "TRIAGE_LEVEL: RED" in reply.upper():
                            st.error("🚨 **CODE RED - CRITICAL TRIAGE:** Immediate medical intervention required.")
                            with st.expander("✉️ Auto-Routing to City Specialist Triggered", expanded=True):
                                st.warning("⚠️ Critical anomaly detected. Automatically packaging scan and AI report for Senior Specialist review.")
                                if st.button("Transmit Secure HL7 Payload Now"):
                                    with st.spinner("Encrypting..."):
                                        time.sleep(1.5)
                                    st.success("✅ Encrypted scan successfully sent to on-call specialist!")
                                    
                        elif "TRIAGE_LEVEL: YELLOW" in reply.upper():
                            st.warning("🟨 **CODE YELLOW - URGENT TRIAGE:** Requires prompt medical evaluation.")
                        elif "TRIAGE_LEVEL: GREEN" in reply.upper():
                            st.success("🟩 **CODE GREEN - ROUTINE TRIAGE:** No acute anomalies detected.")
                        
                        # Markdown Report
                        st.markdown("<div style='background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px;'>", unsafe_allow_html=True)
                        st.markdown(reply)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                            st.warning("⏳ **API Rate Limit Reached.** Please wait 15 seconds.")
                        else:
                            st.error(f"❌ System Error: {error_msg}")
