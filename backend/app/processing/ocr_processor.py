"""
OCR Processing Module for AI Study Partner
Handles text extraction from images using multiple OCR engines
"""

import cv2
import numpy as np
import pytesseract
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from PIL import Image
import re
import logging

# Try to import PaddleOCR (optional)
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False

@dataclass
class OCRResult:
    """OCR processing result"""
    text: str
    confidence: float
    bounding_boxes: List[Tuple[int, int, int, int]]  # (x, y, width, height)
    words: List[Dict[str, any]]
    processing_time: float

@dataclass
class OCRConfig:
    """OCR configuration"""
    engine: str = "tesseract"  # Options: tesseract, paddleocr
    language: str = "eng"
    tesseract_path: Optional[str] = None
    confidence_threshold: float = 60.0
    preprocess: bool = True
    remove_noise: bool = True

class OCRProcessor:
    """Multi-engine OCR processor with image preprocessing"""
    
    def __init__(self, config: Optional[OCRConfig] = None):
        self.config = config or OCRConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Tesseract
        self._setup_tesseract()
            
        # Initialize PaddleOCR if available
        self.paddle_ocr = None
        if PADDLE_AVAILABLE and self.config.engine == "paddleocr":
            try:
                self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
                self.logger.info("PaddleOCR initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize PaddleOCR: {e}")
                self.config.engine = "tesseract"
    
    def _setup_tesseract(self):
        """Setup Tesseract OCR with proper path configuration"""
        # Try to find Tesseract in common locations
        possible_paths = [
            self.config.tesseract_path,
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            "tesseract"  # If it's in PATH
        ]
        
        tesseract_found = False
        for path in possible_paths:
            if path and os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                self.logger.info(f"Tesseract found at: {path}")
                tesseract_found = True
                break
        
        if not tesseract_found:
            self.logger.error("Tesseract OCR not found! Please install Tesseract OCR:")
            self.logger.error("1. Run: winget install tesseract-ocr.tesseract")
            self.logger.error("2. Or download from: https://github.com/UB-Mannheim/tesseract/wiki")
            self.logger.error("3. Install to: C:\\Program Files\\Tesseract-OCR\\")
            self.logger.error("4. Or set TESSERACT_PATH environment variable")
            raise RuntimeError("Tesseract OCR not found. Please install Tesseract OCR first.")
                
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        if not self.config.preprocess:
            return image
            
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Remove noise
        if self.config.remove_noise:
            # Gaussian blur to reduce noise
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return binary
        
    def extract_text_tesseract(self, image: np.ndarray) -> OCRResult:
        """Extract text using Tesseract OCR"""
        import time
        start_time = time.time()
        
        try:
            # Validate input image
            if image is None or image.size == 0:
                self.logger.warning("Empty or invalid image provided to OCR")
                return OCRResult(
                    text="",
                    confidence=0.0,
                    bounding_boxes=[],
                    words=[],
                    processing_time=time.time() - start_time
                )
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Get detailed data from Tesseract
            try:
                data = pytesseract.image_to_data(
                    processed_image, 
                    lang=self.config.language,
                    output_type=pytesseract.Output.DICT
                )
            except Exception as e:
                self.logger.error(f"Tesseract OCR failed: {e}")
                return OCRResult(
                    text="",
                    confidence=0.0,
                    bounding_boxes=[],
                    words=[],
                    processing_time=time.time() - start_time
                )
            
            # Extract text and confidence scores
            words = []
            bounding_boxes = []
            text_parts = []
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = float(data['conf'][i])
                
                if text and conf > self.config.confidence_threshold:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    words.append({
                        'text': text,
                        'confidence': conf,
                        'bbox': (x, y, w, h)
                    })
                    
                    bounding_boxes.append((x, y, w, h))
                    text_parts.append(text)
                    
            # Combine all text
            full_text = ' '.join(text_parts)
            
            # Calculate average confidence
            avg_confidence = np.mean([w['confidence'] for w in words]) if words else 0
            
            processing_time = time.time() - start_time
            
            self.logger.debug(f"OCR extracted {len(full_text)} characters with {avg_confidence:.1f}% confidence")
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                bounding_boxes=bounding_boxes,
                words=words,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"OCR processing error: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                bounding_boxes=[],
                words=[],
                processing_time=time.time() - start_time
            )
        
    def extract_text_paddleocr(self, image: np.ndarray) -> OCRResult:
        """Extract text using PaddleOCR"""
        import time
        start_time = time.time()
        
        if not self.paddle_ocr:
            raise RuntimeError("PaddleOCR not initialized")
            
        # PaddleOCR expects RGB images
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
            
        # Run OCR
        results = self.paddle_ocr.ocr(rgb_image, cls=True)
        
        words = []
        bounding_boxes = []
        text_parts = []
        confidences = []
        
        if results and results[0]:
            for line in results[0]:
                if line:
                    bbox, (text, confidence) = line
                    
                    if confidence > self.config.confidence_threshold / 100:  # PaddleOCR uses 0-1 scale
                        # Convert bbox to (x, y, w, h) format
                        x_coords = [point[0] for point in bbox]
                        y_coords = [point[1] for point in bbox]
                        x, y = min(x_coords), min(y_coords)
                        w, h = max(x_coords) - x, max(y_coords) - y
                        
                        words.append({
                            'text': text,
                            'confidence': confidence * 100,  # Convert to 0-100 scale
                            'bbox': (int(x), int(y), int(w), int(h))
                        })
                        
                        bounding_boxes.append((int(x), int(y), int(w), int(h)))
                        text_parts.append(text)
                        confidences.append(confidence * 100)
                        
        # Combine all text
        full_text = ' '.join(text_parts)
        avg_confidence = np.mean(confidences) if confidences else 0
        
        processing_time = time.time() - start_time
        
        return OCRResult(
            text=full_text,
            confidence=avg_confidence,
            bounding_boxes=bounding_boxes,
            words=words,
            processing_time=processing_time
        )
        
    def extract_text(self, image: np.ndarray) -> OCRResult:
        """Extract text from image using configured OCR engine"""
        try:
            if self.config.engine == "tesseract":
                return self.extract_text_tesseract(image)
            elif self.config.engine == "paddleocr" and PADDLE_AVAILABLE:
                return self.extract_text_paddleocr(image)
            else:
                self.logger.error(f"Unsupported OCR engine: {self.config.engine}")
                return OCRResult(
                    text="",
                    confidence=0.0,
                    bounding_boxes=[],
                    words=[],
                    processing_time=0.0
                )
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                bounding_boxes=[],
                words=[],
                processing_time=0.0
            )
            
    def extract_text_from_region(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> OCRResult:
        """Extract text from a specific region of the image"""
        x, y, w, h = region
        cropped = image[y:y+h, x:x+w]
        return self.extract_text(cropped)
        
    def detect_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect potential text regions in the image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Use MSER (Maximally Stable Extremal Regions) for text detection
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        # Convert regions to bounding boxes
        text_regions = []
        for region in regions:
            x, y, w, h = cv2.boundingRect(region)
            # Filter by size (remove very small or very large regions)
            if 20 < w < 500 and 10 < h < 100:
                text_regions.append((x, y, w, h))
                
        return text_regions
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)
        
        # Remove lines with only numbers or special characters
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not re.match(r'^[\d\s.,!?;:()-]+$', line):
                cleaned_lines.append(line)
                
        return '\n'.join(cleaned_lines)
        
    def get_available_engines(self) -> List[str]:
        """Get list of available OCR engines"""
        engines = ["tesseract"]
        if PADDLE_AVAILABLE:
            engines.append("paddleocr")
        return engines

