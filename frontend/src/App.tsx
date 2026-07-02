import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Home from './pages/Home';
import Capture from './pages/Capture';
import Study from './pages/Study';
import RealTimeStudy from './pages/RealTimeStudy';
import RealTimeStudyDebug from './pages/RealTimeStudyDebug';
import Settings from './pages/Settings';
import { CaptureProvider } from './hooks/useCapture';
import { StudyProvider } from './hooks/useStudy';
import { RealTimeStudyProvider } from './hooks/useRealTimeStudy';

function App() {
  return (
    <CaptureProvider>
      <StudyProvider>
        <RealTimeStudyProvider>
          <Router>
          <div className="min-h-screen bg-brand-cream">
            <Layout>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/capture" element={<Capture />} />
                <Route path="/study" element={<Study />} />
                <Route path="/realtime-study" element={<RealTimeStudy />} />
                <Route path="/realtime-study-debug" element={<RealTimeStudyDebug />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#576F72', // brand.slate
                  color: '#F0EBE3', // brand.cream
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#7D9D9C', // brand.teal
                    secondary: '#F0EBE3', // brand.cream
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: '#7D9D9C', // align icons with brand teal for consistency
                    secondary: '#F0EBE3',
                  },
                },
              }}
            />
          </div>
        </Router>
        </RealTimeStudyProvider>
      </StudyProvider>
    </CaptureProvider>
  );
}

export default App;

