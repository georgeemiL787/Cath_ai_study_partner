#!/usr/bin/env python3
"""
Debug API issues
"""

import requests
import json

def test_api_debug():
    """Debug API issues"""
    print("🔍 Debugging API Issues")
    print("=" * 50)
    
    try:
        # 1. Check server status
        print("1. Checking server status...")
        response = requests.get("http://localhost:8000/api/status")
        if response.status_code == 200:
            print("✅ Server is running")
            status = response.json()
            print(f"   Screen capture: {status.get('screen_capture', False)}")
        else:
            print(f"❌ Server not responding: {response.status_code}")
            return False
        
        # 2. Start capture
        print("\n2. Starting capture...")
        response = requests.post("http://localhost:8000/api/capture/start", 
                               json={"fps": 1, "audio_enabled": False})
        if response.status_code == 200:
            result = response.json()
            print("✅ Capture started")
            print(f"   Session ID: {result['session_id']}")
            session_id = result['session_id']
        else:
            print(f"❌ Failed to start capture: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # 3. Check capture status
        print("\n3. Checking capture status...")
        response = requests.get("http://localhost:8000/api/capture/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Capture status retrieved")
            print(f"   Is capturing: {status.get('is_capturing', False)}")
            print(f"   Session ID: {status.get('session_id', 'None')}")
            print(f"   Screen stats: {status.get('screen_stats', {})}")
        else:
            print(f"❌ Failed to get capture status: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # 4. Try to get frame with detailed error
        print("\n4. Trying to get frame...")
        import time
        time.sleep(2)
        
        try:
            response = requests.get("http://localhost:8000/api/capture/frame")
            print(f"   Status code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("✅ Frame retrieved successfully")
                print(f"   Frame size: {len(result.get('frame', ''))}")
                return True
            else:
                print(f"❌ Frame request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Frame request exception: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎓 AI Study Partner - API Debug")
    print("=" * 60)
    
    success = test_api_debug()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    if not success:
        print("\n🚨 API debugging failed!")
    else:
        print("\n🎉 API is working correctly!")
