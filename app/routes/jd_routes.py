from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_service import parse_job_description

router = APIRouter()

class JDRequest(BaseModel):
    job_description: str

@router.post("/parse-jd")
def parse_jd(request: JDRequest):
    result = parse_job_description(request.job_description)
    return result