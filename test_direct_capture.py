#!/usr/bin/env python3
"""
Direct test of screen capture functionality
"""

import sys
import os
import time
import base64
import cv2
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_direct_capture():
    """Test screen capture directly"""
    print("🧪 Testing Direct Screen Capture")
    print("=" * 50)
    
    try:
        from app.capture.screen_capture import ScreenCapture, CaptureConfig
        
        print("1. Creating screen capture instance...")
        config = CaptureConfig(fps=1)
        capture = ScreenCapture(config)
        print("✅ Screen capture instance created")
        
        print("2. Testing single frame capture...")
        frame = capture.capture_single_frame()
        if frame is not None:
            print("✅ Single frame captured successfully")
            print(f"   Frame shape: {frame.shape}")
            print(f"   Frame type: {frame.dtype}")
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            print(f"   Base64 size: {len(frame_base64)} characters")
            
            # Save frame
            cv2.imwrite("test_frame.jpg", frame)
            print("   Frame saved as: test_frame.jpg")
            return True
        else:
            print("❌ Failed to capture single frame")
            return False
        
    except ImportError as e:
        print(f"❌ Could not import screen capture module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in direct screen capture test: {e}")
        return False

def test_mss_directly():
    """Test MSS library directly"""
    print("\n🔧 Testing MSS Library Directly")
    print("=" * 50)
    
    try:
        import mss
        
        print("1. Creating MSS instance...")
        with mss.mss() as sct:
            print("✅ MSS instance created")
            
            print("2. Getting monitor info...")
            monitors = sct.monitors
            print(f"   Found {len(monitors)} monitors")
            for i, monitor in enumerate(monitors):
                print(f"   Monitor {i}: {monitor}")
            
            print("3. Capturing screenshot...")
            screenshot = sct.grab(monitors[1])  # Primary monitor
            print("✅ Screenshot captured")
            print(f"   Size: {screenshot.size}")
            print(f"   Format: {screenshot.format}")
            
            # Convert to numpy array
            img = np.array(screenshot)
            print(f"   Array shape: {img.shape}")
            
            # Save screenshot
            from PIL import Image
            img_pil = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img_pil.save("mss_test.png")
            print("   Screenshot saved as: mss_test.png")
            
            return True
            
    except ImportError as e:
        print(f"❌ Could not import MSS: {e}")
        print("   Try: pip install mss")
        return False
    except Exception as e:
        print(f"❌ Error in MSS test: {e}")
        return False

if __name__ == "__main__":
    print("🎓 AI Study Partner - Screen Capture Diagnostic")
    print("=" * 60)
    
    # Test 1: MSS library directly
    mss_success = test_mss_directly()
    
    # Test 2: Screen capture module
    capture_success = test_direct_capture()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   MSS Library: {'✅ PASS' if mss_success else '❌ FAIL'}")
    print(f"   Screen Capture: {'✅ PASS' if capture_success else '❌ FAIL'}")
    
    if not mss_success:
        print("\n🚨 MSS library is not working!")
        print("\n🔧 Troubleshooting steps:")
        print("1. Install MSS: pip install mss")
        print("2. On Windows, you might need to run as administrator")
        print("3. Check if any antivirus software is blocking screen capture")
    elif not capture_success:
        print("\n⚠️  MSS works but screen capture module fails")
        print("   This might be a module import or configuration issue")
    else:
        print("\n🎉 Screen capture is working correctly!")
        print("   The issue might be in the API integration")
