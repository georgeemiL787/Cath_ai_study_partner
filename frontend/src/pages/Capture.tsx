import React, { useState, useEffect, useCallback } from 'react';
import { useCapture } from '../hooks/useCapture';
import toast from 'react-hot-toast';
import ScreenPickerModal from '../components/ScreenPickerModal';

// Simple icon components to avoid dependency issues
const Play = () => <span>▶</span>;
const Square = () => <span>⏹</span>;
const Camera = () => <span>📷</span>;
const Mic = () => <span>🎤</span>;
const Monitor = () => <span>🖥</span>;
const Volume2 = () => <span>🔊</span>;
const VolumeX = () => <span>🔇</span>;
const Maximize2 = () => <span>⛶</span>;
const Minimize2 = () => <span>⛷</span>;

const Capture: React.FC = () => {
  const { 
    isCapturing, 
    sessionId, 
    captureStats, 
    startCapture, 
    stopCapture, 
    getCurrentFrame,
    setScreenRegion 
  } = useCapture();

  const [config, setConfig] = useState({
    fps: 1,
    audioEnabled: true,
    screenRegion: 'full' as 'full' | 'custom',
    customRegion: { x: 0, y: 0, width: 1920, height: 1080 }
  });

  const [currentFrame, setCurrentFrame] = useState<string>('');
  const [showPreview, setShowPreview] = useState(false);
  const [showScreenPicker, setShowScreenPicker] = useState(false);
  const [selectedMonitor, setSelectedMonitor] = useState<number | null>(null);
  const [lastSelection, setLastSelection] = useState<any>(() => {
    try {
      const raw = localStorage.getItem('asp.lastShareSelection');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  const saveLastSelection = (selection: any) => {
    try {
      localStorage.setItem('asp.lastShareSelection', JSON.stringify(selection));
      setLastSelection(selection);
    } catch {}
  };

  const handleStartCapture = async () => {
    try {
      const region = config.screenRegion === 'custom' ? config.customRegion : undefined;
      await startCapture({
        fps: config.fps,
        audio_enabled: config.audioEnabled,
        screen_region: region,
        monitor_index: selectedMonitor || undefined
      });
      toast.success('Capture started successfully!');
      // Turn on live preview automatically and fetch an initial frame
      setShowPreview(true);
      setTimeout(() => {
        handleGetFrame();
      }, 500);
      if (selectedMonitor) {
        saveLastSelection({ type: 'monitor', id: selectedMonitor });
      } else if (config.screenRegion === 'custom' && region) {
        saveLastSelection({ type: 'region', region });
      }
    } catch (error) {
      toast.error('Failed to start capture');
    }
  };

  const openScreenPicker = () => setShowScreenPicker(true);
  const handleSelectMonitor = async (id: number) => {
    setShowScreenPicker(false);
    // If id is large (likely hwnd), fetch its rect and use custom region
    if (id > 10000) {
      try {
        const base = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const res = await fetch(`${base}/api/capture/windows`);
        const data = await res.json();
        const win = (data.windows || []).find((w: any) => w.hwnd === id);
        if (win) {
          setSelectedMonitor(null);
          setConfig((prev) => ({
            ...prev,
            screenRegion: 'custom',
            customRegion: { x: win.left, y: win.top, width: win.width, height: win.height }
          }));
          await startCapture({
            fps: config.fps,
            audio_enabled: config.audioEnabled,
            screen_region: { x: win.left, y: win.top, width: win.width, height: win.height }
          });
          toast.success('Application capture started!');
          setShowPreview(true);
          setTimeout(() => { handleGetFrame(); }, 500);
          saveLastSelection({ type: 'window', id, title: win.title, region: { x: win.left, y: win.top, width: win.width, height: win.height } });
          return;
        }
      } catch (e) {
        toast.error('Failed to start application capture');
      }
    }
    // Otherwise treat as monitor index
    setSelectedMonitor(id);
    await handleStartCapture();
    saveLastSelection({ type: 'monitor', id });
  };

  const handleShareLast = async () => {
    if (!lastSelection) return;
    try {
      if (lastSelection.type === 'monitor' && lastSelection.id) {
        setSelectedMonitor(lastSelection.id);
        await handleStartCapture();
        return;
      }
      if (lastSelection.type === 'window' && lastSelection.region) {
        const r = lastSelection.region;
        setSelectedMonitor(null);
        setConfig((prev) => ({ ...prev, screenRegion: 'custom', customRegion: r }));
        await startCapture({ fps: config.fps, audio_enabled: config.audioEnabled, screen_region: r });
        setShowPreview(true);
        setTimeout(() => { handleGetFrame(); }, 500);
        return;
      }
      if (lastSelection.type === 'region' && lastSelection.region) {
        const r = lastSelection.region;
        setSelectedMonitor(null);
        setConfig((prev) => ({ ...prev, screenRegion: 'custom', customRegion: r }));
        await startCapture({ fps: config.fps, audio_enabled: config.audioEnabled, screen_region: r });
        setShowPreview(true);
        setTimeout(() => { handleGetFrame(); }, 500);
        return;
      }
      toast.error('Saved selection is not valid anymore');
    } catch (e) {
      toast.error('Failed to start with last selection');
    }
  };

  const handleStopCapture = async () => {
    try {
      await stopCapture();
      toast.success('Capture stopped successfully!');
    } catch (error) {
      toast.error('Failed to stop capture');
    }
  };

  const handleGetFrame = useCallback(async () => {
    try {
      const frame = await getCurrentFrame();
      setCurrentFrame(frame);
      setShowPreview(true);
    } catch (error) {
      toast.error('Failed to get current frame');
    }
  }, [getCurrentFrame]);

  const handleSetRegion = async () => {
    if (config.screenRegion === 'custom') {
      try {
        await setScreenRegion(config.customRegion);
        toast.success('Screen region updated');
      } catch (error) {
        toast.error('Failed to set screen region');
      }
    }
  };

  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;
    if (isCapturing && showPreview) {
      interval = setInterval(() => {
        handleGetFrame();
      }, Math.max(250, 1000 / config.fps));
    }
    return () => {
      if (interval) clearInterval(interval as any);
    };
  }, [isCapturing, showPreview, config.fps, handleGetFrame]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-brand-slate">Capture</h1>
          <p className="text-brand-slate mt-1 opacity-80">Configure and control your study session capture</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isCapturing ? 'bg-brand-teal animate-pulse' : 'bg-gray-400'}`}></div>
          <span className="text-sm text-brand-slate opacity-80">
            {isCapturing ? 'Recording' : 'Idle'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* Capture Controls */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-brand-slate mb-4">Capture Controls</h2>
            
            <div className="space-y-4">
              <div className="flex space-x-3">
                <button
                  onClick={handleStartCapture}
                  disabled={isCapturing}
                  className={`btn-primary flex-1 ${isCapturing ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Play />
                  Start Capture
                </button>
                <button
                  onClick={openScreenPicker}
                  disabled={isCapturing}
                  className={`btn-outline flex-1 ${isCapturing ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Monitor />
                  Pick Screen
                </button>
                {lastSelection && !isCapturing && (
                  <button
                    onClick={handleShareLast}
                    className="btn-secondary flex-1"
                    title={lastSelection.type === 'monitor' ? `Monitor ${lastSelection.id}` : (lastSelection.title || 'Last selection')}
                  >
                    Share Last
                  </button>
                )}
                <button
                  onClick={handleStopCapture}
                  disabled={!isCapturing}
                  className={`btn-secondary flex-1 ${!isCapturing ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Square />
                  Stop Capture
                </button>
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={handleGetFrame}
                  disabled={!isCapturing}
                  className={`btn-outline flex-1 ${!isCapturing ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Camera />
                  Get Frame
                </button>
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  className={`btn-outline ${showPreview ? 'bg-blue-100 text-blue-700' : ''}`}
                >
                  {showPreview ? <Minimize2 /> : <Maximize2 />}
                </button>
              </div>
            </div>
          </div>

          {/* Settings */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-brand-slate mb-4">Settings</h2>
            
            <div className="space-y-4">
              {/* FPS Setting */}
              <div>
                <label className="block text-sm font-medium text-brand-slate mb-2">
                  Capture FPS
                </label>
                <select
                  value={config.fps}
                  onChange={(e) => setConfig({ ...config, fps: parseInt(e.target.value) })}
                  className="input"
                  disabled={isCapturing}
                >
                  <option value={0.5}>0.5 FPS</option>
                  <option value={1}>1 FPS</option>
                  <option value={2}>2 FPS</option>
                  <option value={5}>5 FPS</option>
                </select>
              </div>

              {/* Audio Setting */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {config.audioEnabled ? (
                    <Volume2 />
                  ) : (
                    <VolumeX />
                  )}
                  <span className="text-sm font-medium text-brand-slate">Audio Capture</span>
                </div>
                <button
                  onClick={() => setConfig({ ...config, audioEnabled: !config.audioEnabled })}
                  disabled={isCapturing}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    config.audioEnabled ? 'bg-brand-teal' : 'bg-gray-200'
                  } ${isCapturing ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      config.audioEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {/* Screen Region */}
              <div>
                <label className="block text-sm font-medium text-brand-slate mb-2">
                  Screen Region
                </label>
                <select
                  value={config.screenRegion}
                  onChange={(e) => setConfig({ ...config, screenRegion: e.target.value as 'full' | 'custom' })}
                  className="input"
                  disabled={isCapturing}
                >
                  <option value="full">Full Screen</option>
                  <option value="custom">Custom Region</option>
                </select>
              </div>

              {/* Custom Region Settings */}
              {config.screenRegion === 'custom' && (
                <div className="space-y-3 p-4 bg-brand-cream rounded-lg">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-brand-slate mb-1">X</label>
                      <input
                        type="number"
                        value={config.customRegion.x}
                        onChange={(e) => setConfig({
                          ...config,
                          customRegion: { ...config.customRegion, x: parseInt(e.target.value) }
                        })}
                        className="input text-sm"
                        disabled={isCapturing}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-brand-slate mb-1">Y</label>
                      <input
                        type="number"
                        value={config.customRegion.y}
                        onChange={(e) => setConfig({
                          ...config,
                          customRegion: { ...config.customRegion, y: parseInt(e.target.value) }
                        })}
                        className="input text-sm"
                        disabled={isCapturing}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-brand-slate mb-1">Width</label>
                      <input
                        type="number"
                        value={config.customRegion.width}
                        onChange={(e) => setConfig({
                          ...config,
                          customRegion: { ...config.customRegion, width: parseInt(e.target.value) }
                        })}
                        className="input text-sm"
                        disabled={isCapturing}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-brand-slate mb-1">Height</label>
                      <input
                        type="number"
                        value={config.customRegion.height}
                        onChange={(e) => setConfig({
                          ...config,
                          customRegion: { ...config.customRegion, height: parseInt(e.target.value) }
                        })}
                        className="input text-sm"
                        disabled={isCapturing}
                      />
                    </div>
                  </div>
                  <button
                    onClick={handleSetRegion}
                    disabled={isCapturing}
                    className="btn-outline w-full btn-sm"
                  >
                    Apply Region
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Live Preview */}
          {showPreview && (
            <div className="card p-6 elev-1">
              <h2 className="text-xl font-semibold text-brand-slate mb-4">Live Preview</h2>
              <div className="bg-brand-sand rounded-lg p-4 min-h-[300px] flex items-center justify-center">
                {currentFrame ? (
                  <img
                    src={`data:image/jpeg;base64,${currentFrame}`}
                    alt="Current frame"
                    className="max-w-full max-h-full rounded-lg shadow-lg"
                  />
                ) : (
                  <div className="text-center text-brand-slate opacity-70">
                    <Camera />
                    <p>No frame available</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Statistics */}
          {captureStats && captureStats.screen_stats && captureStats.audio_stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Screen Stats */}
              <div className="card p-6 elev-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Monitor />
                  Screen Capture
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Status:</span>
                    <span className={`text-sm font-medium ${
                      captureStats.screen_stats?.status === 'capturing' ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {captureStats.screen_stats?.status || 'unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Frames:</span>
                    <span className="text-sm font-medium">{captureStats.screen_stats?.frame_count || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">FPS:</span>
                    <span className="text-sm font-medium">
                      {(captureStats.screen_stats?.actual_fps || 0).toFixed(1)} / {captureStats.screen_stats?.target_fps || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Duration:</span>
                    <span className="text-sm font-medium">
                      {Math.floor((captureStats.screen_stats?.elapsed_time || 0) / 60)}m {Math.floor((captureStats.screen_stats?.elapsed_time || 0) % 60)}s
                    </span>
                  </div>
                </div>
              </div>

              {/* Audio Stats */}
              <div className="card p-6 elev-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Mic />
                  Audio Capture
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Status:</span>
                    <span className={`text-sm font-medium ${
                      captureStats.audio_stats?.status === 'capturing' ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {captureStats.audio_stats?.status || 'unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Speech Segments:</span>
                    <span className="text-sm font-medium">{captureStats.audio_stats?.speech_segments || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Speech Ratio:</span>
                    <span className="text-sm font-medium">
                      {((captureStats.audio_stats?.speech_ratio || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Currently Speaking:</span>
                    <span className={`text-sm font-medium ${
                      captureStats.audio_stats?.in_speech ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {captureStats.audio_stats?.in_speech ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Session Info */}
          {sessionId && (
            <div className="card p-6 elev-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Session Information</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Session ID:</span>
                  <span className="text-sm font-mono text-gray-900">{sessionId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Started:</span>
                  <span className="text-sm text-gray-900">
                    {new Date().toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {showScreenPicker && (
        <ScreenPickerModal
          isOpen={showScreenPicker}
          onClose={() => setShowScreenPicker(false)}
          onSelect={handleSelectMonitor}
          shareAudio={config.audioEnabled}
          onToggleShareAudio={() => setConfig({ ...config, audioEnabled: !config.audioEnabled })}
        />
      )}
    </div>
  );
};

export default Capture;
