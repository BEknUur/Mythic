import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import { LanguageSwitcher } from './LanguageSwitcher';
import { useState, useEffect } from 'react';

export function MainLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const location = useLocation();

  // Закрываем сайдбар при смене роута на мобильных
  useEffect(() => {
    if (isMobile && isSidebarOpen) {
      setIsSidebarOpen(false);
    }
  }, [location.pathname, isMobile]);

  // Проверяем размер экрана
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      // Сайдбар остается закрытым по умолчанию на всех устройствах
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  // Закрываем сайдбар при нажатии Escape на мобильных
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isMobile && isSidebarOpen) {
        closeSidebar();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isMobile, isSidebarOpen]);

  // Предотвращаем скролл body когда сайдбар открыт на мобильных
  useEffect(() => {
    if (isMobile && isSidebarOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isMobile, isSidebarOpen]);

  // Обработчик клика по оверлею с множественными способами закрытия
  const handleOverlayClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    closeSidebar();
  };

  const handleOverlayTouch = (e: React.TouchEvent) => {
    e.preventDefault();
    e.stopPropagation();
    closeSidebar();
  };

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Language Switcher - Fixed position in top-right corner */}
      <div className="fixed top-4 right-4 z-50">
        <LanguageSwitcher />
      </div>

      {/* Улучшенный оверлей для мобильных устройств */}
      {isMobile && isSidebarOpen && (
        <div 
          className="sidebar-overlay"
          onClick={handleOverlayClick}
          onTouchStart={handleOverlayTouch}
          onTouchEnd={handleOverlayTouch}
          onMouseDown={handleOverlayClick}
          aria-label="Закрыть меню"
        />
      )}
      
      {/* Сайдбар */}
      <Sidebar 
        isOpen={isSidebarOpen} 
        onToggle={toggleSidebar}
        isMobile={isMobile}
      />
      
      {/* Основной контент */}
      <main className={`flex-1 transition-all duration-300 overflow-x-hidden`}>
        <div className="min-h-screen w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
} 