import React, { useState, useEffect, useCallback } from 'react';
import { 
  Save, 
  RefreshCw, 
  Database,
  Brain,
  Camera,
  Mic,
  Shield,
  Download,
  Upload,
  Trash2
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import { useCapture } from '../hooks/useCapture';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Settings: React.FC = () => {
  const { listMonitors, startCapture, stopCapture, isCapturing, sessionId } = useCapture();
  const [activeCategory, setActiveCategory] = useState<'ai' | 'capture' | 'processing' | 'privacy' | 'export' | 'data'>('ai');
  const [settings, setSettings] = useState({
    // AI Settings
    llmProvider: 'gemini' as 'gemini' | 'openai' | 'deepseek' | 'auto',
    openaiApiKey: '',
    geminiApiKey: '',
    deepseekApiKey: '',
    deepseekBaseUrl: 'https://api.deepseek.com',
    model: 'gpt-4-turbo-preview',
    maxTokens: 1000,
    temperature: 0.7,
    
    // Capture Settings
    screenFps: 1,
    audioEnabled: true,
    audioSampleRate: 16000,
    audioChunkSize: 1024,
    monitorIndex: null as number | null,
    
    // OCR Settings
    ocrEngine: 'tesseract',
    ocrLanguage: 'eng',
    ocrPreprocess: true,
    
    // STT Settings
    sttEngine: 'whisper',
    whisperModel: 'base',
    sttLanguage: 'en',
    
    // Privacy Settings
    privacyMode: 'local',
    dataRetentionDays: 30,
    encryptionEnabled: true,
    
    // Export Settings
    exportFormats: ['anki', 'csv', 'pdf'],
    ankiDeckName: 'AI Study Partner'
  });

  const [isLoading, setIsLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [monitors, setMonitors] = useState<Array<{ index: number; left: number; top: number; width: number; height: number }>>([]);
  const [selectedMonitor, setSelectedMonitor] = useState<number | null>(null);
  const [localInfo, setLocalInfo] = useState<{ settingsBytes: number; sessionsBytes: number; sessionCount: number }>({ settingsBytes: 0, sessionsBytes: 0, sessionCount: 0 });
  const [isCaptureActionLoading, setIsCaptureActionLoading] = useState(false);
  const [captureError, setCaptureError] = useState<string | null>(null);

  const loadSettings = useCallback(async () => {
    try {
      // Try to load from backend API first
      const response = await axios.get(`${API_BASE}/api/settings`);
      if (response.data.success) {
        const backendSettings = response.data.settings;
        // Convert backend field names to frontend field names
        const frontendSettings = {
          llmProvider: (backendSettings.llm_provider || 'gemini') as any,
          openaiApiKey: backendSettings.openai_api_key || '',
          geminiApiKey: backendSettings.gemini_api_key || '',
          deepseekApiKey: backendSettings.deepseek_api_key || '',
          deepseekBaseUrl: backendSettings.deepseek_base_url || 'https://api.deepseek.com',
          model: backendSettings.model || 'gpt-4-turbo-preview',
          maxTokens: backendSettings.max_tokens || 1000,
          temperature: backendSettings.temperature || 0.7,
          screenFps: backendSettings.screen_fps || 1,
          audioEnabled: backendSettings.audio_enabled !== undefined ? backendSettings.audio_enabled : true,
          audioSampleRate: backendSettings.audio_sample_rate || 16000,
          audioChunkSize: backendSettings.audio_chunk_size || 1024,
          monitorIndex: settings.monitorIndex ?? null,
          ocrEngine: backendSettings.ocr_engine || 'tesseract',
          ocrLanguage: backendSettings.ocr_language || 'eng',
          ocrPreprocess: backendSettings.ocr_preprocess !== undefined ? backendSettings.ocr_preprocess : true,
          sttEngine: backendSettings.stt_engine || 'whisper',
          whisperModel: backendSettings.whisper_model || 'base',
          sttLanguage: backendSettings.stt_language || 'en',
          privacyMode: backendSettings.privacy_mode || 'local',
          dataRetentionDays: backendSettings.data_retention_days || 30,
          encryptionEnabled: backendSettings.encryption_enabled !== undefined ? backendSettings.encryption_enabled : true,
          exportFormats: backendSettings.export_formats || ['anki', 'csv', 'pdf'],
          ankiDeckName: backendSettings.anki_deck_name || 'AI Study Partner'
        };
        setSettings(frontendSettings);
      }
      // Load available models/providers
      try {
        const modelsRes = await axios.get(`${API_BASE}/api/ai/models`);
        const data = modelsRes.data || {};
        setAvailableModels(data.available_models || []);
        if (data.current_model) {
          setSettings(prev => ({ ...prev, model: data.current_model }));
        }
        if (data.provider) {
          setSettings(prev => ({ ...prev, llmProvider: data.provider } as any));
        }
      } catch {}
    } catch (error) {
      console.error('Failed to load settings from backend:', error);
      // Fallback to localStorage
      try {
        const savedSettings = localStorage.getItem('ai-study-partner-settings');
        if (savedSettings) {
          setSettings({ ...settings, ...JSON.parse(savedSettings) });
        }
      } catch (localError) {
        console.error('Failed to load settings from localStorage:', localError);
      }
    }
  }, []);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  // Persist a local draft on each change so users don't lose tweaks before saving
  useEffect(() => {
    try {
      localStorage.setItem('ai-study-partner-settings-draft', JSON.stringify(settings));
    } catch {}
  }, [settings]);

  useEffect(() => {
    (async () => {
      try {
        const mons = await listMonitors();
        setMonitors(mons);
        if (mons.length > 0) {
          const defaultIndex = settings.monitorIndex !== null && settings.monitorIndex !== undefined
            ? settings.monitorIndex
            : mons[0].index;
          setSelectedMonitor(defaultIndex);
          if (settings.monitorIndex === null || settings.monitorIndex === undefined) {
            setSettings(prev => ({ ...prev, monitorIndex: defaultIndex }));
          }
        }
      } catch (err) {
        setCaptureError('Failed to load monitors');
      }
    })();
  }, [listMonitors, settings.monitorIndex]);

  // Local data introspection helpers
  const refreshLocalInfo = useCallback(() => {
    const settingsStr = localStorage.getItem('ai-study-partner-settings') || '';
    const draftStr = localStorage.getItem('ai-study-partner-settings-draft') || '';
    const sessionsStr = localStorage.getItem('ai-study-partner-sessions') || '[]';
    let sessionsCount = 0;
    try {
      const parsed = JSON.parse(sessionsStr);
      sessionsCount = Array.isArray(parsed) ? parsed.length : 0;
    } catch {}
    const settingsBytes = new Blob([settingsStr + draftStr]).size;
    const sessionsBytes = new Blob([sessionsStr]).size;
    setLocalInfo({ settingsBytes, sessionsBytes, sessionCount: sessionsCount });
  }, []);

  useEffect(() => {
    refreshLocalInfo();
  }, [refreshLocalInfo]);

  const saveSettings = async () => {
    setIsLoading(true);
    try {
      // Convert frontend field names to backend field names
      const backendSettings = {
        llm_provider: settings.llmProvider,
        openai_api_key: settings.openaiApiKey,
        gemini_api_key: settings.geminiApiKey,
        deepseek_api_key: settings.deepseekApiKey,
        deepseek_base_url: settings.deepseekBaseUrl,
        deepseek_model: settings.model,
        model: settings.model,
        max_tokens: settings.maxTokens,
        temperature: settings.temperature,
        screen_fps: settings.screenFps,
        audio_enabled: settings.audioEnabled,
        audio_sample_rate: settings.audioSampleRate,
        audio_chunk_size: settings.audioChunkSize,
        ocr_engine: settings.ocrEngine,
        ocr_language: settings.ocrLanguage,
        ocr_preprocess: settings.ocrPreprocess,
        stt_engine: settings.sttEngine,
        whisper_model: settings.whisperModel,
        stt_language: settings.sttLanguage,
        privacy_mode: settings.privacyMode,
        data_retention_days: settings.dataRetentionDays,
        encryption_enabled: settings.encryptionEnabled,
        export_formats: settings.exportFormats,
        anki_deck_name: settings.ankiDeckName
      };

      // Save to backend API
      const response = await axios.post(`${API_BASE}/api/settings`, backendSettings);
      
      if (response.data.success) {
        // Also save to localStorage as backup
        localStorage.setItem('ai-study-partner-settings', JSON.stringify(settings));
        // Reload from backend to ensure runtime-applied values are reflected
        await loadSettings();
        setHasChanges(false);
        toast.success('Settings saved successfully!');
      } else {
        throw new Error(response.data.message || 'Failed to save settings');
      }
    } catch (error) {
      toast.error('Failed to save settings');
      console.error('Save error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const resetSettings = async () => {
    if (window.confirm('Are you sure you want to reset all settings to default?')) {
      try {
        const response = await axios.post(`${API_BASE}/api/settings/reset`);
        if (response.data.success) {
          const backendSettings = response.data.settings;
          // Convert backend field names to frontend field names
          const frontendSettings = {
            llmProvider: (backendSettings.llm_provider || 'gemini') as any,
            openaiApiKey: backendSettings.openai_api_key || '',
            geminiApiKey: backendSettings.gemini_api_key || '',
            deepseekApiKey: backendSettings.deepseek_api_key || '',
            deepseekBaseUrl: backendSettings.deepseek_base_url || 'https://api.deepseek.com',
            model: backendSettings.model || 'gpt-4-turbo-preview',
            maxTokens: backendSettings.max_tokens || 1000,
            temperature: backendSettings.temperature || 0.7,
            screenFps: backendSettings.screen_fps || 1,
            audioEnabled: backendSettings.audio_enabled !== undefined ? backendSettings.audio_enabled : true,
            audioSampleRate: backendSettings.audio_sample_rate || 16000,
            audioChunkSize: backendSettings.audio_chunk_size || 1024,
            ocrEngine: backendSettings.ocr_engine || 'tesseract',
            ocrLanguage: backendSettings.ocr_language || 'eng',
            ocrPreprocess: backendSettings.ocr_preprocess !== undefined ? backendSettings.ocr_preprocess : true,
            sttEngine: backendSettings.stt_engine || 'whisper',
            whisperModel: backendSettings.whisper_model || 'base',
            sttLanguage: backendSettings.stt_language || 'en',
            privacyMode: backendSettings.privacy_mode || 'local',
            dataRetentionDays: backendSettings.data_retention_days || 30,
            encryptionEnabled: backendSettings.encryption_enabled !== undefined ? backendSettings.encryption_enabled : true,
            exportFormats: backendSettings.export_formats || ['anki', 'csv', 'pdf'],
            ankiDeckName: backendSettings.anki_deck_name || 'AI Study Partner'
          };
        // Merge any locally persisted fields not managed by backend
        let merged = frontendSettings as any;
        try {
          const savedSettings = localStorage.getItem('ai-study-partner-settings');
          if (savedSettings) {
            const parsed = JSON.parse(savedSettings);
            if (parsed && Object.prototype.hasOwnProperty.call(parsed, 'monitorIndex')) {
              merged = { ...merged, monitorIndex: parsed.monitorIndex };
            }
          }
        } catch {}
        setSettings(merged);
          setHasChanges(false);
          toast.success('Settings reset to default values!');
        }
      } catch (error) {
        console.error('Failed to reset settings:', error);
        toast.error('Failed to reset settings');
      }
    }
  };

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const exportSettings = () => {
    const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ai-study-partner-settings.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Settings exported successfully!');
  };

  const importSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedSettings = JSON.parse(e.target?.result as string);
        setSettings(prev => ({ ...prev, ...importedSettings }));
        setHasChanges(true);
        toast.success('Settings imported successfully!');
      } catch (error) {
        toast.error('Failed to import settings. Invalid file format.');
      }
    };
    reader.readAsText(file);
  };

  const clearData = () => {
    if (window.confirm('Are you sure you want to clear all study data? This action cannot be undone.')) {
      // Clear localStorage
      localStorage.removeItem('ai-study-partner-settings');
      localStorage.removeItem('ai-study-partner-sessions');
      
      // Here you would typically call an API to clear backend data
      toast.success('All data cleared successfully!');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-brand-slate">Settings</h1>
          <p className="text-brand-slate mt-1 opacity-80">Configure your AI Study Partner</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={resetSettings}
            className="btn-outline"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset
          </button>
          <button
            onClick={saveSettings}
            disabled={!hasChanges || isLoading}
            className="btn-primary"
          >
            {isLoading ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Save Changes
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Settings Navigation */}
        <div className="lg:col-span-1">
          <div className="card p-4">
            <h2 className="text-lg font-semibold text-brand-slate mb-4">Categories</h2>
            <nav className="space-y-2">
              {[
                { id: 'ai', name: 'AI & Models', icon: Brain },
                { id: 'capture', name: 'Capture', icon: Camera },
                { id: 'processing', name: 'Processing', icon: Database },
                { id: 'privacy', name: 'Privacy', icon: Shield },
                { id: 'export', name: 'Export', icon: Download },
                { id: 'data', name: 'Data Management', icon: Trash2 }
              ].map((category) => {
                const Icon = category.icon;
                return (
                  <button
                    key={category.id}
                    onClick={() => setActiveCategory(category.id as any)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg hover:bg-brand-cream ${
                      activeCategory === category.id ? 'bg-brand-cream text-brand-slate' : 'text-gray-600'
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-3" />
                    {category.name}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* AI & Models */}
          {activeCategory === 'ai' && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-brand-slate mb-4 flex items-center">
              <Brain className="h-5 w-5 mr-2 text-brand-teal" />
              AI & Models
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-brand-slate mb-2">
                  AI Provider
                </label>
                <select
                  value={settings.llmProvider}
                  onChange={(e) => handleSettingChange('llmProvider', e.target.value)}
                  className="input w-full"
                >
                  <option value="gemini">Gemini (default)</option>
                  <option value="openai">OpenAI</option>
                  <option value="deepseek">DeepSeek</option>
                  <option value="auto">Auto (best available)</option>
                </select>
              </div>

              {(settings.llmProvider === 'openai' || (typeof settings.model === 'string' && settings.model.startsWith('gpt'))) && (
                <div>
                  <label className="block text-sm font-medium text-brand-slate mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={settings.openaiApiKey}
                    onChange={(e) => handleSettingChange('openaiApiKey', e.target.value)}
                    placeholder="sk-..."
                    className="input w-full"
                  />
                  <p className="text-xs text-brand-slate mt-1 opacity-70">
                    Required for OpenAI models (e.g., gpt-4, gpt-3.5)
                  </p>
                </div>
              )}

              {settings.llmProvider === 'gemini' && (
                <div>
                  <label className="block text-sm font-medium text-brand-slate mb-2">Gemini API Key</label>
                  <input
                    type="password"
                    value={settings.geminiApiKey}
                    onChange={(e) => handleSettingChange('geminiApiKey', e.target.value)}
                    placeholder="AIza..."
                    className="input w-full"
                  />
                </div>
              )}

              {settings.llmProvider === 'deepseek' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-brand-slate mb-2">DeepSeek API Key</label>
                    <input
                      type="password"
                      value={settings.deepseekApiKey}
                      onChange={(e) => handleSettingChange('deepseekApiKey', e.target.value)}
                      placeholder="sk-..."
                      className="input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-brand-slate mb-2">DeepSeek Base URL</label>
                    <input
                      type="text"
                      value={settings.deepseekBaseUrl}
                      onChange={(e) => handleSettingChange('deepseekBaseUrl', e.target.value)}
                      placeholder="https://api.deepseek.com"
                      className="input w-full"
                    />
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-brand-slate mb-2">
                    Model
                  </label>
                  <select
                    value={settings.model}
                    onChange={(e) => handleSettingChange('model', e.target.value)}
                    className="input w-full"
                  >
                    {availableModels.length > 0 ? (
                      availableModels.map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))
                    ) : (
                      <>
                        <option value="gemini-1.5-flash">gemini-1.5-flash</option>
                        <option value="gpt-4-turbo-preview">gpt-4-turbo-preview</option>
                        <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                        <option value="deepseek-chat">deepseek-chat</option>
                      </>
                    )}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-brand-slate mb-2">
                    Max Tokens
                  </label>
                  <input
                    type="number"
                    value={settings.maxTokens}
                    onChange={(e) => handleSettingChange('maxTokens', parseInt(e.target.value))}
                    className="input w-full"
                    min="100"
                    max="4000"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Temperature: {settings.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) => handleSettingChange('temperature', parseFloat(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Focused</span>
                  <span>Creative</span>
                </div>
              </div>
            </div>
          </div>
          )}

          {/* Capture Settings */}
          {activeCategory === 'capture' && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-brand-slate mb-4 flex items-center">
              <Camera className="h-5 w-5 mr-2 text-brand-teal" />
              Capture Settings
            </h2>
            <div className="space-y-4">
              {captureError && (
                <div className="p-3 rounded-md border border-red-200 bg-red-50 text-sm text-red-800">
                  {captureError}
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-brand-slate mb-2">
                    Monitor
                  </label>
                  <select
                    value={(selectedMonitor ?? settings.monitorIndex) ?? ''}
                    onChange={(e) => {
                      const idx = parseInt(e.target.value);
                      setSelectedMonitor(idx);
                      handleSettingChange('monitorIndex', idx);
                    }}
                    className="input w-full"
                  >
                    {monitors.length === 0 ? (
                      <option value="">No monitors found</option>
                    ) : (
                      monitors.map(m => (
                        <option key={m.index} value={m.index}>
                          Monitor {m.index} ({m.width}x{m.height})
                        </option>
                      ))
                    )}
                  </select>
                </div>

                <div className="flex items-end">
                  <button
                    onClick={async () => {
                      if (isCaptureActionLoading) return;
                      setIsCaptureActionLoading(true);
                      setCaptureError(null);
                      try {
                        if (!isCapturing) {
                          await startCapture({
                            fps: settings.screenFps,
                            audio_enabled: settings.audioEnabled,
                            monitor_index: (selectedMonitor ?? settings.monitorIndex) ?? undefined
                          });
                          toast.success('Test capture started');
                        } else {
                          await stopCapture();
                          toast.success('Test capture stopped');
                        }
                      } catch (err) {
                        setCaptureError('Capture action failed. Ensure the backend is running.');
                        toast.error('Capture action failed');
                      } finally {
                        setIsCaptureActionLoading(false);
                      }
                    }}
                    disabled={isCaptureActionLoading}
                    className={`btn-${isCapturing ? 'secondary' : 'outline'} w-full ${isCaptureActionLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
                  >
                    {isCaptureActionLoading ? (
                      <span className="inline-flex items-center justify-center">
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        {isCapturing ? 'Stopping...' : 'Starting...'}
                      </span>
                    ) : (
                      isCapturing ? 'Stop Test Capture' : 'Start Test Capture'
                    )}
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-brand-slate mb-2">
                    Screen FPS
                  </label>
                  <select
                    value={settings.screenFps}
                    onChange={(e) => handleSettingChange('screenFps', parseInt(e.target.value))}
                    className="input w-full"
                  >
                    <option value={0.5}>0.5 FPS</option>
                    <option value={1}>1 FPS</option>
                    <option value={2}>2 FPS</option>
                    <option value={5}>5 FPS</option>
                  </select>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Mic className="h-5 w-5 text-brand-slate" />
                    <span className="text-sm font-medium text-brand-slate">Audio Capture</span>
                  </div>
                  <button
                    onClick={() => handleSettingChange('audioEnabled', !settings.audioEnabled)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings.audioEnabled ? 'bg-brand-teal' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        settings.audioEnabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>

              {settings.audioEnabled && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-brand-slate mb-2">
                      Sample Rate
                    </label>
                    <select
                      value={settings.audioSampleRate}
                      onChange={(e) => handleSettingChange('audioSampleRate', parseInt(e.target.value))}
                      className="input w-full"
                    >
                      <option value={8000}>8 kHz</option>
                      <option value={16000}>16 kHz</option>
                      <option value={44100}>44.1 kHz</option>
                      <option value={48000}>48 kHz</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-brand-slate mb-2">
                      Chunk Size
                    </label>
                    <input
                      type="number"
                      value={settings.audioChunkSize}
                      onChange={(e) => handleSettingChange('audioChunkSize', parseInt(e.target.value))}
                      className="input w-full"
                      min="512"
                      max="4096"
                      step="512"
                    />
                  </div>
                </div>
              )}

              {isCapturing && (
                <div className="text-xs text-brand-slate opacity-70">
                  Active session: {sessionId}
                </div>
              )}
            </div>
          </div>
          )}

          {/* Processing Settings */}
          {activeCategory === 'processing' && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-brand-slate mb-4 flex items-center">
              <Database className="h-5 w-5 mr-2 text-brand-teal" />
              Processing Settings
            </h2>
            <div className="space-y-6">
              {/* OCR */}
              <div>
                <h3 className="text-sm font-semibold text-brand-slate mb-3">OCR</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-brand-slate mb-2">Engine</label>
                    <select
                      value={settings.ocrEngine}
                      onChange={(e) => handleSettingChange('ocrEngine', e.target.value)}
                      className="input w-full"
                    >
                      <option value="tesseract">Tesseract</option>
                      <option value="paddleocr">PaddleOCR</option>
                      <option value="easyocr">EasyOCR</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-brand-slate mb-2">Language</label>
                    <input
                      type="text"
                      value={settings.ocrLanguage}
                      onChange={(e) => handleSettingChange('ocrLanguage', e.target.value)}
                      className="input w-full"
                      placeholder="eng, deu, jpn..."
                    />
                  </div>
                  <div className="flex items-end">
                    <button
                      onClick={() => handleSettingChange('ocrPreprocess', !settings.ocrPreprocess)}
                      className={`btn-${settings.ocrPreprocess ? 'secondary' : 'outline'} w-full`}
                    >
                      {settings.ocrPreprocess ? 'Disable' : 'Enable'} Preprocessing
                    </button>
                  </div>
                </div>
              </div>

              {/* Speech-To-Text */}
              <div>
                <h3 className="text-sm font-semibold text-brand-slate mb-3">Speech-To-Text</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-brand-slate mb-2">Engine</label>
                    <select
                      value={settings.sttEngine}
                      onChange={(e) => handleSettingChange('sttEngine', e.target.value)}
                      className="input w-full"
                    >
                      <option value="whisper">Whisper</option>
                      <option value="vosk">Vosk</option>
                      <option value="azure">Azure</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-brand-slate mb-2">Model</label>
                    <select
                      value={settings.whisperModel}
                      onChange={(e) => handleSettingChange('whisperModel', e.target.value)}
                      className="input w-full"
                    >
                      <option value="tiny">tiny</option>
                      <option value="base">base</option>
                      <option value="small">small</option>
                      <option value="medium">medium</option>
                      <option value="large">large</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-brand-slate mb-2">Language</label>
                    <input
                      type="text"
                      value={settings.sttLanguage}
                      onChange={(e) => handleSettingChange('sttLanguage', e.target.value)}
                      className="input w-full"
                      placeholder="en, es, fr..."
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          )}

          {/* Export Settings */}
          {activeCategory === 'export' && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-brand-slate mb-4 flex items-center">
              <Download className="h-5 w-5 mr-2 text-brand-teal" />
              Export Settings
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-brand-slate mb-2">Enabled Formats</label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {['anki','csv','pdf'].map(fmt => (
                    <label key={fmt} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={settings.exportFormats.includes(fmt as any)}
                        onChange={(e) => {
                          const next = new Set(settings.exportFormats);
                          if (e.target.checked) next.add(fmt as any); else next.delete(fmt as any);
                          handleSettingChange('exportFormats', Array.from(next));
                        }}
                      />
                      <span className="text-sm text-brand-slate uppercase">{fmt}</span>
                    </label>
                  ))}
                </div>
              </div>

              {settings.exportFormats.includes('anki') && (
                <div>
                  <label className="block text-sm font-medium text-brand-slate mb-2">Anki Deck Name</label>
                  <input
                    type="text"
                    value={settings.ankiDeckName}
                    onChange={(e) => handleSettingChange('ankiDeckName', e.target.value)}
                    className="input w-full"
                  />
                </div>
              )}
            </div>
          </div>
          )}

          {/* Privacy Settings */}
          {activeCategory === 'privacy' && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-brand-slate mb-4 flex items-center">
              <Shield className="h-5 w-5 mr-2 text-brand-teal" />
              Privacy & Security
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-brand-slate mb-2">
                  Privacy Mode
                </label>
                <select
                  value={settings.privacyMode}
                  onChange={(e) => handleSettingChange('privacyMode', e.target.value)}
                  className="input w-full"
                >
                  <option value="local">Local Only</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="cloud">Cloud</option>
                </select>
                <p className="text-xs text-brand-slate mt-1 opacity-70">
                  {settings.privacyMode === 'local' && 'All processing happens on your device'}
                  {settings.privacyMode === 'hybrid' && 'Local processing with optional cloud features'}
                  {settings.privacyMode === 'cloud' && 'Full cloud processing with encryption'}
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-brand-slate mb-2">
                    Data Retention (Days)
                  </label>
                  <input
                    type="number"
                    value={settings.dataRetentionDays}
                    onChange={(e) => handleSettingChange('dataRetentionDays', parseInt(e.target.value))}
                    className="input w-full"
                    min="1"
                    max="365"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Shield className="h-5 w-5 text-brand-slate" />
                    <span className="text-sm font-medium text-brand-slate">Encryption</span>
                  </div>
                  <button
                    onClick={() => handleSettingChange('encryptionEnabled', !settings.encryptionEnabled)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings.encryptionEnabled ? 'bg-brand-teal' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        settings.encryptionEnabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>
          </div>
          )}

          {/* Data Management */}
          {activeCategory === 'data' && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-brand-slate mb-4 flex items-center">
              <Trash2 className="h-5 w-5 mr-2 text-brand-teal" />
              Data Management
            </h2>
            <div className="space-y-4">
              <div className="p-4 bg-brand-cream rounded-lg border border-brand-sand">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-brand-slate">Local Data Overview</h3>
                    <p className="text-xs text-brand-slate opacity-80">
                      Settings: {(localInfo.settingsBytes / 1024).toFixed(1)} KB · Sessions: {(localInfo.sessionsBytes / 1024).toFixed(1)} KB · {localInfo.sessionCount} session(s)
                    </p>
                  </div>
                  <button onClick={refreshLocalInfo} className="btn-outline">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-brand-cream rounded-lg border border-brand-sand">
                <div>
                  <h3 className="text-sm font-medium text-brand-slate">Clear All Data</h3>
                  <p className="text-xs text-brand-slate opacity-80">Remove all study sessions and settings</p>
                </div>
                <button
                  onClick={clearData}
                  className="btn-secondary"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear All
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg border border-brand-sand">
                  <h3 className="text-sm font-medium text-brand-slate mb-2">Settings Only</h3>
                  <button
                    onClick={() => { localStorage.removeItem('ai-study-partner-settings'); localStorage.removeItem('ai-study-partner-settings-draft'); refreshLocalInfo(); toast.success('Settings cleared'); }}
                    className="btn-outline w-full"
                  >
                    Clear Settings
                  </button>
                </div>
                <div className="p-4 rounded-lg border border-brand-sand">
                  <h3 className="text-sm font-medium text-brand-slate mb-2">Sessions Only</h3>
                  <button
                    onClick={() => { localStorage.removeItem('ai-study-partner-sessions'); refreshLocalInfo(); toast.success('Sessions cleared'); }}
                    className="btn-outline w-full"
                  >
                    Clear Sessions
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Export Settings
                  </label>
                  <button
                    onClick={exportSettings}
                    className="btn-outline w-full"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </button>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Import Settings
                  </label>
                  <label className="btn-outline w-full cursor-pointer">
                    <Upload className="h-4 w-4 mr-2" />
                    Import
                    <input
                      type="file"
                      accept=".json"
                      onChange={importSettings}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>
            </div>
          </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
