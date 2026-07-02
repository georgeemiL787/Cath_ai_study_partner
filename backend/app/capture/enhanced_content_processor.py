"""
Enhanced Content Processor for AI Study Partner
Processes captured frames with OCR and integrates with AI services
"""

import asyncio
import time
import logging
import json
import os
import base64
import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProcessedFrame:
    """Processed frame with extracted content"""
    id: str
    frame_data: str  # base64 encoded
    extracted_text: str
    confidence: float
    timestamp: float
    session_id: str
    metadata: Dict[str, Any]

class EnhancedContentProcessor:
    """Enhanced content processor that actually extracts text from frames"""
    
    def __init__(self, session_id: str, ocr_processor=None, ai_service=None):
        self.session_id = session_id
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        
        # Services
        self.ocr_processor = ocr_processor
        self.ai_service = ai_service
        
        # Storage
        self.processed_frames: List[ProcessedFrame] = []
        self.extracted_content: List[str] = []
        self.key_points: List[str] = []
        
        # Processing state
        self.last_processing_time = 0
        self.processing_interval = 10  # seconds
        self.auto_ai_processing = True
        
        # Storage path
        self.storage_path = f"./data/sessions/{session_id}"
        os.makedirs(self.storage_path, exist_ok=True)
        
    async def start_processing(self):
        """Start the enhanced content processing"""
        self.is_processing = True
        self.logger.info(f"Enhanced content processing started for session {self.session_id}")
        
        # Start background processing task
        asyncio.create_task(self._background_processor())
        
    async def stop_processing(self):
        """Stop the enhanced content processing"""
        self.is_processing = False
        await self._save_session_data()
        self.logger.info(f"Enhanced content processing stopped for session {self.session_id}")
        
    async def process_frame(self, frame_data: str, metadata: Dict[str, Any] = None) -> Optional[ProcessedFrame]:
        """Process a captured frame and extract text"""
        if not self.is_processing:
            self.logger.warning("Processor not active")
            return None
            
        if not self.ocr_processor:
            self.logger.error("OCR processor not available")
            return None
            
        try:
            # Decode base64 frame
            frame_bytes = base64.b64decode(frame_data)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                self.logger.warning("Failed to decode frame from base64 data")
                return None
                
            # Validate frame dimensions
            if frame.shape[0] < 10 or frame.shape[1] < 10:
                self.logger.warning(f"Frame too small: {frame.shape}")
                return None
                
            # Extract text using OCR
            try:
                ocr_result = self.ocr_processor.extract_text(frame)
                self.logger.debug(f"OCR Result: text='{ocr_result.text[:100]}...', confidence={ocr_result.confidence:.1f}%")
            except Exception as ocr_error:
                self.logger.error(f"OCR processing failed: {ocr_error}")
                return None
            
            # Process if we have meaningful text (lowered threshold for better detection)
            if ocr_result.text.strip() and ocr_result.confidence > 5:
                processed_frame = ProcessedFrame(
                    id=f"frame_{int(time.time() * 1000)}",
                    frame_data=frame_data,
                    extracted_text=ocr_result.text.strip(),
                    confidence=ocr_result.confidence,
                    timestamp=time.time(),
                    session_id=self.session_id,
                    metadata=metadata or {}
                )
                
                self.processed_frames.append(processed_frame)
                self.extracted_content.append(ocr_result.text.strip())
                
                self.logger.info(f"Successfully processed frame: {len(ocr_result.text)} characters, confidence: {ocr_result.confidence:.1f}%")
                
                return processed_frame
            else:
                self.logger.debug(f"No meaningful text found (confidence: {ocr_result.confidence:.1f}%, text length: {len(ocr_result.text)})")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
            
    async def _background_processor(self):
        """Background task for periodic AI processing"""
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
        if not self.extracted_content or not self.ai_service:
            return
            
        try:
            # Combine recent content
            recent_content = self.extracted_content[-10:]  # Last 10 extractions
            combined_text = "\n".join(recent_content)
            
            if len(combined_text.strip()) < 50:
                return
                
            # Generate key points
            await self._generate_key_points(combined_text)
            
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
                
                # Update key points
                for point in points:
                    if point not in self.key_points:
                        self.key_points.append(point)
                        
                self.logger.info(f"Generated {len(points)} key points")
                        
        except Exception as e:
            self.logger.error(f"Key points generation error: {e}")
            
    async def search_content(self, query: str, top_k: int = 5) -> List[ProcessedFrame]:
        """Search through processed frames"""
        query_lower = query.lower()
        scored_frames = []
        
        for frame in self.processed_frames:
            text_lower = frame.extracted_text.lower()
            score = 0
            
            # Simple scoring based on word matches
            query_words = query_lower.split()
            text_words = text_lower.split()
            
            for word in query_words:
                if word in text_words:
                    score += 1
                    
            if score > 0:
                scored_frames.append((score, frame))
                
        # Sort by score and return top_k
        scored_frames.sort(key=lambda x: x[0], reverse=True)
        return [frame for score, frame in scored_frames[:top_k]]
        
    async def get_session_summary(self) -> str:
        """Get AI-generated session summary"""
        if not self.extracted_content or not self.ai_service:
            return "No content available for summary."
            
        try:
            # Combine all content
            all_content = "\n".join(self.extracted_content)
            
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
            file_path = os.path.join(self.storage_path, "enhanced_session_data.json")
            
            session_data = {
                "session_id": self.session_id,
                "processed_frames": [
                    {
                        "id": frame.id,
                        "extracted_text": frame.extracted_text,
                        "confidence": frame.confidence,
                        "timestamp": frame.timestamp,
                        "metadata": frame.metadata
                    }
                    for frame in self.processed_frames
                ],
                "extracted_content": self.extracted_content,
                "key_points": self.key_points,
                "saved_at": time.time()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Session save error: {e}")
            
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_frames = len(self.processed_frames)
        total_content = len(self.extracted_content)
        total_text_length = sum(len(content) for content in self.extracted_content)
        
        avg_confidence = 0
        if self.processed_frames:
            avg_confidence = sum(frame.confidence for frame in self.processed_frames) / len(self.processed_frames)
        
        return {
            "session_id": self.session_id,
            "is_processing": self.is_processing,
            "total_frames": total_frames,
            "total_content_items": total_content,
            "total_text_length": total_text_length,
            "average_confidence": avg_confidence,
            "key_points_count": len(self.key_points),
            "last_processing_time": self.last_processing_time
        }

# Global enhanced processors
enhanced_processors: Dict[str, EnhancedContentProcessor] = {}

async def start_enhanced_processing(session_id: str, ocr_processor=None, ai_service=None):
    """Start enhanced content processing for a session"""
    if session_id in enhanced_processors:
        return enhanced_processors[session_id]
        
    processor = EnhancedContentProcessor(
        session_id=session_id,
        ocr_processor=ocr_processor,
        ai_service=ai_service
    )
    
    enhanced_processors[session_id] = processor
    await processor.start_processing()
    
    return processor

async def stop_enhanced_processing(session_id: str):
    """Stop enhanced content processing for a session"""
    if session_id in enhanced_processors:
        processor = enhanced_processors[session_id]
        await processor.stop_processing()
        del enhanced_processors[session_id]

def get_enhanced_processor(session_id: str) -> Optional[EnhancedContentProcessor]:
    """Get enhanced processor for a session"""
    return enhanced_processors.get(session_id)
