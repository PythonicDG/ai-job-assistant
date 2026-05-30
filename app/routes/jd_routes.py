"""
API endpoints for Job Description analysis and parsing.
Defines schemas and methods to extract structure (skills, keywords, experience, and responsibilities) from raw description text.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.ai_service import parse_job_description

router: APIRouter = APIRouter()

class JDRequest(BaseModel):
    """Request model representation for Job Description parsing."""
    job_description: str = Field(..., description="The raw, complete text of the job description block.")

@router.post("/parse-jd")
def parse_jd(request: JDRequest) -> dict:
    """
    Parses and extracts structured entities from a job description payload.
    Args:
        request: The JDRequest body containing raw text.
    Returns:
        dict: A dictionary containing lists of skills, keywords, responsibilities, and experience level.
    """
    result: dict = parse_job_description(request.job_description)
    return result
