#!/usr/bin/env python3
"""
Test service initialization
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_service_initialization():
    """Test service initialization"""
    print("🔧 Testing Service Initialization")
    print("=" * 50)
    
    try:
        from app.services import ServiceManager
        
        print("1. Creating service manager...")
        service_manager = ServiceManager()
        print("✅ Service manager created")
        
        print("2. Initializing services...")
        await service_manager.initialize()
        print("✅ Services initialized")
        
        print("3. Checking screen capture service...")
        if service_manager.screen_capture:
            print("✅ Screen capture service available")
            print(f"   Is capturing: {service_manager.screen_capture.is_capturing}")
            print(f"   Last frame: {service_manager.screen_capture.last_frame is not None}")
        else:
            print("❌ Screen capture service not available")
            return False
        
        print("4. Testing single frame capture...")
        frame = service_manager.screen_capture.capture_single_frame()
        if frame is not None:
            print("✅ Single frame captured")
            print(f"   Frame shape: {frame.shape}")
        else:
            print("❌ Failed to capture single frame")
            return False
        
        print("5. Starting continuous capture...")
        service_manager.screen_capture.start_capture()
        print("✅ Continuous capture started")
        
        print("6. Waiting for frames...")
        for i in range(5):
            await asyncio.sleep(1)
            if service_manager.screen_capture.last_frame is not None:
                print(f"✅ Frame available after {i+1} seconds")
                print(f"   Frame count: {service_manager.screen_capture.frame_count}")
                return True
            else:
                print(f"   ⏳ No frame yet... (attempt {i+1})")
        
        print("❌ No frames in continuous mode")
        return False
        
    except Exception as e:
        print(f"❌ Service initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎓 AI Study Partner - Service Initialization Test")
    print("=" * 60)
    
    success = asyncio.run(test_service_initialization())
    
    print("\n" + "=" * 60)
    print(f"📊 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    if not success:
        print("\n🚨 Service initialization failed!")
    else:
        print("\n🎉 Service initialization working correctly!")
