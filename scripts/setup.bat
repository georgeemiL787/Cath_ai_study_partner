@echo off
REM AI Study Partner Setup Script for Windows
REM This script sets up the development environment for AI Study Partner

echo 🚀 Setting up AI Study Partner...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

echo ✅ Python check passed

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

echo ✅ Node.js check passed

REM Create virtual environment
echo 📦 Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📦 Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
npm install
cd ..

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "data\vector_db" mkdir data\vector_db
if not exist "logs" mkdir logs
if not exist "exports" mkdir exports

REM Copy environment file
if not exist ".env" (
    echo 📝 Creating environment file...
    copy env.example .env
    echo ⚠️  Please edit .env file with your API keys and configuration
)

echo ✅ Setup completed successfully!
echo.
echo 🎯 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Activate virtual environment: venv\Scripts\activate.bat
echo 3. Start the backend: cd backend ^&^& python main.py
echo 4. Start the frontend: cd frontend ^&^& npm start
echo 5. Open http://localhost:3000 in your browser
echo.
echo 📚 For more information, see README.md
pause

