#!/usr/bin/env python3
"""
Test frame API directly
"""

import sys
import os
import asyncio
import requests

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_frame_api():
    """Test the frame API directly"""
    print("🔍 Testing Frame API Directly")
    print("=" * 50)
    
    try:
        from app.services import service_manager
        
        print("1. Initializing service manager...")
        await service_manager.initialize()
        print("✅ Service manager initialized")
        
        print("2. Starting screen capture...")
        service_manager.screen_capture.start_capture()
        print("✅ Screen capture started")
        
        print("3. Waiting for frames...")
        for i in range(5):
            await asyncio.sleep(1)
            if service_manager.screen_capture.last_frame is not None:
                print(f"✅ Frame available after {i+1} seconds")
                break
            else:
                print(f"   ⏳ No frame yet... (attempt {i+1})")
        
        if service_manager.screen_capture.last_frame is None:
            print("❌ No frames captured")
            return False
        
        print("4. Testing get_frame_as_base64...")
        try:
            frame_base64 = service_manager.screen_capture.get_frame_as_base64()
            print(f"✅ Base64 encoding successful")
            print(f"   Base64 length: {len(frame_base64)}")
            return True
        except Exception as e:
            print(f"❌ Base64 encoding failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test the API endpoint"""
    print("\n🌐 Testing API Endpoint")
    print("=" * 50)
    
    try:
        # Start capture
        print("1. Starting capture via API...")
        response = requests.post("http://localhost:8000/api/capture/start", 
                               json={"fps": 1, "audio_enabled": False})
        if response.status_code != 200:
            print(f"❌ Failed to start capture: {response.status_code}")
            return False
        print("✅ Capture started")
        
        # Wait and get frame
        print("2. Waiting for frames...")
        for i in range(5):
            import time
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8000/api/capture/frame")
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Frame retrieved successfully")
                    print(f"   Frame size: {len(result['frame'])}")
                    return True
                elif response.status_code == 404:
                    print(f"   ⏳ No frame yet... (attempt {i+1})")
                else:
                    print(f"   ❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
        
        print("❌ No frames retrieved")
        return False
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎓 AI Study Partner - Frame API Test")
    print("=" * 60)
    
    # Test 1: Direct service test
    direct_success = asyncio.run(test_frame_api())
    
    # Test 2: API endpoint test
    api_success = test_api_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Direct Service: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"   API Endpoint: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if not direct_success and not api_success:
        print("\n🚨 Both tests failed - there's a fundamental issue")
    elif not direct_success:
        print("\n⚠️  API works but direct service fails")
    elif not api_success:
        print("\n⚠️  Direct service works but API fails")
    else:
        print("\n🎉 Everything is working!")
