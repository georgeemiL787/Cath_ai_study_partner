"""
Content Processing Pipeline for AI Study Partner
Automatically processes captured frames and audio to extract study content
"""

import asyncio
import time
import logging
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
import numpy as np
from datetime import datetime

from ..processing.ocr_processor import OCRProcessor, OCRResult
from ..processing.speech_processor import SpeechProcessor, TranscriptionResult
from ..database.vector_db import VectorDB, Document
from ..services import service_manager

@dataclass
class ProcessedContent:
    """Processed content from capture"""
    content_type: str  # "screen_text" or "audio_text"
    content: str
    timestamp: float
    confidence: float
    metadata: Dict[str, Any]

class ContentProcessor:
    """Automatically processes captured content and stores it in vector database"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        self.processing_task: Optional[asyncio.Task] = None
        
        # Get services
        self.ocr_processor = service_manager.ocr_processor
        self.speech_processor = service_manager.speech_processor
        self.vector_db = service_manager.vector_db
        
        # Processing queues
        self.frame_queue = asyncio.Queue()
        self.audio_queue = asyncio.Queue()
        
        # Processing settings
        self.ocr_interval = 5.0  # Process OCR every 5 seconds
        self.audio_interval = 10.0  # Process audio every 10 seconds
        self.min_confidence = 0.7  # Minimum confidence threshold
        
        # Last processed timestamps
        self.last_ocr_time = 0
        self.last_audio_time = 0
        
    async def start_processing(self):
        """Start the content processing pipeline"""
        if self.is_processing:
            return
            
        self.is_processing = True
        self.processing_task = asyncio.create_task(self._processing_loop())
        self.logger.info(f"Content processing started for session {self.session_id}")
        
    async def stop_processing(self):
        """Stop the content processing pipeline"""
        self.is_processing = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        self.logger.info(f"Content processing stopped for session {self.session_id}")
        
    def add_frame(self, frame: np.ndarray, timestamp: float):
        """Add a frame to the processing queue"""
        if self.is_processing and not self.frame_queue.full():
            self.frame_queue.put_nowait((frame, timestamp))
            
    def add_audio(self, audio_data: np.ndarray, timestamp: float):
        """Add audio data to the processing queue"""
        if self.is_processing and not self.audio_queue.full():
            self.audio_queue.put_nowait((audio_data, timestamp))
            
    async def _processing_loop(self):
        """Main processing loop"""
        while self.is_processing:
            try:
                current_time = time.time()
                
                # Process frames for OCR
                if (current_time - self.last_ocr_time) >= self.ocr_interval:
                    await self._process_frames()
                    self.last_ocr_time = current_time
                    
                # Process audio for transcription
                if (current_time - self.last_audio_time) >= self.audio_interval:
                    await self._process_audio()
                    self.last_audio_time = current_time
                    
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(1.0)
                
    async def _process_frames(self):
        """Process captured frames for text extraction"""
        if not self.ocr_processor or not self.vector_db:
            return
            
        try:
            # Get the latest frame from screen capture
            screen_capture = service_manager.screen_capture
            if not screen_capture or not screen_capture.last_frame:
                return
                
            frame = screen_capture.last_frame
            timestamp = time.time()
            
            # Run OCR on the frame
            ocr_result = self.ocr_processor.extract_text(frame)
            
            # Only process if we got meaningful text
            if ocr_result.text.strip() and ocr_result.confidence >= self.min_confidence:
                # Create document for vector database
                document = Document(
                    id=f"screen_{timestamp}_{hash(ocr_result.text) % 10000}",
                    content=ocr_result.text,
                    metadata={
                        "type": "screen_capture",
                        "confidence": ocr_result.confidence,
                        "word_count": len(ocr_result.words),
                        "timestamp": timestamp,
                        "session_id": self.session_id
                    },
                    timestamp=timestamp,
                    source_type="screen",
                    session_id=self.session_id
                )
                
                # Add to vector database
                await self.vector_db.add_document(
                    content=document.content,
                    metadata=document.metadata,
                    source_type=document.source_type,
                    session_id=document.session_id
                )
                
                self.logger.info(f"Processed screen content: {len(ocr_result.text)} characters")
                
        except Exception as e:
            self.logger.error(f"Error processing frames: {e}")
            
    async def _process_audio(self):
        """Process captured audio for speech transcription"""
        if not self.speech_processor or not self.vector_db:
            return
            
        try:
            # Get audio segments from audio capture
            audio_capture = service_manager.audio_capture
            if not audio_capture:
                return
                
            # Get recent speech segments
            speech_segments = audio_capture.get_speech_segments()
            if not speech_segments:
                return
                
            # Process the most recent segment
            latest_segment = speech_segments[-1] if speech_segments else None
            if latest_segment is None:
                return
                
            # Run speech-to-text
            transcription_result = self.speech_processor.transcribe(latest_segment)
            
            # Only process if we got meaningful text
            if transcription_result.text.strip() and transcription_result.confidence >= self.min_confidence:
                timestamp = time.time()
                
                # Create document for vector database
                document = Document(
                    id=f"audio_{timestamp}_{hash(transcription_result.text) % 10000}",
                    content=transcription_result.text,
                    metadata={
                        "type": "audio_transcription",
                        "confidence": transcription_result.confidence,
                        "language": transcription_result.language,
                        "timestamp": timestamp,
                        "session_id": self.session_id
                    },
                    timestamp=timestamp,
                    source_type="audio",
                    session_id=self.session_id
                )
                
                # Add to vector database
                await self.vector_db.add_document(
                    content=document.content,
                    metadata=document.metadata,
                    source_type=document.source_type,
                    session_id=document.session_id
                )
                
                self.logger.info(f"Processed audio content: {len(transcription_result.text)} characters")
                
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")
            
    async def process_manual_content(self, content: str, content_type: str = "manual"):
        """Process manually added content"""
        if not self.vector_db:
            return
            
        try:
            timestamp = time.time()
            
            document = Document(
                id=f"manual_{timestamp}_{hash(content) % 10000}",
                content=content,
                metadata={
                    "type": content_type,
                    "timestamp": timestamp,
                    "session_id": self.session_id
                },
                timestamp=timestamp,
                source_type="manual",
                session_id=self.session_id
            )
            
            await self.vector_db.add_document(
                content=document.content,
                metadata=document.metadata,
                source_type=document.source_type,
                session_id=document.session_id
            )
            
            self.logger.info(f"Processed manual content: {len(content)} characters")
            
        except Exception as e:
            self.logger.error(f"Error processing manual content: {e}")

# Global content processors for active sessions
active_processors: Dict[str, ContentProcessor] = {}

async def start_session_processing(session_id: str):
    """Start content processing for a session"""
    if session_id in active_processors:
        return
        
    processor = ContentProcessor(session_id)
    active_processors[session_id] = processor
    await processor.start_processing()
    
async def stop_session_processing(session_id: str):
    """Stop content processing for a session"""
    if session_id in active_processors:
        processor = active_processors[session_id]
        await processor.stop_processing()
        del active_processors[session_id]
        
def get_session_processor(session_id: str) -> Optional[ContentProcessor]:
    """Get the processor for a session"""
    return active_processors.get(session_id)
