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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend & External API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
LATEX_COMPILER_URL = os.getenv("LATEX_COMPILER_URL", "https://latexonline.cc/compile")

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Global Overrides ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
    }

    /* ── Section Headers ── */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.01em;
    }
    .section-header .accent-bar {
        width: 3px;
        height: 18px;
        border-radius: 2px;
        background: #6366F1;
    }
    .section-subheader {
        font-size: 0.875rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
        line-height: 1.45;
    }

    /* ── Flat Card ── */
    .glass-card {
        background: #1E293B;
        border-radius: 8px;
        padding: 24px;
        border: 1px solid #334155;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    .glass-card-sm {
        background: #0F172A;
        border-radius: 6px;
        padding: 16px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }

    /* ── Score Ring ── */
    .score-ring-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        padding: 24px 16px;
    }
    .score-ring {
        position: relative;
        width: 160px;
        height: 160px;
    }
    .score-ring svg {
        transform: rotate(-90deg);
    }
    .score-ring .score-label {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }
    .score-ring .score-value {
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1;
    }
    .score-ring .score-unit {
        font-size: 0.875rem;
        font-weight: 500;
        color: #64748B;
    }
    .score-status {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ── Tag / Badge ── */
    .tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
        margin-bottom: 16px;
    }
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
        transition: transform 0.1s ease;
    }
    .tag-skill {
        background: rgba(99, 102, 241, 0.08);
        color: #A5B4FC;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    .tag-keyword {
        background: rgba(16, 185, 129, 0.08);
        color: #6EE7B7;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    /* ── Info Cards ── */
    .info-card {
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-size: 0.875rem;
        line-height: 1.5;
        border: 1px solid transparent;
    }
    .info-card-strength {
        background: rgba(16, 185, 129, 0.04);
        border: 1px solid rgba(16, 185, 129, 0.15);
        border-left: 4px solid #10B981;
        color: #E2E8F0;
    }
    .info-card-improve {
        background: rgba(245, 158, 11, 0.04);
        border: 1px solid rgba(245, 158, 11, 0.15);
        border-left: 4px solid #F59E0B;
        color: #E2E8F0;
    }

    /* ── Responsibility List ── */
    .resp-list {
        list-style: none;
        padding: 0;
        margin: 8px 0 16px 0;
    }
    .resp-list li {
        padding: 8px 12px;
        margin-bottom: 6px;
        border-radius: 6px;
        background: #1E293B;
        border: 1px solid #334155;
        font-size: 0.85rem;
        color: #CBD5E1;
        line-height: 1.45;
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    .resp-list li .num {
        color: #94A3B8;
        font-size: 0.75rem;
        font-weight: 600;
        width: 18px;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        flex-shrink: 0;
    }

    /* ── Experience Badge ── */
    .exp-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 4px;
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.25);
        font-size: 0.75rem;
        font-weight: 500;
        color: #C7D2FE;
        margin-top: 4px;
    }

    /* ── Cover Letter Output ── */
    .cover-header {
        background: rgba(99, 102, 241, 0.04);
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid rgba(99, 102, 241, 0.15);
        margin-bottom: 16px;
    }
    .cover-header .cover-meta {
        font-size: 0.875rem;
        color: #94A3B8;
        line-height: 1.45;
    }
    .cover-header .cover-meta strong {
        color: #A5B4FC;
    }

    /* ── Divider ── */
    .styled-divider {
        border: none;
        height: 1px;
        background: rgba(255, 255, 255, 0.06);
        margin: 20px 0;
    }

    /* ── Sidebar styling ── */
    section[data-testid="stSidebar"] .stMarkdown h1 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }

    /* ── Label tweaks ── */
    .cat-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Helper: extract text from PDF ──
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

# ── Helper: build score ring SVG ──
def build_score_ring(score, color):
    radius = 68
    circumference = 2 * 3.14159 * radius
    offset = circumference - (score / 100) * circumference
    if score >= 80:
        status_text, status_bg = "Excellent Match", "rgba(16,185,129,0.08)"
        status_color = "#10B981"
    elif score >= 60:
        status_text, status_bg = "Good Match", "rgba(245,158,11,0.08)"
        status_color = "#F59E0B"
    elif score >= 40:
        status_text, status_bg = "Moderate Match", "rgba(245,158,11,0.08)"
        status_color = "#F59E0B"
    else:
        status_text, status_bg = "Needs Improvement", "rgba(239,68,68,0.08)"
        status_color = "#EF4444"
    
    return f"""
    <div class="glass-card">
        <div class="score-ring-container">
            <div class="score-ring">
                <svg width="160" height="160">
                    <circle cx="80" cy="80" r="{radius}" fill="none" stroke="rgba(51,65,85,0.3)" stroke-width="8"/>
                    <circle cx="80" cy="80" r="{radius}" fill="none" stroke="{color}" stroke-width="8"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                        stroke-linecap="round" style="transition: stroke-dashoffset 1s ease;"/>
                </svg>
                <div class="score-label">
                    <div class="score-value" style="color: {color};">{score}</div>
                    <div class="score-unit">/ 100</div>
                </div>
            </div>
            <div class="score-status" style="background: {status_bg}; color: {status_color};">
                {status_text}
            </div>
        </div>
    </div>
    """

def build_comparative_scores(score_before, score_after):
    radius = 50
    circumference = 2 * 3.14159 * radius
    
    offset_before = circumference - (score_before / 100) * circumference
    offset_after = circumference - (score_after / 100) * circumference
    
    def get_color_details(score):
        if score >= 80:
            return "#10B981", "rgba(16,185,129,0.08)", "Excellent Match"
        elif score >= 60:
            return "#F59E0B", "rgba(245,158,11,0.08)", "Good Match"
        elif score >= 40:
            return "#F59E0B", "rgba(245,158,11,0.08)", "Moderate Match"
        else:
            return "#EF4444", "rgba(239,68,68,0.08)", "Needs Improvement"
            
    color_before, bg_before, status_before = get_color_details(score_before)
    color_after, bg_after, status_after = get_color_details(score_after)
    
    diff = score_after - score_before
    diff_indicator = ""
    if diff > 0:
        diff_indicator = f'<div style="font-size:0.95rem;font-weight:600;color:#10B981;margin-top:6px;">+{diff}% Alignment Gain</div>'
    elif diff < 0:
        diff_indicator = f'<div style="font-size:0.95rem;font-weight:600;color:#EF4444;margin-top:6px;">{diff}% Alignment Loss</div>'
    else:
        diff_indicator = f'<div style="font-size:0.95rem;font-weight:600;color:#94A3B8;margin-top:6px;">No Delta</div>'
        
    return f'<div class="glass-card"><div style="text-align:center;font-weight:600;color:#F1F5F9;font-size:0.95rem;margin-bottom:20px;text-transform:uppercase;letter-spacing:0.05em;">Alignment Comparative Report</div><div style="display:flex;justify-content:space-around;align-items:center;gap:15px;flex-wrap:wrap;"><div style="display:flex;flex-direction:column;align-items:center;gap:8px;"><div style="font-size:0.75rem;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.05em;">Original Resume</div><div class="score-ring" style="width:120px;height:120px;position:relative;"><svg width="120" height="120" viewBox="0 0 120 120"><circle cx="60" cy="60" r="{radius}" fill="none" stroke="rgba(51,65,85,0.3)" stroke-width="6"/><circle cx="60" cy="60" r="{radius}" fill="none" stroke="{color_before}" stroke-width="6" stroke-dasharray="{circumference}" stroke-dashoffset="{offset_before}" stroke-linecap="round" transform="rotate(-90 60 60)" style="transition:stroke-dashoffset 1s ease;"/></svg><div class="score-label" style="top:50%;left:50%;transform:translate(-50%,-50%);position:absolute;text-align:center;"><div class="score-value" style="color:{color_before};font-size:1.8rem;font-weight:700;line-height:1;">{score_before}</div><div class="score-unit" style="font-size:0.7rem;color:#64748B;">/ 100</div></div></div><div class="score-status" style="background:{bg_before};color:{color_before};font-size:0.7rem;padding:2px 10px;">{status_before}</div></div><div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:100px;"><div style="font-size:1.5rem;color:#6366F1;line-height:1;font-weight:300;">&rarr;</div>{diff_indicator}</div><div style="display:flex;flex-direction:column;align-items:center;gap:8px;"><div style="font-size:0.75rem;font-weight:600;color:#A5B4FC;text-transform:uppercase;letter-spacing:0.05em;">Optimized Resume</div><div class="score-ring" style="width:120px;height:120px;position:relative;"><svg width="120" height="120" viewBox="0 0 120 120"><circle cx="60" cy="60" r="{radius}" fill="none" stroke="rgba(51,65,85,0.3)" stroke-width="6"/><circle cx="60" cy="60" r="{radius}" fill="none" stroke="{color_after}" stroke-width="6" stroke-dasharray="{circumference}" stroke-dashoffset="{offset_after}" stroke-linecap="round" transform="rotate(-90 60 60)" style="transition:stroke-dashoffset 1s ease;"/></svg><div class="score-label" style="top:50%;left:50%;transform:translate(-50%,-50%);position:absolute;text-align:center;"><div class="score-value" style="color:{color_after};font-size:1.8rem;font-weight:700;line-height:1;">{score_after}</div><div class="score-unit" style="font-size:0.7rem;color:#64748B;">/ 100</div></div></div><div class="score-status" style="background:{bg_after};color:{color_after};font-size:0.7rem;padding:2px 10px;">{status_after}</div></div></div></div>'

def compile_latex_to_pdf_online(latex_code: str):
    # Helper to execute sync post request compiling LaTeX source code to a PDF binary
    try:
        response = requests.post(LATEX_COMPILER_URL, files={"file": ("main.tex", latex_code)}, timeout=30)
        if response.status_code == 200 and response.headers.get("content-type") == "application/pdf":
            return response.content, None
        else:
            error_log = response.text[:2500] if response.text else "No compiler logs returned."
            return None, f"LaTeX Compilation Error (Status Code: {response.status_code}).\n\nCompiler Log:\n{error_log}"
    except Exception as e:
        return None, f"Could not reach LaTeX compilation service: {str(e)}"

# ── Helper: render tags ──
def render_tags(items, tag_class="tag-skill"):
    tags = "".join([f'<span class="tag {tag_class}">{item}</span>' for item in items])
    return f'<div class="tag-container">{tags}</div>'

# ── Helper: render numbered list ──
def render_resp_list(items):
    lis = "".join([f'<li><span class="num">{i+1}</span><span>{item}</span></li>' for i, item in enumerate(items)])
    return f'<ul class="resp-list">{lis}</ul>'

# ── Helper: render info cards ──
def render_info_cards(items, card_type="strength"):
    css_class = f"info-card-{card_type}" if card_type == "strength" else "info-card-improve"
    cards = "".join([
        f'<div class="info-card {css_class}"><span>{item}</span></div>'
        for item in items
    ])
    return cards

# ── Verify backend ──
backend_online = False
try:
    response = requests.get(f"{BACKEND_URL}/", timeout=3)
    if response.status_code == 200:
        backend_online = True
except Exception:
    backend_online = False

# ── Sidebar ──
with st.sidebar:
    st.markdown("## AI Job Assistant")
    st.caption("Advanced resume engineering and analytics.")
    
    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
    
    st.markdown("#### Connection Status")
    if backend_online:
        st.success("API Backend Online")
    else:
        st.error("API Backend Offline")
        st.warning("Start the backend via uvicorn")

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    st.markdown("#### Features")
    st.markdown("""
    * **Match Engine**: Computes ATS alignment score.
    * **Extraction**: Structural parsing of job details.
    * **Tailoring Insights**: Detailed gap and strength analysis.
    * **Outreach**: Automated professional cover message.
    """)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
    st.caption("Engine: Llama 3.3 · Groq SDK")

# ── Main Title ──
st.markdown("""
<div style="margin-bottom: 12px; letter-spacing: -0.02em;">
    <h1 style="font-size: 2.2rem; font-weight: 700; color: #F8FAFC; margin: 0; padding: 0; line-height: 1.2;">
        Resume Alignment Engine
    </h1>
    <p style="color: #94A3B8; font-size: 0.95rem; margin-top: 8px; font-weight: 400; line-height: 1.5; max-width: 800px;">
        Analyze resume ATS score against target job description, identify explicit requirements, generate structured tailoring feedback, and produce customized PDF resumes and cover letters.
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

if not backend_online:
    st.error("Unable to reach the FastAPI backend.")
    st.info("Ensure the backend service is running locally on port 8000:")
    st.code("uvicorn app.main:app --reload --port 8000")
    st.stop()

# ── Layout ──
col_inputs, col_spacer, col_results = st.columns([4, 0.3, 5])

with col_inputs:
    st.markdown("""
    <div class="section-header"><span class="accent-bar"></span>Inputs</div>
    <div class="section-subheader">Provide the job listing and your resume to get started.</div>
    """, unsafe_allow_html=True)
    
    jd_input = st.text_area(
        "Job Description *",
        placeholder="Paste the full job description here...",
        height=200,
        help="Copy-paste the complete job posting including responsibilities and requirements."
    )
    
    resume_file = st.file_uploader("Resume (PDF or TXT) *", type=["pdf", "txt"])
    
    resume_text = ""
    if resume_file is not None:
        if resume_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_file)
        else:
            resume_text = resume_file.read().decode("utf-8")
        st.success(f"Loaded: **{resume_file.name}**")

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header"><span class="accent-bar"></span>Cover Letter Details</div>
    <div class="section-subheader">Enter target company and position details.</div>
    """, unsafe_allow_html=True)

    col_company, col_role = st.columns(2)
    with col_company:
        company_name = st.text_input("Company Name *", placeholder="e.g. Netflix")
    with col_role:
        role_name = st.text_input("Role / Position *", placeholder="e.g. Senior Frontend Dev")

    st.markdown("")  # spacer
    analyze_button = st.button(
        "Analyze & Optimize",
        type="primary",
        use_container_width=True
    )

with col_results:
    st.markdown("""
    <div class="section-header"><span class="accent-bar"></span>Results</div>
    <div class="section-subheader">Your evaluation report and generated assets will appear here.</div>
    """, unsafe_allow_html=True)

    if not analyze_button:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px 30px;">
            <div style="font-size: 1rem; font-weight: 600; color: #E2E8F0; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em;">Awaiting Analysis</div>
            <div style="font-size: 0.88rem; color: #64748B; line-height: 1.6;">
                Provide the job description, upload your resume, and enter target company info on the left, then click <strong>Analyze & Optimize</strong> to run.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if not jd_input:
            st.error("Please paste a job description first.")
        elif not resume_text:
            st.error("Please upload your resume (PDF or TXT) first.")
        elif "Error" in resume_text:
            st.error(resume_text)
        elif not company_name or not role_name:
            st.error("Please enter both Company Name and Role.")
        else:
            with st.spinner("Analyzing resume, matching requirements, and generating tailored assets..."):
                # 1. JD requirements
                jd_payload = {"job_description": jd_input}
                jd_res = requests.post(f"{BACKEND_URL}/api/parse-jd", json=jd_payload)
                
                # 2. Original Resume match
                match_payload = {"resume_text": resume_text, "job_description": jd_input}
                match_res = requests.post(f"{BACKEND_URL}/api/analyze-resume", json=match_payload)
                
                # 3. Cover letter
                cv_payload = {
                    "resume_text": resume_text,
                    "job_description": jd_input,
                    "company_name": company_name,
                    "role": role_name
                }
                cv_res = requests.post(f"{BACKEND_URL}/api/generate-cover-message", json=cv_payload)

                # 4. Tailored Resume Generation
                resume_payload = {
                    "resume_text": resume_text,
                    "job_description": jd_input,
                    "company_name": company_name,
                    "role": role_name
                }
                resume_res = requests.post(f"{BACKEND_URL}/api/generate-tailored-resume", json=resume_payload)

                if jd_res.status_code == 200 and match_res.status_code == 200 and resume_res.status_code == 200:
                    jd_data = jd_res.json()
                    match_data = match_res.json()
                    resume_data = resume_res.json()

                    if "error" in match_data:
                        st.error(f"Analysis failed: {match_data.get('details')}")
                        st.code(match_data.get("raw_response"))
                    elif "error" in resume_data:
                        st.error(f"Resume Tailoring failed: {resume_data.get('error')}")
                        if "details" in resume_data:
                            st.code(resume_data.get("raw_response"))
                    else:
                        match_score_before = match_data.get("match_percentage", 0)
                        
                        # 5. Compute optimized match score on optimized resume text
                        opt_resume_text = resume_data.get("optimized_resume_text", "")
                        match_score_after = match_score_before # fallback
                        
                        if opt_resume_text:
                            opt_match_payload = {"resume_text": opt_resume_text, "job_description": jd_input}
                            opt_match_res = requests.post(f"{BACKEND_URL}/api/analyze-resume", json=opt_match_payload)
                            if opt_match_res.status_code == 200:
                                opt_match_data = opt_match_res.json()
                                match_score_after = opt_match_data.get("match_percentage", 0)

                        # 6. Compile LaTeX to PDF online
                        pdf_bytes = None
                        pdf_error = None
                        latex_code = resume_data.get("optimized_latex_code", "")
                        
                        if latex_code and latex_code != "% No LaTeX generated.":
                            with st.spinner("Compiling tailored resume to PDF..."):
                                pdf_bytes, pdf_error = compile_latex_to_pdf_online(latex_code)

                        # ── Comparative Score Ring ──
                        st.markdown(build_comparative_scores(match_score_before, match_score_after), unsafe_allow_html=True)

                        # ── Result Sub-Tabs ──
                        tab_req, tab_tips, tab_resume, tab_cover = st.tabs([
                            "Requirements",
                            "AI Insights",
                            "Tailored Resume",
                            "Cover Letter"
                        ])

                        # ── Tab: Requirements ──
                        with tab_req:
                            # Skills
                            skills = jd_data.get("skills", [])
                            st.markdown('<p class="cat-label">Core Skills Required</p>', unsafe_allow_html=True)
                            if skills:
                                st.markdown(render_tags(skills, "tag-skill"), unsafe_allow_html=True)
                            else:
                                st.caption("No skills extracted.")

                            # Keywords
                            keywords = jd_data.get("keywords", [])
                            st.markdown('<p class="cat-label">Important Keywords</p>', unsafe_allow_html=True)
                            if keywords:
                                st.markdown(render_tags(keywords, "tag-keyword"), unsafe_allow_html=True)
                            else:
                                st.caption("No keywords extracted.")

                            # Experience
                            exp = jd_data.get("experience_level", "Not specified")
                            st.markdown('<p class="cat-label">Experience Level</p>', unsafe_allow_html=True)
                            st.markdown(f'<div class="exp-badge">{exp}</div>', unsafe_allow_html=True)
                            st.markdown("")  # spacer

                            # Responsibilities
                            resps = jd_data.get("responsibilities", [])
                            st.markdown('<p class="cat-label">Key Responsibilities</p>', unsafe_allow_html=True)
                            if resps:
                                st.markdown(render_resp_list(resps), unsafe_allow_html=True)
                            else:
                                st.caption("No responsibilities extracted.")

                        # ── Tab: AI Insights ──
                        with tab_tips:
                            strengths = match_data.get("strengths", [])
                            improvements = match_data.get("improvements", [])

                            # Render the optimized changes
                            st.markdown('<p class="cat-label">Resume Tailoring Modifications</p>', unsafe_allow_html=True)
                            changes = resume_data.get("changes", [])
                            if changes:
                                changes_html = ""
                                for change in changes:
                                    action = change.get("action", "OPTIMIZED").upper()
                                    section = change.get("section", "General")
                                    detail = change.get("detail", "")
                                    reason = change.get("reason", "")
                                    
                                    if action == "ADDED":
                                        action_badge = '<span style="background: rgba(16,185,129,0.08); color: #10B981; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">ADDED</span>'
                                    elif action == "REMOVED":
                                        action_badge = '<span style="background: rgba(239,68,68,0.08); color: #EF4444; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">REMOVED</span>'
                                    else:
                                        action_badge = '<span style="background: rgba(245,158,11,0.08); color: #F59E0B; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">OPTIMIZED</span>'
                                        
                                    changes_html += f"""
                                    <div style="background: #1E293B; border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                                            <strong style="color: #E2E8F0; font-size: 0.88rem;">{section}</strong>
                                            {action_badge}
                                        </div>
                                        <div style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 4px;"><strong>Change:</strong> {detail}</div>
                                        <div style="font-size: 0.82rem; color: #94A3B8;"><strong>Why:</strong> {reason}</div>
                                    </div>
                                    """
                                st.markdown(changes_html, unsafe_allow_html=True)
                            else:
                                st.caption("No specific modifications listed.")

                            st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

                            st.markdown('<p class="cat-label">Your Strengths</p>', unsafe_allow_html=True)
                            if strengths:
                                st.markdown(render_info_cards(strengths, "strength"), unsafe_allow_html=True)
                            else:
                                st.caption("No strengths identified.")

                        # ── Tab: Tailored Resume ──
                        with tab_resume:
                            st.markdown('<p class="cat-label">Tailored Resume Preview</p>', unsafe_allow_html=True)

                            if pdf_bytes:
                                # Action buttons
                                st.download_button(
                                    label="Download Tailored PDF",
                                    data=pdf_bytes,
                                    file_name=f"{company_name.lower().replace(' ', '_')}_{role_name.lower().replace(' ', '_')}_resume.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                                
                                # Visual PDF Previewer (iframe base64)
                                import base64
                                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="850" type="application/pdf" style="border:1px solid rgba(100,116,139,0.25); border-radius:12px; margin-top:5px;"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                            else:
                                if pdf_error:
                                    st.warning("Live PDF Preview is currently unavailable.")
                                    with st.expander("View LaTeX Compilation Error Log"):
                                        st.code(pdf_error, language="text")
                                else:
                                    st.warning("LaTeX compilation did not return a valid PDF. Use the LaTeX source below for manual compilation.")
                                
                            st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
                            st.markdown('<p class="cat-label">Tailored LaTeX Code Source</p>', unsafe_allow_html=True)
                            st.code(latex_code, language="latex")

                        # ── Tab: Cover Letter ──
                        with tab_cover:
                            if cv_res.status_code == 200:
                                cv_data = cv_res.json()
                                if "error" in cv_data:
                                    st.error(f"Cover letter generation failed: {cv_data.get('details')}")
                                    st.code(cv_data.get("raw_response"))
                                else:
                                    cover_letter = cv_data.get("cover_message", "No letter was generated.")
                                    st.markdown(f"""
                                    <div class="cover-header">
                                        <div class="cover-meta">
                                            Tailored for <strong>{role_name}</strong> at <strong>{company_name}</strong>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.text_area(
                                        "Your Tailored Cover Letter",
                                        value=cover_letter,
                                        height=380,
                                        key="generated_letter",
                                        label_visibility="collapsed"
                                    )
                                    st.caption("Copy the text above into your application portal.")
                            else:
                                st.error("Cover letter generation failed. Analysis completed but the cover letter service had an issue.")
                else:
                    st.error("Error communicating with AI services. Check that the backend is running.")

