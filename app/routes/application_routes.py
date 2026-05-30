"""
API endpoints for application tracking database management.
Provides standard CRUD methods backing the Supabase Postgres application board.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db.supabase_client import supabase

router: APIRouter = APIRouter()

class ApplicationCreate(BaseModel):
    """Payload representing a newly submitted job application to track."""
    company_name: str = Field(..., description="Name of the target employer.")
    role: str = Field(..., description="Target job title.")
    status: str = Field("Applied", description="Current pipeline state (e.g. Applied, Interviewing, Offer, Rejected).")
    job_description: str | None = Field(None, description="Optional job posting description copy.")

class ApplicationUpdate(BaseModel):
    """Payload representing status transitions for tracked applications."""
    status: str = Field(..., description="New pipeline state target.")

@router.post("/applications")
def create_application(application: ApplicationCreate) -> list:
    """
    Creates and records a new tracked job application in the Supabase db.
    """
    try:
        data = supabase.table("applications").insert(application.model_dump()).execute()
        return data.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/applications")
def get_applications() -> list:
    """
    Retrieves all recorded job applications ordered by creation timestamp.
    """
    try:
        data = supabase.table("applications").select("*").order("created_at", desc=True).execute()
        return data.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/applications/{application_id}")
def update_application(application_id: str, application: ApplicationUpdate) -> list:
    """
    Updates the pipeline state / status for a specific application record.
    """
    try:
        try:
            target_id = int(application_id)
        except ValueError:
            target_id = application_id

        data = supabase.table("applications").update(application.model_dump()).eq("id", target_id).execute()
        return data.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/applications/{application_id}")
def delete_application(application_id: str) -> list:
    """
    Deletes a specific application record from the tracking system.
    """
    try:
        try:
            target_id = int(application_id)
        except ValueError:
            target_id = application_id

        data = supabase.table("applications").delete().eq("id", target_id).execute()
        return data.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
