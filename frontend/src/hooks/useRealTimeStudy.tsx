import React, { createContext, useContext, useState, ReactNode } from 'react';
import axios from 'axios';

interface StudySession {
  session_id: string;
  is_active: boolean;
  stats: {
    session_id: string;
    is_active: boolean;
    duration: number;
    total_content_items: number;
    ocr_items: number;
    speech_items: number;
    manual_items: number;
    key_points_count: number;
    questions_count: number;
  };
  key_points: string[];
  recent_content: Array<{
    id: string;
    content: string;
    type: string;
    timestamp: number;
    confidence: number;
  }>;
}

interface RealTimeStudyContextType {
  currentSession: StudySession | null;
  isSessionActive: boolean;
  startStudySession: (config: {
    auto_ai_processing?: boolean;
    processing_interval?: number;
    screen_region?: { x: number; y: number; width: number; height: number };
    fps?: number;
    audio_enabled?: boolean;
  }) => Promise<string>;
  stopStudySession: (sessionId: string) => Promise<void>;
  addContent: (sessionId: string, content: string, contentType?: string) => Promise<void>;
  askQuestion: (sessionId: string, question: string) => Promise<any>;
  getSessionSummary: (sessionId: string) => Promise<string>;
  getKeyPoints: (sessionId: string) => Promise<string[]>;
  processFrame: (sessionId: string, frameData: string) => Promise<void>;
  exportSession: (sessionId: string, format?: string) => Promise<any>;
  refreshSessionStatus: (sessionId: string) => Promise<void>;
}

const RealTimeStudyContext = createContext<RealTimeStudyContextType | undefined>(undefined);

export const useRealTimeStudy = () => {
  const context = useContext(RealTimeStudyContext);
  if (context === undefined) {
    throw new Error('useRealTimeStudy must be used within a RealTimeStudyProvider');
  }
  return context;
};

interface RealTimeStudyProviderProps {
  children: ReactNode;
}

export const RealTimeStudyProvider: React.FC<RealTimeStudyProviderProps> = ({ children }) => {
  const [currentSession, setCurrentSession] = useState<StudySession | null>(null);
  const [isSessionActive, setIsSessionActive] = useState(false);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const startStudySession = async (config: {
    auto_ai_processing?: boolean;
    processing_interval?: number;
    screen_region?: { x: number; y: number; width: number; height: number };
    fps?: number;
    audio_enabled?: boolean;
  }) => {
    try {
      const response = await axios.post(`${API_BASE}/api/realtime-study/start`, {
        auto_ai_processing: config.auto_ai_processing !== false,
        processing_interval: config.processing_interval || 30,
        screen_region: config.screen_region,
        fps: config.fps || 2,
        audio_enabled: config.audio_enabled !== false
      });

      setCurrentSession(response.data);
      setIsSessionActive(true);
      
      return response.data.session_id;
    } catch (error) {
      console.error('Failed to start study session:', error);
      throw error;
    }
  };

  const stopStudySession = async (sessionId: string) => {
    try {
      await axios.post(`${API_BASE}/api/realtime-study/stop`, {
        session_id: sessionId
      });

      setCurrentSession(null);
      setIsSessionActive(false);
    } catch (error) {
      console.error('Failed to stop study session:', error);
      throw error;
    }
  };

  const addContent = async (sessionId: string, content: string, contentType: string = 'manual') => {
    try {
      await axios.post(`${API_BASE}/api/realtime-study/${sessionId}/content`, {
        content,
        content_type: contentType
      });
    } catch (error) {
      console.error('Failed to add content:', error);
      throw error;
    }
  };

  const askQuestion = async (sessionId: string, question: string) => {
    try {
      const response = await axios.post(`${API_BASE}/api/realtime-study/${sessionId}/question`, {
        question,
        session_id: sessionId,
        include_citations: true,
        top_k: 5
      });
      return response.data;
    } catch (error) {
      console.error('Failed to ask question:', error);
      throw error;
    }
  };

  const getSessionSummary = async (sessionId: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/realtime-study/${sessionId}/summary`);
      return response.data.summary;
    } catch (error) {
      console.error('Failed to get session summary:', error);
      throw error;
    }
  };

  const getKeyPoints = async (sessionId: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/realtime-study/${sessionId}/key-points`);
      return response.data.key_points;
    } catch (error) {
      console.error('Failed to get key points:', error);
      throw error;
    }
  };

  const processFrame = async (sessionId: string, frameData: string) => {
    try {
      await axios.post(`${API_BASE}/api/realtime-study/${sessionId}/process-frame`, frameData, {
        headers: {
          'Content-Type': 'text/plain'
        }
      });
    } catch (error) {
      console.error('Failed to process frame:', error);
      throw error;
    }
  };

  const exportSession = async (sessionId: string, format: string = 'json') => {
    try {
      const response = await axios.get(`${API_BASE}/api/realtime-study/${sessionId}/export?format=${format}`);
      return response.data;
    } catch (error) {
      console.error('Failed to export session:', error);
      throw error;
    }
  };

  const refreshSessionStatus = async (sessionId: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/realtime-study/${sessionId}/status`);
      setCurrentSession(response.data);
      setIsSessionActive(response.data.is_active);
    } catch (error) {
      console.error('Failed to refresh session status:', error);
    }
  };

  const value: RealTimeStudyContextType = {
    currentSession,
    isSessionActive,
    startStudySession,
    stopStudySession,
    addContent,
    askQuestion,
    getSessionSummary,
    getKeyPoints,
    processFrame,
    exportSession,
    refreshSessionStatus
  };

  return (
    <RealTimeStudyContext.Provider value={value}>
      {children}
    </RealTimeStudyContext.Provider>
  );
};
