from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.supabase_client import supabase

router = APIRouter()

class ApplicationCreate(BaseModel):
    company_name: str
    role: str
    status: str = "Applied"
    job_description: str | None = None

class ApplicationUpdate(BaseModel):
    status: str

@router.post("/applications")
def create_application(application: ApplicationCreate):
    try:
        data = supabase.table("applications").insert(application.model_dump()).execute()
        return data.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/applications")
def get_applications():
    try:
        data = supabase.table("applications").select("*").order("created_at", desc=True).execute()
        return data.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/applications/{application_id}")
def update_application(application_id: str, application: ApplicationUpdate):
    try:
        # Check if id can be cast to int, otherwise treat as string/UUID
        try:
            target_id = int(application_id)
        except ValueError:
            target_id = application_id

        data = supabase.table("applications").update(application.model_dump()).eq("id", target_id).execute()
        return data.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/applications/{application_id}")
def delete_application(application_id: str):
    try:
        # Check if id can be cast to int, otherwise treat as string/UUID
        try:
            target_id = int(application_id)
        except ValueError:
            target_id = application_id

        data = supabase.table("applications").delete().eq("id", target_id).execute()
        return data.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
