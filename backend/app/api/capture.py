"""
Capture API endpoints for AI Study Partner
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import uuid

from ..capture.screen_capture import ScreenCapture, CaptureConfig
from ..capture.audio_capture import AudioCapture, AudioConfig
from ..capture.simple_content_processor import start_simple_session_processing, stop_simple_session_processing, get_simple_session_processor
from ..capture.enhanced_content_processor import start_enhanced_processing, stop_enhanced_processing, get_enhanced_processor
from ..services import service_manager

router = APIRouter()

# Session management
current_session_id: Optional[str] = None

class CaptureStartRequest(BaseModel):
    screen_region: Optional[Dict[str, int]] = None  # {"x": 0, "y": 0, "width": 1920, "height": 1080}
    fps: int = 1
    audio_enabled: bool = True
    session_id: Optional[str] = None
    monitor_index: Optional[int] = None  # 1-based index used by mss

class CaptureStopRequest(BaseModel):
    session_id: Optional[str] = None

class CaptureStatusResponse(BaseModel):
    is_capturing: bool
    session_id: Optional[str]
    screen_stats: Dict[str, Any]
    audio_stats: Dict[str, Any]

@router.post("/start")
async def start_capture(request: CaptureStartRequest):
    """Start screen and/or audio capture"""
    global current_session_id
    
    try:
        # Generate session ID if not provided
        if not request.session_id:
            current_session_id = str(uuid.uuid4())
        else:
            current_session_id = request.session_id
            
        # Get services from service manager
        screen_capture = service_manager.screen_capture
        audio_capture = service_manager.audio_capture
        
        if not screen_capture or not audio_capture:
            raise HTTPException(status_code=500, detail="Capture services not initialized")
            
        # Apply fps and monitor selection before start
        if request.fps and screen_capture:
            screen_capture.config.fps = request.fps
        if request.monitor_index and screen_capture:
            screen_capture.config.monitor_index = max(1, int(request.monitor_index))

        # Start screen capture
        region = None
        if request.screen_region:
            region = (
                request.screen_region["x"],
                request.screen_region["y"], 
                request.screen_region["width"],
                request.screen_region["height"]
            )
            
        screen_capture.start_capture(region)
        
        # Start audio capture if enabled
        if request.audio_enabled:
            audio_capture.start_capture()
            
        # Start content processing pipeline
        await start_simple_session_processing(current_session_id)
        
        # Also start enhanced processing with OCR
        try:
            await start_enhanced_processing(
                current_session_id,
                ocr_processor=service_manager.ocr_processor,
                ai_service=service_manager.llm_service
            )
        except Exception as e:
            print(f"Warning: Enhanced processing not available: {e}")
            
        return {
            "message": "Capture started successfully",
            "session_id": current_session_id,
            "screen_capture": True,
            "audio_capture": request.audio_enabled
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start capture: {str(e)}")

@router.get("/monitors")
async def list_monitors():
    """List available monitors for selection"""
    screen_capture = service_manager.screen_capture
    if not screen_capture:
        raise HTTPException(status_code=400, detail="Screen capture not initialized")
    try:
        mons = ScreenCapture.list_monitors()
        return {"monitors": mons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list monitors: {str(e)}")

@router.get("/monitors/{index}/thumbnail")
async def monitor_thumbnail(index: int):
    """Return a small thumbnail of a monitor so the user can preview before selecting"""
    screen_capture = service_manager.screen_capture
    if not screen_capture:
        raise HTTPException(status_code=400, detail="Screen capture not initialized")
    try:
        img_b64 = ScreenCapture.capture_monitor_thumbnail(index)
        return {"thumbnail": img_b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to capture thumbnail: {str(e)}")

@router.get("/windows")
async def list_windows():
    """List top-level application windows (Windows only)."""
    screen_capture = service_manager.screen_capture
    if not screen_capture:
        raise HTTPException(status_code=400, detail="Screen capture not initialized")
    try:
        wins = ScreenCapture.list_windows()
        return {"windows": wins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list windows: {str(e)}")

@router.get("/windows/{hwnd}/thumbnail")
async def window_thumbnail(hwnd: int):
    """Return a small thumbnail for a given window handle."""
    screen_capture = service_manager.screen_capture
    if not screen_capture:
        raise HTTPException(status_code=400, detail="Screen capture not initialized")
    try:
        img_b64 = ScreenCapture.capture_window_thumbnail(hwnd)
        return {"thumbnail": img_b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to capture window thumbnail: {str(e)}")

@router.post("/stop")
async def stop_capture(request: CaptureStopRequest):
    """Stop screen and audio capture"""
    global current_session_id
    
    try:
        # Get services from service manager
        screen_capture = service_manager.screen_capture
        audio_capture = service_manager.audio_capture
        
        # Stop screen capture
        if screen_capture:
            screen_capture.stop_capture()
            
        # Stop audio capture
        if audio_capture:
            audio_capture.stop_capture()
            
        # Stop content processing pipeline
        session_to_stop = request.session_id or current_session_id
        if session_to_stop:
            await stop_simple_session_processing(session_to_stop)
            # Also stop enhanced processing
            try:
                await stop_enhanced_processing(session_to_stop)
            except Exception as e:
                print(f"Warning: Enhanced processing stop failed: {e}")
            
        # Clear session ID
        if request.session_id == current_session_id or not request.session_id:
            current_session_id = None
            
        return {
            "message": "Capture stopped successfully",
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop capture: {str(e)}")

@router.get("/status")
async def get_capture_status():
    """Get current capture status"""
    global current_session_id
    
    screen_capture = service_manager.screen_capture
    audio_capture = service_manager.audio_capture
    
    screen_stats = {}
    audio_stats = {}
    
    if screen_capture:
        screen_stats = screen_capture.get_capture_stats()
        
    if audio_capture:
        audio_stats = audio_capture.get_capture_stats()
        
    is_capturing = (
        (screen_capture and screen_capture.is_capturing) or
        (audio_capture and audio_capture.is_capturing)
    )
    
    return CaptureStatusResponse(
        is_capturing=is_capturing,
        session_id=current_session_id,
        screen_stats=screen_stats,
        audio_stats=audio_stats
    )

@router.get("/frame")
async def get_current_frame():
    """Get current captured frame as base64"""
    try:
        screen_capture = service_manager.screen_capture
        
        if not screen_capture or not screen_capture.is_capturing:
            raise HTTPException(status_code=400, detail="Screen capture not active")
            
        if screen_capture.last_frame is None:
            raise HTTPException(status_code=404, detail="No frame available")
            
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

@router.get("/audio/segments")
async def get_audio_segments():
    """Get captured audio segments"""
    audio_capture = service_manager.audio_capture
    
    if not audio_capture:
        raise HTTPException(status_code=400, detail="Audio capture not initialized")
        
    segments = audio_capture.get_speech_segments()
    
    return {
        "segments": len(segments),
        "session_id": current_session_id,
        "total_duration": sum(len(seg) / audio_capture.config.sample_rate for seg in segments)
    }

@router.post("/audio/clear")
async def clear_audio_segments():
    """Clear stored audio segments"""
    audio_capture = service_manager.audio_capture
    
    if not audio_capture:
        raise HTTPException(status_code=400, detail="Audio capture not initialized")
        
    audio_capture.clear_speech_segments()
    
    return {
        "message": "Audio segments cleared",
        "session_id": current_session_id
    }

@router.post("/screen/region")
async def set_screen_region(region: Dict[str, int]):
    """Set screen capture region"""
    screen_capture = service_manager.screen_capture
    
    if not screen_capture:
        raise HTTPException(status_code=400, detail="Screen capture not initialized")
        
    try:
        # Stop current capture
        if screen_capture.is_capturing:
            screen_capture.stop_capture()
            
        # Start with new region
        new_region = (region["x"], region["y"], region["width"], region["height"])
        screen_capture.start_capture(new_region)
        
        return {
            "message": "Screen region updated",
            "region": region,
            "session_id": current_session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set screen region: {str(e)}")

@router.post("/content/add")
async def add_manual_content(request: Dict[str, Any]):
    """Add manual content to the current session"""
    global current_session_id
    
    if not current_session_id:
        raise HTTPException(status_code=400, detail="No active session")
        
    content = request.get("content", "")
    content_type = request.get("type", "manual")
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
        
    try:
        processor = get_simple_session_processor(current_session_id)
        if processor:
            await processor.add_content(content, content_type)
            
        return {
            "message": "Content added successfully",
            "session_id": current_session_id,
            "content_length": len(content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add content: {str(e)}")

class ProcessFrameRequest(BaseModel):
    frame_data: str

@router.post("/process-frame")
async def process_frame_with_ocr(request: ProcessFrameRequest):
    """Process a frame with OCR to extract text"""
    global current_session_id
    
    if not current_session_id:
        raise HTTPException(status_code=400, detail="No active session")
        
    if not request.frame_data:
        raise HTTPException(status_code=400, detail="No frame data provided")
        
    try:
        # Get enhanced processor
        enhanced_processor = get_enhanced_processor(current_session_id)
        if not enhanced_processor:
            raise HTTPException(status_code=400, detail="Enhanced processing not available")
            
        # Process frame
        processed_frame = await enhanced_processor.process_frame(request.frame_data)
        
        if processed_frame:
            return {
                "message": "Frame processed successfully",
                "session_id": current_session_id,
                "extracted_text": processed_frame.extracted_text,
                "confidence": processed_frame.confidence,
                "text_length": len(processed_frame.extracted_text),
                "processing_time": processed_frame.timestamp
            }
        else:
            return {
                "message": "Frame processed but no text extracted",
                "session_id": current_session_id,
                "extracted_text": "",
                "confidence": 0,
                "text_length": 0,
                "processing_time": time.time()
            }
            
    except Exception as e:
        print(f"Error in process_frame_with_ocr: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process frame: {str(e)}")

@router.get("/extracted-content")
async def get_extracted_content():
    """Get all extracted content from the current session"""
    global current_session_id
    
    if not current_session_id:
        raise HTTPException(status_code=400, detail="No active session")
        
    try:
        enhanced_processor = get_enhanced_processor(current_session_id)
        if not enhanced_processor:
            return {
                "message": "Enhanced processing not available",
                "content": [],
                "total_items": 0
            }
            
        return {
            "message": "Extracted content retrieved",
            "session_id": current_session_id,
            "content": enhanced_processor.extracted_content,
            "total_items": len(enhanced_processor.extracted_content),
            "key_points": enhanced_processor.key_points,
            "stats": enhanced_processor.get_session_stats()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get extracted content: {str(e)}")

@router.get("/config")
async def get_capture_config():
    """Get current capture configuration"""
    screen_capture = service_manager.screen_capture
    audio_capture = service_manager.audio_capture
    
    config = {
        "screen": {},
        "audio": {}
    }
    
    if screen_capture:
        config["screen"] = {
            "fps": screen_capture.config.fps,
            "region": screen_capture.config.region,
            "quality": screen_capture.config.quality
        }
        
    if audio_capture:
        config["audio"] = {
            "sample_rate": audio_capture.config.sample_rate,
            "chunk_size": audio_capture.config.chunk_size,
            "channels": audio_capture.config.channels,
            "vad_aggressiveness": audio_capture.config.vad_aggressiveness
        }
        
    return config

