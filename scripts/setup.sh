#!/bin/bash

# AI Study Partner Setup Script
# This script sets up the development environment for AI Study Partner

set -e

echo "🚀 Setting up AI Study Partner..."

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

node_version=$(node --version | cut -d'v' -f2 | cut -d. -f1)
if [ "$node_version" -lt 18 ]; then
    echo "❌ Node.js 18+ is required. Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js version check passed: $(node --version)"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/vector_db
mkdir -p logs
mkdir -p exports

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
fi

# Check for required system dependencies
echo "🔍 Checking system dependencies..."

# Check for Tesseract OCR
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found. Please install it:"
    echo "   - Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   - macOS: brew install tesseract"
    echo "   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found. Please install it:"
    echo "   - Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Windows: Download from https://ffmpeg.org/download.html"
fi

echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Start the backend: cd backend && python main.py"
echo "4. Start the frontend: cd frontend && npm start"
echo "5. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For more information, see README.md"

