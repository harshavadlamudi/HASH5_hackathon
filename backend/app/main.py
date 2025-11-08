from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, patients
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="HealthLake AI API",
    description="Backend API for HealthLake AI Assistant",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8501",  # Streamlit (for testing)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(patients.router, prefix="/api", tags=["patients"])

@app.get("/")
async def root():
    return {
        "message": "HealthLake AI API",
        "docs": "/docs",
        "health": "/api/health"
    }
