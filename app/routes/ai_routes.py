from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import analyze_resume, generate_cover_message

router = APIRouter()

class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str

class CoverMessageRequest(BaseModel):
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
        raise HTTPException(status_code=500, detail=str(e))
