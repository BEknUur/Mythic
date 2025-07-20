import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useState, useEffect } from 'react';

export function MainLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Проверяем размер экрана
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      // На десктопе автоматически открываем сайдбар
      if (window.innerWidth >= 768) {
        setIsSidebarOpen(true);
      } else {
        setIsSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Оверлей для мобильных устройств */}
      {isMobile && isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
      
      {/* Сайдбар */}
      <Sidebar 
        isOpen={isSidebarOpen} 
        onToggle={toggleSidebar}
        isMobile={isMobile}
      />
      
      {/* Основной контент */}
      <main className={`flex-1 transition-all duration-300 overflow-x-hidden ${
        isMobile ? 'ml-0' : isSidebarOpen ? 'ml-80' : 'ml-0'
      }`}>
        <div className="min-h-screen w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
} 