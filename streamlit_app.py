import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load env variables if present
load_dotenv()

# We can import PdfReader safely
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# App configuration
st.set_page_config(
    page_title="AI Job Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Apply custom dark theme styles
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border: 1px solid #334155;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #6366F1;
        margin-bottom: 0.25rem;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94A3B8;
        font-weight: 500;
    }
    /* Section Headers */
    .section-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 1rem;
        border-left: 4px solid #6366F1;
        padding-left: 10px;
    }
    /* Custom subheader */
    .section-subheader {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    if PdfReader is None:
        return "Error: pypdf library is not installed."
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"

# Verify if backend is reachable
backend_online = False
try:
    response = requests.get(f"{BACKEND_URL}/")
    if response.status_code == 200:
        backend_online = True
except Exception:
    backend_online = False

# Sidebar
with st.sidebar:
    st.title("💼 AI Job Assistant")
    st.subheader("Your ultimate career companion")
    
    st.markdown("---")
    st.markdown("### Status Connection")
    if backend_online:
        st.success("API Backend: Connected")
    else:
        st.error("API Backend: Disconnected")
        st.warning("Please start the FastAPI server: `uvicorn app.main:app --reload`")

    st.markdown("---")
    st.markdown("""
    ### Features included:
    - **Resume Match Score**: Instantly see how well your resume matches a target job.
    - **Resume Optimizer**: Get concrete suggestions on how to tailor your resume.
    - **JD Analyzer**: Automatically extract core skills, keywords, and tasks.
    - **Cover Letter**: Auto-generate a tailored cover letter with your analysis.
    """)

# Main Title
st.title("🚀 Career Copilot & Resume Optimizer")
st.markdown("Optimize your resume, extract requirements, and generate cover letters in one unified space.")
st.markdown("---")

if not backend_online:
    st.error("### Unable to communicate with the FastAPI backend.")
    st.info("The application requires the FastAPI backend to run. Please run the following command in your terminal and reload this page:")
    st.code("uvicorn app.main:app --reload --port 8000")
    st.stop()

# Single unified tab
st.markdown("<div class='section-header'>Resume Matcher & AI Optimizer</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subheader'>Compare your resume against any job description. Get match scores, optimization tips, and a tailored cover letter — all in one place.</div>", unsafe_allow_html=True)

col_inputs, col_results = st.columns([1, 1])

with col_inputs:
    st.subheader("📝 Inputs")
    
    # Job Description input
    jd_input = st.text_area("Paste Job Description*", placeholder="Paste the full job description details here...", height=200)
    
    # Resume file uploader
    resume_file = st.file_uploader("Upload Resume (PDF or TXT)*", type=["pdf", "txt"])
    
    resume_text = ""
    if resume_file is not None:
        if resume_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_file)
        else:
            resume_text = resume_file.read().decode("utf-8")
        st.success(f"Successfully loaded: {resume_file.name}")

    st.markdown("---")
    st.subheader("🏢 Cover Letter Details")
    
    col_company, col_role = st.columns(2)
    with col_company:
        company_name = st.text_input("Company Name*", placeholder="e.g. Netflix")
    with col_role:
        role_name = st.text_input("Role / Position*", placeholder="e.g. Senior Frontend Developer")

    analyze_button = st.button("🎯 Analyze, Optimize & Generate Cover Letter", type="primary", use_container_width=True)

with col_results:
    st.subheader("📊 Evaluation Report")
    if not analyze_button:
        st.info("Fill out the job description, upload your resume, and enter the company name & role on the left, then click the button to view your full evaluation report and cover letter.")
    else:
        if not jd_input:
            st.error("Please paste a job description first.")
        elif not resume_text:
            st.error("Please upload your resume (PDF or TXT) first.")
        elif "Error" in resume_text:
            st.error(resume_text)
        elif not company_name or not role_name:
            st.error("Please enter both Company Name and Role to generate the cover letter.")
        else:
            with st.spinner("Analyzing requirements, calculating match metrics & generating cover letter..."):
                # 1. Fetch JD requirements
                jd_payload = {"job_description": jd_input}
                jd_res = requests.post(f"{BACKEND_URL}/api/parse-jd", json=jd_payload)
                
                # 2. Fetch Resume matching score and improvement tips
                match_payload = {
                    "resume_text": resume_text,
                    "job_description": jd_input
                }
                match_res = requests.post(f"{BACKEND_URL}/api/analyze-resume", json=match_payload)
                
                # 3. Generate cover letter
                cv_payload = {
                    "resume_text": resume_text,
                    "job_description": jd_input,
                    "company_name": company_name,
                    "role": role_name
                }
                cv_res = requests.post(f"{BACKEND_URL}/api/generate-cover-message", json=cv_payload)
                
                if jd_res.status_code == 200 and match_res.status_code == 200:
                    jd_data = jd_res.json()
                    match_data = match_res.json()
                    
                    # Check for API Errors
                    if "error" in match_data:
                        st.error(f"Analysis failed: {match_data.get('details')}")
                        st.text("Raw Response:")
                        st.code(match_data.get("raw_response"))
                    else:
                        # Render Match Score
                        match_score = match_data.get("match_percentage", 0)
                        
                        score_color = "#EF4444"
                        if match_score >= 80:
                            score_color = "#10B981"
                        elif match_score >= 50:
                            score_color = "#F59E0B"
                            
                        st.markdown(f"""
                        <div style='background-color: #1E293B; border-radius: 12px; padding: 25px; border: 1px solid #334155; text-align: center; margin-bottom: 20px;'>
                            <div style='font-size: 1.1rem; color: #94A3B8; font-weight: 500; margin-bottom: 5px;'>MATCH RATING</div>
                            <div style='font-size: 3.8rem; font-weight: 800; color: {score_color}; line-height: 1;'>{match_score}%</div>
                            <div style='margin-top: 10px; height: 10px; background-color: #334155; border-radius: 5px; overflow: hidden;'>
                                <div style='height: 100%; width: {match_score}%; background-color: {score_color}; border-radius: 5px;'></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Create nested tabs: Requirements, Suggestions, and Cover Letter
                        res_tab_requirements, res_tab_feedback, res_tab_cover = st.tabs([
                            "📌 Key Requirements", 
                            "💡 AI Suggestions", 
                            "✍️ Cover Letter"
                        ])
                        
                        with res_tab_requirements:
                            st.markdown("#### Core Skills Needed:")
                            for skill in jd_data.get("skills", ["None extracted"]):
                                st.markdown(f"- **{skill}**")
                                
                            st.markdown("#### Primary Responsibilities:")
                            for resp in jd_data.get("responsibilities", ["None extracted"]):
                                st.markdown(f"- {resp}")
                                
                            st.markdown("#### Experience Level:")
                            st.info(jd_data.get("experience_level", "Not explicitly specified"))
                            
                            st.markdown("#### Important Keywords:")
                            if jd_data.get("keywords"):
                                st.write(", ".join([f"`{kw}`" for kw in jd_data.get("keywords")]))
                            else:
                                st.write("None")

                        with res_tab_feedback:
                            st.markdown("#### 💪 Key Strengths Found:")
                            for strength in match_data.get("strengths", ["No major matches found"]):
                                st.success(strength)
                                
                            st.markdown("#### 🛠️ Recommended Resume Enhancements:")
                            for imp in match_data.get("improvements", ["Your profile matches this job description perfectly!"]):
                                st.info(imp)

                        with res_tab_cover:
                            if cv_res.status_code == 200:
                                cv_data = cv_res.json()
                                if "error" in cv_data:
                                    st.error(f"Cover letter generation failed: {cv_data.get('details')}")
                                    st.code(cv_data.get("raw_response"))
                                else:
                                    cover_letter = cv_data.get("cover_message", "No letter was generated.")
                                    st.markdown(f"""
                                    <div style='background-color: #1E293B; border-radius: 12px; padding: 20px; border: 1px solid #334155; margin-bottom: 15px;'>
                                        <div style='font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;'>
                                            Generated for <strong style='color: #6366F1;'>{role_name}</strong> at <strong style='color: #6366F1;'>{company_name}</strong>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.text_area("Your Tailored Cover Letter:", value=cover_letter, height=400, key="generated_letter")
                                    st.info("💡 You can select the text above and copy it directly to your clipboard.")
                            else:
                                st.error("Error generating cover letter. The analysis completed but the cover letter service encountered an issue.")
                else:
                    st.error("Error communicating with AI services.")
