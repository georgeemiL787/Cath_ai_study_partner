"""
Speech-to-Text Processing Module for AI Study Partner
Handles audio transcription using multiple STT engines
"""

import numpy as np
import time
import logging
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
import io
import wave

# Try to import Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class TranscriptionResult:
    """Speech-to-text transcription result"""
    text: str
    confidence: float
    language: str
    segments: List[Dict[str, any]]
    processing_time: float
    word_timestamps: Optional[List[Dict[str, any]]] = None

@dataclass
class STTConfig:
    """Speech-to-text configuration"""
    engine: str = "whisper"  # Options: whisper, openai, google
    model: str = "base"  # Model size/type
    language: str = "en"
    sample_rate: int = 16000
    chunk_duration: float = 30.0  # seconds
    openai_api_key: Optional[str] = None
    confidence_threshold: float = 0.5

class SpeechProcessor:
    """Multi-engine speech-to-text processor"""
    
    def __init__(self, config: Optional[STTConfig] = None):
        self.config = config or STTConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Whisper
        self.whisper_model = None
        if WHISPER_AVAILABLE and self.config.engine == "whisper":
            try:
                self.whisper_model = whisper.load_model(self.config.model)
                self.logger.info(f"Whisper model '{self.config.model}' loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load Whisper model: {e}")
                raise
                
        # Initialize OpenAI
        if OPENAI_AVAILABLE and self.config.engine == "openai":
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key required for OpenAI STT")
            openai.api_key = self.config.openai_api_key
            
    def transcribe_whisper(self, audio_data: np.ndarray) -> TranscriptionResult:
        """Transcribe audio using Whisper"""
        if not self.whisper_model:
            raise RuntimeError("Whisper model not initialized")
            
        start_time = time.time()
        
        # Ensure audio is in the right format
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
            
        # Normalize audio
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
            
        # Transcribe
        result = self.whisper_model.transcribe(
            audio_data,
            language=self.config.language,
            word_timestamps=True,
            verbose=False
        )
        
        # Extract segments with timestamps
        segments = []
        word_timestamps = []
        
        for segment in result.get("segments", []):
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "confidence": segment.get("avg_logprob", 0)
            })
            
        # Extract word-level timestamps
        for segment in result.get("segments", []):
            for word_info in segment.get("words", []):
                word_timestamps.append({
                    "word": word_info["word"],
                    "start": word_info["start"],
                    "end": word_info["end"],
                    "confidence": word_info.get("probability", 0)
                })
                
        processing_time = time.time() - start_time
        
        return TranscriptionResult(
            text=result["text"].strip(),
            confidence=1.0,  # Whisper doesn't provide overall confidence
            language=result.get("language", self.config.language),
            segments=segments,
            processing_time=processing_time,
            word_timestamps=word_timestamps
        )
        
    def transcribe_openai(self, audio_data: np.ndarray) -> TranscriptionResult:
        """Transcribe audio using OpenAI Whisper API"""
        if not OPENAI_AVAILABLE:
            raise RuntimeError("OpenAI library not available")
            
        start_time = time.time()
        
        # Convert numpy array to WAV format
        wav_buffer = self._numpy_to_wav_buffer(audio_data)
        
        # Transcribe using OpenAI API
        wav_buffer.seek(0)
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=wav_buffer,
            language=self.config.language,
            response_format="verbose_json"
        )
        
        # Extract segments
        segments = []
        for segment in transcript.get("segments", []):
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "confidence": segment.get("avg_logprob", 0)
            })
            
        processing_time = time.time() - start_time
        
        return TranscriptionResult(
            text=transcript["text"].strip(),
            confidence=1.0,
            language=transcript.get("language", self.config.language),
            segments=segments,
            processing_time=processing_time
        )
        
    def _numpy_to_wav_buffer(self, audio_data: np.ndarray) -> io.BytesIO:
        """Convert numpy audio array to WAV buffer"""
        # Ensure audio is in the right format
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
            
        # Convert to 16-bit PCM
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Create WAV buffer
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.config.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
            
        return wav_buffer
        
    def transcribe(self, audio_data: np.ndarray) -> TranscriptionResult:
        """Transcribe audio using configured STT engine"""
        if self.config.engine == "whisper":
            return self.transcribe_whisper(audio_data)
        elif self.config.engine == "openai":
            return self.transcribe_openai(audio_data)
        else:
            raise ValueError(f"Unsupported STT engine: {self.config.engine}")
            
    def transcribe_chunks(self, audio_chunks: List[np.ndarray]) -> List[TranscriptionResult]:
        """Transcribe multiple audio chunks"""
        results = []
        for chunk in audio_chunks:
            try:
                result = self.transcribe(chunk)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to transcribe chunk: {e}")
                # Create empty result for failed chunk
                results.append(TranscriptionResult(
                    text="",
                    confidence=0.0,
                    language=self.config.language,
                    segments=[],
                    processing_time=0.0
                ))
        return results
        
    def combine_transcriptions(self, results: List[TranscriptionResult]) -> TranscriptionResult:
        """Combine multiple transcription results into one"""
        if not results:
            return TranscriptionResult(
                text="",
                confidence=0.0,
                language=self.config.language,
                segments=[],
                processing_time=0.0
            )
            
        # Combine text
        combined_text = " ".join([r.text for r in results if r.text])
        
        # Combine segments with adjusted timestamps
        combined_segments = []
        current_time = 0.0
        
        for result in results:
            for segment in result.segments:
                adjusted_segment = {
                    "start": segment["start"] + current_time,
                    "end": segment["end"] + current_time,
                    "text": segment["text"],
                    "confidence": segment["confidence"]
                }
                combined_segments.append(adjusted_segment)
                
            # Update current time for next result
            if result.segments:
                current_time += result.segments[-1]["end"]
                
        # Calculate average confidence
        avg_confidence = np.mean([r.confidence for r in results if r.confidence > 0])
        
        # Calculate total processing time
        total_processing_time = sum(r.processing_time for r in results)
        
        return TranscriptionResult(
            text=combined_text,
            confidence=avg_confidence,
            language=results[0].language,
            segments=combined_segments,
            processing_time=total_processing_time
        )
        
    def get_available_engines(self) -> List[str]:
        """Get list of available STT engines"""
        engines = []
        if WHISPER_AVAILABLE:
            engines.append("whisper")
        if OPENAI_AVAILABLE:
            engines.append("openai")
        return engines
        
    def get_whisper_models(self) -> List[str]:
        """Get available Whisper models"""
        if not WHISPER_AVAILABLE:
            return []
        return ["tiny", "base", "small", "medium", "large"]

