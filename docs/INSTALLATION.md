# Installation Guide

This guide will help you install and set up AI Study Partner on your system.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **Python**: 3.9 or higher
- **Node.js**: 18.0 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Required for AI features and model downloads

### Recommended Requirements
- **RAM**: 16GB or more
- **Storage**: 10GB free space (for models and data)
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster processing)

## Prerequisites

### 1. Python 3.9+
Download and install Python from [python.org](https://www.python.org/downloads/).

**Verify installation:**
```bash
python --version
# or
python3 --version
```

### 2. Node.js 18+
Download and install Node.js from [nodejs.org](https://nodejs.org/).

**Verify installation:**
```bash
node --version
npm --version
```

### 3. System Dependencies

#### Windows
- **Tesseract OCR**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- **FFmpeg**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

#### macOS
```bash
# Install using Homebrew
brew install tesseract
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng ffmpeg
```

## Installation Methods

### Method 1: Automated Setup (Recommended)

#### Windows
1. Download the project
2. Open Command Prompt or PowerShell in the project directory
3. Run the setup script:
```cmd
scripts\setup.bat
```

#### macOS/Linux
1. Download the project
2. Open Terminal in the project directory
3. Make the setup script executable and run it:
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Method 2: Manual Installation

#### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd ai-study-partner
```

#### 2. Create Python Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### 5. Create Environment File
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your configuration
# Add your OpenAI API key and other settings
```

#### 6. Create Data Directories
```bash
mkdir -p data/vector_db
mkdir -p logs
mkdir -p exports
```

### Method 3: Docker Installation

#### 1. Install Docker
Download and install Docker from [docker.com](https://www.docker.com/get-started).

#### 2. Build and Run with Docker Compose
```bash
# Copy environment file
cp env.example .env

# Edit .env with your configuration
# Add your OpenAI API key

# Build and start services
docker-compose up --build
```

## Configuration

### 1. Environment Variables
Edit the `.env` file with your settings:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Vector Database Configuration
VECTOR_DB_TYPE=faiss
VECTOR_DB_PATH=./data/vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Capture Configuration
SCREEN_CAPTURE_FPS=1
AUDIO_CAPTURE_RATE=16000
AUDIO_CHUNK_SIZE=1024

# OCR Configuration
OCR_ENGINE=tesseract
TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe

# Privacy and Security
PRIVACY_MODE=local
ENCRYPTION_KEY=your_encryption_key_here
DATA_RETENTION_DAYS=30
```

### 2. API Keys

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add it to your `.env` file

#### Optional: Other API Keys
- **Google Cloud Speech-to-Text**: For alternative STT
- **Azure Cognitive Services**: For alternative OCR/STT
- **Anthropic Claude**: For alternative LLM

## Verification

### 1. Test Backend
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Start backend
cd backend
python main.py
```

You should see:
```
✅ AI Study Partner initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test Frontend
```bash
# In a new terminal
cd frontend
npm start
```

You should see:
```
webpack compiled with 0 errors
Local:            http://localhost:3000
```

### 3. Test API
Open your browser and go to:
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Troubleshooting

### Common Issues

#### 1. Python Version Issues
**Error**: `Python 3.9+ required`
**Solution**: Install Python 3.9 or higher

#### 2. Node.js Version Issues
**Error**: `Node.js 18+ required`
**Solution**: Install Node.js 18 or higher

#### 3. Tesseract Not Found
**Error**: `Tesseract not found`
**Solution**: 
- Windows: Add Tesseract to PATH or set TESSERACT_PATH in .env
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

#### 4. FFmpeg Not Found
**Error**: `FFmpeg not found`
**Solution**:
- Windows: Add FFmpeg to PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

#### 5. Port Already in Use
**Error**: `Port 8000/3000 already in use`
**Solution**: 
- Kill existing processes: `lsof -ti:8000 | xargs kill -9`
- Or change ports in configuration

#### 6. Permission Issues
**Error**: `Permission denied`
**Solution**:
- Windows: Run as Administrator
- macOS/Linux: Use `sudo` if needed

#### 7. OpenAI API Issues
**Error**: `OpenAI API key invalid`
**Solution**:
- Check your API key in .env file
- Verify you have credits in your OpenAI account
- Check API key permissions

### Getting Help

1. **Check Logs**: Look in the `logs/` directory for error messages
2. **API Documentation**: Visit http://localhost:8000/docs when running
3. **GitHub Issues**: Report bugs and ask questions on GitHub
4. **Community**: Join our Discord server for support

## Next Steps

After successful installation:

1. **Read the User Guide**: See `docs/USER_GUIDE.md`
2. **Configure Settings**: Adjust settings in the web interface
3. **Start Your First Session**: Begin capturing and studying!
4. **Explore Features**: Try different AI tools and export options

## Uninstallation

### Remove Application
```bash
# Remove virtual environment
rm -rf venv

# Remove node modules
rm -rf frontend/node_modules

# Remove data (optional)
rm -rf data logs exports
```

### Docker Cleanup
```bash
docker-compose down
docker system prune -a
```

