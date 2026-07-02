"""
Processing API endpoints for AI Study Partner
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np
import cv2
import time

from ..processing.ocr_processor import OCRProcessor, OCRConfig, OCRResult
from ..processing.speech_processor import SpeechProcessor, STTConfig, TranscriptionResult
from ..services import service_manager

router = APIRouter()

class OCRRequest(BaseModel):
    image_base64: Optional[str] = None
    region: Optional[Dict[str, int]] = None  # {"x": 0, "y": 0, "width": 100, "height": 100}
    engine: str = "tesseract"
    language: str = "eng"
    preprocess: bool = True

class STTRequest(BaseModel):
    audio_data: Optional[List[float]] = None  # Audio samples as list
    engine: str = "whisper"
    model: str = "base"
    language: str = "en"

class ProcessingResponse(BaseModel):
    success: bool
    result: Dict[str, Any]
    processing_time: float
    error: Optional[str] = None

# Dependencies for processing services
async def get_ocr_processor() -> OCRProcessor:
    return service_manager.ocr_processor

async def get_speech_processor() -> SpeechProcessor:
    return service_manager.speech_processor

@router.post("/ocr/extract", response_model=ProcessingResponse)
async def extract_text_ocr(request: OCRRequest, ocr_processor: OCRProcessor = Depends(get_ocr_processor)):
    """Extract text from image using OCR"""
    if not ocr_processor:
        raise HTTPException(status_code=500, detail="OCR processor not initialized")
        
    start_time = time.time()
    
    try:
        # Decode base64 image
        if not request.image_base64:
            raise HTTPException(status_code=400, detail="No image data provided")
            
        import base64
        from PIL import Image
        import io
        
        # Decode base64
        image_data = base64.b64decode(request.image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to OpenCV format
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Update OCR config
        ocr_processor.config.engine = request.engine
        ocr_processor.config.language = request.language
        ocr_processor.config.preprocess = request.preprocess
        
        # Extract text
        if request.region:
            region = (request.region["x"], request.region["y"], 
                     request.region["width"], request.region["height"])
            result = ocr_processor.extract_text_from_region(frame, region)
        else:
            result = ocr_processor.extract_text(frame)
            
        processing_time = time.time() - start_time
        
        return ProcessingResponse(
            success=True,
            result={
                "text": result.text,
                "confidence": result.confidence,
                "bounding_boxes": result.bounding_boxes,
                "word_count": len(result.words),
                "engine": request.engine
            },
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ProcessingResponse(
            success=False,
            result={},
            processing_time=processing_time,
            error=str(e)
        )

@router.post("/ocr/upload", response_model=ProcessingResponse)
async def extract_text_upload(file: UploadFile = File(...), ocr_processor: OCRProcessor = Depends(get_ocr_processor)):
    """Extract text from uploaded image file"""
    if not ocr_processor:
        raise HTTPException(status_code=500, detail="OCR processor not initialized")
        
    start_time = time.time()
    
    try:
        # Read uploaded file
        contents = await file.read()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
            
        # Extract text
        result = ocr_processor.extract_text(frame)
        
        processing_time = time.time() - start_time
        
        return ProcessingResponse(
            success=True,
            result={
                "text": result.text,
                "confidence": result.confidence,
                "bounding_boxes": result.bounding_boxes,
                "word_count": len(result.words),
                "filename": file.filename
            },
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ProcessingResponse(
            success=False,
            result={},
            processing_time=processing_time,
            error=str(e)
        )

@router.post("/stt/transcribe", response_model=ProcessingResponse)
async def transcribe_audio(request: STTRequest, speech_processor: SpeechProcessor = Depends(get_speech_processor)):
    """Transcribe audio using speech-to-text"""
    if not speech_processor:
        raise HTTPException(status_code=500, detail="STT processor not initialized")
        
    start_time = time.time()
    
    try:
        # Convert audio data to numpy array
        if not request.audio_data:
            raise HTTPException(status_code=400, detail="No audio data provided")
            
        audio_array = np.array(request.audio_data, dtype=np.float32)
        
        # Update STT config
        speech_processor.config.engine = request.engine
        speech_processor.config.model = request.model
        speech_processor.config.language = request.language
        
        # Transcribe
        result = speech_processor.transcribe(audio_array)
        
        processing_time = time.time() - start_time
        
        return ProcessingResponse(
            success=True,
            result={
                "text": result.text,
                "confidence": result.confidence,
                "language": result.language,
                "segments": result.segments,
                "word_timestamps": result.word_timestamps,
                "engine": request.engine
            },
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ProcessingResponse(
            success=False,
            result={},
            processing_time=processing_time,
            error=str(e)
        )

@router.post("/stt/upload", response_model=ProcessingResponse)
async def transcribe_audio_upload(file: UploadFile = File(...), speech_processor: SpeechProcessor = Depends(get_speech_processor)):
    """Transcribe uploaded audio file"""
    if not speech_processor:
        raise HTTPException(status_code=500, detail="STT processor not initialized")
        
    start_time = time.time()
    
    try:
        # Read uploaded file
        contents = await file.read()
        
        # Load audio using librosa
        import librosa
        import io
        
        audio_data, sample_rate = librosa.load(io.BytesIO(contents), sr=None)
        
        # Update sample rate in config
        speech_processor.config.sample_rate = sample_rate
        
        # Transcribe
        result = speech_processor.transcribe(audio_data)
        
        processing_time = time.time() - start_time
        
        return ProcessingResponse(
            success=True,
            result={
                "text": result.text,
                "confidence": result.confidence,
                "language": result.language,
                "segments": result.segments,
                "word_timestamps": result.word_timestamps,
                "filename": file.filename,
                "duration": len(audio_data) / sample_rate
            },
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ProcessingResponse(
            success=False,
            result={},
            processing_time=processing_time,
            error=str(e)
        )

@router.get("/ocr/engines")
async def get_ocr_engines(ocr_processor: OCRProcessor = Depends(get_ocr_processor)):
    """Get available OCR engines"""
    if not ocr_processor:
        raise HTTPException(status_code=500, detail="OCR processor not initialized")
        
    engines = ocr_processor.get_available_engines()
    
    return {
        "available_engines": engines,
        "current_engine": ocr_processor.config.engine
    }

@router.get("/stt/engines")
async def get_stt_engines(speech_processor: SpeechProcessor = Depends(get_speech_processor)):
    """Get available STT engines"""
    if not speech_processor:
        raise HTTPException(status_code=500, detail="STT processor not initialized")
        
    engines = speech_processor.get_available_engines()
    whisper_models = speech_processor.get_whisper_models()
    
    return {
        "available_engines": engines,
        "current_engine": speech_processor.config.engine,
        "whisper_models": whisper_models
    }

@router.post("/batch/process")
async def batch_process(requests: List[Dict[str, Any]]):
    """Process multiple OCR/STT requests in batch"""
    results = []
    
    for req in requests:
        try:
            if req.get("type") == "ocr":
                ocr_req = OCRRequest(**req.get("data", {}))
                result = await extract_text_ocr(ocr_req)
                results.append({"type": "ocr", "result": result})
                
            elif req.get("type") == "stt":
                stt_req = STTRequest(**req.get("data", {}))
                result = await transcribe_audio(stt_req)
                results.append({"type": "stt", "result": result})
                
        except Exception as e:
            results.append({
                "type": req.get("type", "unknown"),
                "error": str(e)
            })
            
    return {
        "results": results,
        "total_processed": len(results)
    }

