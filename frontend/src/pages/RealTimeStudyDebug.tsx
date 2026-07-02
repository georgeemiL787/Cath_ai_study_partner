import React, { useState, useEffect, useCallback } from 'react';
import { 
  Play, 
  Square, 
  Camera, 
  Mic, 
  MicOff,
  Monitor, 
  Volume2, 
  VolumeX, 
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
  EyeOff,
  Settings,
  Maximize2,
  Minimize2,
  Clock,
  Activity,
  Bug,
  AlertTriangle
} from 'lucide-react';
import { useStudy } from '../hooks/useStudy';
import { useCapture } from '../hooks/useCapture';
import { useRealTimeStudy } from '../hooks/useRealTimeStudy';
import toast from 'react-hot-toast';

const RealTimeStudyDebug: React.FC = () => {
  const { 
    askQuestion, 
    generateSummary, 
    generateFlashcards, 
    generateQuiz,
    extractKeyConcepts,
    createStudyPlan
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
    isSessionActive,
    startStudySession: startRealtimeSession,
    stopStudySession: stopRealtimeSession,
    addContent,
    askQuestion: askRealtimeQuestion,
    getSessionSummary,
    getKeyPoints,
    processFrame,
    exportSession: exportRealtimeSession,
    refreshSessionStatus
  } = useRealTimeStudy();

  // Debug state
  const [debugInfo, setDebugInfo] = useState<any>({});
  const [currentFrame, setCurrentFrame] = useState<string>('');
  const [frameError, setFrameError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Update debug info
  const updateDebugInfo = useCallback(() => {
    setDebugInfo({
      isCapturing,
      sessionId,
      captureStats,
      realtimeSession,
      isSessionActive,
      currentFrame: currentFrame ? `${currentFrame.length} chars` : 'none',
      timestamp: new Date().toISOString()
    });
  }, [isCapturing, sessionId, captureStats, realtimeSession, isSessionActive, currentFrame]);

  useEffect(() => {
    updateDebugInfo();
  }, [updateDebugInfo]);

  // Test frame capture
  const testFrameCapture = async () => {
    setIsLoading(true);
    setFrameError('');
    
    try {
      console.log('Testing frame capture...');
      const frame = await getCurrentFrame();
      console.log('Frame received:', frame ? `${frame.length} chars` : 'null');
      
      if (frame) {
        setCurrentFrame(frame);
        toast.success('Frame captured successfully!');
      } else {
        setFrameError('No frame data received');
        toast.error('No frame data received');
      }
    } catch (error) {
      console.error('Frame capture error:', error);
      setFrameError(error instanceof Error ? error.message : 'Unknown error');
      toast.error('Frame capture failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Test start capture
  const testStartCapture = async () => {
    setIsLoading(true);
    try {
      console.log('Starting capture...');
      const newSessionId = await startCapture({
        fps: 1,
        audio_enabled: false,
        screen_region: undefined
      });
      console.log('Capture started with session:', newSessionId);
      toast.success('Capture started!');
    } catch (error) {
      console.error('Start capture error:', error);
      toast.error('Failed to start capture');
    } finally {
      setIsLoading(false);
    }
  };

  // Test stop capture
  const testStopCapture = async () => {
    setIsLoading(true);
    try {
      console.log('Stopping capture...');
      await stopCapture();
      console.log('Capture stopped');
      toast.success('Capture stopped!');
    } catch (error) {
      console.error('Stop capture error:', error);
      toast.error('Failed to stop capture');
    } finally {
      setIsLoading(false);
    }
  };

  // Test API status
  const testApiStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/status');
      const data = await response.json();
      console.log('API Status:', data);
      toast.success('API status retrieved');
    } catch (error) {
      console.error('API status error:', error);
      toast.error('Failed to get API status');
    }
  };

  return (
    <div className="min-h-screen bg-brand-cream p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white shadow-sm border-b rounded-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Bug className="h-8 w-8 text-brand-teal" />
              <div>
                <h1 className="text-2xl font-bold text-brand-slate">Real-Time Study Debug</h1>
                <p className="text-brand-slate opacity-80">Debug screen capture and AI integration</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isCapturing ? 'bg-brand-teal animate-pulse' : 'bg-gray-400'}`}></div>
              <span className="text-sm text-brand-slate opacity-80">
                {isCapturing ? 'Recording' : 'Idle'}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Debug Information */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Bug className="h-5 w-5 mr-2 text-brand-teal" />
                Debug Information
              </h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Is Capturing:</span>
                  <span className={`font-medium ${isCapturing ? 'text-green-600' : 'text-gray-500'}`}>
                    {isCapturing ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Session ID:</span>
                  <span className="font-mono text-xs text-gray-900">
                    {sessionId || 'None'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Real-time Session:</span>
                  <span className={`font-medium ${realtimeSession ? 'text-green-600' : 'text-gray-500'}`}>
                    {realtimeSession ? 'Active' : 'None'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Current Frame:</span>
                  <span className="font-medium">
                    {currentFrame ? `${currentFrame.length} chars` : 'None'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Frame Error:</span>
                  <span className={`font-medium ${frameError ? 'text-red-600' : 'text-gray-500'}`}>
                    {frameError || 'None'}
                  </span>
                </div>
              </div>
            </div>

            {/* Capture Statistics */}
            {captureStats && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Activity className="h-5 w-5 mr-2 text-brand-teal" />
                  Capture Statistics
                </h2>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Screen Status:</span>
                    <span className="font-medium">
                      {captureStats.screen_stats?.status || 'unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Frame Count:</span>
                    <span className="font-medium">
                      {captureStats.screen_stats?.frame_count || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Target FPS:</span>
                    <span className="font-medium">
                      {captureStats.screen_stats?.target_fps || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Actual FPS:</span>
                    <span className="font-medium">
                      {(captureStats.screen_stats?.actual_fps || 0).toFixed(1)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Audio Status:</span>
                    <span className="font-medium">
                      {captureStats.audio_stats?.status || 'unknown'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Raw Debug Data */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2 text-brand-teal" />
                Raw Debug Data
              </h2>
              <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto max-h-64">
                {JSON.stringify(debugInfo, null, 2)}
              </pre>
            </div>
          </div>

          {/* Test Controls */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Settings className="h-5 w-5 mr-2 text-brand-teal" />
                Test Controls
              </h2>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={testStartCapture}
                    disabled={isLoading || isCapturing}
                    className="btn-primary flex items-center justify-center space-x-2"
                  >
                    <Play className="h-4 w-4" />
                    <span>Start Capture</span>
                  </button>
                  
                  <button
                    onClick={testStopCapture}
                    disabled={isLoading || !isCapturing}
                    className="btn-secondary flex items-center justify-center space-x-2"
                  >
                    <Square className="h-4 w-4" />
                    <span>Stop Capture</span>
                  </button>
                </div>
                
                <button
                  onClick={testFrameCapture}
                  disabled={isLoading || !isCapturing}
                  className="btn-outline w-full flex items-center justify-center space-x-2"
                >
                  <Camera className="h-4 w-4" />
                  <span>Test Frame Capture</span>
                </button>
                
                <button
                  onClick={testApiStatus}
                  className="btn-outline w-full flex items-center justify-center space-x-2"
                >
                  <Activity className="h-4 w-4" />
                  <span>Test API Status</span>
                </button>
              </div>
            </div>

            {/* Live Preview */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Monitor className="h-5 w-5 mr-2 text-brand-teal" />
                Live Preview
              </h2>
              <div className="bg-brand-sand rounded-lg p-4 min-h-[300px] flex items-center justify-center">
                {currentFrame ? (
                  <img
                    src={`data:image/jpeg;base64,${currentFrame}`}
                    alt="Captured frame"
                    className="max-w-full max-h-full rounded-lg shadow-lg"
                  />
                ) : (
                  <div className="text-center text-brand-slate opacity-70">
                    <Camera className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No frame available</p>
                    {frameError && (
                      <p className="text-red-600 text-sm mt-2">{frameError}</p>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Console Log */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <MessageCircle className="h-5 w-5 mr-2 text-brand-teal" />
                Console Log
              </h2>
              <div className="bg-black text-green-400 p-3 rounded text-xs font-mono h-32 overflow-auto">
                <div>Open browser console (F12) to see detailed logs</div>
                <div>Check Network tab for API requests</div>
                <div>Look for any error messages</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeStudyDebug;
