import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Square, 
  Camera, 
  Monitor, 
  Brain,
  MessageCircle,
  FileText,
  BookOpen,
  HelpCircle,
  Lightbulb,
  Download,
  Send,
  Loader2,
  Zap,
  Target,
  Eye,
  Settings,
  Minimize2,
  Clock,
  Activity
} from 'lucide-react';
import { useStudy } from '../hooks/useStudy';
import { useCapture } from '../hooks/useCapture';
import { useRealTimeStudy } from '../hooks/useRealTimeStudy';
import toast from 'react-hot-toast';

interface StudySession {
  id: string;
  startTime: Date;
  endTime?: Date;
  content: string[];
  questions: Array<{ question: string; answer: string; timestamp: Date }>;
  keyPoints: string[];
  isActive: boolean;
}

const RealTimeStudy: React.FC = () => {
  const { 
    generateSummary, 
    generateFlashcards, 
    generateQuiz,
    extractKeyConcepts
  } = useStudy();
  
  const { 
    isCapturing, 
    sessionId, 
    captureStats, 
    startCapture, 
    stopCapture, 
    getCurrentFrame,
    setScreenRegion 
  } = useCapture();
  
  const {
    currentSession: realtimeSession,
    startStudySession: startRealtimeSession,
    stopStudySession: stopRealtimeSession,
    askQuestion: askRealtimeQuestion,
    refreshSessionStatus
  } = useRealTimeStudy();

  // Session state
  const [currentSession, setCurrentSession] = useState<StudySession | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [autoProcess, setAutoProcess] = useState(true);
  const [showPreview, setShowPreview] = useState(true);
  const [currentFrame, setCurrentFrame] = useState<string>('');
  
  // AI Analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState('');
  
  // OCR Status state
  const [ocrStatus, setOcrStatus] = useState<'checking' | 'available' | 'unavailable'>('checking');
  
  // AI Assistant state
  const [activeTab, setActiveTab] = useState<'chat' | 'summary' | 'flashcards' | 'quiz' | 'concepts' | 'plan'>('chat');
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ type: 'user' | 'ai', content: string, timestamp: Date }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionContent, setSessionContent] = useState('');
  const [keyPoints, setKeyPoints] = useState<string[]>([]);
  const [isProcessingFrame, setIsProcessingFrame] = useState(false);
  // AI Provider state
  const [aiProvider, setAiProvider] = useState<'gemini' | 'openai' | 'deepseek' | 'auto'>('auto');
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("gemini-1.5-flash");
  const [servicesStatus, setServicesStatus] = useState<{ gemini_available?: boolean; openai_available?: boolean; deepseek_available?: boolean }>({});
  const [deepseekKeyInput, setDeepseekKeyInput] = useState('');
  
  // Configuration
  const [config, setConfig] = useState({
    fps: 2,
    audioEnabled: true,
    screenRegion: 'full' as 'full' | 'custom',
    customRegion: { x: 0, y: 0, width: 1920, height: 1080 },
    autoProcessInterval: 0.5, // seconds
    aiAssistanceLevel: 'medium' as 'low' | 'medium' | 'high',
    maxContentLength: 50000, // Maximum characters to store in memory
    maxContentItems: 100 // Maximum content items to keep
  });

  const processingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Refs to get current values in intervals
  const isCapturingRef = useRef(isCapturing);
  const autoProcessRef = useRef(autoProcess);
  const sessionIdRef = useRef(sessionId);

  // Load saved AI provider/model from localStorage on mount
  useEffect(() => {
    try {
      const savedProvider = localStorage.getItem('ai_provider');
      const savedModel = localStorage.getItem('ai_model');
      if (savedProvider) setAiProvider(savedProvider as any);
      if (savedModel) setSelectedModel(savedModel);
    } catch (e) {
      console.warn('Failed to load saved AI settings from localStorage', e);
    }
  }, []);

  // Persist AI provider/model changes to localStorage
  useEffect(() => {
    try {
      if (aiProvider) localStorage.setItem('ai_provider', aiProvider);
    } catch {}
  }, [aiProvider]);

  useEffect(() => {
    try {
      if (selectedModel) localStorage.setItem('ai_model', selectedModel);
    } catch {}
  }, [selectedModel]);

  // Check OCR status
  const checkOcrStatus = async () => {
    try {
      setOcrStatus('checking');
      
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('http://localhost:8000/api/capture/config', {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        setOcrStatus('available');
      } else {
        setOcrStatus('unavailable');
        console.warn('OCR service unavailable:', response.status);
      }
    } catch (error) {
      console.error('Failed to check OCR status:', error);
      setOcrStatus('unavailable');
      if (error instanceof Error && error.name === 'AbortError') {
        toast.error('OCR service timeout. Please check if the backend is running.');
      } else {
        toast.error('OCR service is not available. Please check if the backend is running.');
      }
    }
  };

  // Start a new study session
  const startStudySession = async () => {
    try {
      console.log('🚀 STARTING STUDY SESSION - Debug Info:');
      console.log('Current state:', {
        isCapturing,
        sessionId,
        realtimeSession: realtimeSession?.session_id,
        autoProcess,
        config
      });
      
      // Start the regular capture system first
      const region = config.screenRegion === 'custom' ? config.customRegion : undefined;
      console.log('Starting capture session with config:', {
        fps: config.fps,
        audio_enabled: config.audioEnabled,
        screen_region: region
      });
      
      const newSessionId = await startCapture({
        fps: config.fps,
        audio_enabled: config.audioEnabled,
        screen_region: region
      });
      
      console.log('✅ Capture session started with ID:', newSessionId);

      // Also start the real-time study session
      try {
        console.log('Starting real-time study session with config:', {
          auto_ai_processing: autoProcess,
          processing_interval: config.autoProcessInterval,
          screen_region: region,
          fps: config.fps,
          audio_enabled: config.audioEnabled
        });
        
        const realtimeSessionId = await startRealtimeSession({
          auto_ai_processing: autoProcess,
          processing_interval: config.autoProcessInterval,
          screen_region: region,
          fps: config.fps,
          audio_enabled: config.audioEnabled
        });
        
        console.log('✅ Real-time study session started with ID:', realtimeSessionId);
      } catch (realtimeError) {
        console.warn('⚠️ Real-time session failed to start, continuing with regular capture:', realtimeError);
      }

      const newSession: StudySession = {
        id: newSessionId,
        startTime: new Date(),
        content: [],
        questions: [],
        keyPoints: [],
        isActive: true
      };

      setCurrentSession(newSession);
      setSessionContent('');
      setKeyPoints([]);
      setChatHistory([]);
      
      // Reset analysis state
      setIsAnalyzing(false);
      setAnalysisProgress(0);
      setAnalysisComplete(false);
      setAnalysisStatus('');
      
      // Start auto-processing if enabled
      if (autoProcess) {
        console.log('🔄 Starting auto-processing with interval:', config.autoProcessInterval, 'seconds');
        startAutoProcessing();
      } else {
        console.log('⏸️ Auto-processing disabled');
      }
      
      // Start frame preview
      if (showPreview) {
        console.log('👁️ Starting frame preview');
        startFramePreview();
      }
      
      console.log('🎉 Study session setup complete!');
      toast.success('Study session started! AI assistant is ready to help.');
    } catch (error) {
      toast.error('Failed to start study session');
      console.error('Start session error:', error);
    }
  };

  // Stop the current study session
  const stopStudySession = async () => {
    try {
      // Preserve content before stopping sessions
      let preservedContent = '';
      let preservedKeyPoints: string[] = [];
      
      // Get content from current session before it gets cleared
      if (currentSession && currentSession.content && currentSession.content.length > 0) {
        preservedContent = currentSession.content.join('\n\n');
        preservedKeyPoints = currentSession.keyPoints || [];
        console.log('📝 Preserving content for analysis:', preservedContent.length, 'characters');
      }
      
      // Also try to get content from real-time session
      if (realtimeSession && realtimeSession.session_id) {
        try {
          console.log('📝 Fetching content from real-time session before stopping...');
          const response = await fetch(`http://localhost:8000/api/realtime-study/${realtimeSession.session_id}/status`);
          if (response.ok) {
            const data = await response.json();
            if (data.recent_content && data.recent_content.length > 0) {
              const realtimeContent = data.recent_content.map((item: any) => item.content).join('\n');
              if (realtimeContent.trim()) {
                preservedContent = realtimeContent;
                console.log('📝 Using real-time session content:', preservedContent.length, 'characters');
              }
            }
            if (data.key_points && data.key_points.length > 0) {
              preservedKeyPoints = data.key_points;
            }
          }
        } catch (error) {
          console.warn('Failed to fetch real-time session content:', error);
        }
      }
      
      // Stop the regular capture system
      await stopCapture();
      
      // Also stop the real-time study session if it exists
      if (sessionId) {
        try {
          await stopRealtimeSession(sessionId);
        } catch (realtimeError) {
          console.warn('Real-time session stop failed:', realtimeError);
        }
      }
      
      // Update current session with preserved content but mark as inactive
      if (currentSession) {
        setCurrentSession(prev => prev ? { 
          ...prev, 
          endTime: new Date(), 
          isActive: false,
          content: prev.content, // Keep the content
          keyPoints: preservedKeyPoints.length > 0 ? preservedKeyPoints : prev.keyPoints
        } : null);
      } else if (preservedContent.trim()) {
        // If no currentSession but we have content, create a minimal session record
        const sessionRecord: StudySession = {
          id: sessionId || 'unknown',
          startTime: new Date(),
          endTime: new Date(),
          content: preservedContent.split('\n\n'),
          questions: [],
          keyPoints: preservedKeyPoints,
          isActive: false
        };
        setCurrentSession(sessionRecord);
        console.log('📝 Created session record for preserved content');
      }
      
      // Set the preserved content for AI analysis
      if (preservedContent.trim()) {
        setSessionContent(preservedContent);
        setKeyPoints(preservedKeyPoints);
        console.log('📝 Content preserved for analysis:', preservedContent.length, 'characters');
        toast.success(`Prepared ${preservedContent.split('\n\n').length} content items for AI analysis`);
      } else {
        console.warn('⚠️ No content found to preserve for analysis');
        toast.error('No content captured during session. Please try capturing some content first.');
      }
      
      // Stop auto-processing
      stopAutoProcessing();
      stopFramePreview();
      
      // Reset processing states
      setIsProcessing(false);
      setIsProcessingFrame(false);
      
      // Start AI analysis of captured content if we have content
      if (preservedContent.trim()) {
        await startAIAnalysis();
        toast.success('Study session ended. AI is analyzing your content...');
      } else {
        toast.error('Study session ended but no content was captured for analysis.');
      }
    } catch (error) {
      toast.error('Failed to stop study session');
      console.error('Stop session error:', error);
      
      // Force cleanup even if there's an error
      stopAutoProcessing();
      stopFramePreview();
      setIsProcessing(false);
      setIsProcessingFrame(false);
    }
  };

  // Auto-process content periodically
  const startAutoProcessing = () => {
    if (processingIntervalRef.current) {
      console.log('⚠️ Auto-processing already running, skipping start');
      return;
    }
    
    console.log('🔄 Setting up auto-processing interval:', config.autoProcessInterval, 'seconds');
    processingIntervalRef.current = setInterval(async () => {
      // Get current values from refs
      const currentIsCapturing = isCapturingRef.current;
      const currentAutoProcess = autoProcessRef.current;
      const currentSessionId = sessionIdRef.current;
      
      if (process.env.NODE_ENV === 'development') {
        console.log('⏰ Auto-processing tick - checking conditions:', {
          isCapturing: currentIsCapturing,
          autoProcess: currentAutoProcess,
          sessionId: currentSessionId,
          hasInterval: !!processingIntervalRef.current,
          sessionContentLength: sessionContent.length,
          currentSessionContentItems: currentSession?.content?.length || 0
        });
      }
      
      if (currentIsCapturing && currentAutoProcess && currentSessionId) {
        console.log('✅ Conditions met, processing content...');
        await processCurrentContent();
      } else {
        console.log('❌ Conditions not met for auto-processing:', {
          isCapturing: currentIsCapturing,
          autoProcess: currentAutoProcess,
          sessionId: !!currentSessionId,
          reason: !currentIsCapturing ? 'Not capturing' : 
                  !currentAutoProcess ? 'Auto-process disabled' : 
                  !currentSessionId ? 'No session ID' : 'Unknown'
        });
      }
    }, config.autoProcessInterval * 1000);
    
    console.log('✅ Auto-processing interval started');
  };

  const stopAutoProcessing = () => {
    if (processingIntervalRef.current) {
      clearInterval(processingIntervalRef.current);
      processingIntervalRef.current = null;
    }
  };

  // Process current screen content
  const processCurrentContent = async () => {
    // Get current values from refs
    const currentIsCapturing = isCapturingRef.current;
    const currentSessionId = sessionIdRef.current;
    
    console.log('🎬 PROCESSING CONTENT - Debug Info:', {
      isCapturing: currentIsCapturing,
      sessionId: currentSessionId,
      hasFrame: !!currentFrame
    });
    
    if (!currentIsCapturing || !currentSessionId) {
      console.log('❌ Cannot process content - missing requirements:', {
        isCapturing: currentIsCapturing,
        sessionId: !!currentSessionId
      });
      return;
    }
    
    setIsProcessing(true);
    setIsProcessingFrame(true);
    try {
      // Get current frame
      console.log('📸 Getting current frame...');
      const frame = await getCurrentFrame();
      if (frame && frame.length > 0) {
        setCurrentFrame(frame);
        console.log('✅ Frame received, length:', frame.length);
        
        // Process frame with OCR
        try {
          const response = await fetch(`http://localhost:8000/api/capture/process-frame`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              frame_data: frame
            })
          });
          
          if (response.ok) {
            const result = await response.json();
            console.log('OCR Result:', result);
            
            if (result.extracted_text && result.extracted_text.trim()) {
              const extractedContent = `[${new Date().toLocaleTimeString()}] ${result.extracted_text}`;
              
              setSessionContent(prev => {
                const newContent = prev + '\n' + extractedContent;
                
                // Memory management: trim content if it gets too large
                if (newContent.length > config.maxContentLength) {
                  const trimmedContent = newContent.slice(-config.maxContentLength);
                  console.warn(`Content trimmed to prevent memory issues: ${newContent.length} -> ${trimmedContent.length} characters`);
                  return trimmedContent;
                }
                
                console.log('Updated session content length:', newContent.length);
                console.log('Previous content length:', prev.length);
                console.log('New extracted content:', extractedContent.substring(0, 100) + '...');
                return newContent;
              });
              
              // Always update currentSession if it exists
              setCurrentSession(prev => {
                if (prev) {
                  const newContent = [...prev.content, extractedContent];
                  
                  // Memory management: limit number of content items
                  const trimmedContent = newContent.length > config.maxContentItems 
                    ? newContent.slice(-config.maxContentItems)
                    : newContent;
                  
                  if (trimmedContent.length < newContent.length) {
                    console.warn(`Content items trimmed: ${newContent.length} -> ${trimmedContent.length} items`);
                  }
                  
                  const updatedSession = {
                    ...prev,
                    content: trimmedContent
                  };
                  console.log('📝 Updated currentSession.content:', {
                    previousLength: prev.content.length,
                    newLength: updatedSession.content.length,
                    newItem: extractedContent.substring(0, 50) + '...',
                    sessionId: prev.id
                  });
                  return updatedSession;
                } else {
                  console.warn('⚠️ No currentSession to update! Creating new session...');
                  // Create a new session if none exists
                  const newSession: StudySession = {
                    id: sessionId || 'unknown',
                    startTime: new Date(),
                    content: [extractedContent],
                    questions: [],
                    keyPoints: [],
                    isActive: true
                  };
                  console.log('📝 Created new currentSession:', newSession);
                  return newSession;
                }
              });
              
              // Show success message with confidence level
              const confidenceLevel = result.confidence > 80 ? 'high' : result.confidence > 50 ? 'medium' : 'low';
              toast.success(`✅ Extracted ${result.text_length} characters (${confidenceLevel} confidence: ${result.confidence.toFixed(1)}%) - Content saved to session!`);
              
              // Send extracted text to real-time study session
              if (realtimeSession && realtimeSession.session_id) {
                try {
                  console.log('Sending extracted text to real-time session:', realtimeSession.session_id);
                  const response = await fetch(`http://localhost:8000/api/realtime-study/${realtimeSession.session_id}/content`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                      content: extractedContent,
                      content_type: 'ocr',
                      metadata: {
                        confidence: result.confidence,
                        text_length: result.text_length,
                        timestamp: new Date().toISOString()
                      }
                    })
                  });
                  
                  if (response.ok) {
                    console.log('Extracted text sent successfully to real-time session');
                  } else {
                    console.warn('Failed to send extracted text to real-time session:', response.status);
                  }
                } catch (error) {
                  console.warn('Error sending extracted text to real-time session:', error);
                }
              }
              
              // Also save to regular capture session for backup
              if (sessionId) {
                try {
                  console.log('Saving extracted text to capture session:', sessionId);
                  const response = await fetch(`http://localhost:8000/api/capture/save-content`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                      session_id: sessionId,
                      content: extractedContent,
                      content_type: 'ocr',
                      metadata: {
                        confidence: result.confidence,
                        text_length: result.text_length,
                        timestamp: new Date().toISOString()
                      }
                    })
                  });
                  
                  if (response.ok) {
                    console.log('Extracted text saved successfully to capture session');
                  } else {
                    console.warn('Failed to save extracted text to capture session:', response.status);
                  }
                } catch (error) {
                  console.warn('Error saving extracted text to capture session:', error);
                }
              }
              
              // Auto-generate key points if content is substantial
              if (sessionContent.length > 500 && config.aiAssistanceLevel !== 'low') {
                await generateKeyPoints();
              }
            } else {
              console.log('No text detected in frame');
              toast('📝 No text detected in this frame. Try capturing a different area with visible text.');
            }
          } else {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            console.error('OCR processing failed:', response.status, errorData);
            toast.error(`❌ OCR processing failed: ${errorData.detail || response.statusText}`);
          }
        } catch (ocrError) {
          console.error('OCR processing error:', ocrError);
          toast.error('❌ Failed to process frame with OCR. Check if Tesseract is installed.');
        }
        
        // Note: Extracted text is now sent to real-time session above in the OCR processing section
      } else {
        console.log('❌ No frame received or empty frame');
        toast('📸 No frame captured. Make sure the screen capture is working properly.');
      }
    } catch (error) {
      console.error('Content processing error:', error);
      toast.error('Failed to process content. Check console for details.');
    } finally {
      setIsProcessing(false);
      setIsProcessingFrame(false);
    }
  };

  // Generate key points from session content
  const generateKeyPoints = async () => {
    if (!sessionContent.trim()) return;
    
    try {
      const response = await extractKeyConcepts(sessionContent, 5);
      const points = response.content.split('\n').filter((point: string) => point.trim());
      setKeyPoints(points);
      
      if (currentSession) {
        setCurrentSession(prev => prev ? {
          ...prev,
          keyPoints: points
        } : null);
      }
    } catch (error) {
      console.error('Key points generation error:', error);
    }
  };

  // AI Analysis function with progress simulation
  const startAIAnalysis = async () => {
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setAnalysisComplete(false);
    setAnalysisStatus('Starting AI analysis...');

    try {
      // Debug: Log current state before analysis
      console.log('=== STARTING AI ANALYSIS ===');
      console.log('Current sessionContent length:', sessionContent.length);
      console.log('Current sessionContent preview:', sessionContent.substring(0, 200));
      console.log('Current session ID:', sessionId);
      console.log('Real-time session ID:', realtimeSession?.session_id);
      console.log('Current session content items:', currentSession?.content?.length || 0);
      console.log('Current session content preview:', currentSession?.content?.map(item => item.substring(0, 50) + '...') || []);
      
      // First, fetch the latest session content
      setAnalysisStatus('Fetching captured content...');
      setAnalysisProgress(10);
      
      let contentToAnalyze = sessionContent; // Start with current local content
      console.log('Starting with local session content length:', contentToAnalyze.length);
      
      // If we have local content, use it as primary source
      if (contentToAnalyze.trim()) {
        console.log('Using local session content for analysis:', contentToAnalyze.length, 'characters');
      } else if (currentSession && currentSession.content && currentSession.content.length > 0) {
        // Fallback: use content from currentSession.content array
        contentToAnalyze = currentSession.content.join('\n\n');
        setSessionContent(contentToAnalyze);
        console.log('Using currentSession.content for analysis:', contentToAnalyze.length, 'characters');
      } else {
        console.log('No local content, trying to fetch from sessions...');
        
        // Try to fetch content from real-time study session
        if (realtimeSession && realtimeSession.session_id) {
          try {
            console.log('Fetching content for real-time session:', realtimeSession.session_id);
            const response = await fetch(`http://localhost:8000/api/realtime-study/${realtimeSession.session_id}/status`);
            if (response.ok) {
              const data = await response.json();
              console.log('Fetched real-time session data:', data);
              
              // Extract content from recent_content items
              if (data.recent_content && data.recent_content.length > 0) {
                const allContent = data.recent_content.map((item: any) => item.content).join('\n');
                if (allContent.trim()) {
                  contentToAnalyze = allContent;
                  setSessionContent(allContent);
                  console.log('Updated content to analyze from real-time session:', contentToAnalyze.length, 'characters');
                } else {
                  console.log('No content in recent_content items');
                }
              } else {
                console.log('No recent_content in fetched data');
              }
            } else {
              console.log('Failed to fetch real-time session content, status:', response.status);
            }
          } catch (error) {
            console.warn('Failed to fetch latest real-time session content:', error);
          }
        } else {
          console.log('No real-time session available for content fetching');
        }

        // If still no content, try to get content from regular capture session
        if (!contentToAnalyze.trim() && sessionId) {
          try {
            console.log('Trying to fetch content from capture session:', sessionId);
            const response = await fetch(`http://localhost:8000/api/capture/extracted-content`);
            if (response.ok) {
              const result = await response.json();
              console.log('Fetched capture session content:', result);
              
              if (result.content && result.content.length > 0) {
                const combinedContent = result.content.join('\n\n');
                if (combinedContent.trim()) {
                  contentToAnalyze = combinedContent;
                  setSessionContent(combinedContent);
                  console.log('Updated content to analyze from capture session:', contentToAnalyze.length, 'characters');
                }
              }
            }
          } catch (error) {
            console.warn('Failed to fetch capture session content:', error);
          }
        }
      }

      // Check if we have content to analyze (use the fetched content, not the state)
      console.log('Content to analyze length:', contentToAnalyze.length);
      console.log('Content preview:', contentToAnalyze.substring(0, 200));
      
      if (!contentToAnalyze.trim()) {
        console.log('No content found for analysis');
        setAnalysisStatus('No content available for analysis');
        setAnalysisComplete(false); // Ensure this is false when no content
        
        // Try one more fallback - check if we have any content in currentSession
        if (currentSession && currentSession.content && currentSession.content.length > 0) {
          const fallbackContent = currentSession.content.join('\n\n');
          if (fallbackContent.trim()) {
            console.log('Using fallback content from currentSession:', fallbackContent.length, 'characters');
            contentToAnalyze = fallbackContent;
            setSessionContent(fallbackContent);
          }
        }
        
        // If still no content after fallback
        if (!contentToAnalyze.trim()) {
          toast.error('No content to analyze yet. Start capturing to build content.');
          setIsAnalyzing(false);
          return;
        }
      }

      // Simulate analysis progress
      const analysisSteps = [
        { progress: 20, status: 'Processing video content...' },
        { progress: 40, status: 'Extracting text with OCR...' },
        { progress: 60, status: 'Transcribing audio...' },
        { progress: 80, status: 'Analyzing content with AI...' },
        { progress: 95, status: 'Generating key insights...' },
        { progress: 100, status: 'Analysis complete!' }
      ];

      for (const step of analysisSteps) {
        setAnalysisProgress(step.progress);
        setAnalysisStatus(step.status);
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulate processing time
      }

      // Generate key points and summary
      await generateKeyPoints();
      
      // Generate summary
      try {
        const summaryResponse = await generateSummary(contentToAnalyze);
        setSessionContent(summaryResponse.content);
      } catch (error) {
        console.error('Summary generation error:', error);
      }

      setAnalysisComplete(true);
      setAnalysisStatus('Ready for questions!');
      toast.success('AI analysis complete! You can now ask questions about the content.');
      
    } catch (error) {
      console.error('AI analysis error:', error);
      toast.error('Failed to complete AI analysis. Please try again.');
      setAnalysisStatus('Analysis failed - please try again');
      setAnalysisProgress(0);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Start frame preview
  const startFramePreview = () => {
    if (frameIntervalRef.current) return;
    
    frameIntervalRef.current = setInterval(async () => {
      if (isCapturing && showPreview) {
        try {
          const frame = await getCurrentFrame();
          setCurrentFrame(frame);
        } catch (error) {
          console.error('Frame preview error:', error);
        }
      }
    }, 1000 / config.fps);
  };

  const stopFramePreview = () => {
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }
  };

  // AI Assistant functions
  const askQuestionDirectly = async (question: string, content: string) => {
    try {
      console.log('🤖 Asking question directly with content...');
      
      // Create a prompt that includes both the content and the question
      const prompt = `Based on the following content, please answer the question:

CONTENT:
${content}

QUESTION: ${question}

Please provide a comprehensive answer based on the content above.`;

      const response = await fetch('http://localhost:8000/api/ai/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: prompt,
          max_length: 1000
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Direct AI response received:', result);
        return result;
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('❌ Direct AI question failed:', response.status, errorData);
        throw new Error(errorData.detail || response.statusText);
      }
    } catch (error) {
      console.error('❌ Error asking question directly:', error);
      throw error;
    }
  };

  const askQuestionWithContent = async (question: string, content: string) => {
    try {
      console.log('🤖 Sending question with content to AI:', {
        questionLength: question.length,
        contentLength: content.length,
        hasContent: !!content.trim(),
        sessionId: sessionId
      });
      
      // First, try to save the content to the session if we have a sessionId
      if (sessionId && content.trim()) {
        try {
          console.log('💾 Saving content to session for AI access...');
          const saveResponse = await fetch(`http://localhost:8000/api/capture/save-content`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              session_id: sessionId,
              content: content,
              content_type: 'manual',
              metadata: {
                timestamp: new Date().toISOString(),
                source: 'frontend_question'
              }
            })
          });
          
          if (saveResponse.ok) {
            console.log('✅ Content saved to session successfully');
          } else {
            console.warn('⚠️ Failed to save content to session:', saveResponse.status);
          }
        } catch (saveError) {
          console.warn('⚠️ Error saving content to session:', saveError);
        }
      }
      
      // Now ask the question using the session_id
      const response = await fetch('http://localhost:8000/api/ai/question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          session_id: sessionId, // Use session_id so backend can find the content
          include_citations: true,
          top_k: 5
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ AI response received:', result);
        
        // Check if the response indicates no context was found
        if (result.content && result.content.includes('Please provide the context')) {
          console.log('⚠️ AI says no context found, trying direct content approach...');
          // Fallback: use the content directly with a different approach
          return await askQuestionDirectly(question, content);
        }
        
        return result;
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('❌ AI question failed:', response.status, errorData);
        
        // Fallback: try direct content approach
        console.log('🔄 Trying fallback approach with direct content...');
        return await askQuestionDirectly(question, content);
      }
    } catch (error) {
      console.error('❌ Error asking question with content:', error);
      throw error;
    }
  };

  const handleAskQuestion = async () => {
    // Input validation
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      toast.error('Please enter a question.');
      return;
    }

    // Sanitize input (basic XSS protection)
    const sanitizedQuestion = trimmedQuestion.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    if (sanitizedQuestion !== trimmedQuestion) {
      toast.error('Invalid characters detected in question.');
      return;
    }

    // Check if we have content to analyze
    if (!sessionContent.trim()) {
      // Try to get content from currentSession as fallback
      if (currentSession && currentSession.content && currentSession.content.length > 0) {
        const fallbackContent = currentSession.content.join('\n\n');
        if (fallbackContent.trim()) {
          console.log('Using fallback content from currentSession for question:', fallbackContent.length, 'characters');
          setSessionContent(fallbackContent);
        } else {
          toast.error('No content available to analyze. Please capture some content first.');
          return;
        }
      } else {
        toast.error('No content available to analyze. Please capture some content first.');
        return;
      }
    }

    // Check if analysis is complete
    if (!analysisComplete) {
      toast.error('Please complete AI analysis first before asking questions.');
      return;
    }

    console.log('🤖 Question asked:', question);
    console.log('📄 Content available:', sessionContent.length, 'characters');
    console.log('📄 Content preview:', sessionContent.substring(0, 200) + '...');

    const userMessage = { type: 'user' as const, content: question, timestamp: new Date() };
    setChatHistory(prev => [...prev, userMessage]);
    setQuestion('');
    setIsLoading(true);

    try {
      let response;
      
      // Try real-time session first, fallback to regular AI
      if (realtimeSession && realtimeSession.session_id) {
        try {
          console.log('🤖 Asking question via real-time session:', realtimeSession.session_id);
          response = await askRealtimeQuestion(realtimeSession.session_id, question);
          response = { content: response.answer };
        } catch (realtimeError) {
          console.warn('Real-time question failed, using regular AI with content:', realtimeError);
          // Fallback: send question with captured content
          response = await askQuestionWithContent(question, sessionContent);
        }
      } else {
        console.log('🤖 Asking question with captured content:', sessionContent.length, 'characters');
        // Send question with captured content
        response = await askQuestionWithContent(question, sessionContent);
      }
      
      const aiMessage = { 
        type: 'ai' as const, 
        content: response.content, 
        timestamp: new Date() 
      };
      setChatHistory(prev => [...prev, aiMessage]);
      
      // Add to session questions
      if (currentSession) {
        setCurrentSession(prev => prev ? {
          ...prev,
          questions: [...prev.questions, {
            question: question,
            answer: response.content,
            timestamp: new Date()
          }]
        } : null);
      }
    } catch (error) {
      toast.error('Failed to get answer');
      console.error('Question error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!sessionContent.trim()) {
      toast.error('No content to summarize yet. Start capturing to build content.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateSummary(sessionContent);
      setSessionContent(response.content);
      toast.success('Summary generated successfully!');
    } catch (error) {
      toast.error('Failed to generate summary');
      console.error('Summary error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateFlashcards = async () => {
    if (!sessionContent.trim()) {
      toast.error('No content for flashcards yet. Start capturing to build content.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateFlashcards(sessionContent);
      setSessionContent(response.content);
      toast.success('Flashcards generated successfully!');
    } catch (error) {
      toast.error('Failed to generate flashcards');
      console.error('Flashcards error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!sessionContent.trim()) {
      toast.error('No content for quiz yet. Start capturing to build content.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateQuiz(sessionContent);
      setSessionContent(response.content);
      toast.success('Quiz generated successfully!');
    } catch (error) {
      toast.error('Failed to generate quiz');
      console.error('Quiz error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Get extracted content from backend
  const getExtractedContent = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/capture/extracted-content');
      if (response.ok) {
        const result = await response.json();
        console.log('Extracted content:', result);
        
        if (result.content && result.content.length > 0) {
          const combinedContent = result.content.join('\n\n');
          setSessionContent(combinedContent);
          setKeyPoints(result.key_points || []);
          toast.success(`Loaded ${result.total_items} extracted content items`);
        } else {
          toast('No extracted content available yet');
        }
      } else {
        console.error('Failed to get extracted content:', response.statusText);
      }
    } catch (error) {
      console.error('Error getting extracted content:', error);
    }
  };

  // Export session data
  const exportSession = () => {
    if (!currentSession) {
      toast.error('No active session to export');
      return;
    }

    const exportData = {
      session: currentSession,
      content: sessionContent,
      keyPoints: keyPoints,
      chatHistory: chatHistory,
      exportTime: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `study-session-${currentSession.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success('Session exported successfully!');
  };

  // Update refs when values change
  useEffect(() => {
    isCapturingRef.current = isCapturing;
  }, [isCapturing]);
  
  useEffect(() => {
    autoProcessRef.current = autoProcess;
  }, [autoProcess]);
  
  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  // Load AI models/providers status
  useEffect(() => {
    const loadModels = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/ai/models');
        if (res.ok) {
          const data = await res.json();
          // Dedupe models while preserving order
          const rawModels: string[] = data.available_models || [];
          const seen = new Set<string>();
          const uniqueModels = rawModels.filter((m: string) => {
            if (seen.has(m)) return false;
            seen.add(m);
            return true;
          });
          setAvailableModels(uniqueModels);
          setServicesStatus(data.services || {});
          // Only apply backend-reported provider/model if not already saved locally
          const savedProvider = (() => { try { return localStorage.getItem('ai_provider'); } catch { return null; } })();
          const savedModel = (() => { try { return localStorage.getItem('ai_model'); } catch { return null; } })();
          if (!savedProvider) {
            setAiProvider((data.provider || 'gemini') as any);
          }
          if (!savedModel && data.current_model) {
            setSelectedModel(data.current_model);
          }
        }
      } catch (e) {
        console.warn('Failed to load AI models/providers', e);
      }
    };
    loadModels();
  }, []);

  const handleSaveAISettings = async () => {
    try {
      const payload: any = { llm_provider: aiProvider, model: selectedModel };
      if (deepseekKeyInput.trim()) {
        payload.deepseek_api_key = deepseekKeyInput.trim();
      }
      const res = await fetch('http://localhost:8000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        toast.success('AI settings saved. Restart backend to apply.');
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(`Failed to save AI settings${err.detail ? `: ${err.detail}` : ''}`);
      }
    } catch (e) {
      toast.error('Failed to save AI settings');
      console.error(e);
    }
  };

  // Debug currentSession changes (only in development)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🔄 currentSession changed:', {
        id: currentSession?.id,
        contentLength: currentSession?.content?.length || 0,
        isActive: currentSession?.isActive,
        contentItems: currentSession?.content?.map(item => item.substring(0, 50) + '...') || []
      });
    }
  }, [currentSession]);

  // Check OCR status on mount
  useEffect(() => {
    checkOcrStatus();
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopAutoProcessing();
      stopFramePreview();
    };
  }, []);

  // Update frame preview when showPreview changes
  useEffect(() => {
    if (showPreview && isCapturing) {
      startFramePreview();
    } else {
      stopFramePreview();
    }
  }, [showPreview, isCapturing]);

  const tabs = [
    { id: 'chat', name: 'AI Chat', icon: MessageCircle },
    { id: 'summary', name: 'Summary', icon: FileText },
    { id: 'flashcards', name: 'Flashcards', icon: BookOpen },
    { id: 'quiz', name: 'Quiz', icon: HelpCircle },
    { id: 'concepts', name: 'Key Concepts', icon: Lightbulb },
    { id: 'plan', name: 'Study Plan', icon: Target }
  ];

  return (
    <div className="min-h-screen bg-brand-cream">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-brand-teal" />
                <div>
                  <h1 className="text-xl font-bold text-brand-slate">Real-Time Study Assistant</h1>
                  <p className="text-sm text-brand-slate opacity-80">AI-powered study session with live capture</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Session Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isCapturing ? 'bg-brand-teal animate-pulse' : 'bg-gray-400'}`}></div>
                <span className="text-sm text-brand-slate opacity-80">
                  {isCapturing ? 'Recording' : 'Idle'}
                </span>
              </div>
              
              {/* OCR Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  ocrStatus === 'available' ? 'bg-brand-teal' : 
                  ocrStatus === 'unavailable' ? 'bg-red-500' : 
                  'bg-brand-sand animate-pulse'
                }`}></div>
                <span className="text-sm text-brand-slate opacity-80">
                  OCR: {ocrStatus === 'available' ? 'Ready' : ocrStatus === 'unavailable' ? 'Unavailable' : 'Checking...'}
                </span>
              </div>
              
              {/* Session Controls */}
              <div className="flex items-center space-x-2">
                {!isCapturing ? (
                  <button
                    onClick={startStudySession}
                    className="btn-primary btn-md flex items-center space-x-2"
                  >
                    <Play className="h-4 w-4" />
                    <span>Start Session</span>
                  </button>
                ) : (
                  <button
                    onClick={stopStudySession}
                    className="btn-secondary btn-md flex items-center space-x-2"
                  >
                    <Square className="h-4 w-4" />
                    <span>Stop Session</span>
                  </button>
                )}
                
                {isCapturing && (
                  <button
                    onClick={processCurrentContent}
                    className="btn-outline btn-md flex items-center space-x-2"
                    disabled={ocrStatus === 'unavailable'}
                    title={ocrStatus === 'unavailable' ? 'OCR is not available. Please check Tesseract installation.' : 'Capture and process current frame with OCR'}
                  >
                    <Camera className="h-4 w-4" />
                    <span>Capture Frame</span>
                  </button>
                )}
                
                {isCapturing && (
                  <button
                    onClick={getExtractedContent}
                    className="btn-outline btn-md flex items-center space-x-2"
                  >
                    <FileText className="h-4 w-4" />
                    <span>Load Content</span>
                  </button>
                )}
                
                {currentSession && (
                  <button
                    onClick={exportSession}
                    className="btn-outline btn-md flex items-center space-x-2"
                  >
                    <Download className="h-4 w-4" />
                    <span>Export</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Session Info & Controls */}
          <div className="lg:col-span-1 space-y-6">
            {/* Session Information */}
            {currentSession ? (
              <div className="card p-4">
                <h3 className="text-lg font-semibold text-brand-slate mb-3 flex items-center">
                  <Clock className="h-5 w-5 mr-2 text-brand-teal" />
                  Session Info
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Started:</span>
                    <span className="text-gray-900">{currentSession.startTime.toLocaleTimeString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span className="text-gray-900">
                      {Math.floor((Date.now() - currentSession.startTime.getTime()) / 60000)}m
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Content Items:</span>
                    <span className="text-gray-900 font-semibold">{currentSession.content.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Questions:</span>
                    <span className="text-gray-900">{currentSession.questions.length}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Clock className="h-5 w-5 mr-2 text-gray-400" />
                  No Active Session
                </h3>
                <div className="text-sm text-gray-600">
                  <p className="mb-2">Click "Start Session" to begin capturing study content.</p>
                  <p className="text-xs text-gray-500">
                    Once started, the system will automatically capture screen content and extract text for AI analysis.
                  </p>
                </div>
              </div>
            )}

            {/* Capture Statistics */}
            {captureStats && (
              <div className="card p-4">
                <h3 className="text-lg font-semibold text-brand-slate mb-3 flex items-center">
                  <Activity className="h-5 w-5 mr-2 text-brand-teal" />
                  Capture Stats
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Screen FPS:</span>
                    <span className="text-gray-900">
                      {(captureStats.screen_stats?.actual_fps || 0).toFixed(1)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Frames:</span>
                    <span className="text-gray-900">{captureStats.screen_stats?.frame_count || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Audio:</span>
                    <span className={`${captureStats.audio_stats?.status === 'capturing' ? 'chip-success' : 'chip-neutral'}`}>
                      {captureStats.audio_stats?.status === 'capturing' ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* AI Analysis Status */}
            {isAnalyzing && (
              <div className="card p-4">
                <h3 className="text-lg font-semibold text-brand-slate mb-3 flex items-center">
                  <Brain className="h-5 w-5 mr-2 text-brand-teal" />
                  AI Analysis
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Progress</span>
                    <span className="text-sm font-medium text-brand-teal">{analysisProgress}%</span>
                  </div>
                  <div className="w-full bg-brand-sand rounded-full h-2">
                    <div 
                      className="bg-brand-teal h-2 rounded-full transition-all duration-500 ease-out"
                      style={{ width: `${analysisProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-600">{analysisStatus}</p>
                </div>
              </div>
            )}

            {/* Analysis Complete Status */}
            {analysisComplete && !isAnalyzing && (
              <div className="card p-4">
                <h3 className="text-lg font-semibold text-brand-slate mb-3 flex items-center">
                  <Brain className="h-5 w-5 mr-2 text-brand-teal" />
                  AI Ready
                </h3>
                <div className="flex items-center space-x-2 text-sm text-green-700">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Ready for questions</span>
                </div>
              </div>
            )}

            {/* OCR Status */}
            <div className="card p-4">
              <h3 className="text-lg font-semibold text-brand-slate mb-3 flex items-center">
                <Eye className="h-5 w-5 mr-2 text-brand-teal" />
                OCR Status
              </h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className={
                    ocrStatus === 'available' ? 'chip-success' : ocrStatus === 'unavailable' ? 'chip-error' : 'chip-warning'
                  }>
                    {ocrStatus === 'available' ? 'Ready' : ocrStatus === 'unavailable' ? 'Unavailable' : 'Checking...'}
                  </span>
                </div>
                {ocrStatus === 'unavailable' && (
                  <div className="text-xs chip-error rounded">
                    OCR is not available. Please ensure Tesseract is installed.
                  </div>
                )}
                {ocrStatus === 'available' && (
                  <div className="text-xs chip-success rounded">
                    Text extraction is ready for captured frames.
                  </div>
                )}
              </div>
            </div>

            {/* Key Points */}
            {keyPoints.length > 0 && (
              <div className="card p-4">
                <h3 className="text-lg font-semibold text-brand-slate mb-3 flex items-center">
                  <Lightbulb className="h-5 w-5 mr-2 text-brand-teal" />
                  Key Points
                </h3>
                <div className="space-y-2">
                  {keyPoints.map((point, index) => (
                    <div key={index} className="text-sm text-brand-slate bg-brand-sand p-2 rounded">
                      {point}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Debug Panel */}
            <div className="card p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <Activity className="h-5 w-5 mr-2 text-purple-600" />
                Debug Info
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-600">isCapturing:</span>
                  <span className={`font-mono ${isCapturing ? 'text-green-600' : 'text-red-600'}`}>
                    {isCapturing.toString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">sessionId:</span>
                  <span className="font-mono text-gray-900 truncate max-w-32">
                    {sessionId || 'null'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">realtimeSession:</span>
                  <span className="font-mono text-gray-900 truncate max-w-32">
                    {realtimeSession?.session_id || 'null'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">autoProcess:</span>
                  <span className={`font-mono ${autoProcess ? 'text-green-600' : 'text-red-600'}`}>
                    {autoProcess.toString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">sessionContent:</span>
                  <span className="font-mono text-gray-900">
                    {sessionContent.length} chars
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">currentSession.content:</span>
                  <span className="font-mono text-gray-900">
                    {currentSession?.content?.length || 0} items
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">processingInterval:</span>
                  <span className="font-mono text-gray-900">
                    {processingIntervalRef.current ? 'active' : 'inactive'}
                  </span>
                </div>
              </div>
            </div>

            {/* Performance Settings */}
            <div className="card p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <Settings className="h-5 w-5 mr-2 text-gray-600" />
                Performance Settings
              </h3>
              <div className="space-y-3">
                {/* AI Provider */}
                <div>
                  <label className="block text-sm text-gray-600 mb-1">AI Provider</label>
                  <select
                    value={aiProvider}
                    onChange={(e) => setAiProvider(e.target.value as any)}
                    className="input text-sm"
                  >
                    <option value="gemini">Gemini</option>
                    <option value="openai">OpenAI</option>
                    <option value="deepseek">DeepSeek</option>
                    <option value="auto">Auto (best available)</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Status: Gemini {servicesStatus.gemini_available ? '✅' : '❌'} · OpenAI {servicesStatus.openai_available ? '✅' : '❌'} · DeepSeek {servicesStatus.deepseek_available ? '✅' : '❌'}
                  </p>
                </div>

                {/* Model Selection */}
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Model</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="input text-sm"
                  >
                    {availableModels.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">List includes models from Gemini, OpenAI, and DeepSeek.</p>
                </div>

                {/* DeepSeek Key (optional) */}
                {aiProvider === 'deepseek' && (
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">DeepSeek API Key</label>
                    <input
                      type="password"
                      value={deepseekKeyInput}
                      onChange={(e) => setDeepseekKeyInput(e.target.value)}
                      placeholder="Enter DeepSeek API Key"
                      className="input text-sm w-full"
                    />
                    <p className="text-xs text-gray-500 mt-1">Key is saved to backend settings.</p>
                  </div>
                )}

                <div>
                  <button onClick={handleSaveAISettings} className="btn-primary btn-sm">Save AI Settings</button>
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">FPS (Screen Capture)</label>
                  <select
                    value={config.fps}
                    onChange={(e) => setConfig({ ...config, fps: parseInt(e.target.value) })}
                    className="input text-sm"
                  >
                    <option value={1}>1 FPS (Low CPU)</option>
                    <option value={2}>2 FPS (Balanced)</option>
                    <option value={5}>5 FPS (High Quality)</option>
                    <option value={10}>10 FPS (Maximum)</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Auto Process Interval</label>
                  <select
                    value={config.autoProcessInterval}
                    onChange={(e) => setConfig({ ...config, autoProcessInterval: parseFloat(e.target.value) })}
                    className="input text-sm"
                  >
                    <option value={0.5}>0.5s (Real-time)</option>
                    <option value={1}>1s (Fast)</option>
                    <option value={5}>5s (Balanced)</option>
                    <option value={10}>10s (Low CPU)</option>
                    <option value={30}>30s (Minimal)</option>
                  </select>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Audio Capture</span>
                  <button
                    onClick={() => setConfig({ ...config, audioEnabled: !config.audioEnabled })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      config.audioEnabled ? 'bg-green-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        config.audioEnabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Screen Region</label>
                  <select
                    value={config.screenRegion}
                    onChange={(e) => setConfig({ ...config, screenRegion: e.target.value as any })}
                    className="input text-sm"
                  >
                    <option value="full">Full Screen</option>
                    <option value="custom">Custom Region</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-600 mb-1">AI Assistance</label>
                  <select
                    value={config.aiAssistanceLevel}
                    onChange={(e) => setConfig({ ...config, aiAssistanceLevel: e.target.value as any })}
                    className="input text-sm"
                  >
                    <option value="low">Low (Minimal AI)</option>
                    <option value="medium">Medium (Balanced)</option>
                    <option value="high">High (Maximum AI)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Quick Settings */}
            <div className="card p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <Settings className="h-5 w-5 mr-2 text-gray-600" />
                Quick Settings
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Auto Process</span>
                  <button
                    onClick={() => setAutoProcess(!autoProcess)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      autoProcess ? 'bg-green-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        autoProcess ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Show Preview</span>
                  <button
                    onClick={() => setShowPreview(!showPreview)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      showPreview ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        showPreview ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                
                <div className="pt-2 border-t space-y-2">
                  <button
                    onClick={processCurrentContent}
                    className="w-full btn-outline btn-sm text-xs"
                    disabled={!isCapturing}
                  >
                    Test Auto-Process
                  </button>
                  <button
                    onClick={async () => {
                      console.log('🔍 Manual debug check...');
                      console.log('isCapturing:', isCapturing);
                      console.log('sessionId:', sessionId);
                      console.log('realtimeSession:', realtimeSession?.session_id);
                      console.log('sessionContent length:', sessionContent.length);
                      console.log('currentSession content items:', currentSession?.content?.length || 0);
                      console.log('autoProcess:', autoProcess);
                      console.log('processingInterval active:', !!processingIntervalRef.current);
                      
                      if (isCapturing) {
                        try {
                          const frame = await getCurrentFrame();
                          console.log('Current frame length:', frame?.length || 0);
                          if (frame) {
                            setCurrentFrame(frame);
                            toast.success(`Frame captured: ${frame.length} bytes`);
                          } else {
                            toast.error('No frame captured');
                          }
                        } catch (error) {
                          console.error('Frame capture error:', error);
                          toast.error('Frame capture failed');
                        }
                      } else {
                        toast.error('Not currently capturing');
                      }
                    }}
                    className="w-full btn-outline btn-sm text-xs"
                  >
                    Debug Capture
                  </button>
                  <button
                    onClick={() => {
                      console.log('🔄 Force refresh debug info...');
                      console.log('Current state snapshot:', {
                        isCapturing,
                        sessionId,
                        sessionContentLength: sessionContent.length,
                        currentSessionId: currentSession?.id,
                        currentSessionContentLength: currentSession?.content?.length || 0,
                        currentSessionContent: currentSession?.content || [],
                        realtimeSessionId: realtimeSession?.session_id
                      });
                      toast('Debug info logged to console');
                    }}
                    className="w-full btn-outline btn-sm text-xs"
                  >
                    Force Refresh
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3 space-y-6">
            {/* Live Preview */}
            {showPreview && isCapturing && (
              <div className="card p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-brand-slate flex items-center">
                    <Monitor className="h-5 w-5 mr-2 text-brand-teal" />
                    Live Preview
                  </h3>
                  <div className="flex items-center space-x-2">
                    {isProcessing && (
                      <div className="flex items-center space-x-2 text-sm text-brand-teal">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Processing...</span>
                      </div>
                    )}
                    <button
                      onClick={() => setShowPreview(false)}
                      className="btn-outline btn-sm"
                    >
                      <Minimize2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <div className="bg-brand-sand rounded-lg p-4 min-h-[200px] flex items-center justify-center">
                  {currentFrame ? (
                    <img
                      src={`data:image/jpeg;base64,${currentFrame}`}
                      alt="Current frame"
                      className="max-w-full max-h-full rounded-lg shadow-lg"
                    />
                  ) : (
                    <div className="text-center text-brand-slate opacity-70">
                      <Camera className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>No frame available</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* AI Assistant */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-brand-slate flex items-center">
                  <Brain className="h-5 w-5 mr-2 text-brand-teal" />
                  AI Study Assistant
                </h2>
                <div className="flex items-center space-x-2">
                  {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`p-2 rounded-lg transition-colors ${
                          activeTab === tab.id
                            ? 'bg-brand-sand text-brand-slate'
                            : 'text-gray-600 hover:bg-brand-cream'
                        }`}
                        title={tab.name}
                      >
                        <Icon className="h-4 w-4" />
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Chat Interface */}
              {activeTab === 'chat' && (
                <div>
                  {/* Chat History */}
                  <div className="h-64 overflow-y-auto border border-brand-sand rounded-lg p-4 mb-4 bg-brand-cream">
                    {chatHistory.length === 0 ? (
                      <div className="text-center text-gray-500 py-8">
                        <MessageCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                        <p>Ask questions about your study content</p>
                        <p className="text-sm mt-1">The AI will analyze your captured content to provide answers</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {chatHistory.map((message, index) => (
                          <div
                            key={index}
                            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                          >
                            <div
                              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                message.type === 'user'
                                  ? 'bg-brand-teal text-white'
                                  : 'bg-white text-gray-900 border border-brand-sand'
                              }`}
                            >
                              <p className="text-sm">{message.content}</p>
                              <p className={`text-xs mt-1 ${
                                message.type === 'user' ? 'text-brand-cream' : 'text-gray-500'
                              }`}>
                                {message.timestamp.toLocaleTimeString()}
                              </p>
                            </div>
                          </div>
                        ))}
                        {isLoading && (
                          <div className="flex justify-start">
                            <div className="bg-white text-gray-900 border border-gray-200 px-4 py-2 rounded-lg">
                              <div className="flex items-center space-x-2">
                                <Loader2 className="h-4 w-4 animate-spin" />
                                <span className="text-sm">Thinking...</span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* AI Analysis Status */}
                  {isAnalyzing && (
                    <div className="mb-4 p-4 bg-brand-cream rounded-lg border border-brand-sand">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-brand-slate">AI Analysis in Progress</h3>
                        <span className="text-sm text-brand-slate">{analysisProgress}%</span>
                      </div>
                      <div className="w-full bg-brand-sand rounded-full h-2 mb-2">
                        <div 
                          className="bg-brand-teal h-2 rounded-full transition-all duration-500 ease-out"
                          style={{ width: `${analysisProgress}%` }}
                        ></div>
                      </div>
                      <p className="text-sm text-brand-slate">{analysisStatus}</p>
                    </div>
                  )}

                  {/* Analysis Complete Status */}
                  {analysisComplete && !isAnalyzing && sessionContent.trim() && (
                    <div className="mb-4 p-4 bg-brand-cream rounded-lg border border-brand-sand">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-brand-teal rounded-full animate-pulse"></div>
                        <p className="text-sm font-medium text-brand-slate">AI Analysis Complete!</p>
                      </div>
                      <p className="text-sm text-brand-slate mt-1">You can now ask questions about the analyzed content.</p>
                    </div>
                  )}

                  {/* No Content Error Messages */}
                  {!sessionContent.trim() && !isAnalyzing && (
                    <div className="mb-4 p-4 bg-brand-cream rounded-lg border border-brand-sand">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <p className="text-sm font-medium text-brand-slate">No content available to analyze</p>
                      </div>
                      <p className="text-sm text-brand-slate mt-1">Please capture some content first.</p>
                    </div>
                  )}

                  {/* Question Input */}
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
                      placeholder={
                        isAnalyzing 
                          ? "AI is analyzing content, please wait..." 
                          : analysisComplete 
                            ? "Ask a question about your analyzed content..." 
                            : "Start AI analysis to enable questions..."
                      }
                      className="input flex-1"
                      disabled={isLoading || isAnalyzing || !analysisComplete}
                    />
                    <button
                      onClick={handleAskQuestion}
                      disabled={isLoading || isAnalyzing || !question.trim() || !analysisComplete}
                      className="btn-primary"
                    >
                      <Send className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Start Analysis Button */}
                  {!analysisComplete && !isAnalyzing && (
                    <div className="mt-4">
                      {sessionContent.trim() ? (
                        <button
                          onClick={startAIAnalysis}
                          className="btn-primary w-full flex items-center justify-center space-x-2"
                        >
                          <Brain className="h-4 w-4" />
                          <span>Start AI Analysis</span>
                        </button>
                      ) : (
                        <div className="text-center p-4 bg-brand-cream rounded-lg border border-brand-sand">
                          <p className="text-sm text-brand-slate mb-2">
                            No content available for analysis.
                          </p>
                          {!isCapturing ? (
                            <div>
                              <p className="text-sm text-brand-slate mb-2">
                                Click "Start Session" in the top bar to begin capturing content.
                              </p>
                              <p className="text-xs text-brand-slate opacity-80">
                                Once started, content will be automatically captured every {config.autoProcessInterval} seconds, or you can manually click "Capture Frame".
                              </p>
                            </div>
                          ) : (
                            <div>
                              <p className="text-sm text-brand-slate mb-2">
                                Session is active but no content captured yet.
                              </p>
                              <p className="text-xs text-brand-slate opacity-80">
                                Content will be automatically captured every {config.autoProcessInterval} seconds, or click "Capture Frame" to process immediately.
                              </p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Other AI Tools */}
              {activeTab !== 'chat' && (
                <div>
                  <div className="mb-4">
                    <textarea
                      value={sessionContent}
                      onChange={(e) => setSessionContent(e.target.value)}
                      placeholder={
                        activeTab === 'summary' ? 'Content will be automatically captured and summarized...' :
                        activeTab === 'flashcards' ? 'Content will be automatically captured for flashcards...' :
                        activeTab === 'quiz' ? 'Content will be automatically captured for quiz questions...' :
                        activeTab === 'concepts' ? 'Key concepts will be automatically extracted...' :
                        activeTab === 'plan' ? 'Enter topics for study plan (one per line)...' :
                        'Content will be automatically captured...'
                      }
                      className="textarea w-full h-32"
                      disabled={isLoading}
                    />
                  </div>

                  <div className="flex justify-between items-center">
                    <button
                      onClick={
                        activeTab === 'summary' ? handleGenerateSummary :
                        activeTab === 'flashcards' ? handleGenerateFlashcards :
                        activeTab === 'quiz' ? handleGenerateQuiz :
                        () => {}
                      }
                      disabled={isLoading || !sessionContent.trim()}
                      className="btn-primary"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Zap className="h-4 w-4 mr-2" />
                          Generate
                        </>
                      )}
                    </button>

                    {sessionContent && (
                      <button
                        onClick={() => {
                          const blob = new Blob([sessionContent], { type: 'text/plain' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `${activeTab}-${Date.now()}.txt`;
                          document.body.appendChild(a);
                          a.click();
                          document.body.removeChild(a);
                          URL.revokeObjectURL(url);
                        }}
                        className="btn-outline"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </button>
                    )}
                  </div>

                  {/* Generated Content Display */}
                  {sessionContent && (
                    <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Generated Content:</h3>
                      <div className="prose prose-sm max-w-none">
                        <pre className="whitespace-pre-wrap text-sm text-gray-900">{sessionContent}</pre>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeStudy;
