from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.jd_routes import router as jd_router
from app.routes.ai_routes import router as ai_router

app = FastAPI(title="AI Job Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jd_router, prefix="/api")
app.include_router(ai_router, prefix="/api")

@app.get("/")
def home():
    return {"message": "AI Job Assistant API is running"}