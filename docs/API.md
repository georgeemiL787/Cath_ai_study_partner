# AI Study Partner API Documentation

## Overview

The AI Study Partner API provides endpoints for screen capture, audio processing, AI-powered study assistance, and data management.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, you should implement proper authentication.

## Endpoints

### Capture Endpoints

#### Start Capture
```http
POST /api/capture/start
```

**Request Body:**
```json
{
  "fps": 1,
  "audio_enabled": true,
  "session_id": "optional-session-id",
  "screen_region": {
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1080
  }
}
```

**Response:**
```json
{
  "message": "Capture started successfully",
  "session_id": "uuid-string",
  "screen_capture": true,
  "audio_capture": true
}
```

#### Stop Capture
```http
POST /api/capture/stop
```

**Request Body:**
```json
{
  "session_id": "session-id"
}
```

#### Get Capture Status
```http
GET /api/capture/status
```

**Response:**
```json
{
  "is_capturing": true,
  "session_id": "uuid-string",
  "screen_stats": {
    "status": "capturing",
    "frame_count": 150,
    "elapsed_time": 150.5,
    "target_fps": 1,
    "actual_fps": 0.99
  },
  "audio_stats": {
    "status": "capturing",
    "elapsed_time": 150.5,
    "total_samples": 2408000,
    "speech_samples": 1204000,
    "speech_ratio": 0.5,
    "speech_segments": 5,
    "in_speech": false
  }
}
```

### Processing Endpoints

#### Extract Text (OCR)
```http
POST /api/processing/ocr/extract
```

**Request Body:**
```json
{
  "image_base64": "base64-encoded-image",
  "engine": "tesseract",
  "language": "eng",
  "preprocess": true
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "text": "Extracted text content",
    "confidence": 85.5,
    "bounding_boxes": [[x, y, w, h], ...],
    "word_count": 25,
    "engine": "tesseract"
  },
  "processing_time": 1.2
}
```

#### Transcribe Audio
```http
POST /api/processing/stt/transcribe
```

**Request Body:**
```json
{
  "audio_data": [0.1, -0.2, 0.3, ...],
  "engine": "whisper",
  "model": "base",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "text": "Transcribed speech content",
    "confidence": 0.95,
    "language": "en",
    "segments": [
      {
        "start": 0.0,
        "end": 5.2,
        "text": "Hello world",
        "confidence": 0.95
      }
    ],
    "word_timestamps": [...],
    "engine": "whisper"
  },
  "processing_time": 2.1
}
```

### AI Endpoints

#### Ask Question
```http
POST /api/ai/question
```

**Request Body:**
```json
{
  "question": "What is machine learning?",
  "session_id": "session-id",
  "include_citations": true,
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "content": "Machine learning is a subset of artificial intelligence...",
  "processing_time": 1.5,
  "model": "gpt-4-turbo-preview",
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  },
  "citations": [
    {
      "id": "1",
      "content": "Relevant context from your study materials..."
    }
  ]
}
```

#### Generate Summary
```http
POST /api/ai/summarize
```

**Request Body:**
```json
{
  "content": "Long text content to summarize...",
  "max_length": 200
}
```

#### Generate Flashcards
```http
POST /api/ai/flashcards
```

**Request Body:**
```json
{
  "content": "Study material content...",
  "num_cards": 5
}
```

#### Generate Quiz
```http
POST /api/ai/quiz
```

**Request Body:**
```json
{
  "content": "Study material content...",
  "num_questions": 5,
  "question_types": ["multiple_choice", "short_answer"]
}
```

### Database Endpoints

#### Add Document
```http
POST /api/database/documents
```

**Request Body:**
```json
{
  "content": "Document content",
  "metadata": {
    "title": "Chapter 1",
    "page": 1
  },
  "source_type": "screen",
  "session_id": "session-id"
}
```

#### Search Documents
```http
POST /api/database/search
```

**Request Body:**
```json
{
  "query": "machine learning algorithms",
  "top_k": 5,
  "session_id": "session-id",
  "source_type": "screen"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "document_id": "doc-123",
        "content": "Relevant content...",
        "score": 0.95,
        "rank": 1,
        "metadata": {...},
        "timestamp": 1640995200.0,
        "source_type": "screen",
        "session_id": "session-id"
      }
    ],
    "query": "machine learning algorithms",
    "total_results": 1
  }
}
```

#### Get Session Documents
```http
GET /api/database/sessions/{session_id}/documents
```

#### Export Session
```http
POST /api/database/export/session/{session_id}?format=json
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "success": false,
  "data": {},
  "error": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. In production, you should implement appropriate rate limiting.

## WebSocket Support

Real-time updates for capture status and processing results are available via WebSocket connections (to be implemented).

## Examples

### Complete Study Session Workflow

1. **Start Capture:**
```bash
curl -X POST http://localhost:8000/api/capture/start \
  -H "Content-Type: application/json" \
  -d '{"fps": 1, "audio_enabled": true}'
```

2. **Check Status:**
```bash
curl http://localhost:8000/api/capture/status
```

3. **Ask Question:**
```bash
curl -X POST http://localhost:8000/api/ai/question \
  -H "Content-Type: application/json" \
  -d '{"question": "What did I learn today?", "session_id": "your-session-id"}'
```

4. **Stop Capture:**
```bash
curl -X POST http://localhost:8000/api/capture/stop \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id"}'
```

## SDK Examples

### Python
```python
import requests

# Start capture
response = requests.post('http://localhost:8000/api/capture/start', json={
    'fps': 1,
    'audio_enabled': True
})
session_id = response.json()['session_id']

# Ask question
response = requests.post('http://localhost:8000/api/ai/question', json={
    'question': 'What is the main topic?',
    'session_id': session_id
})
answer = response.json()['content']
```

### JavaScript
```javascript
// Start capture
const response = await fetch('http://localhost:8000/api/capture/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ fps: 1, audio_enabled: true })
});
const { session_id } = await response.json();

// Ask question
const answerResponse = await fetch('http://localhost:8000/api/ai/question', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'What is the main topic?', session_id })
});
const { content } = await answerResponse.json();
```

