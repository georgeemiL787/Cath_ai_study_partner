"""
AI Study Partner - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from app.api import capture, processing, ai, database, settings, realtime_study
from app.services import service_manager

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Study Partner API",
    description="AI-powered study companion with real-time screen and audio capture",
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

# Include API routers
app.include_router(capture.router, prefix="/api/capture", tags=["capture"])
app.include_router(processing.router, prefix="/api/processing", tags=["processing"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(database.router, prefix="/api/database", tags=["database"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(realtime_study.router, prefix="/api/realtime-study", tags=["realtime-study"])

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
        "vector_db": service_manager.vector_db is not None,
        "screen_capture": service_manager.screen_capture is not None,
        "audio_capture": service_manager.audio_capture is not None,
        "llm_service": service_manager.llm_service is not None,
        "ocr_processor": service_manager.ocr_processor is not None,
        "speech_processor": service_manager.speech_processor is not None,
        "services": {
            "ocr": service_manager.ocr_processor is not None,
            "stt": service_manager.speech_processor is not None,
            "llm": service_manager.llm_service is not None
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

