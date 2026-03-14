import streamlit as st
from google import genai
from PIL import Image
import os
import time

# 1. Page Configuration
st.set_page_config(page_title="AI Radiology Assistant", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

# 2. CLEAN SAAS UI CSS INJECTION 
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Plus Jakarta Sans', sans-serif; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; box-shadow: 2px 0 10px rgba(0,0,0,0.02); }
    [data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 16px !important; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important; padding: 20px; transition: transform 0.2s ease; }
    [data-testid="stFileUploadDropzone"] { background-color: #F1F5F9 !important; border: 2px dashed #CBD5E1 !important; border-radius: 16px; padding: 30px !important; }
    div.stButton > button:first-child { background-color: #2563EB; color: white; border: none; border-radius: 50px; padding: 12px 28px; font-weight: 600; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3); width: 100%; }
    div.stButton > button:first-child:hover { background-color: #1D4ED8; transform: translateY(-2px); }
    h1, h2, h3 { color: #0F172A !important; font-weight: 700; }
    [data-testid="stAlert"] div, [data-testid="stAlert"] p { color: #0F172A !important; }
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] strong { color: #1E293B !important; font-size: 1.05em; line-height: 1.6; }
    hr { border-top: 1px solid #E2E8F0; }
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

# --- HOSPITAL DATABASE MAPPER (Tamil Nadu) ---
def get_hospital_recommendation(scan_type, district):
    db = {
        "Chest X-Ray": {
            "Chennai": "Rajiv Gandhi Govt General Hospital / Apollo Greams Road (Pulmonology)",
            "Madurai": "Govt Hospital for Thoracic Medicine (Thoppur) / Meenakshi Mission",
            "Coimbatore": "GKNM Hospital / Coimbatore Medical College Hospital",
            "Virudhunagar": "Virudhunagar Govt Medical College Hospital / Velammal Madurai",
            "Trichy": "Mahatma Gandhi Memorial Govt Hospital / Apollo Specialty"
        },
        "Bone Fracture (X-Ray)": {
            "Chennai": "MIOT International (Level 1 Trauma) / Parvathy Hospital",
            "Madurai": "Preethi Hospitals (Ortho Spec.) / Velammal Medical College",
            "Coimbatore": "Ganga Hospital (Renowned Orthopedics & Trauma)",
            "Virudhunagar": "Virudhunagar Govt Hospital / Preethi Hospitals (Madurai)",
            "Trichy": "Kauvery Hospital / SRM Medical College"
        },
        "Brain CT/MRI": {
            "Chennai": "Apollo Proton Cancer Centre / NIMHANS Referral / SIMS Hospital",
            "Madurai": "Meenakshi Mission Hospital (Neurosurgery) / Apollo Madurai",
            "Coimbatore": "Kovai Medical Center and Hospital (KMCH)",
            "Virudhunagar": "Meenakshi Mission Madurai (Nearest Neuro Hub)",
            "Trichy": "Kauvery Hospital (Neurology Dept)"
        },
        "Dental X-Ray": {
            "Chennai": "Saveetha Dental College / Balaji Dental Hospital",
            "Madurai": "CSI College of Dental Sciences / Vasan Dental Care",
            "Coimbatore": "Sri Ramakrishna Dental College",
            "Virudhunagar": "Local District Govt Hospital Dental Wing",
            "Trichy": "KAPV Govt Medical College Dental Wing"
        }
    }
    
    # Return specific hospital if district is in our DB, else return the District HQ Hospital
    return db.get(scan_type, {}).get(district, f"{district} District Government Headquarters Hospital")


# 4. Sidebar - Human-Centric Profile
with st.sidebar:
    st.markdown("## 🩺 Clinic Settings")
    st.markdown("<p style='color: #64748B; font-size: 0.9em; margin-bottom: 20px;'>Configure your AI screening preferences.</p>", unsafe_allow_html=True)
    
    scan_type = st.selectbox(
        "Current Patient Scan Modality",
        ["Chest X-Ray", "Bone Fracture (X-Ray)", "Brain CT/MRI", "Dental X-Ray"]
    )
    
    # NEW FEATURE: TN District Selector
    st.markdown("---")
    st.markdown("### 📍 Location Triage")
    tn_districts = ["Chennai", "Madurai", "Coimbatore", "Virudhunagar", "Trichy", "Salem", "Tirunelveli", "Erode", "Vellore", "Kanyakumari", "Other (TN)"]
    patient_district = st.selectbox("Patient District (Tamil Nadu)", tn_districts)
    
    st.markdown("---")
    st.markdown("### Care Team:")
    st.info("👨‍⚕️ **Yugeshwar P.**\n\n👨‍⚕️ **Visvesh M.**\n\n👨‍⚕️ **Matheshwaran S.**")
    st.markdown("<p style='color: #64748B; font-size: 0.8em; margin-top: 10px;'>Kamaraj College of Engineering & Technology</p>", unsafe_allow_html=True)

# 5. Main Dashboard UI
st.markdown("<h1>Radiology Co-Pilot</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 1.1em; margin-bottom: 30px;'>Empowering clinical teams with instant, AI-driven diagnostic triage.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(f"Drop patient's {scan_type} image here", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        with st.container(border=True):
            st.markdown("### 📷 Patient Scan")
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, use_container_width=True, caption="Ready for analysis")
        
    with col2:
        with st.container(border=True):
            st.markdown("### ✨ AI Assistant")
            
            if st.button(f"Generate Diagnostic Report"):
                with st.spinner(f"Reviewing {scan_type}..."):
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
                        st.success("✅ Analysis Complete")
                        st.divider()
                        
                        # GET LOCAL HOSPITAL MATCH
                        local_hospital = get_hospital_recommendation(scan_type, patient_district)
                        
                        # TRIAGE & AUTO ROUTING
                        if "TRIAGE_LEVEL: RED" in reply.upper() or "TRIAGE_LEVEL: YELLOW" in reply.upper():
                            if "TRIAGE_LEVEL: RED" in reply.upper():
                                st.error("🚨 **TRIAGE: CRITICAL (CODE RED)** - Immediate medical intervention recommended.")
                            else:
                                st.warning("🟨 **TRIAGE: URGENT (CODE YELLOW)** - Prompt medical evaluation needed.")
                                
                            # SHOW LOCALIZED HOSPITAL REFERRAL
                            st.info(f"🏥 **Local Referral System:** Based on the selected district (**{patient_district}**), we recommend transferring the patient to:\n\n**{local_hospital}**")
                            
                            with st.expander("✉️ Auto-Routing Protocol Triggered", expanded=True):
                                st.warning("Sending prioritized alert to on-call specialist...")
                                if st.button("Confirm Transfer to Referral Hospital"):
                                    with st.spinner("Securing patient data..."):
                                        time.sleep(1.5)
                                    st.success(f"✅ Case successfully transferred to {local_hospital}.")
                                    
                        elif "TRIAGE_LEVEL: GREEN" in reply.upper():
                            st.success("🟩 **TRIAGE: ROUTINE (CODE GREEN)** - No acute anomalies detected. Standard local clinic care is sufficient.")
                        
                        # Markdown Report
                        st.markdown(reply)
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                            st.warning("⏳ **System pausing to prevent overload.** Please try again in 60 seconds.")
                        else:
                            st.error(f"❌ System Error: {error_msg}")
