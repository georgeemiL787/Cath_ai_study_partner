"""
Audio Capture Module for AI Study Partner
Handles real-time audio capture and processing
"""

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: PyAudio not available. Audio capture will be disabled.")

try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    print("Warning: WebRTC VAD not available. Voice activity detection will be disabled.")

import numpy as np
import threading
import time
import wave
import io
from typing import Optional, Callable, List
from dataclasses import dataclass
import librosa
from collections import deque

@dataclass
class AudioConfig:
    """Configuration for audio capture"""
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1
    format: int = 8 if PYAUDIO_AVAILABLE else 8  # paInt16 = 8
    vad_aggressiveness: int = 2  # 0-3, higher is more aggressive
    silence_threshold: float = 0.01
    min_speech_duration: float = 0.5  # seconds
    max_silence_duration: float = 2.0  # seconds

class AudioCapture:
    """Real-time audio capture with voice activity detection"""
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        if PYAUDIO_AVAILABLE:
            self.audio = pyaudio.PyAudio()
        else:
            self.audio = None
        self.stream: Optional[pyaudio.Stream] = None
        self.is_capturing = False
        self.capture_thread: Optional[threading.Thread] = None
        self.audio_callback: Optional[Callable] = None
        
        # Voice Activity Detection
        if WEBRTCVAD_AVAILABLE:
            self.vad = webrtcvad.Vad(self.config.vad_aggressiveness)
        else:
            self.vad = None
        
        # Audio buffer for processing
        self.audio_buffer = deque(maxlen=int(self.config.sample_rate * 10))  # 10 seconds
        self.speech_segments: List[np.ndarray] = []
        self.current_segment = []
        self.in_speech = False
        self.silence_start = None
        
        # Statistics
        self.start_time = None
        self.total_samples = 0
        self.speech_samples = 0
        
    def set_callback(self, callback: Callable[[np.ndarray, float], None]):
        """Set callback function for audio chunks"""
        self.audio_callback = callback
        
    def start_capture(self):
        """Start audio capture"""
        if not PYAUDIO_AVAILABLE:
            print("❌ Audio capture not available: PyAudio not installed")
            return False
            
        if self.is_capturing:
            return True
            
        try:
            self.stream = self.audio.open(
                format=self.config.format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                frames_per_buffer=self.config.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_capturing = True
            self.start_time = time.time()
            self.total_samples = 0
            self.speech_samples = 0
            
            self.stream.start_stream()
            print("🎤 Audio capture started")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start audio capture: {e}")
            return False
            
    def stop_capture(self):
        """Stop audio capture"""
        self.is_capturing = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        # Process any remaining speech segment
        if self.current_segment:
            self._finalize_speech_segment()
            
        print("Audio capture stopped")
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for real-time audio processing"""
        if not self.is_capturing:
            return (None, pyaudio.paComplete)
            
        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        self.audio_buffer.extend(audio_data)
        self.total_samples += len(audio_data)
        
        # Voice Activity Detection
        is_speech = self._detect_speech(audio_data)
        
        if is_speech:
            self.speech_samples += len(audio_data)
            self.current_segment.extend(audio_data)
            self.silence_start = None
            
            if not self.in_speech:
                self.in_speech = True
                print("Speech detected")
        else:
            if self.in_speech:
                if self.silence_start is None:
                    self.silence_start = time.time()
                elif time.time() - self.silence_start > self.config.max_silence_duration:
                    self._finalize_speech_segment()
                    self.in_speech = False
                    self.silence_start = None
                    
        # Call user callback
        if self.audio_callback:
            timestamp = time.time() - self.start_time if self.start_time else 0
            self.audio_callback(audio_data, timestamp)
            
        return (None, 0)  # paContinue = 0
        
    def _detect_speech(self, audio_data: np.ndarray) -> bool:
        """Detect speech using WebRTC VAD"""
        if not WEBRTCVAD_AVAILABLE or self.vad is None:
            # Fallback: simple energy-based detection
            energy = np.mean(np.abs(audio_data))
            return energy > 0.01  # Simple threshold
            
        try:
            # WebRTC VAD expects 10ms, 20ms, or 30ms frames
            # We'll use 20ms frames (320 samples at 16kHz)
            frame_duration_ms = 20
            frame_size = int(self.config.sample_rate * frame_duration_ms / 1000)
            
            if len(audio_data) < frame_size:
                return False
                
            # Convert to bytes for VAD
            audio_bytes = audio_data.astype(np.int16).tobytes()
            
            # Check if speech is detected in any frame
            for i in range(0, len(audio_bytes) - frame_size * 2, frame_size * 2):
                frame = audio_bytes[i:i + frame_size * 2]
                if self.vad.is_speech(frame, self.config.sample_rate):
                    return True
                    
            return False
            
        except Exception as e:
            print(f"VAD error: {e}")
            # Fallback to simple amplitude-based detection
            return np.max(np.abs(audio_data)) > self.config.silence_threshold * 32767
            
    def _finalize_speech_segment(self):
        """Finalize current speech segment"""
        if not self.current_segment:
            return
            
        # Convert to numpy array
        segment = np.array(self.current_segment, dtype=np.float32) / 32767.0
        
        # Check minimum duration
        duration = len(segment) / self.config.sample_rate
        if duration >= self.config.min_speech_duration:
            self.speech_segments.append(segment)
            print(f"Speech segment saved: {duration:.2f}s")
            
        self.current_segment = []
        
    def get_audio_buffer(self, duration_seconds: float = 5.0) -> np.ndarray:
        """Get recent audio buffer"""
        samples_needed = int(duration_seconds * self.config.sample_rate)
        buffer_array = np.array(list(self.audio_buffer))
        
        if len(buffer_array) > samples_needed:
            return buffer_array[-samples_needed:]
        return buffer_array
        
    def get_speech_segments(self) -> List[np.ndarray]:
        """Get all captured speech segments"""
        return self.speech_segments.copy()
        
    def clear_speech_segments(self):
        """Clear stored speech segments"""
        self.speech_segments = []
        
    def save_audio_to_file(self, filename: str, audio_data: np.ndarray):
        """Save audio data to WAV file"""
        # Convert float32 to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.config.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.config.format))
            wf.setframerate(self.config.sample_rate)
            wf.writeframes(audio_int16.tobytes())
            
    def get_capture_stats(self) -> dict:
        """Get audio capture statistics"""
        if not self.start_time:
            return {"status": "not_started"}
            
        elapsed = time.time() - self.start_time
        speech_ratio = self.speech_samples / self.total_samples if self.total_samples > 0 else 0
        
        return {
            "status": "capturing" if self.is_capturing else "stopped",
            "elapsed_time": elapsed,
            "total_samples": self.total_samples,
            "speech_samples": self.speech_samples,
            "speech_ratio": speech_ratio,
            "speech_segments": len(self.speech_segments),
            "in_speech": self.in_speech,
            "sample_rate": self.config.sample_rate
        }
        
    def cleanup(self):
        """Cleanup audio resources"""
        self.stop_capture()
        if hasattr(self, 'audio') and self.audio is not None:
            self.audio.terminate()
