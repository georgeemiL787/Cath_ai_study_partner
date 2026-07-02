# 🔧 OCR Installation Guide for AI Study Partner

## Problem
Text extraction from screen frames is not working because Tesseract OCR is not installed on your system.

## Solution

### Step 1: Install Tesseract OCR

#### Option A: Using Chocolatey (Recommended)
```powershell
# Install Chocolatey if you don't have it
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Tesseract
choco install tesseract
```

#### Option B: Manual Installation
1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (or latest version)

2. **Install Tesseract:**
   - Run the installer as Administrator
   - Install to: `C:\Program Files\Tesseract-OCR\`
   - ✅ Check "Additional language data" during installation
   - ✅ Check "Add to PATH" if available

3. **Verify Installation:**
   ```cmd
   tesseract --version
   ```

### Step 2: Test Installation

Run the test script:
```bash
python test_ocr_installation.py
```

### Step 3: Configure Environment (if needed)

If Tesseract is not in PATH, update your `.env` file:
```env
TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe
```

### Step 4: Restart the Application

After installation, restart your AI Study Partner:
```bash
# Stop the current server (Ctrl+C)
# Then restart
cd backend
python main.py
```

## Expected Results

After installation, you should see:
- ✅ OCR processor initialized
- ✅ Text extraction from frames working
- ✅ Session data with extracted content
- ✅ AI analysis working with captured text

## Troubleshooting

### If Tesseract is not found:
1. Check if it's installed: `tesseract --version`
2. Add to PATH or set TESSERACT_PATH in .env
3. Restart the application

### If OCR quality is poor:
1. Ensure good image quality
2. Check if text is clear and readable
3. Try different OCR engines (tesseract vs paddleocr)

### If still not working:
1. Run the test script: `python test_ocr_installation.py`
2. Check the console output for error messages
3. Verify all dependencies are installed

## Alternative: Use PaddleOCR

If Tesseract doesn't work, you can switch to PaddleOCR:

1. Install PaddleOCR:
   ```bash
   pip install paddlepaddle paddleocr
   ```

2. Update .env:
   ```env
   OCR_ENGINE=paddleocr
   ```

3. Restart the application

## Verification

After installation, check that:
- [ ] `tesseract --version` works
- [ ] `python test_ocr_installation.py` passes all tests
- [ ] AI Study Partner shows "OCR processor initialized"
- [ ] Text extraction works in real-time study sessions
