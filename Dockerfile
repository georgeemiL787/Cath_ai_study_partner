# AI Study Partner Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    ffmpeg \
    libsndfile1 \
    libasound2-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create necessary directories
RUN mkdir -p data/vector_db logs exports

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000 3000

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app/backend\n\
python main.py &\n\
cd /app/frontend\n\
npm start\n\
' > /app/start.sh && chmod +x /app/start.sh

# Default command
CMD ["/app/start.sh"]

