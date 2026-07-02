#!/usr/bin/env python3
"""
Debug screen capture in the backend
"""

import sys
import os
import time
import requests
import json

def test_capture_flow():
    """Test the complete capture flow"""
    print("🔍 Debugging Screen Capture Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    try:
        # 1. Check server status
        print("1. Checking server status...")
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Services: {response.json()}")
        else:
            print(f"❌ Server not responding: {response.status_code}")
            return False
        
        # 2. Start capture
        print("\n2. Starting capture...")
        capture_data = {
            "fps": 1,
            "audio_enabled": False
        }
        response = requests.post(f"{base_url}/capture/start", json=capture_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Capture started")
            print(f"   Session ID: {result['session_id']}")
            session_id = result['session_id']
        else:
            print(f"❌ Failed to start capture: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # 3. Wait and check for frames
        print("\n3. Waiting for frames...")
        for i in range(5):
            print(f"   Attempt {i+1}/5...")
            time.sleep(2)
            
            try:
                response = requests.get(f"{base_url}/capture/frame")
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Frame captured!")
                    print(f"   Frame size: {len(result['frame'])} characters")
                    print(f"   Timestamp: {result['timestamp']}")
                    return True
                elif response.status_code == 404:
                    print("   ⏳ No frame available yet...")
                else:
                    print(f"   ❌ Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
        
        print("❌ No frames captured after 10 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_direct_backend():
    """Test the backend screen capture directly"""
    print("\n🔧 Testing Backend Screen Capture Directly")
    print("=" * 50)
    
    try:
        # Add backend to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from app.capture.screen_capture import ScreenCapture, CaptureConfig
        from app.services import ServiceManager
        
        print("1. Creating service manager...")
        service_manager = ServiceManager()
        print("✅ Service manager created")
        
        print("2. Getting screen capture service...")
        screen_capture = service_manager.screen_capture
        if screen_capture:
            print("✅ Screen capture service available")
        else:
            print("❌ Screen capture service not available")
            return False
        
        print("3. Testing single frame capture...")
        frame = screen_capture.capture_single_frame()
        if frame is not None:
            print("✅ Single frame captured")
            print(f"   Frame shape: {frame.shape}")
        else:
            print("❌ Failed to capture single frame")
            return False
        
        print("4. Starting continuous capture...")
        screen_capture.start_capture()
        print("✅ Continuous capture started")
        
        print("5. Waiting for frames in continuous mode...")
        for i in range(5):
            time.sleep(1)
            if screen_capture.last_frame is not None:
                print(f"✅ Frame available after {i+1} seconds")
                print(f"   Frame shape: {screen_capture.last_frame.shape}")
                print(f"   Frame count: {screen_capture.frame_count}")
                return True
            else:
                print(f"   ⏳ No frame yet... (attempt {i+1})")
        
        print("❌ No frames in continuous mode")
        return False
        
    except Exception as e:
        print(f"❌ Direct backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎓 AI Study Partner - Capture Debug")
    print("=" * 60)
    
    # Test 1: API flow
    api_success = test_capture_flow()
    
    # Test 2: Direct backend
    backend_success = test_direct_backend()
    
    print("\n" + "=" * 60)
    print("📊 Debug Results:")
    print(f"   API Flow: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   Backend Direct: {'✅ PASS' if backend_success else '❌ FAIL'}")
    
    if not api_success and not backend_success:
        print("\n🚨 Both tests failed - there's a fundamental issue")
    elif not api_success:
        print("\n⚠️  Backend works but API integration fails")
    elif not backend_success:
        print("\n⚠️  API works but direct backend fails")
    else:
        print("\n🎉 Everything is working!")
