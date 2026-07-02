# 🚀 Real-Time Study Session Guide

## Overview

The **Real-Time Study Session** is the flagship feature of the AI Study Partner that provides live screen recording with intelligent AI assistance. This feature transforms your study sessions into interactive, AI-powered learning experiences.

## ✨ Key Features

### 🎥 Live Screen Capture
- **Real-time screen recording** with configurable FPS (0.5-5 FPS)
- **Custom region selection** for focused capture
- **Live preview** of captured content
- **Automatic content extraction** using OCR

### 🎤 Audio Processing
- **Voice activity detection** for speech segmentation
- **Speech-to-text conversion** using Whisper
- **Real-time audio analysis** and transcription

### 🧠 AI-Powered Assistance
- **Contextual Q&A** based on captured content
- **Automatic key point extraction**
- **Smart summarization** of study materials
- **Flashcard generation** from content
- **Quiz creation** with multiple question types
- **Study plan generation** based on topics

### 📊 Session Management
- **Real-time statistics** and progress tracking
- **Session export** in multiple formats (JSON, CSV)
- **Content timeline** with timestamps
- **Automatic content processing** and indexing

## 🚀 Getting Started

### 1. Start the Application

```bash
# Start the backend server
cd backend
python main.py

# In another terminal, start the frontend
cd frontend
npm start
```

### 2. Access Real-Time Study

1. Open your browser to `http://localhost:3000`
2. Navigate to **"Real-Time Study"** in the sidebar
3. Click **"Start Session"** to begin

### 3. Configure Your Session

- **FPS**: Adjust capture rate (1-2 FPS recommended)
- **Audio**: Enable/disable audio capture
- **Screen Region**: Choose full screen or custom region
- **AI Assistance**: Set level (Low/Medium/High)

## 🎯 How It Works

### Content Capture Pipeline

```
Screen/Audio → OCR/STT → Content Processing → AI Analysis → Study Tools
```

1. **Capture**: Screen and audio are continuously recorded
2. **Extract**: OCR extracts text from images, STT transcribes speech
3. **Process**: Content is chunked and indexed for search
4. **Analyze**: AI identifies key concepts and patterns
5. **Assist**: Generate summaries, flashcards, quizzes, and answer questions

### Real-Time Processing

- **Automatic Processing**: Content is processed every 30 seconds (configurable)
- **Smart Buffering**: Recent content is kept in memory for quick access
- **Background Analysis**: AI works in the background to extract insights
- **Live Updates**: UI updates in real-time with new content and insights

## 🛠️ API Endpoints

### Session Management

```http
POST /api/realtime-study/start
POST /api/realtime-study/stop
GET  /api/realtime-study/{session_id}/status
```

### Content Operations

```http
POST /api/realtime-study/{session_id}/content
POST /api/realtime-study/{session_id}/process-frame
GET  /api/realtime-study/{session_id}/summary
GET  /api/realtime-study/{session_id}/key-points
```

### AI Assistance

```http
POST /api/realtime-study/{session_id}/question
GET  /api/realtime-study/{session_id}/export
```

## 📱 User Interface

### Main Dashboard
- **Session Controls**: Start/stop recording
- **Live Preview**: Real-time screen capture preview
- **Statistics**: Capture stats and session metrics
- **Settings**: Quick configuration options

### AI Assistant Panel
- **Chat Interface**: Ask questions about your content
- **Study Tools**: Generate summaries, flashcards, quizzes
- **Key Points**: Automatically extracted important concepts
- **Export Options**: Download session data

### Sidebar Information
- **Session Info**: Duration, content count, questions asked
- **Capture Stats**: FPS, frame count, audio status
- **Key Points**: Live list of extracted concepts
- **Quick Settings**: Toggle auto-processing, preview, AI level

## 🔧 Configuration Options

### Capture Settings
```json
{
  "fps": 2,
  "audio_enabled": true,
  "screen_region": {
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1080
  }
}
```

### AI Processing
```json
{
  "auto_ai_processing": true,
  "processing_interval": 30,
  "ai_assistance_level": "medium"
}
```

## 📊 Session Data Structure

```json
{
  "session": {
    "id": "uuid",
    "start_time": 1234567890,
    "end_time": 1234567890,
    "is_active": true
  },
  "content_items": [
    {
      "id": "screen_1234567890",
      "content": "Extracted text content",
      "type": "ocr",
      "timestamp": 1234567890,
      "confidence": 0.95,
      "metadata": {}
    }
  ],
  "key_points": [
    "Machine learning fundamentals",
    "Supervised vs unsupervised learning"
  ],
  "questions": [
    {
      "question": "What is machine learning?",
      "answer": "Machine learning is...",
      "timestamp": 1234567890
    }
  ]
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_realtime_study.py
```

This will test:
- ✅ Session start/stop
- ✅ Content addition
- ✅ AI question answering
- ✅ Summary generation
- ✅ Key point extraction
- ✅ Session export
- ✅ Status monitoring

## 🎓 Use Cases

### 1. Online Course Study
- Record lecture videos or slides
- Ask questions about specific concepts
- Generate flashcards for key terms
- Create study summaries

### 2. Research and Reading
- Capture research papers and articles
- Extract key findings automatically
- Generate research summaries
- Create knowledge maps

### 3. Presentation Preparation
- Record practice presentations
- Get feedback on content clarity
- Generate speaking notes
- Create audience Q&A preparation

### 4. Exam Preparation
- Record study materials
- Generate practice quizzes
- Create comprehensive summaries
- Track study progress

## 🔒 Privacy and Security

- **Local Processing**: All content processing happens on your device
- **Session Isolation**: Each session is completely separate
- **Data Encryption**: Optional encryption for sensitive content
- **No Cloud Storage**: Content stays on your machine unless explicitly exported

## 🚨 Troubleshooting

### Common Issues

1. **Screen Capture Not Working**
   - Check screen permissions
   - Ensure no other screen recording software is running
   - Try reducing FPS or changing screen region

2. **Audio Not Capturing**
   - Check microphone permissions
   - Verify audio device is working
   - Try different audio settings

3. **AI Not Responding**
   - Check API key configuration
   - Verify internet connection
   - Check service status in settings

4. **Performance Issues**
   - Reduce capture FPS
   - Disable auto-processing
   - Close other applications

### Performance Optimization

- **Lower FPS**: Use 1 FPS for better performance
- **Smaller Region**: Capture only the relevant screen area
- **Disable Audio**: If not needed, disable audio capture
- **Batch Processing**: Process content in larger batches

## 🔮 Future Enhancements

- **Multi-monitor Support**: Capture from multiple screens
- **Collaborative Sessions**: Share sessions with study groups
- **Advanced Analytics**: Learning progress tracking
- **Mobile Integration**: Companion mobile app
- **Voice Commands**: Hands-free operation
- **AR/VR Support**: Immersive study environments

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation
3. Run the test suite to verify functionality
4. Check server logs for error details

---

**Ready to revolutionize your study sessions with AI! 🎓✨**
