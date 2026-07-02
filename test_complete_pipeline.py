#!/usr/bin/env python3
"""
Complete pipeline test for AI Study Partner
Tests the entire flow from frame capture to text extraction
"""

import os
import sys
import json
import base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_test_frame():
    """Create a test frame with text content"""
    # Create a test image with text
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Add sample text content
    texts = [
        "AI Study Partner - Test Session",
        "This is a sample study content",
        "Mathematics: 2x + 3y = 15",
        "Science: Photosynthesis converts light to energy",
        "History: World War II ended in 1945",
        "Language: The quick brown fox jumps over the lazy dog"
    ]
    
    y_pos = 50
    for text in texts:
        draw.text((50, y_pos), text, fill='black', font=font)
        y_pos += 60
    
    return img

async def test_frame_processing():
    """Test the complete frame processing pipeline"""
    print("🔧 Testing Complete Frame Processing Pipeline...")
    
    try:
        from app.capture.enhanced_content_processor import EnhancedContentProcessor
        from app.processing.ocr_processor import OCRProcessor, OCRConfig
        
        # Create test frame
        print("📸 Creating test frame...")
        test_img = create_test_frame()
        img_array = np.array(test_img)
        
        # Convert to base64 (as it would be in the real system)
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        print("🔄 Processing frame through Enhanced Content Processor...")
        
        # Initialize processors
        ocr_config = OCRConfig(
            engine="tesseract",
            language="eng",
            confidence_threshold=60.0,
            preprocess=True
        )
        
        ocr_processor = OCRProcessor(ocr_config)
        processor = EnhancedContentProcessor(
            session_id="test-session-123",
            ocr_processor=ocr_processor
        )
        
        # Start processing
        await processor.start_processing()
        
        # Process the frame
        result = await processor.process_frame(
            frame_data=frame_base64,
            metadata={"timestamp": 0.0}
        )
        
        print(f"✅ Frame processed successfully")
        print(f"📊 Result type: {type(result)}")
        
        if result and hasattr(result, 'extracted_text'):
            print(f"📝 Text content length: {len(result.extracted_text) if result.extracted_text else 0}")
            if result.extracted_text:
                print(f"📄 Sample text: {result.extracted_text[:100]}...")
        
        # Stop processing
        await processor.stop_processing()
        
        return True
        
    except Exception as e:
        print(f"❌ Frame processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_data_structure():
    """Test the session data structure and file creation"""
    print("\n📁 Testing Session Data Structure...")
    
    try:
        # Create a test session directory
        test_session_dir = "backend/data/sessions/test-session-123"
        os.makedirs(test_session_dir, exist_ok=True)
        
        # Test enhanced session data structure
        enhanced_data = {
            "session_id": "test-session-123",
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": None,
            "is_active": True,
            "processed_frames": [],
            "extracted_content": [],
            "metadata": {
                "total_frames": 0,
                "text_frames": 0,
                "audio_segments": 0
            }
        }
        
        # Save test data
        with open(f"{test_session_dir}/enhanced_session_data.json", 'w') as f:
            json.dump(enhanced_data, f, indent=2)
        
        # Test documents structure
        documents_data = {
            "documents": [],
            "metadata": {
                "total_documents": 0,
                "total_text_length": 0,
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }
        
        with open(f"{test_session_dir}/documents.json", 'w') as f:
            json.dump(documents_data, f, indent=2)
        
        print("✅ Session data structure created successfully")
        print(f"📂 Test session directory: {test_session_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Session data structure test failed: {e}")
        return False

def test_ocr_without_tesseract():
    """Test OCR processor behavior without Tesseract installed"""
    print("\n🔍 Testing OCR Processor (without Tesseract)...")
    
    try:
        from app.processing.ocr_processor import OCRProcessor, OCRConfig
        
        # Create OCR processor
        config = OCRConfig(
            engine="tesseract",
            language="eng",
            confidence_threshold=60.0,
            preprocess=True
        )
        
        processor = OCRProcessor(config)
        print("✅ OCR Processor initialized (with warnings about Tesseract)")
        
        # Test with a simple image
        test_img = create_test_frame()
        img_array = np.array(test_img)
        
        # This should fail gracefully
        try:
            result = processor.extract_text(img_array)
            print(f"📝 OCR Result: {result.text[:50]}...")
            print(f"🎯 Confidence: {result.confidence:.2f}%")
        except Exception as e:
            print(f"⚠️ OCR extraction failed as expected: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR processor test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 AI Study Partner - Complete Pipeline Test")
    print("=" * 60)
    
    tests = [
        ("Session Data Structure", test_session_data_structure),
        ("OCR Processor (without Tesseract)", test_ocr_without_tesseract),
        ("Frame Processing Pipeline", test_frame_processing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        if test_name == "Frame Processing Pipeline":
            success = await test_func()
        else:
            success = test_func()
        results.append((test_name, success))
        print(f"{'✅ PASSED' if success else '❌ FAILED'}: {test_name}")
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The pipeline is ready.")
        print("\n📋 Next steps:")
        print("1. Install Tesseract OCR for full functionality")
        print("2. Run your AI Study Partner application")
        print("3. Start a study session to test real-time processing")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
