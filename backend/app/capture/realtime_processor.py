"""
Real-time Content Processor for AI Study Partner
Enhanced processor that handles live screen and audio content with AI integration
"""

import asyncio
import time
import logging
import json
import os
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
import cv2
import numpy as np
from PIL import Image
import io

@dataclass
class ProcessedContent:
    """Processed content item"""
    id: str
    content: str
    content_type: str  # 'ocr', 'speech', 'manual'
    timestamp: float
    confidence: float
    metadata: Dict[str, Any]
    session_id: str
    source_frame: Optional[str] = None  # base64 encoded frame

@dataclass
class StudySession:
    """Study session data"""
    id: str
    start_time: float
    end_time: Optional[float] = None
    content_items: List[ProcessedContent] = None
    key_points: List[str] = None
    questions: List[Dict[str, Any]] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.content_items is None:
            self.content_items = []
        if self.key_points is None:
            self.key_points = []
        if self.questions is None:
            self.questions = []

class RealTimeProcessor:
    """Real-time content processor with AI integration"""
    
    def __init__(self, session_id: str, ai_service=None, ocr_processor=None, speech_processor=None):
        self.session_id = session_id
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        
        # Services
        self.ai_service = ai_service
        self.ocr_processor = ocr_processor
        self.speech_processor = speech_processor
        
        # Session data
        self.session = StudySession(
            id=session_id,
            start_time=time.time()
        )
        
        # Processing state
        self.content_buffer: List[ProcessedContent] = []
        self.last_processing_time = 0
        self.processing_interval = 30  # seconds
        self.auto_ai_processing = True
        
        # Callbacks
        self.on_content_processed: Optional[Callable] = None
        self.on_key_points_updated: Optional[Callable] = None
        self.on_session_updated: Optional[Callable] = None
        
        # Storage
        self.storage_path = f"./data/sessions/{session_id}"
        os.makedirs(self.storage_path, exist_ok=True)
        
    async def start_processing(self):
        """Start real-time processing"""
        self.is_processing = True
        self.logger.info(f"Real-time processing started for session {self.session_id}")
        
        # Start background processing task
        asyncio.create_task(self._background_processor())
        
    async def stop_processing(self):
        """Stop real-time processing"""
        self.is_processing = False
        self.session.end_time = time.time()
        self.session.is_active = False
        
        # Final processing
        await self._process_accumulated_content()
        await self._save_session_data()
        
        self.logger.info(f"Real-time processing stopped for session {self.session_id}")
        
    async def add_screen_content(self, frame_data: str, metadata: Dict[str, Any] = None):
        """Add screen content for processing"""
        if not self.is_processing:
            return
            
        try:
            # Decode base64 frame
            frame_bytes = base64.b64decode(frame_data)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                return
                
            # Process with OCR if available
            content = ""
            confidence = 0.0
            
            if self.ocr_processor:
                try:
                    ocr_result = self.ocr_processor.extract_text(frame)
                    content = ocr_result.get('text', '')
                    confidence = ocr_result.get('confidence', 0.0)
                except Exception as e:
                    self.logger.error(f"OCR processing error: {e}")
            
            # Only add if we have meaningful content
            if content.strip() and confidence > 0.3:
                processed_content = ProcessedContent(
                    id=f"screen_{int(time.time() * 1000)}",
                    content=content.strip(),
                    content_type="ocr",
                    timestamp=time.time(),
                    confidence=confidence,
                    metadata=metadata or {},
                    session_id=self.session_id,
                    source_frame=frame_data
                )
                
                await self._add_content(processed_content)
                
        except Exception as e:
            self.logger.error(f"Screen content processing error: {e}")
            
    async def add_audio_content(self, audio_data: bytes, metadata: Dict[str, Any] = None):
        """Add audio content for processing"""
        if not self.is_processing:
            return
            
        try:
            content = ""
            confidence = 0.0
            
            if self.speech_processor:
                try:
                    stt_result = self.speech_processor.transcribe_audio(audio_data)
                    content = stt_result.get('text', '')
                    confidence = stt_result.get('confidence', 0.0)
                except Exception as e:
                    self.logger.error(f"Speech processing error: {e}")
            
            # Only add if we have meaningful content
            if content.strip() and confidence > 0.5:
                processed_content = ProcessedContent(
                    id=f"audio_{int(time.time() * 1000)}",
                    content=content.strip(),
                    content_type="speech",
                    timestamp=time.time(),
                    confidence=confidence,
                    metadata=metadata or {},
                    session_id=self.session_id
                )
                
                await self._add_content(processed_content)
                
        except Exception as e:
            self.logger.error(f"Audio content processing error: {e}")
            
    async def add_manual_content(self, content: str, content_type: str = "manual", metadata: Dict[str, Any] = None):
        """Add manual content"""
        if not content.strip():
            return
            
        processed_content = ProcessedContent(
            id=f"manual_{int(time.time() * 1000)}",
            content=content.strip(),
            content_type=content_type,
            timestamp=time.time(),
            confidence=1.0,
            metadata=metadata or {},
            session_id=self.session_id
        )
        
        await self._add_content(processed_content)
        
    async def _add_content(self, content: ProcessedContent):
        """Add content to session and buffer"""
        self.session.content_items.append(content)
        self.content_buffer.append(content)
        
        # Notify callback
        if self.on_content_processed:
            try:
                await self.on_content_processed(content)
            except Exception as e:
                self.logger.error(f"Content processed callback error: {e}")
        
        # Check if we should trigger AI processing
        if self.auto_ai_processing and len(self.content_buffer) >= 5:
            await self._process_accumulated_content()
            
    async def _background_processor(self):
        """Background task for periodic processing"""
        while self.is_processing:
            try:
                current_time = time.time()
                
                # Process accumulated content periodically
                if (current_time - self.last_processing_time) >= self.processing_interval:
                    await self._process_accumulated_content()
                    self.last_processing_time = current_time
                    
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Background processor error: {e}")
                await asyncio.sleep(10)
                
    async def _process_accumulated_content(self):
        """Process accumulated content with AI"""
        if not self.content_buffer or not self.ai_service:
            return
            
        try:
            # Combine recent content
            recent_content = self.content_buffer[-10:]  # Last 10 items
            combined_text = "\n".join([item.content for item in recent_content])
            
            if not combined_text.strip():
                return
                
            # Generate key points
            if len(combined_text) > 100:
                await self._generate_key_points(combined_text)
                
            # Clear buffer after processing
            self.content_buffer.clear()
            
        except Exception as e:
            self.logger.error(f"Content processing error: {e}")
            
    async def _generate_key_points(self, content: str):
        """Generate key points from content"""
        try:
            if not self.ai_service:
                return
                
            # Use AI to extract key points
            response = self.ai_service.extract_key_concepts(content, 5)
            if response and response.content:
                points = [point.strip() for point in response.content.split('\n') if point.strip()]
                
                # Update session key points
                for point in points:
                    if point not in self.session.key_points:
                        self.session.key_points.append(point)
                
                # Notify callback
                if self.on_key_points_updated:
                    try:
                        await self.on_key_points_updated(self.session.key_points)
                    except Exception as e:
                        self.logger.error(f"Key points callback error: {e}")
                        
        except Exception as e:
            self.logger.error(f"Key points generation error: {e}")
            
    async def search_content(self, query: str, top_k: int = 5) -> List[ProcessedContent]:
        """Search through session content"""
        query_lower = query.lower()
        scored_items = []
        
        for item in self.session.content_items:
            content_lower = item.content.lower()
            score = 0
            
            # Simple scoring based on word matches
            query_words = query_lower.split()
            content_words = content_lower.split()
            
            for word in query_words:
                if word in content_words:
                    score += 1
                    
            if score > 0:
                scored_items.append((score, item))
                
        # Sort by score and return top_k
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_items[:top_k]]
        
    async def get_session_summary(self) -> str:
        """Get AI-generated session summary"""
        if not self.session.content_items or not self.ai_service:
            return "No content available for summary."
            
        try:
            # Combine all content
            all_content = "\n".join([item.content for item in self.session.content_items])
            
            if len(all_content) < 50:
                return "Not enough content for a meaningful summary."
                
            # Generate summary
            response = self.ai_service.generate_summary(all_content, 300)
            return response.content if response else "Failed to generate summary."
            
        except Exception as e:
            self.logger.error(f"Summary generation error: {e}")
            return "Error generating summary."
            
    async def _save_session_data(self):
        """Save session data to file"""
        try:
            file_path = os.path.join(self.storage_path, "session_data.json")
            
            # Convert to serializable format
            session_data = {
                "session": asdict(self.session),
                "content_items": [asdict(item) for item in self.session.content_items],
                "saved_at": time.time()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Session save error: {e}")
            
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_content = len(self.session.content_items)
        ocr_content = len([item for item in self.session.content_items if item.content_type == "ocr"])
        speech_content = len([item for item in self.session.content_items if item.content_type == "speech"])
        manual_content = len([item for item in self.session.content_items if item.content_type == "manual"])
        
        duration = time.time() - self.session.start_time
        if self.session.end_time:
            duration = self.session.end_time - self.session.start_time
            
        return {
            "session_id": self.session_id,
            "is_active": self.session.is_active,
            "duration": duration,
            "total_content_items": total_content,
            "ocr_items": ocr_content,
            "speech_items": speech_content,
            "manual_items": manual_content,
            "key_points_count": len(self.session.key_points),
            "questions_count": len(self.session.questions)
        }

# Global real-time processors
realtime_processors: Dict[str, RealTimeProcessor] = {}

async def start_realtime_processing(session_id: str, ai_service=None, ocr_processor=None, speech_processor=None):
    """Start real-time processing for a session"""
    if session_id in realtime_processors:
        return realtime_processors[session_id]
        
    processor = RealTimeProcessor(
        session_id=session_id,
        ai_service=ai_service,
        ocr_processor=ocr_processor,
        speech_processor=speech_processor
    )
    
    realtime_processors[session_id] = processor
    await processor.start_processing()
    
    return processor

async def stop_realtime_processing(session_id: str):
    """Stop real-time processing for a session"""
    if session_id in realtime_processors:
        processor = realtime_processors[session_id]
        await processor.stop_processing()
        del realtime_processors[session_id]

def get_realtime_processor(session_id: str) -> Optional[RealTimeProcessor]:
    """Get real-time processor for a session"""
    return realtime_processors.get(session_id)
