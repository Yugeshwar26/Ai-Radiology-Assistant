import streamlit as st
from google import genai
from PIL import Image
import os

# 1. Page Configuration (Makes it look wide and professional)
st.set_page_config(page_title="AI Radiologist", page_icon="🩺", layout="wide")

# 2. Secure API Key Loading for Streamlit Cloud
try:
    # This looks for the key in Streamlit Cloud's secure vault
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # Fallback for local testing
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key is missing! Please configure it in Streamlit Secrets.")
    st.stop()

# Initialize the Gemini Client
client = genai.Client(api_key=API_KEY)

# 3. Build the Dashboard UI
st.title("🩺 AI Radiology Assistant (GenAI)")
st.markdown("### PS-4: Radiology Report Generation")
st.markdown("Upload a PA-view Chest X-ray to instantly generate a structured, preliminary medical report.")
st.divider()

# Upload Box
uploaded_file = st.file_uploader("Upload X-Ray Image (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Create two columns: Left for Image, Right for Report
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Uploaded Scan")
        # Open and force RGB to prevent errors
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, use_container_width=True)
        
    with col2:
        st.subheader("Automated AI Report")
        
        # Big Generate Button
        if st.button("Generate Radiology Report", type="primary", use_container_width=True):
            with st.spinner("Analyzing scan and formatting report..."):
                try:
                    system_prompt = """
                    You are an expert radiologist. Analyze this Chest X-ray.
                    Provide a structured report with:
                    **1. Clinical Indication**
                    **2. Findings** (Comment on Lungs, Pleura, Heart Size, and Bones)
                    **3. Impression**
                    Conclude with a bold disclaimer that this is an AI-generated preliminary report.
                    """
                    
                    # Call Gemini 2.5 Flash
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[system_prompt, img]
                    )
                    
                    # Display the report in a nice box
                    st.success("Analysis Complete!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
