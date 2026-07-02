"""
Real-time Study API endpoints for AI Study Partner
Enhanced endpoints for live study sessions with AI integration
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import time
import uuid

from ..capture.realtime_processor import (
    start_realtime_processing, 
    stop_realtime_processing, 
    get_realtime_processor
)
from ..services import service_manager

router = APIRouter()

class StudySessionStartRequest(BaseModel):
    session_id: Optional[str] = None
    auto_ai_processing: bool = True
    processing_interval: int = 30
    screen_region: Optional[Dict[str, int]] = None
    fps: int = 2
    audio_enabled: bool = True

class StudySessionStopRequest(BaseModel):
    session_id: str

class ContentAddRequest(BaseModel):
    content: str
    content_type: str = "manual"
    metadata: Optional[Dict[str, Any]] = None

class QuestionRequest(BaseModel):
    question: str
    session_id: str
    include_citations: bool = True
    top_k: int = 5

class StudySessionResponse(BaseModel):
    session_id: str
    is_active: bool
    stats: Dict[str, Any]
    key_points: List[str]
    recent_content: List[Dict[str, Any]]

@router.post("/start", response_model=StudySessionResponse)
async def start_study_session(request: StudySessionStartRequest):
    """Start a new real-time study session"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get services from service manager
        ai_service = service_manager.llm_service
        ocr_processor = service_manager.ocr_processor
        speech_processor = service_manager.speech_processor
        
        # Start real-time processing
        processor = await start_realtime_processing(
            session_id=session_id,
            ai_service=ai_service,
            ocr_processor=ocr_processor,
            speech_processor=speech_processor
        )
        
        # Configure processor
        processor.auto_ai_processing = request.auto_ai_processing
        processor.processing_interval = request.processing_interval
        
        # Start screen and audio capture
        screen_capture = service_manager.screen_capture
        audio_capture = service_manager.audio_capture
        
        if screen_capture:
            region = None
            if request.screen_region:
                region = (
                    request.screen_region["x"],
                    request.screen_region["y"], 
                    request.screen_region["width"],
                    request.screen_region["height"]
                )
            screen_capture.start_capture(region)
            
        if audio_capture and request.audio_enabled:
            audio_capture.start_capture()
        
        # Get initial stats
        stats = processor.get_session_stats()
        
        return StudySessionResponse(
            session_id=session_id,
            is_active=True,
            stats=stats,
            key_points=processor.session.key_points,
            recent_content=[]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start study session: {str(e)}")

@router.post("/stop", response_model=Dict[str, Any])
async def stop_study_session(request: StudySessionStopRequest):
    """Stop a real-time study session"""
    try:
        # Stop real-time processing
        await stop_realtime_processing(request.session_id)
        
        # Stop screen and audio capture
        screen_capture = service_manager.screen_capture
        audio_capture = service_manager.audio_capture
        
        if screen_capture:
            screen_capture.stop_capture()
            
        if audio_capture:
            audio_capture.stop_capture()
        
        return {
            "message": "Study session stopped successfully",
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop study session: {str(e)}")

@router.get("/{session_id}/status", response_model=StudySessionResponse)
async def get_session_status(session_id: str):
    """Get current session status and data"""
    processor = get_realtime_processor(session_id)
    
    if not processor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    stats = processor.get_session_stats()
    recent_content = [
        {
            "id": item.id,
            "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
            "type": item.content_type,
            "timestamp": item.timestamp,
            "confidence": item.confidence
        }
        for item in processor.session.content_items[-10:]  # Last 10 items
    ]
    
    return StudySessionResponse(
        session_id=session_id,
        is_active=processor.session.is_active,
        stats=stats,
        key_points=processor.session.key_points,
        recent_content=recent_content
    )

@router.post("/{session_id}/content", response_model=Dict[str, Any])
async def add_content_to_session(session_id: str, request: ContentAddRequest):
    """Add manual content to a study session"""
    processor = get_realtime_processor(session_id)
    
    if not processor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        await processor.add_manual_content(
            content=request.content,
            content_type=request.content_type,
            metadata=request.metadata
        )
        
        return {
            "message": "Content added successfully",
            "session_id": session_id,
            "content_length": len(request.content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add content: {str(e)}")

@router.post("/{session_id}/question", response_model=Dict[str, Any])
async def ask_session_question(session_id: str, request: QuestionRequest):
    """Ask a question about session content"""
    processor = get_realtime_processor(session_id)
    
    if not processor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    ai_service = service_manager.llm_service
    if not ai_service:
        raise HTTPException(status_code=500, detail="AI service not available")
    
    try:
        # Search for relevant content
        relevant_content = await processor.search_content(request.question, request.top_k)
        context = [item.content for item in relevant_content]
        
        # Generate answer
        response = ai_service.answer_question(
            request.question,
            context,
            include_citations=request.include_citations
        )
        
        # Add question to session
        processor.session.questions.append({
            "question": request.question,
            "answer": response.content,
            "timestamp": time.time()
        })
        
        return {
            "success": True,
            "answer": response.content,
            "model": response.model,
            "citations": response.citations,
            "relevant_content_count": len(relevant_content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")

@router.get("/{session_id}/summary", response_model=Dict[str, Any])
async def get_session_summary(session_id: str):
    """Get AI-generated summary of session content"""
    processor = get_realtime_processor(session_id)
    
    if not processor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        summary = await processor.get_session_summary()
        
        return {
            "success": True,
            "summary": summary,
            "content_items_count": len(processor.session.content_items),
            "session_duration": time.time() - processor.session.start_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.get("/{session_id}/key-points", response_model=Dict[str, Any])
async def get_session_key_points(session_id: str):
    """Get key points extracted from session content"""
    processor = get_realtime_processor(session_id)
    
    if not processor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "key_points": processor.session.key_points,
        "count": len(processor.session.key_points)
    }

@router.post("/{session_id}/process-frame")
async def process_screen_frame(session_id: str, frame_data: str):
    """Process a screen frame for content extraction"""
    processor = get_realtime_processor(session_id)
    
    if not processor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        await processor.add_screen_content(frame_data)
        
        return {
            "message": "Frame processed successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process frame: {str(e)}")

@router.get("/{session_id}/export")
async def export_session_data(session_id: str, format: str = "json"):
    """Export session data"""
    processor = get_realtime_processor(session_id)
    
    if not processor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        if format == "json":
            # Return session data as JSON
            session_data = {
                "session": {
                    "id": processor.session.id,
                    "start_time": processor.session.start_time,
                    "end_time": processor.session.end_time,
                    "is_active": processor.session.is_active
                },
                "content_items": [
                    {
                        "id": item.id,
                        "content": item.content,
                        "type": item.content_type,
                        "timestamp": item.timestamp,
                        "confidence": item.confidence,
                        "metadata": item.metadata
                    }
                    for item in processor.session.content_items
                ],
                "key_points": processor.session.key_points,
                "questions": processor.session.questions,
                "stats": processor.get_session_stats(),
                "exported_at": time.time()
            }
            
            return {
                "success": True,
                "data": session_data,
                "format": "json"
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export session: {str(e)}")

@router.get("/sessions")
async def list_active_sessions():
    """List all active study sessions"""
    from ..capture.realtime_processor import realtime_processors
    
    sessions = []
    for session_id, processor in realtime_processors.items():
        sessions.append({
            "session_id": session_id,
            "is_active": processor.session.is_active,
            "start_time": processor.session.start_time,
            "stats": processor.get_session_stats()
        })
    
    return {
        "success": True,
        "sessions": sessions,
        "count": len(sessions)
    }
