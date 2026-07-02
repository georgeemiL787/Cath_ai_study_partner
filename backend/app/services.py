"""
Service Manager for AI Study Partner
Centralized service initialization and dependency injection
"""

import os
from typing import Optional, Dict, Any

# Import services with error handling
try:
    from .database.vector_db import VectorDB
    VECTOR_DB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: VectorDB not available: {e}")
    VECTOR_DB_AVAILABLE = False

try:
    from .capture.screen_capture import ScreenCapture, CaptureConfig
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ScreenCapture not available: {e}")
    SCREEN_CAPTURE_AVAILABLE = False

try:
    from .capture.audio_capture import AudioCapture, AudioConfig
    AUDIO_CAPTURE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AudioCapture not available: {e}")
    AUDIO_CAPTURE_AVAILABLE = False

try:
    from .ai.unified_llm_service import UnifiedLLMService
    LLM_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: UnifiedLLMService not available: {e}")
    LLM_SERVICE_AVAILABLE = False

try:
    from .processing.ocr_processor import OCRProcessor, OCRConfig
    OCR_PROCESSOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OCRProcessor not available: {e}")
    OCR_PROCESSOR_AVAILABLE = False

try:
    from .processing.speech_processor import SpeechProcessor, STTConfig
    SPEECH_PROCESSOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SpeechProcessor not available: {e}")
    SPEECH_PROCESSOR_AVAILABLE = False

class ServiceManager:
    """Centralized service manager for dependency injection"""
    
    def __init__(self):
        self.vector_db: Optional[VectorDB] = None
        self.screen_capture: Optional[ScreenCapture] = None
        self.audio_capture: Optional[AudioCapture] = None
        self.llm_service: Optional[UnifiedLLMService] = None
        self.ocr_processor: Optional[OCRProcessor] = None
        self.speech_processor: Optional[SpeechProcessor] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize all services"""
        if self._initialized:
            return
        
        try:
            # Initialize AI service
            if LLM_SERVICE_AVAILABLE:
                try:
                    # Determine provider from env or settings
                    provider = os.getenv("LLM_PROVIDER") or os.getenv("llm_provider") or "gemini"
                    # If DeepSeek key present, prefer deepseek when provider is auto
                    if provider == "auto" and os.getenv("DEEPSEEK_API_KEY"):
                        provider = "deepseek"
                    self.llm_service = UnifiedLLMService(provider=provider)
                    if self.llm_service.active_service:
                        print(f"[OK] AI service initialized with {self.llm_service.active_service['provider']}")
                    else:
                        print("[WARN] AI service not available")
                        self.llm_service = None
                except Exception as e:
                    print(f"[WARN] AI service not available: {e}")
                    self.llm_service = None
            else:
                print("[WARN] AI service not available (missing dependencies)")
                self.llm_service = None
            
            # Initialize Vector Database
            if VECTOR_DB_AVAILABLE:
                try:
                    db_path = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
                    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
                    self.vector_db = VectorDB(db_path=db_path, embedding_model=embedding_model)
                    print("[OK] Vector database initialized")
                except Exception as e:
                    print(f"[WARN] Vector database not available: {e}")
                    self.vector_db = None
            else:
                print("[WARN] Vector database not available (missing dependencies)")
                self.vector_db = None
            
            # Initialize Screen Capture
            if SCREEN_CAPTURE_AVAILABLE:
                try:
                    fps = int(os.getenv("SCREEN_CAPTURE_FPS", "1"))
                    capture_config = CaptureConfig(fps=fps)
                    self.screen_capture = ScreenCapture(capture_config)
                    print("[OK] Screen capture service initialized")
                except Exception as e:
                    print(f"[WARN] Screen capture not available: {e}")
                    self.screen_capture = None
            else:
                print("[WARN] Screen capture not available (missing dependencies)")
                self.screen_capture = None
            
            # Initialize Audio Capture
            if AUDIO_CAPTURE_AVAILABLE:
                try:
                    sample_rate = int(os.getenv("AUDIO_CAPTURE_RATE", "16000"))
                    chunk_size = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))
                    audio_config = AudioConfig(sample_rate=sample_rate, chunk_size=chunk_size)
                    self.audio_capture = AudioCapture(audio_config)
                    print("[OK] Audio capture service initialized")
                except Exception as e:
                    print(f"[WARN] Audio capture not available: {e}")
                    self.audio_capture = None
            else:
                print("[WARN] Audio capture not available (missing dependencies)")
                self.audio_capture = None
            
            # Initialize OCR Processor
            if OCR_PROCESSOR_AVAILABLE:
                try:
                    ocr_engine = os.getenv("OCR_ENGINE", "tesseract")
                    tesseract_path = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
                    ocr_config = OCRConfig(engine=ocr_engine, tesseract_path=tesseract_path)
                    self.ocr_processor = OCRProcessor(ocr_config)
                    print("[OK] OCR processor initialized")
                except Exception as e:
                    print(f"[WARN] OCR processor not available: {e}")
                    self.ocr_processor = None
            else:
                print("[WARN] OCR processor not available (missing dependencies)")
                self.ocr_processor = None
            
            # Initialize Speech Processor
            if SPEECH_PROCESSOR_AVAILABLE:
                try:
                    stt_engine = os.getenv("STT_ENGINE", "whisper")
                    whisper_model = os.getenv("WHISPER_MODEL", "base")
                    stt_config = STTConfig(engine=stt_engine, model=whisper_model)
                    self.speech_processor = SpeechProcessor(stt_config)
                    print("[OK] Speech processor initialized")
                except Exception as e:
                    print(f"[WARN] Speech processor not available: {e}")
                    self.speech_processor = None
            else:
                print("[WARN] Speech processor not available (missing dependencies)")
                self.speech_processor = None
            
            self._initialized = True
            print("[OK] All services initialized successfully!")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize services: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup all services"""
        if self.vector_db:
            await self.vector_db.close()
        if self.screen_capture:
            self.screen_capture.cleanup()
        if self.audio_capture:
            self.audio_capture.cleanup()
        
        self._initialized = False
        print("[INFO] Service cleanup complete")

    async def apply_settings(self, settings: Dict[str, Any]):
        """Apply runtime settings by updating environment variables and reinitializing services as needed."""
        # Update environment variables from settings (used by initializers)
        if settings is None:
            return

        # AI / LLM
        if "llm_provider" in settings and settings["llm_provider"] is not None:
            os.environ["LLM_PROVIDER"] = str(settings["llm_provider"]) or os.environ.get("LLM_PROVIDER", "")
        if "openai_api_key" in settings and settings["openai_api_key"] is not None:
            os.environ["OPENAI_API_KEY"] = settings["openai_api_key"]
        if "gemini_api_key" in settings and settings["gemini_api_key"] is not None:
            os.environ["GEMINI_API_KEY"] = settings["gemini_api_key"]
        if "deepseek_api_key" in settings and settings["deepseek_api_key"] is not None:
            os.environ["DEEPSEEK_API_KEY"] = settings["deepseek_api_key"]
        if "deepseek_base_url" in settings and settings["deepseek_base_url"] is not None:
            os.environ["DEEPSEEK_BASE_URL"] = settings["deepseek_base_url"]
        if "deepseek_model" in settings and settings["deepseek_model"] is not None:
            os.environ["DEEPSEEK_MODEL"] = settings["deepseek_model"]
        if "model" in settings and settings["model"] is not None:
            # Default OpenAI model env for compatibility
            os.environ["OPENAI_MODEL"] = settings["model"]

        # Capture
        if "screen_fps" in settings and settings["screen_fps"] is not None:
            os.environ["SCREEN_CAPTURE_FPS"] = str(settings["screen_fps"])
        if "audio_sample_rate" in settings and settings["audio_sample_rate"] is not None:
            os.environ["AUDIO_CAPTURE_RATE"] = str(settings["audio_sample_rate"])
        if "audio_chunk_size" in settings and settings["audio_chunk_size"] is not None:
            os.environ["AUDIO_CHUNK_SIZE"] = str(settings["audio_chunk_size"])

        # OCR
        if "ocr_engine" in settings and settings["ocr_engine"] is not None:
            os.environ["OCR_ENGINE"] = settings["ocr_engine"]

        # STT
        if "stt_engine" in settings and settings["stt_engine"] is not None:
            os.environ["STT_ENGINE"] = settings["stt_engine"]
        if "whisper_model" in settings and settings["whisper_model"] is not None:
            os.environ["WHISPER_MODEL"] = settings["whisper_model"]

        # Branding / Persona
        if "assistant_name" in settings and settings["assistant_name"] is not None:
            os.environ["ASSISTANT_NAME"] = str(settings["assistant_name"])
        if "brand_name" in settings and settings["brand_name"] is not None:
            os.environ["BRAND_NAME"] = str(settings["brand_name"])

        # Reinitialize impacted services
        # LLM
        if self.llm_service is not None:
            try:
                # Drop existing instance
                self.llm_service = None
            except Exception:
                self.llm_service = None
        try:
            if LLM_SERVICE_AVAILABLE:
                from .ai.unified_llm_service import UnifiedLLMService  # local import to avoid cycles
                provider = os.getenv("LLM_PROVIDER") or "gemini"
                self.llm_service = UnifiedLLMService(provider=provider)
                if self.llm_service.active_service:
                    print(f"[OK] AI service reinitialized with {self.llm_service.active_service['provider']}")
                else:
                    print("[WARN] AI service not available after reinit")
        except Exception as e:
            print(f"[WARN] Failed to reinitialize AI service: {e}")
            self.llm_service = None

        # Screen capture
        if self.screen_capture is not None:
            try:
                self.screen_capture.cleanup()
            except Exception:
                pass
            self.screen_capture = None
        try:
            if SCREEN_CAPTURE_AVAILABLE:
                fps = int(os.getenv("SCREEN_CAPTURE_FPS", "1"))
                capture_config = CaptureConfig(fps=fps)
                self.screen_capture = ScreenCapture(capture_config)
                print("[OK] Screen capture service reinitialized")
        except Exception as e:
            print(f"[WARN] Failed to reinitialize screen capture: {e}")
            self.screen_capture = None

        # Audio capture
        if self.audio_capture is not None:
            try:
                self.audio_capture.cleanup()
            except Exception:
                pass
            self.audio_capture = None
        try:
            if AUDIO_CAPTURE_AVAILABLE:
                sample_rate = int(os.getenv("AUDIO_CAPTURE_RATE", "16000"))
                chunk_size = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))
                audio_config = AudioConfig(sample_rate=sample_rate, chunk_size=chunk_size)
                self.audio_capture = AudioCapture(audio_config)
                print("[OK] Audio capture service reinitialized")
        except Exception as e:
            print(f"[WARN] Failed to reinitialize audio capture: {e}")
            self.audio_capture = None

        # OCR
        self.ocr_processor = None
        try:
            if OCR_PROCESSOR_AVAILABLE:
                ocr_engine = os.getenv("OCR_ENGINE", "tesseract")
                tesseract_path = os.getenv("TESSERACT_PATH", r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
                ocr_config = OCRConfig(engine=ocr_engine, tesseract_path=tesseract_path)
                self.ocr_processor = OCRProcessor(ocr_config)
                print("[OK] OCR processor reinitialized")
        except Exception as e:
            print(f"[WARN] Failed to reinitialize OCR processor: {e}")
            self.ocr_processor = None

        # STT
        self.speech_processor = None
        try:
            if SPEECH_PROCESSOR_AVAILABLE:
                stt_engine = os.getenv("STT_ENGINE", "whisper")
                whisper_model = os.getenv("WHISPER_MODEL", "base")
                stt_config = STTConfig(engine=stt_engine, model=whisper_model)
                self.speech_processor = SpeechProcessor(stt_config)
                print("[OK] Speech processor reinitialized")
        except Exception as e:
            print(f"[WARN] Failed to reinitialize speech processor: {e}")
            self.speech_processor = None

# Global service manager instance
service_manager = ServiceManager()
