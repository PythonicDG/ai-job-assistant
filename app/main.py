"""
AI Job Assistant FastAPI Backend Application.
This module serves as the primary entry point, configuring middleware, CORS origins,
and registering routing endpoints for Job Description Parsing, AI Analysis, and Database Operations.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.jd_routes import router as jd_router
from app.routes.ai_routes import router as ai_router

app: FastAPI = FastAPI(
    title="AI Job Assistant",
    description="High-performance backend engine for ATS matching, requirement extraction, and LaTeX resume tailoring.",
    version="1.0.0"
)

# Configure cross-origin resource sharing middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register application API routers under the /api prefix
app.include_router(jd_router, prefix="/api")
app.include_router(ai_router, prefix="/api")

@app.get("/")
def home() -> dict[str, str]:
    """
    Health check home endpoint.
    Returns:
        dict: Operational status message.
    """
    return {"message": "AI Job Assistant API is running"}
