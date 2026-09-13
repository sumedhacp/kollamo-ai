# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Kollamo.ai Backend",
    description="Malayalam-English Code-Mixed Sentiment Analysis API grounded on DravidianCodeMix FIRE Benchmark & MuRIL",
    version="2.0.0"
)

# Configure CORS for local development and frontend Vite ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API endpoints
app.include_router(api_router, prefix="/api")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "system": "Kollamo.ai Malayalam-English Sentiment Engine",
        "model": "google/muril-base-cased (Calibrated 3-Class)",
        "version": "2.0.0"
    }