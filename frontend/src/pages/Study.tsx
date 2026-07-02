import React, { useState, useEffect, useCallback } from 'react';
import { 
  MessageCircle, 
  FileText, 
  BookOpen, 
  HelpCircle, 
  Lightbulb,
  Download,
  Send,
  Loader2,
  Brain,
  Zap,
  Target
} from 'lucide-react';
import { useStudy } from '../hooks/useStudy';
import { useCapture } from '../hooks/useCapture';
import toast from 'react-hot-toast';

const Study: React.FC = () => {
  const { 
    askQuestion, 
    generateSummary, 
    generateFlashcards, 
    generateQuiz,
    extractKeyConcepts,
    createStudyPlan,
    exportSession
  } = useStudy();
  
  const { sessionId, getExtractedContent } = useCapture();

  const [activeTab, setActiveTab] = useState<'chat' | 'summary' | 'flashcards' | 'quiz' | 'concepts' | 'plan'>('chat');
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ type: 'user' | 'ai', content: string, timestamp: Date }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [content, setContent] = useState('');
  const [sessions, setSessions] = useState<any[]>([]);
  const [selectedSession, setSelectedSession] = useState<string>('');

  const loadSessions = useCallback(async () => {
    try {
      // This would typically come from an API endpoint
      // For now, we'll use the current session if available
      if (sessionId) {
        setSessions([{ id: sessionId, name: `Session ${sessionId.slice(0, 8)}` }]);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  }, [sessionId]);

  useEffect(() => {
    loadSessions();
    if (sessionId) {
      setSelectedSession(sessionId);
    }
  }, [sessionId, loadSessions]);

  const handleAskQuestion = async () => {
    if (!question.trim()) return;

    const userMessage = { type: 'user' as const, content: question, timestamp: new Date() };
    setChatHistory(prev => [...prev, userMessage]);
    setQuestion('');
    setIsLoading(true);

    try {
      const response = await askQuestion(question, selectedSession || undefined);
      const aiMessage = { 
        type: 'ai' as const, 
        content: response.content, 
        timestamp: new Date() 
      };
      setChatHistory(prev => [...prev, aiMessage]);
    } catch (error) {
      toast.error('Failed to get answer');
      console.error('Question error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!content.trim()) {
      toast.error('Please enter content to summarize');
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateSummary(content);
      setContent(response.content);
      toast.success('Summary generated successfully!');
    } catch (error) {
      toast.error('Failed to generate summary');
      console.error('Summary error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateFlashcards = async () => {
    if (!content.trim()) {
      toast.error('Please enter content for flashcards');
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateFlashcards(content);
      setContent(response.content);
      toast.success('Flashcards generated successfully!');
    } catch (error) {
      toast.error('Failed to generate flashcards');
      console.error('Flashcards error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!content.trim()) {
      toast.error('Please enter content for quiz');
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateQuiz(content);
      setContent(response.content);
      toast.success('Quiz generated successfully!');
    } catch (error) {
      toast.error('Failed to generate quiz');
      console.error('Quiz error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExtractConcepts = async () => {
    if (!content.trim()) {
      toast.error('Please enter content to extract concepts from');
      return;
    }

    setIsLoading(true);
    try {
      const response = await extractKeyConcepts(content);
      setContent(response.content);
      toast.success('Key concepts extracted successfully!');
    } catch (error) {
      toast.error('Failed to extract key concepts');
      console.error('Concepts error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateStudyPlan = async () => {
    const topics = content.split('\n').filter(topic => topic.trim());
    if (topics.length === 0) {
      toast.error('Please enter topics for the study plan');
      return;
    }

    setIsLoading(true);
    try {
      const response = await createStudyPlan(topics);
      setContent(response.content);
      toast.success('Study plan created successfully!');
    } catch (error) {
      toast.error('Failed to create study plan');
      console.error('Study plan error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportSession = async () => {
    if (!selectedSession) {
      toast.error('Please select a session to export');
      return;
    }

    try {
      const response = await exportSession(selectedSession, 'json');
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session-${selectedSession}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Session exported successfully!');
    } catch (error) {
      toast.error('Failed to export session');
      console.error('Export error:', error);
    }
  };

  const tabs = [
    { id: 'chat', name: 'AI Chat', icon: MessageCircle },
    { id: 'summary', name: 'Summary', icon: FileText },
    { id: 'flashcards', name: 'Flashcards', icon: BookOpen },
    { id: 'quiz', name: 'Quiz', icon: HelpCircle },
    { id: 'concepts', name: 'Key Concepts', icon: Lightbulb },
    { id: 'plan', name: 'Study Plan', icon: Target }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-brand-slate">Study Assistant</h1>
          <p className="text-brand-slate mt-1 opacity-80">AI-powered study tools and content analysis</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedSession}
            onChange={(e) => setSelectedSession(e.target.value)}
            className="input"
          >
            <option value="">Select Session</option>
            {sessions.map(session => (
              <option key={session.id} value={session.id}>
                {session.name}
              </option>
            ))}
          </select>
          <button
            onClick={handleExportSession}
            disabled={!selectedSession}
            className="btn-outline"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="card p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Study Tools</h2>
            <nav className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-brand-sand text-brand-slate'
                        : 'text-gray-600 hover:bg-brand-cream'
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-3" />
                    {tab.name}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {activeTab === 'chat' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-brand-slate mb-4 flex items-center">
                <Brain className="h-5 w-5 mr-2 text-brand-teal" />
                AI Study Assistant
              </h2>
              
              {/* Chat History */}
              <div className="h-96 overflow-y-auto border border-brand-sand rounded-lg p-4 mb-4 bg-brand-cream elev-1">
                {chatHistory.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <MessageCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>Start a conversation with your AI study assistant</p>
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
                              : 'bg-white text-gray-900 border border-gray-200'
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

              {/* Question Input */}
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
                  placeholder="Ask a question about your study content..."
                  className="input flex-1"
                  disabled={isLoading}
                />
                <button
                  onClick={handleAskQuestion}
                  disabled={isLoading || !question.trim()}
                  className="btn-primary"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}

          {activeTab !== 'chat' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                {React.createElement(tabs.find(t => t.id === activeTab)?.icon || FileText, { 
                  className: "h-5 w-5 mr-2 text-blue-600" 
                })}
                {tabs.find(t => t.id === activeTab)?.name}
              </h2>

              {/* Content Input */}
              <div className="mb-4">
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder={
                    activeTab === 'summary' ? 'Enter content to summarize...' :
                    activeTab === 'flashcards' ? 'Enter content to create flashcards from...' :
                    activeTab === 'quiz' ? 'Enter content to create quiz questions from...' :
                    activeTab === 'concepts' ? 'Enter content to extract key concepts from...' :
                    activeTab === 'plan' ? 'Enter topics for study plan (one per line)...' :
                    'Enter content...'
                  }
                  className="textarea w-full h-32"
                  disabled={isLoading}
                />
                {!content && (
                  <div className="mt-2">
                    <button
                      onClick={async () => {
                        try {
                          const data = await getExtractedContent();
                          const text = (data?.content || []).map((c: any) => (typeof c === 'string' ? c : (c?.content || ''))).filter(Boolean).join('\n');
                          if (text) {
                            setContent(text);
                            toast.success('Loaded content from current session');
                          } else {
                            toast.error('No extracted content available yet');
                          }
                        } catch {}
                      }}
                      className="btn-outline"
                    >
                      Load from current session
                    </button>
                  </div>
                )}
              </div>

              {/* Action Button */}
              <div className="flex justify-between items-center">
                <button
                  onClick={
                    activeTab === 'summary' ? handleGenerateSummary :
                    activeTab === 'flashcards' ? handleGenerateFlashcards :
                    activeTab === 'quiz' ? handleGenerateQuiz :
                    activeTab === 'concepts' ? handleExtractConcepts :
                    activeTab === 'plan' ? handleCreateStudyPlan :
                    () => {}
                  }
                  disabled={isLoading || !content.trim()}
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

                {content && (
                  <button
                    onClick={() => {
                      const blob = new Blob([content], { type: 'text/plain' });
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
              {content && (
                <div className="mt-6 p-4 bg-brand-cream rounded-lg border border-brand-sand elev-1">
                  <h3 className="text-sm font-medium text-brand-slate mb-2">Generated Content:</h3>
                  <div className="prose prose-sm max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-brand-slate">{content}</pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Study;
