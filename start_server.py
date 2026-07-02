#!/usr/bin/env python3
"""
Simple server startup script for AI Study Partner
"""

import subprocess
import sys
import time
import requests

def start_server():
    """Start the AI Study Partner server"""
    print("🚀 Starting AI Study Partner Server...")
    
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, "backend/main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:8000/api/status", timeout=1)
                if response.status_code == 200:
                    print("✅ Server started successfully!")
                    print("🌐 Server running at: http://localhost:8000")
                    print("📚 API Documentation: http://localhost:8000/docs")
                    print("\n🎯 Ready to test! Run: python test_ai_study_partner.py")
                    return process
            except:
                time.sleep(1)
                print(f"   Waiting... ({i+1}/30)")
        
        print("❌ Server failed to start within 30 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

if __name__ == "__main__":
    process = start_server()
    if process:
        try:
            print("\n🔄 Server is running. Press Ctrl+C to stop.")
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
            process.wait()
            print("✅ Server stopped.")
