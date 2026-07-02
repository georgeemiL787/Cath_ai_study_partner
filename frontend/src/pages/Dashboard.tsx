import React, { useState } from 'react';
import { 
  Play, 
  Square, 
  Camera, 
  Mic, 
  BookOpen, 
  Brain, 
  Activity,
  Clock
} from 'lucide-react';
import { useCapture } from '../hooks/useCapture';
import { useStudy } from '../hooks/useStudy';
import toast from 'react-hot-toast';

const Dashboard: React.FC = () => {
  const { isCapturing, startCapture, stopCapture, captureStats } = useCapture();
  const { studyStats } = useStudy();
  const [sessionId, setSessionId] = useState<string>('');

  const handleStartCapture = async () => {
    try {
      const newSessionId = await startCapture({
        fps: 1,
        audio_enabled: true,
        session_id: sessionId || undefined
      });
      setSessionId(newSessionId);
      toast.success('Capture started successfully!');
    } catch (error) {
      toast.error('Failed to start capture');
      console.error('Capture start error:', error);
    }
  };

  const handleStopCapture = async () => {
    try {
      await stopCapture();
      toast.success('Capture stopped successfully!');
    } catch (error) {
      toast.error('Failed to stop capture');
      console.error('Capture stop error:', error);
    }
  };

  const quickActions = [
    {
      title: 'Start Study Session',
      description: 'Begin capturing screen and audio',
      icon: Play,
      action: handleStartCapture,
      disabled: isCapturing,
      color: 'bg-green-600 hover:bg-green-700'
    },
    {
      title: 'Stop Capture',
      description: 'End current capture session',
      icon: Square,
      action: handleStopCapture,
      disabled: !isCapturing,
      color: 'bg-red-600 hover:bg-red-700'
    },
    {
      title: 'View Study Materials',
      description: 'Browse captured content',
      icon: BookOpen,
      action: () => window.location.href = '/study',
      disabled: false,
      color: 'bg-brand-teal hover:bg-brand-slate'
    },
    {
      title: 'AI Assistant',
      description: 'Ask questions about your study content',
      icon: Brain,
      action: () => window.location.href = '/study',
      disabled: false,
      color: 'bg-brand-teal hover:bg-brand-slate'
    }
  ];

  const stats = [
    {
      title: 'Active Session',
      value: isCapturing ? 'Running' : 'Stopped',
      icon: Activity,
      color: isCapturing ? 'text-green-600' : 'text-gray-500',
      bgColor: isCapturing ? 'bg-green-100' : 'bg-gray-100'
    },
    {
      title: 'Session Duration',
      value: captureStats?.screen_stats?.elapsed_time 
        ? `${Math.floor(captureStats.screen_stats.elapsed_time / 60)}m ${Math.floor(captureStats.screen_stats.elapsed_time % 60)}s`
        : '0m 0s',
      icon: Clock,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Frames Captured',
      value: captureStats?.screen_stats?.frame_count?.toString() || '0',
      icon: Camera,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Speech Segments',
      value: captureStats?.audio_stats?.speech_segments?.toString() || '0',
      icon: Mic,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-brand-slate">Dashboard</h1>
          <p className="text-brand-slate mt-1 opacity-80">Monitor your AI study sessions</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isCapturing ? 'bg-brand-teal animate-pulse' : 'bg-gray-400'}`}></div>
          <span className="text-sm text-brand-slate opacity-80">
            {isCapturing ? 'Recording' : 'Idle'}
          </span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action, index) => {
          const Icon = action.icon;
          return (
            <button
              key={index}
              onClick={action.action}
              disabled={action.disabled}
              className={`
                p-6 rounded-lg text-left transition-all duration-200 transform hover:scale-105
                ${action.disabled 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                  : `${action.color} text-white`
                }
              `}
            >
              <Icon className="h-8 w-8 mb-3" />
              <h3 className="font-semibold text-lg mb-1">{action.title}</h3>
              <p className="text-sm opacity-90">{action.description}</p>
            </button>
          );
        })}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="card p-6 elev-1">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-brand-slate opacity-80">{stat.title}</p>
                  <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Activity */}
      <div className="card p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {isCapturing ? (
            <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
              <Activity className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-green-900">Capture session active</p>
                <p className="text-xs text-green-700">
                  Started {new Date().toLocaleTimeString()}
                </p>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <Square className="h-5 w-5 text-gray-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">No active session</p>
                <p className="text-xs text-gray-700">
                  Start a new capture session to begin studying
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Study Progress */}
      {studyStats && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Study Progress</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{studyStats.totalSessions}</div>
              <div className="text-sm text-gray-600">Total Sessions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{studyStats.totalDocuments}</div>
              <div className="text-sm text-gray-600">Documents Indexed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{studyStats.totalQuestions}</div>
              <div className="text-sm text-gray-600">Questions Asked</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
