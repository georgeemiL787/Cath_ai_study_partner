import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';
import axios from 'axios';

interface CaptureStats {
  screen_stats: {
    status: string;
    frame_count: number;
    elapsed_time: number;
    target_fps: number;
    actual_fps: number;
    region?: [number, number, number, number];
  };
  audio_stats: {
    status: string;
    elapsed_time: number;
    total_samples: number;
    speech_samples: number;
    speech_ratio: number;
    speech_segments: number;
    in_speech: boolean;
    sample_rate: number;
  };
}

interface CaptureContextType {
  isCapturing: boolean;
  sessionId: string | null;
  captureStats: CaptureStats | null;
  startCapture: (config: {
    fps?: number;
    audio_enabled?: boolean;
    session_id?: string;
    screen_region?: { x: number; y: number; width: number; height: number };
    monitor_index?: number;
  }) => Promise<string>;
  stopCapture: () => Promise<void>;
  getCurrentFrame: () => Promise<string>;
  getAudioSegments: () => Promise<any>;
  clearAudioSegments: () => Promise<void>;
  setScreenRegion: (region: { x: number; y: number; width: number; height: number }) => Promise<void>;
  refreshStats: () => Promise<void>;
  listMonitors: () => Promise<Array<{ index: number; left: number; top: number; width: number; height: number }>>;
  getExtractedContent: () => Promise<{ content: string[]; key_points?: string[] } | null>;
}

const CaptureContext = createContext<CaptureContextType | undefined>(undefined);

export const useCapture = () => {
  const context = useContext(CaptureContext);
  if (context === undefined) {
    throw new Error('useCapture must be used within a CaptureProvider');
  }
  return context;
};

interface CaptureProviderProps {
  children: ReactNode;
}

export const CaptureProvider: React.FC<CaptureProviderProps> = ({ children }) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [captureStats, setCaptureStats] = useState<CaptureStats | null>(null);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const startCapture = useCallback(async (config: {
    fps?: number;
    audio_enabled?: boolean;
    session_id?: string;
    screen_region?: { x: number; y: number; width: number; height: number };
    monitor_index?: number;
  }) => {
    try {
      const response = await axios.post(`${API_BASE}/api/capture/start`, {
        fps: config.fps || 1,
        audio_enabled: config.audio_enabled !== false,
        session_id: config.session_id,
        screen_region: config.screen_region,
        monitor_index: config.monitor_index
      });

      setIsCapturing(true);
      setSessionId(response.data.session_id);
      
      // Start polling for stats
      startStatsPolling();
      
      return response.data.session_id;
    } catch (error) {
      console.error('Failed to start capture:', error);
      throw error;
    }
  }, [API_BASE]);

  const stopCapture = useCallback(async () => {
    try {
      await axios.post(`${API_BASE}/api/capture/stop`, {
        session_id: sessionId
      });

      setIsCapturing(false);
      setSessionId(null);
      setCaptureStats(null);
      
      // Stop polling
      stopStatsPolling();
    } catch (error) {
      console.error('Failed to stop capture:', error);
      throw error;
    }
  }, [API_BASE, sessionId, /* stable */]);

  const getCurrentFrame = useCallback(async (): Promise<string> => {
    try {
      const response = await axios.get(`${API_BASE}/api/capture/frame`);
      return response.data.frame;
    } catch (error) {
      console.error('Failed to get current frame:', error);
      throw error;
    }
  }, [API_BASE]);

  const getAudioSegments = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/capture/audio/segments`);
      return response.data;
    } catch (error) {
      console.error('Failed to get audio segments:', error);
      throw error;
    }
  }, [API_BASE]);

  const clearAudioSegments = useCallback(async () => {
    try {
      await axios.post(`${API_BASE}/api/capture/audio/clear`);
    } catch (error) {
      console.error('Failed to clear audio segments:', error);
      throw error;
    }
  }, [API_BASE]);

  const setScreenRegion = useCallback(async (region: { x: number; y: number; width: number; height: number }) => {
    try {
      await axios.post(`${API_BASE}/api/capture/screen/region`, region);
    } catch (error) {
      console.error('Failed to set screen region:', error);
      throw error;
    }
  }, [API_BASE]);

  const refreshStats = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/capture/status`);
      setCaptureStats(response.data);
      setIsCapturing(response.data.is_capturing);
      if (response.data.session_id) {
        setSessionId(response.data.session_id);
      }
    } catch (error) {
      console.error('Failed to refresh stats:', error);
    }
  }, [API_BASE]);

  const listMonitors = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/capture/monitors`);
      return response.data.monitors as Array<{ index: number; left: number; top: number; width: number; height: number }>;
    } catch (error) {
      console.error('Failed to list monitors:', error);
      throw error;
    }
  }, [API_BASE]);

  const getExtractedContent = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/capture/extracted-content`);
      const data = response.data || {};
      const items = Array.isArray(data.content) ? data.content : [];
      return { content: items, key_points: data.key_points };
    } catch (error) {
      console.error('Failed to get extracted content:', error);
      return null;
    }
  }, [API_BASE]);

  // Polling for stats with stable ref
  const statsIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const startStatsPolling = useCallback(() => {
    if (statsIntervalRef.current) return;
    statsIntervalRef.current = setInterval(async () => {
      if (isCapturing) {
        await refreshStats();
      }
    }, 1000);
  }, [isCapturing, refreshStats]);

  const stopStatsPolling = useCallback(() => {
    if (statsIntervalRef.current) {
      clearInterval(statsIntervalRef.current);
      statsIntervalRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopStatsPolling();
    };
  }, [stopStatsPolling]);

  // Initial stats load
  useEffect(() => {
    refreshStats();
  }, [refreshStats]);

  const value: CaptureContextType = {
    isCapturing,
    sessionId,
    captureStats,
    startCapture,
    stopCapture,
    getCurrentFrame,
    getAudioSegments,
    clearAudioSegments,
    setScreenRegion,
    refreshStats,
    listMonitors,
    getExtractedContent
  };

  return (
    <CaptureContext.Provider value={value}>
      {children}
    </CaptureContext.Provider>
  );
};

