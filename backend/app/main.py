# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Kollamo.ai Backend",
    description="Malayalam-English Code-Mixed Sentiment Analysis API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all frontend ports (5173, 3000, 127.0.0.1, localhost)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "engine": "Kollamo.ai MuRIL Sequence Classifier"}