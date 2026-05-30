"""
API endpoints for AI-driven resume analysis, cover letter outreach, and LaTeX resume tailoring.
Combines user profiles and job descriptions to generate tailored application materials via LLM services.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.ai_service import analyze_resume, generate_cover_message, generate_tailored_resume
import traceback
import os

router: APIRouter = APIRouter()

LOG_FILE: str = os.path.join(os.path.dirname(__file__), "..", "..", "backend_error.log")

def log_exception(e: Exception, context: str) -> None:
    """
    Helper to log stack traces of API exceptions to a local log file.
    Args:
        e: The exception instance.
        context: Context label or API endpoint name.
    """
    tb = traceback.format_exc()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"=== ERROR IN {context} ===\n")
        f.write(f"Exception: {str(e)}\n")
        f.write(f"Traceback:\n{tb}\n\n")
    print(f"ERROR IN {context}: {str(e)}")
    print(tb)

class ResumeAnalysisRequest(BaseModel):
    """Payload representing a request to analyze a resume against a job description."""
    resume_text: str = Field(..., description="The raw textual content of the candidate's resume.")
    job_description: str = Field(..., description="The job posting text block.")

class CoverMessageRequest(BaseModel):
    """Payload representing a request to generate a tailored cover outreach message."""
    resume_text: str = Field(..., description="The candidate's resume text.")
    job_description: str = Field(..., description="The target job description text.")
    company_name: str = Field(..., description="The name of the target company.")
    role: str = Field(..., description="The specific position title.")

class TailoredResumeRequest(BaseModel):
    """Payload representing a request to optimize a LaTeX resume template."""
    resume_text: str = Field(..., description="The candidate's resume text.")
    job_description: str = Field(..., description="The job posting text.")
    company_name: str = Field(..., description="The name of the target company.")
    role: str = Field(..., description="The specific position title.")

@router.post("/analyze-resume")
def analyze_resume_endpoint(request: ResumeAnalysisRequest) -> dict:
    """
    Compares resume text against a job description to calculate an alignment score and suggestions.
    """
    try:
        result = analyze_resume(request.resume_text, request.job_description)
        return result
    except Exception as e:
        log_exception(e, "analyze-resume")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-cover-message")
def generate_cover_message_endpoint(request: CoverMessageRequest) -> dict:
    """
    Creates a customized outreach cover letter template tailored to the target role.
    """
    try:
        result = generate_cover_message(
            resume_text=request.resume_text,
            job_description=request.job_description,
            company_name=request.company_name,
            role=request.role
        )
        return result
    except Exception as e:
        log_exception(e, "generate-cover-message")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-tailored-resume")
def generate_tailored_resume_endpoint(request: TailoredResumeRequest) -> dict:
    """
    Optimizes bullet points and layout structures, returning high-performance LaTeX code.
    """
    try:
        result = generate_tailored_resume(
            resume_text=request.resume_text,
            job_description=request.job_description,
            company_name=request.company_name,
            role=request.role
        )
        return result
    except Exception as e:
        log_exception(e, "generate-tailored-resume")
        raise HTTPException(status_code=500, detail=str(e))
