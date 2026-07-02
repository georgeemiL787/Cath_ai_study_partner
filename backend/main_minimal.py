"""
AI Study Partner - Minimal FastAPI Application (AI Only)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from app.api import ai
from app.services import service_manager

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Study Partner API",
    description="AI-powered study companion with Gemini AI support",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only AI router for now
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.on_event("startup")
async def startup_event():
    """Initialize global services on startup"""
    await service_manager.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await service_manager.cleanup()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Study Partner API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "llm_service": service_manager.llm_service is not None,
        "services": {
            "llm": service_manager.llm_service is not None
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

