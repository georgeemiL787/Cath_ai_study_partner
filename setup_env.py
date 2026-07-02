#!/usr/bin/env python3
"""
Environment Setup Script for AI Study Partner
This script helps you create the .env file with proper configuration
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ env.example file not found!")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists. Backing up to .env.backup")
        shutil.copy(env_file, ".env.backup")
    
    # Copy template to .env
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from template")
    
    return True

def check_tesseract_path():
    """Check for Tesseract installation"""
    possible_paths = [
        "C:/Program Files/Tesseract-OCR/tesseract.exe",
        "C:/Program Files (x86)/Tesseract-OCR/tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
        "tesseract"  # If in PATH
    ]
    
    for path in possible_paths:
        if os.path.exists(path) or (path == "tesseract" and shutil.which("tesseract")):
            return path
    
    return None

def update_env_file():
    """Update .env file with detected paths"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check Tesseract
    tesseract_path = check_tesseract_path()
    if tesseract_path:
        print(f"✅ Found Tesseract at: {tesseract_path}")
        content = content.replace(
            "TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe",
            f"TESSERACT_PATH={tesseract_path}"
        )
    else:
        print("⚠️  Tesseract not found. Please install it manually.")
        print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Updated .env file with detected paths")
    return True

def main():
    """Main setup function"""
    print("🚀 AI Study Partner Environment Setup")
    print("=" * 50)
    
    # Create .env file
    if not create_env_file():
        return
    
    # Update with detected paths
    update_env_file()
    
    print("\n📝 Next Steps:")
    print("1. Edit .env file and add your OpenAI API key:")
    print("   OPENAI_API_KEY=your_actual_api_key_here")
    print("\n2. Install Python dependencies:")
    print("   pip install -r requirements.txt")
    print("\n3. Install Node.js dependencies:")
    print("   cd frontend && npm install")
    print("\n4. Start the backend:")
    print("   python main.py")
    print("\n5. Start the frontend (in another terminal):")
    print("   cd frontend && npm start")
    
    print("\n✅ Environment setup complete!")

if __name__ == "__main__":
    main()
