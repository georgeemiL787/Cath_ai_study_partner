import React, { useEffect, useState } from 'react';
import { useCapture } from '../hooks/useCapture';
import axios from 'axios';

interface ScreenPickerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (monitorIndex: number) => void;
  shareAudio?: boolean;
  onToggleShareAudio?: () => void;
}

const ScreenPickerModal: React.FC<ScreenPickerModalProps> = ({ isOpen, onClose, onSelect, shareAudio, onToggleShareAudio }) => {
  const { listMonitors } = useCapture();
  const [monitors, setMonitors] = useState<Array<{ index: number; left: number; top: number; width: number; height: number }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [thumbs, setThumbs] = useState<Record<number, string>>({});
  const [tab, setTab] = useState<'screens' | 'apps'>('screens');
  const [apps, setApps] = useState<Array<{ hwnd: number; title: string; left: number; top: number; width: number; height: number }>>([]);
  const [appThumbs, setAppThumbs] = useState<Record<number, string>>({});

  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    const base = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const fetchScreens = async () => {
      const m = await listMonitors();
      if (!cancelled) setMonitors(m);
      const arr = await Promise.all(m.map(async (mon) => {
        try {
          const res = await axios.get(`${base}/api/capture/monitors/${mon.index}/thumbnail`);
          return { index: mon.index, b64: res.data.thumbnail as string };
        } catch {
          return { index: mon.index, b64: '' };
        }
      }));
      if (!cancelled) {
        const map: Record<number, string> = {};
        arr.forEach((t) => (map[t.index] = t.b64));
        setThumbs(map);
      }
    };
    const fetchApps = async () => {
      try {
        const res = await axios.get(`${base}/api/capture/windows`);
        const wins = res.data.windows as Array<{ hwnd: number; title: string; left: number; top: number; width: number; height: number }>;
        if (!cancelled) setApps(wins);
        const arr = await Promise.all(wins.slice(0, 12).map(async (w) => {
          try {
            const r = await axios.get(`${base}/api/capture/windows/${w.hwnd}/thumbnail`);
            return { hwnd: w.hwnd, b64: r.data.thumbnail as string };
          } catch {
            return { hwnd: w.hwnd, b64: '' };
          }
        }));
        if (!cancelled) {
          const map: Record<number, string> = {};
          arr.forEach((t) => (map[t.hwnd] = t.b64));
          setAppThumbs(map);
        }
      } catch {
        if (!cancelled) setError('Failed to load applications');
      }
    };
    Promise.all([fetchScreens(), fetchApps()]).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-5xl p-6 border border-brand-sand max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-brand-slate">Select what you want to share</h3>
          <button onClick={onClose} className="text-brand-slate hover:text-brand-teal">✕</button>
        </div>
        <div className="mb-4 flex items-center justify-between">
          <div className="flex space-x-4">
          <button onClick={() => setTab('screens')} className={`px-3 py-1 rounded ${tab==='screens' ? 'bg-brand-teal text-white' : 'bg-brand-cream text-brand-slate'}`}>Screens</button>
          <button onClick={() => setTab('apps')} className={`px-3 py-1 rounded ${tab==='apps' ? 'bg-brand-teal text-white' : 'bg-brand-cream text-brand-slate'}`}>Applications</button>
          </div>
          {typeof shareAudio === 'boolean' && onToggleShareAudio && (
            <button
              onClick={onToggleShareAudio}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${shareAudio ? 'bg-brand-teal' : 'bg-gray-200'}`}
              title="Share system audio"
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${shareAudio ? 'translate-x-6' : 'translate-x-1'}`}
              />
              <span className="ml-2 text-sm text-brand-slate">Share audio</span>
            </button>
          )}
        </div>
        {loading && <div className="text-brand-slate">Loading…</div>}
        {error && <div className="text-red-600 text-sm">{error}</div>}
        {!loading && !error && tab==='screens' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {monitors.map((m) => (
              <button
                key={m.index}
                onClick={() => onSelect(m.index)}
                className="group border rounded-lg p-4 hover:border-brand-teal transition flex flex-col items-center bg-brand-cream"
              >
                {thumbs[m.index] ? (
                  <img
                    src={`data:image/jpeg;base64,${thumbs[m.index]}`}
                    alt={`Display ${m.index}`}
                    className="w-full aspect-video object-cover rounded-md mb-3 shadow"
                  />
                ) : (
                  <div className="w-full aspect-video bg-brand-sand rounded-md mb-3 flex items-center justify-center text-brand-slate">
                    <span className="opacity-70">Display {m.index}</span>
                  </div>
                )}
                <div className="text-xs text-brand-slate opacity-80">{m.width}×{m.height}</div>
              </button>
            ))}
            {monitors.length === 0 && (
              <div className="text-sm text-brand-slate">No displays detected</div>
            )}
          </div>
        )}
        {!loading && !error && tab==='apps' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {apps.map((a) => (
              <button
                key={a.hwnd}
                onClick={() => {
                  // When picking an app, we start capture by region (left, top, width, height)
                  // The parent handler will call startCapture after modal closes
                  onSelect(a.hwnd);
                }}
                className="group border rounded-lg p-4 hover:border-brand-teal transition flex flex-col items-center bg-brand-cream"
              >
                {appThumbs[a.hwnd] ? (
                  <img
                    src={`data:image/jpeg;base64,${appThumbs[a.hwnd]}`}
                    alt={a.title}
                    className="w-full aspect-video object-cover rounded-md mb-3 shadow"
                  />
                ) : (
                  <div className="w-full aspect-video bg-brand-sand rounded-md mb-3 flex items-center justify-center text-brand-slate">
                    <span className="opacity-70">{a.title}</span>
                  </div>
                )}
                <div className="text-xs text-brand-slate opacity-80 truncate w-full text-center" title={a.title}>{a.title}</div>
              </button>
            ))}
            {apps.length === 0 && (
              <div className="text-sm text-brand-slate">No applications detected</div>
            )}
          </div>
        )}
        <div className="mt-6 flex justify-end">
          <button onClick={onClose} className="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default ScreenPickerModal;


