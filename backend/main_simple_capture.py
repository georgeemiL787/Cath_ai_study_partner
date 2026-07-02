"""
Simple FastAPI server for screen capture testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import uuid
from typing import Optional
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from app.capture.screen_capture import ScreenCapture, CaptureConfig

app = FastAPI(
    title="Simple Screen Capture API",
    description="Simple screen capture for testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
screen_capture: Optional[ScreenCapture] = None
current_session_id: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize screen capture on startup"""
    global screen_capture
    try:
        config = CaptureConfig(fps=1)
        screen_capture = ScreenCapture(config)
        print("✅ Screen capture service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize screen capture: {e}")
        screen_capture = None

@app.get("/api/status")
async def get_status():
    """Get service status"""
    return {
        "screen_capture": screen_capture is not None,
        "is_capturing": screen_capture.is_capturing if screen_capture else False,
        "session_id": current_session_id
    }

@app.post("/api/capture/start")
async def start_capture():
    """Start screen capture"""
    global current_session_id, screen_capture
    
    if not screen_capture:
        raise HTTPException(status_code=500, detail="Screen capture not initialized")
    
    if screen_capture.is_capturing:
        return {
            "message": "Capture already running",
            "session_id": current_session_id,
            "screen_capture": True
        }
    
    current_session_id = str(uuid.uuid4())
    screen_capture.start_capture()
    
    return {
        "message": "Capture started successfully",
        "session_id": current_session_id,
        "screen_capture": True
    }

@app.post("/api/capture/stop")
async def stop_capture():
    """Stop screen capture"""
    global current_session_id, screen_capture
    
    if not screen_capture:
        raise HTTPException(status_code=500, detail="Screen capture not initialized")
    
    if not screen_capture.is_capturing:
        return {
            "message": "Capture not running",
            "session_id": current_session_id
        }
    
    screen_capture.stop_capture()
    current_session_id = None
    
    return {
        "message": "Capture stopped successfully",
        "session_id": None
    }

@app.get("/api/capture/status")
async def get_capture_status():
    """Get capture status"""
    global screen_capture, current_session_id
    
    if not screen_capture:
        return {
            "is_capturing": False,
            "session_id": None,
            "screen_stats": {"status": "not_initialized"}
        }
    
    screen_stats = screen_capture.get_capture_stats()
    
    return {
        "is_capturing": screen_capture.is_capturing,
        "session_id": current_session_id,
        "screen_stats": screen_stats
    }

@app.get("/api/capture/frame")
async def get_current_frame():
    """Get current captured frame as base64"""
    global screen_capture, current_session_id
    
    if not screen_capture:
        raise HTTPException(status_code=500, detail="Screen capture not initialized")
    
    if not screen_capture.is_capturing:
        raise HTTPException(status_code=400, detail="Screen capture not active")
        
    if screen_capture.last_frame is None:
        raise HTTPException(status_code=404, detail="No frame available")
        
    try:
        frame_base64 = screen_capture.get_frame_as_base64()
        
        return {
            "frame": frame_base64,
            "timestamp": time.time(),
            "session_id": current_session_id
        }
    except Exception as e:
        print(f"Error in get_current_frame: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
