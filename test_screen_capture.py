#!/usr/bin/env python3
"""
Test script to verify screen capture functionality
"""

import sys
import os
import time
import base64
import requests
import json

def test_screen_capture():
    """Test the screen capture API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Screen Capture Functionality")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("1. Checking server status...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            print("✅ Server is running")
            status = response.json()
            print(f"   Screen capture available: {status.get('screen_capture', False)}")
            print(f"   Audio capture available: {status.get('audio_capture', False)}")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the backend is running: python backend/main.py")
        return False
    
    # Test 2: Start capture
    print("\n2. Starting screen capture...")
    try:
        response = requests.post(f"{base_url}/api/capture/start", json={
            "fps": 1,
            "audio_enabled": False,
            "screen_region": None
        })
        
        if response.status_code == 200:
            print("✅ Screen capture started")
            data = response.json()
            session_id = data.get("session_id")
            print(f"   Session ID: {session_id}")
        else:
            print(f"❌ Failed to start capture: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting capture: {e}")
        return False
    
    # Test 3: Wait a moment for capture to initialize
    print("\n3. Waiting for capture to initialize...")
    time.sleep(2)
    
    # Test 4: Check capture status
    print("\n4. Checking capture status...")
    try:
        response = requests.get(f"{base_url}/api/capture/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Capture status retrieved")
            print(f"   Is capturing: {data.get('is_capturing', False)}")
            print(f"   Session ID: {data.get('session_id', 'None')}")
            
            screen_stats = data.get('screen_stats', {})
            print(f"   Screen status: {screen_stats.get('status', 'unknown')}")
            print(f"   Frame count: {screen_stats.get('frame_count', 0)}")
            print(f"   Target FPS: {screen_stats.get('target_fps', 0)}")
            print(f"   Actual FPS: {screen_stats.get('actual_fps', 0)}")
        else:
            print(f"❌ Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting status: {e}")
    
    # Test 5: Try to get a frame
    print("\n5. Attempting to capture a frame...")
    try:
        response = requests.get(f"{base_url}/api/capture/frame")
        if response.status_code == 200:
            data = response.json()
            frame_data = data.get("frame", "")
            if frame_data:
                print("✅ Frame captured successfully!")
                print(f"   Frame size: {len(frame_data)} characters (base64)")
                print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
                
                # Save frame for inspection
                try:
                    frame_bytes = base64.b64decode(frame_data)
                    with open("test_frame.jpg", "wb") as f:
                        f.write(frame_bytes)
                    print("   Frame saved as: test_frame.jpg")
                except Exception as e:
                    print(f"   Warning: Could not save frame: {e}")
            else:
                print("❌ No frame data received")
        else:
            print(f"❌ Failed to get frame: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error getting frame: {e}")
    
    # Test 6: Stop capture
    print("\n6. Stopping capture...")
    try:
        response = requests.post(f"{base_url}/api/capture/stop", json={})
        if response.status_code == 200:
            print("✅ Capture stopped successfully")
        else:
            print(f"❌ Failed to stop capture: {response.status_code}")
    except Exception as e:
        print(f"❌ Error stopping capture: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Screen capture test completed")
    return True

def test_direct_screen_capture():
    """Test screen capture directly without API"""
    print("\n🔧 Testing Direct Screen Capture")
    print("=" * 50)
    
    try:
        # Import the screen capture module directly
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
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
            import cv2
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            print(f"   Base64 size: {len(frame_base64)} characters")
            
            # Save frame
            cv2.imwrite("direct_test_frame.jpg", frame)
            print("   Frame saved as: direct_test_frame.jpg")
        else:
            print("❌ Failed to capture single frame")
            return False
        
        print("3. Testing continuous capture...")
        capture.start_capture()
        time.sleep(3)  # Capture for 3 seconds
        
        stats = capture.get_capture_stats()
        print(f"✅ Continuous capture test completed")
        print(f"   Frames captured: {stats.get('frame_count', 0)}")
        print(f"   Status: {stats.get('status', 'unknown')}")
        
        capture.stop_capture()
        print("✅ Capture stopped")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import screen capture module: {e}")
        print("   Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error in direct screen capture test: {e}")
        return False

def main():
    """Main test function"""
    print("🎓 AI Study Partner - Screen Capture Diagnostic")
    print("=" * 60)
    
    # Test 1: API-based screen capture
    api_success = test_screen_capture()
    
    # Test 2: Direct screen capture
    direct_success = test_direct_screen_capture()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   API-based capture: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   Direct capture: {'✅ PASS' if direct_success else '❌ FAIL'}")
    
    if not api_success and not direct_success:
        print("\n🚨 Screen capture is not working!")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure the backend server is running: python backend/main.py")
        print("2. Check if you have the required dependencies:")
        print("   - pip install mss opencv-python pillow")
        print("3. On Windows, you might need to run as administrator")
        print("4. Check if any antivirus software is blocking screen capture")
        print("5. Try running the backend in a different terminal")
    elif api_success and not direct_success:
        print("\n⚠️  API works but direct capture fails - this might be a module import issue")
    elif not api_success and direct_success:
        print("\n⚠️  Direct capture works but API fails - check the backend server")
    else:
        print("\n🎉 Screen capture is working correctly!")
        print("   The 'No frame available' issue might be in the frontend integration")

if __name__ == "__main__":
    main()
