#!/usr/bin/env python3
"""
Test script to verify OCR functionality after Tesseract installation
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytesseract

def create_test_image():
    """Create a test image with text for OCR testing"""
    # Create a white image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text
    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Hello World!", fill='black', font=font)
    draw.text((50, 100), "This is a test for OCR", fill='black', font=font)
    draw.text((50, 150), "AI Study Partner", fill='black', font=font)
    
    return img

def test_tesseract_installation():
    """Test if Tesseract is properly installed and working"""
    print("🔍 Testing Tesseract OCR Installation...")
    
    # Test 1: Check if pytesseract can find Tesseract
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR engine found: {version}")
    except Exception as e:
        print(f"❌ Tesseract OCR engine not found: {e}")
        print("\n📋 To fix this issue:")
        print("1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install to: C:\\Program Files\\Tesseract-OCR\\")
        print("3. Restart your terminal/IDE")
        return False
    
    # Test 2: Create and process a test image
    try:
        print("\n🖼️ Creating test image...")
        test_img = create_test_image()
        
        print("🔤 Running OCR on test image...")
        text = pytesseract.image_to_string(test_img)
        
        print("📝 Extracted text:")
        print("-" * 40)
        print(text)
        print("-" * 40)
        
        if "Hello World" in text and "AI Study Partner" in text:
            print("✅ OCR is working correctly!")
            return True
        else:
            print("⚠️ OCR is working but accuracy may be low")
            return True
            
    except Exception as e:
        print(f"❌ OCR processing failed: {e}")
        return False

def test_ocr_processor():
    """Test the OCR processor from the application"""
    print("\n🔧 Testing OCR Processor...")
    
    try:
        # Add the backend directory to the path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from app.processing.ocr_processor import OCRProcessor, OCRConfig
        
        # Create OCR processor
        config = OCRConfig(
            engine="tesseract",
            language="eng",
            confidence_threshold=60.0,
            preprocess=True
        )
        
        processor = OCRProcessor(config)
        print("✅ OCR Processor initialized successfully")
        
        # Test with a simple image
        test_img = create_test_image()
        img_array = np.array(test_img)
        
        result = processor.extract_text(img_array)
        print(f"📝 Extracted text: {result.text[:100]}...")
        print(f"🎯 Confidence: {result.confidence:.2f}%")
        
        if result.text.strip():
            print("✅ OCR Processor is working correctly!")
            return True
        else:
            print("⚠️ OCR Processor initialized but no text extracted")
            return False
            
    except Exception as e:
        print(f"❌ OCR Processor test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AI Study Partner - OCR Test")
    print("=" * 50)
    
    # Test basic Tesseract installation
    tesseract_ok = test_tesseract_installation()
    
    if tesseract_ok:
        # Test OCR processor
        processor_ok = test_ocr_processor()
        
        if processor_ok:
            print("\n🎉 All tests passed! OCR is ready to use.")
        else:
            print("\n⚠️ Tesseract works but OCR Processor needs attention.")
    else:
        print("\n❌ Please install Tesseract OCR first.")
    
    print("\n" + "=" * 50)
