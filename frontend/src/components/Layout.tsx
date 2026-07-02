import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Camera, 
  BookOpen, 
  Settings, 
  Menu, 
  X,
  Brain,
  Activity
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Activity },
    { name: 'Real-Time Study', href: '/realtime-study', icon: Brain },
    { name: 'Debug Capture', href: '/realtime-study-debug', icon: Activity },
    { name: 'Capture', href: '/capture', icon: Camera },
    { name: 'Study', href: '/study', icon: BookOpen },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const isHome = location.pathname === '/';

  if (isHome) {
    // Home page: no sidebar, full-bleed content
    return (
      <div className="flex h-screen bg-white">
        <div className="flex-1 flex flex-col overflow-hidden">
          <main className="flex-1 overflow-auto">
            <div className="h-full">
              {children}
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-brand-cream">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="absolute inset-0 bg-gray-600 opacity-75"></div>
        </div>
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between h-24 px-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Link to="/">
              <img
                src="/logo-catherine-ai-partner.png"
                alt="Catherine AI Partner"
                className="w-56 h-auto object-contain"
                onError={(e) => {
                  // Fallback to icon + text if image not found
                  const parent = (e.target as HTMLImageElement).parentElement;
                  if (parent) {
                    parent.innerHTML = '';
                    const span = document.createElement('span');
                    span.className = 'text-xl font-bold text-gray-900';
                    span.textContent = 'AI Study Partner';
                    parent.appendChild(span);
                  }
                }}
              />
            </Link>
          </div>
          <button
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-6 w-6 text-gray-500" />
          </button>
        </div>

        <nav className="mt-8 px-4">
          <div className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors duration-200
                    ${isActive(item.href)
                      ? 'bg-brand-sand text-brand-slate border-r-2 border-brand-teal'
                      : 'text-gray-600 hover:bg-brand-cream hover:text-gray-900'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Status indicator */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="flex items-center space-x-2 p-3 bg-green-50 rounded-lg border border-green-200">
            <Activity className="h-4 w-4 text-green-600" />
            <span className="text-sm text-green-700">System Online</span>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden lg:ml-0">
        {/* Top bar */}
        <header className="bg-white shadow-sm border-b border-gray-200 lg:hidden">
          <div className="flex items-center justify-between h-16 px-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-500 hover:text-gray-700"
            >
              <Menu className="h-6 w-6" />
            </button>
            <div className="flex items-center space-x-2">
              <Link to="/">
                <img
                  src="/logo-catherine-ai-partner.png"
                  alt="Catherine AI Partner"
                  className="w-40 h-auto object-contain"
                  onError={(e) => {
                    const parent = (e.target as HTMLImageElement).parentElement;
                    if (parent) {
                      parent.innerHTML = '<span class="text-lg font-semibold text-gray-900">AI Study Partner</span>';
                    }
                  }}
                />
              </Link>
            </div>
            <div className="w-6"></div> {/* Spacer for centering */}
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <div className="h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;

