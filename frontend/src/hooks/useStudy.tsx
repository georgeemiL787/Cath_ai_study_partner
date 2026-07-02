import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface StudyStats {
  totalSessions: number;
  totalDocuments: number;
  totalQuestions: number;
  totalFlashcards: number;
  totalQuizzes: number;
}

interface StudyContextType {
  studyStats: StudyStats | null;
  askQuestion: (question: string, sessionId?: string) => Promise<any>;
  generateSummary: (content: string, maxLength?: number) => Promise<any>;
  generateFlashcards: (content: string, numCards?: number) => Promise<any>;
  generateQuiz: (content: string, numQuestions?: number) => Promise<any>;
  extractKeyConcepts: (content: string, maxConcepts?: number) => Promise<any>;
  createStudyPlan: (topics: string[], timeAvailable?: string) => Promise<any>;
  parseFlashcards: (content: string) => Promise<any>;
  parseQuiz: (content: string) => Promise<any>;
  getSessionDocuments: (sessionId: string) => Promise<any>;
  exportSession: (sessionId: string, format?: string) => Promise<any>;
  refreshStats: () => Promise<void>;
}

const StudyContext = createContext<StudyContextType | undefined>(undefined);

export const useStudy = () => {
  const context = useContext(StudyContext);
  if (context === undefined) {
    throw new Error('useStudy must be used within a StudyProvider');
  }
  return context;
};

interface StudyProviderProps {
  children: ReactNode;
}

export const StudyProvider: React.FC<StudyProviderProps> = ({ children }) => {
  const [studyStats, setStudyStats] = useState<StudyStats | null>(null);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const askQuestion = async (question: string, sessionId?: string) => {
    try {
      const response = await axios.post(`${API_BASE}/api/ai/question`, {
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

  const generateSummary = async (content: string, maxLength: number = 200) => {
    try {
      const response = await axios.post(`${API_BASE}/api/ai/summarize`, {
        content,
        max_length: maxLength
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate summary:', error);
      throw error;
    }
  };

  const generateFlashcards = async (content: string, numCards: number = 5) => {
    try {
      const response = await axios.post(`${API_BASE}/api/ai/flashcards`, {
        content,
        num_cards: numCards
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate flashcards:', error);
      throw error;
    }
  };

  const generateQuiz = async (content: string, numQuestions: number = 5) => {
    try {
      const response = await axios.post(`${API_BASE}/api/ai/quiz`, {
        content,
        num_questions: numQuestions,
        question_types: ['multiple_choice', 'short_answer']
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate quiz:', error);
      throw error;
    }
  };

  const extractKeyConcepts = async (content: string, maxConcepts: number = 10) => {
    try {
      const response = await axios.post(`${API_BASE}/api/ai/key-concepts`, {
        content,
        max_length: maxConcepts
      });
      return response.data;
    } catch (error) {
      console.error('Failed to extract key concepts:', error);
      throw error;
    }
  };

  const createStudyPlan = async (topics: string[], timeAvailable: string = '1 week') => {
    try {
      const response = await axios.post(`${API_BASE}/api/ai/study-plan`, {
        topics,
        time_available: timeAvailable
      });
      return response.data;
    } catch (error) {
      console.error('Failed to create study plan:', error);
      throw error;
    }
  };

  const parseFlashcards = async (content: string) => {
    try {
      const response = await axios.post(`${API_BASE}/api/ai/parse/flashcards`, content, {
        headers: {
          'Content-Type': 'text/plain'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to parse flashcards:', error);
      throw error;
    }
  };

  const parseQuiz = async (content: string) => {
    try {
      const response = await axios.post(`${API_BASE}/api/ai/parse/quiz`, content, {
        headers: {
          'Content-Type': 'text/plain'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to parse quiz:', error);
      throw error;
    }
  };

  const getSessionDocuments = async (sessionId: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/database/sessions/${sessionId}/documents`);
      return response.data;
    } catch (error) {
      console.error('Failed to get session documents:', error);
      throw error;
    }
  };

  const exportSession = async (sessionId: string, format: string = 'json') => {
    try {
      const response = await axios.post(`${API_BASE}/api/database/export/session/${sessionId}?format=${format}`);
      return response.data;
    } catch (error) {
      console.error('Failed to export session:', error);
      throw error;
    }
  };

  const refreshStats = async () => {
    try {
      const [dbStats, sessionsResponse] = await Promise.all([
        axios.get(`${API_BASE}/api/database/stats`),
        axios.get(`${API_BASE}/api/database/sessions`)
      ]);

      const dbData = dbStats.data.data;
      const sessionsData = sessionsResponse.data.data;

      setStudyStats({
        totalSessions: sessionsData.total_sessions || 0,
        totalDocuments: dbData.total_documents || 0,
        totalQuestions: 0, // This would need to be tracked separately
        totalFlashcards: 0, // This would need to be tracked separately
        totalQuizzes: 0 // This would need to be tracked separately
      });
    } catch (error) {
      console.error('Failed to refresh study stats:', error);
    }
  };

  // Initial stats load
  useEffect(() => {
    refreshStats();
  }, [refreshStats]);

  const value: StudyContextType = {
    studyStats,
    askQuestion,
    generateSummary,
    generateFlashcards,
    generateQuiz,
    extractKeyConcepts,
    createStudyPlan,
    parseFlashcards,
    parseQuiz,
    getSessionDocuments,
    exportSession,
    refreshStats
  };

  return (
    <StudyContext.Provider value={value}>
      {children}
    </StudyContext.Provider>
  );
};

