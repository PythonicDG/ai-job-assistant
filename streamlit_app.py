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
        font-size: 1.5rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-header .accent-bar {
        width: 4px;
        height: 28px;
        border-radius: 4px;
        background: linear-gradient(180deg, #818CF8, #6366F1);
    }
    .section-subheader {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }

    /* ── Glass Card ── */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(100, 116, 139, 0.25);
        margin-bottom: 16px;
    }
    .glass-card-sm {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid rgba(100, 116, 139, 0.2);
        margin-bottom: 12px;
    }

    /* ── Score Ring ── */
    .score-ring-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        padding: 30px 20px;
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
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1;
    }
    .score-ring .score-unit {
        font-size: 1rem;
        font-weight: 600;
        color: #94A3B8;
    }
    .score-status {
        font-size: 0.85rem;
        font-weight: 600;
        padding: 4px 14px;
        border-radius: 20px;
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
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .tag:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .tag-skill {
        background: rgba(99, 102, 241, 0.15);
        color: #A5B4FC;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .tag-keyword {
        background: rgba(16, 185, 129, 0.12);
        color: #6EE7B7;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    /* ── Info Cards for Strengths / Improvements ── */
    .info-card {
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        font-size: 0.88rem;
        line-height: 1.55;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .info-card .icon {
        font-size: 1.2rem;
        flex-shrink: 0;
        margin-top: 1px;
    }
    .info-card-strength {
        background: rgba(16, 185, 129, 0.08);
        border-left: 3px solid #10B981;
        color: #D1FAE5;
    }
    .info-card-improve {
        background: rgba(245, 158, 11, 0.08);
        border-left: 3px solid #F59E0B;
        color: #FEF3C7;
    }

    /* ── Responsibility List ── */
    .resp-list {
        list-style: none;
        padding: 0;
        margin: 8px 0 16px 0;
    }
    .resp-list li {
        padding: 10px 14px;
        margin-bottom: 6px;
        border-radius: 10px;
        background: rgba(51, 65, 85, 0.4);
        border: 1px solid rgba(71, 85, 105, 0.3);
        font-size: 0.87rem;
        color: #CBD5E1;
        line-height: 1.5;
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    .resp-list li .num {
        background: linear-gradient(135deg, #6366F1, #818CF8);
        color: #fff;
        font-size: 0.72rem;
        font-weight: 700;
        width: 22px;
        height: 22px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-top: 1px;
    }

    /* ── Experience Badge ── */
    .exp-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 10px;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.25);
        font-size: 0.88rem;
        font-weight: 600;
        color: #C7D2FE;
        margin-top: 4px;
    }

    /* ── Cover Letter Output ── */
    .cover-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .cover-header .cover-meta {
        font-size: 0.88rem;
        color: #94A3B8;
        line-height: 1.5;
    }
    .cover-header .cover-meta strong {
        color: #A5B4FC;
    }

    /* ── Divider ── */
    .styled-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(100, 116, 139, 0.3), transparent);
        margin: 20px 0;
    }

    /* ── Sidebar styling ── */
    section[data-testid="stSidebar"] .stMarkdown h1 {
        font-size: 1.4rem !important;
    }

    /* ── Label tweaks ── */
    .cat-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
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
        status_text, status_bg = "Excellent Match", "rgba(16,185,129,0.15)"
        status_color = "#10B981"
    elif score >= 60:
        status_text, status_bg = "Good Match", "rgba(245,158,11,0.15)"
        status_color = "#F59E0B"
    elif score >= 40:
        status_text, status_bg = "Moderate Match", "rgba(245,158,11,0.15)"
        status_color = "#F59E0B"
    else:
        status_text, status_bg = "Needs Improvement", "rgba(239,68,68,0.15)"
        status_color = "#EF4444"
    
    return f"""
    <div class="glass-card">
        <div class="score-ring-container">
            <div class="score-ring">
                <svg width="160" height="160">
                    <circle cx="80" cy="80" r="{radius}" fill="none" stroke="rgba(51,65,85,0.5)" stroke-width="10"/>
                    <circle cx="80" cy="80" r="{radius}" fill="none" stroke="{color}" stroke-width="10"
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
    icon = "✅" if card_type == "strength" else "💡"
    css_class = f"info-card-{card_type}" if card_type == "strength" else "info-card-improve"
    cards = "".join([
        f'<div class="info-card {css_class}"><span class="icon">{icon}</span><span>{item}</span></div>'
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
    st.markdown("## 💼 AI Job Assistant")
    st.caption("Your career copilot powered by AI")
    
    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
    
    st.markdown("#### Connection")
    if backend_online:
        st.success("✅  API Backend Online")
    else:
        st.error("❌  API Backend Offline")
        st.warning("Run: `uvicorn app.main:app --reload`")

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    st.markdown("#### What you get")
    st.markdown("""
    🎯 **Match Score** — See how your resume stacks up  
    📌 **Requirements Extraction** — Skills, keywords, responsibilities  
    💡 **AI Suggestions** — Strengths & improvements  
    ✍️ **Cover Letter** — Auto-generated, tailored letter  
    """)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
    st.caption("Built with Llama 3.3 · Groq · Streamlit")

# ── Main Title ──
st.markdown("""
<div style="margin-bottom: 8px;">
    <span style="font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #818CF8, #6366F1, #A78BFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Career Copilot
    </span>
    <span style="font-size: 2.2rem; font-weight: 800; color: #F1F5F9;"> & Resume Optimizer</span>
</div>
<p style="color: #94A3B8; font-size: 1rem; margin-bottom: 0;">
    Paste a job description, upload your resume, and get a match score, optimization tips, and a tailored cover letter — all in one click.
</p>
""", unsafe_allow_html=True)
st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

if not backend_online:
    st.error("### Unable to reach the FastAPI backend.")
    st.info("Start the server and reload this page:")
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
        st.success(f"📄 Loaded: **{resume_file.name}**")

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header"><span class="accent-bar"></span>Cover Letter Details</div>
    <div class="section-subheader">Enter the company and role so we can generate a personalized cover letter.</div>
    """, unsafe_allow_html=True)

    col_company, col_role = st.columns(2)
    with col_company:
        company_name = st.text_input("Company Name *", placeholder="e.g. Netflix")
    with col_role:
        role_name = st.text_input("Role / Position *", placeholder="e.g. Senior Frontend Dev")

    st.markdown("")  # spacer
    analyze_button = st.button(
        "🚀 Analyze & Generate",
        type="primary",
        use_container_width=True
    )

with col_results:
    st.markdown("""
    <div class="section-header"><span class="accent-bar"></span>Results</div>
    <div class="section-subheader">Your evaluation report, AI suggestions, and generated cover letter appear here.</div>
    """, unsafe_allow_html=True)

    if not analyze_button:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px 30px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">🎯</div>
            <div style="font-size: 1.1rem; font-weight: 600; color: #E2E8F0; margin-bottom: 8px;">Ready when you are</div>
            <div style="font-size: 0.9rem; color: #64748B; line-height: 1.6;">
                Fill in the job description, upload your resume, and enter the<br>
                company & role on the left — then hit <strong style="color: #818CF8;">Analyze & Generate</strong>.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Validation ──
        if not jd_input:
            st.error("Please paste a job description first.")
        elif not resume_text:
            st.error("Please upload your resume (PDF or TXT) first.")
        elif "Error" in resume_text:
            st.error(resume_text)
        elif not company_name or not role_name:
            st.error("Please enter both Company Name and Role.")
        else:
            with st.spinner("🔍 Analyzing resume, extracting requirements & writing cover letter..."):
                # 1. JD requirements
                jd_payload = {"job_description": jd_input}
                jd_res = requests.post(f"{BACKEND_URL}/api/parse-jd", json=jd_payload)
                
                # 2. Resume match
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

                if jd_res.status_code == 200 and match_res.status_code == 200:
                    jd_data = jd_res.json()
                    match_data = match_res.json()

                    if "error" in match_data:
                        st.error(f"Analysis failed: {match_data.get('details')}")
                        st.code(match_data.get("raw_response"))
                    else:
                        match_score = match_data.get("match_percentage", 0)

                        score_color = "#EF4444"
                        if match_score >= 80:
                            score_color = "#10B981"
                        elif match_score >= 50:
                            score_color = "#F59E0B"

                        # ── Score Ring ──
                        st.markdown(build_score_ring(match_score, score_color), unsafe_allow_html=True)

                        # ── Result Sub-Tabs ──
                        tab_req, tab_tips, tab_cover = st.tabs([
                            "📌  Requirements",
                            "💡  AI Insights",
                            "✍️  Cover Letter"
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
                            st.markdown(f'<div class="exp-badge">🎓 {exp}</div>', unsafe_allow_html=True)
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

                            st.markdown('<p class="cat-label">Your Strengths</p>', unsafe_allow_html=True)
                            if strengths:
                                st.markdown(render_info_cards(strengths, "strength"), unsafe_allow_html=True)
                            else:
                                st.caption("No strengths identified.")

                            st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

                            st.markdown('<p class="cat-label">Suggested Improvements</p>', unsafe_allow_html=True)
                            if improvements:
                                st.markdown(render_info_cards(improvements, "improve"), unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div class="info-card info-card-strength">
                                    <span class="icon">🎉</span>
                                    <span>Your resume looks great for this role — no major changes needed!</span>
                                </div>
                                """, unsafe_allow_html=True)

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
                                        <div style="font-size: 1.5rem;">📬</div>
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
                                    st.caption("💡 Select all text above and copy to clipboard.")
                            else:
                                st.error("Cover letter generation failed. Analysis completed but the cover letter service had an issue.")
                else:
                    st.error("Error communicating with AI services. Check that the backend is running.")
