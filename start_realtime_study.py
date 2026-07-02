#!/usr/bin/env python3
"""
Startup script for AI Study Partner Real-Time Study Session
This script starts both the backend and frontend for the real-time study feature
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    try:
        import fastapi
        import uvicorn
        print("✅ Backend dependencies found")
    except ImportError as e:
        print(f"❌ Missing backend dependencies: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    # Check Node.js and npm
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm found: {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False
    
    return True

def install_frontend_dependencies():
    """Install frontend dependencies if needed"""
    frontend_path = Path("frontend")
    node_modules = frontend_path / "node_modules"
    
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_path, check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return False
    else:
        print("✅ Frontend dependencies already installed")
    
    return True

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    
    backend_path = Path("backend")
    main_py = backend_path / "main.py"
    
    if not main_py.exists():
        print(f"❌ Backend main.py not found at {main_py}")
        return None
    
    try:
        # Start backend in a subprocess
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], cwd=backend_path)
        
        print("✅ Backend server starting...")
        print("   URL: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("🎨 Starting frontend server...")
    
    frontend_path = Path("frontend")
    
    try:
        # Start frontend in a subprocess
        process = subprocess.Popen([
            'npm', 'start'
        ], cwd=frontend_path)
        
        print("✅ Frontend server starting...")
        print("   URL: http://localhost:3000")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def wait_for_servers():
    """Wait for servers to be ready"""
    print("⏳ Waiting for servers to start...")
    
    import requests
    
    # Wait for backend
    backend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/api/status", timeout=1)
            if response.status_code == 200:
                backend_ready = True
                break
        except:
            pass
        time.sleep(1)
    
    if backend_ready:
        print("✅ Backend server is ready")
    else:
        print("⚠️  Backend server may not be ready yet")
    
    # Wait for frontend
    frontend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:3000", timeout=1)
            if response.status_code == 200:
                frontend_ready = True
                break
        except:
            pass
        time.sleep(1)
    
    if frontend_ready:
        print("✅ Frontend server is ready")
    else:
        print("⚠️  Frontend server may not be ready yet")
    
    return backend_ready and frontend_ready

def open_browser():
    """Open browser to the real-time study page"""
    print("🌐 Opening browser...")
    
    try:
        webbrowser.open("http://localhost:3000/realtime-study")
        print("✅ Browser opened to Real-Time Study page")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please manually open: http://localhost:3000/realtime-study")

def main():
    """Main startup function"""
    print("🎓 AI Study Partner - Real-Time Study Session")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Please run this script from the AI Study Partner root directory")
        print("   The directory should contain 'backend' and 'frontend' folders")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        return 1
    
    # Install frontend dependencies if needed
    if not install_frontend_dependencies():
        print("\n❌ Failed to install frontend dependencies.")
        return 1
    
    print("\n🚀 Starting AI Study Partner...")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend server")
        return 1
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend server")
        backend_process.terminate()
        return 1
    
    # Wait for servers to be ready
    if wait_for_servers():
        print("\n🎉 AI Study Partner is ready!")
        print("\n📱 Access your Real-Time Study Session:")
        print("   Frontend: http://localhost:3000/realtime-study")
        print("   Backend API: http://localhost:8000/docs")
        
        # Open browser
        open_browser()
        
        print("\n🛑 To stop the servers, press Ctrl+C")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down servers...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Servers stopped")
            return 0
    else:
        print("\n⚠️  Servers may not be fully ready yet")
        print("   Please check the URLs manually:")
        print("   Frontend: http://localhost:3000")
        print("   Backend: http://localhost:8000")
        
        print("\n🛑 To stop the servers, press Ctrl+C")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down servers...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Servers stopped")
            return 0

if __name__ == "__main__":
    sys.exit(main())
