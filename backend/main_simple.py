"""
AI Study Partner - Simplified FastAPI Application for Testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
        "vector_db": False,
        "screen_capture": False,
        "audio_capture": False,
        "services": {
            "ocr": False,
            "stt": False,
            "llm": False
        },
        "message": "Simplified mode - full features not yet loaded"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
