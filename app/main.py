from fastapi import FastAPI
from app.routes.jd_routes import router as jd_router

app = FastAPI(title="AI Job Assistant")

app.include_router(jd_router, prefix="/api")

@app.get("/")
def home():
    return {"message": "AI Job Assistant API is running"}