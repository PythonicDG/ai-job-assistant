from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import analyze_resume, generate_cover_message, generate_tailored_resume
import traceback
import os

router = APIRouter()

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "backend_error.log")

def log_exception(e: Exception, context: str):
    tb = traceback.format_exc()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"=== ERROR IN {context} ===\n")
        f.write(f"Exception: {str(e)}\n")
        f.write(f"Traceback:\n{tb}\n\n")
    print(f"ERROR IN {context}: {str(e)}")
    print(tb)

class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str

class CoverMessageRequest(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    role: str

class TailoredResumeRequest(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    role: str

@router.post("/analyze-resume")
def analyze_resume_endpoint(request: ResumeAnalysisRequest):
    try:
        result = analyze_resume(request.resume_text, request.job_description)
        return result
    except Exception as e:
        log_exception(e, "analyze-resume")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-cover-message")
def generate_cover_message_endpoint(request: CoverMessageRequest):
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
def generate_tailored_resume_endpoint(request: TailoredResumeRequest):
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


