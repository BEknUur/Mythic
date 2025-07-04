import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

import { Button } from '@/components/ui/button';
import {
  BookOpen,
  Video,
  PenTool,
  FileImage,
  Library,
  Image,
  Settings,
  HelpCircle,
  Menu,
  ChevronLeft,
  Sparkles
} from 'lucide-react';
import './FloatingBook.css';

interface SidebarProps {
  onNavigation: (section: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onNavigation }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleNavClick = (section: string) => {
    onNavigation(section);
  };

  return (
    <>
      {/* Floating Books Animation with beautiful covers */}
      <div className="floating-book-container">
        {/* Book 1 - Сердца в цифровом мире */}
        <div className="floating-book">
          <div className="book-pages"></div>
          
        </div>
        
        {/* Book 2 - Мистерии прошлого */}
        <div className="floating-book">
          <div className="book-pages"></div>
          
        </div>
        
        {/* Book 3 - Космические приключения */}
        <div className="floating-book">
          <div className="book-pages"></div>
         
        </div>
        
        {/* Book 4 - Философия души */}
        <div className="floating-book">
          <div className="book-pages"></div>
        
        </div>
        
        {/* Book 5 - Магия повседневности */}
        <div className="floating-book">
          <div className="book-pages"></div>
         
        </div>
      </div>

      {/* Mobile backdrop */}
      {!isCollapsed && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden" 
          onClick={toggleSidebar}
        />
      )}
      
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 h-full bg-white border-r border-gray-200 shadow-lg transition-all duration-300 ease-in-out z-50",
          isCollapsed ? "-translate-x-full" : "w-80"
        )}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                <BookOpen className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  Mythic AI
                </h1>
                <p className="text-sm text-gray-500">Создаём истории</p>
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleSidebar}
              className="h-9 w-9 p-0 hover:bg-gray-100 rounded-xl"
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Navigation */}
        <div className="p-4 space-y-6 overflow-y-auto h-[calc(100vh-200px)]">
          {/* Create Section */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Создать
            </h3>
            <div className="space-y-2">
              <Button
                variant="ghost"
                className="w-full justify-start h-12 text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 rounded-xl px-4"
                onClick={() => handleNavClick('create-book')}
              >
                <BookOpen className="h-5 w-5 text-purple-500" />
                <span className="ml-3 font-medium">Создать книгу</span>
              </Button>

              <Button
                variant="ghost"
                className="w-full justify-start h-12 text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 rounded-xl px-4"
                onClick={() => handleNavClick('book-to-tiktok')}
              >
                <Video className="h-5 w-5 text-red-500" />
                <div className="flex items-center justify-between w-full ml-3">
                  <span className="font-medium">Книга → TikTok</span>
                  <Badge variant="secondary" className="bg-red-100 text-red-700 text-xs px-2 py-1">
                    Новое
                  </Badge>
                </div>
              </Button>

              <Button
                variant="ghost"
                className="w-full justify-start h-12 text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 rounded-xl px-4"
                onClick={() => handleNavClick('write-fanfic')}
              >
                <PenTool className="h-5 w-5 text-blue-500" />
                <span className="ml-3 font-medium">Написать фанфик</span>
              </Button>

              <Button
                variant="ghost"
                className="w-full justify-start h-12 text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 rounded-xl px-4"
                onClick={() => handleNavClick('generate-comic')}
              >
                <FileImage className="h-5 w-5 text-green-500" />
                <span className="ml-3 font-medium">Генерировать комикс</span>
              </Button>
            </div>
          </div>

          {/* Library Section */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Библиотека
            </h3>
            <div className="space-y-2">
              <Button
                variant="ghost"
                className="w-full justify-start h-12 text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 rounded-xl px-4"
                onClick={() => handleNavClick('my-books')}
              >
                <Library className="h-5 w-5 text-amber-500" />
                <span className="ml-3 font-medium">Мои книги</span>
              </Button>

              <Button
                variant="ghost"
                className="w-full justify-start h-12 text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 rounded-xl px-4"
                onClick={() => handleNavClick('gallery')}
              >
                <Image className="h-5 w-5 text-indigo-500" />
                <span className="ml-3 font-medium">Галерея</span>
              </Button>
            </div>
          </div>

          {/* Settings Section */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Настройки
            </h3>
            <div className="space-y-2">
              <Button
                variant="ghost"
                className="w-full justify-start h-12 text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 rounded-xl px-4"
                onClick={() => handleNavClick('settings')}
              >
                <Settings className="h-5 w-5 text-gray-500" />
                <span className="ml-3 font-medium">Настройки</span>
              </Button>

              <Button
                variant="ghost"
                className="w-full justify-start h-12 text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200 rounded-xl px-4"
                onClick={() => handleNavClick('help')}
              >
                <HelpCircle className="h-5 w-5 text-gray-500" />
                <span className="ml-3 font-medium">Помощь</span>
              </Button>
            </div>
          </div>
        </div>

        {/* Footer - теперь всегда показывается когда сайдбар открыт */}
        <div className="absolute bottom-6 left-4 right-4">
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <Sparkles className="h-5 w-5 text-purple-500 mr-2" />
              <span className="text-sm font-medium text-gray-700">Mythic AI</span>
            </div>
            <p className="text-xs text-gray-500 mb-3">
              Превращаем мысли в истории
            </p>
            <div className="text-xs text-gray-400">
              <p>Связь: t.me/beknur_10</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile menu button - показывается только когда сайдбар скрыт */}
      {isCollapsed && (
        <Button
          variant="outline"
          size="icon"
          className="fixed top-4 left-4 z-50 bg-white shadow-lg"
          onClick={toggleSidebar}
        >
          <Menu className="h-4 w-4" />
        </Button>
      )}
    </>
  );
};

export default Sidebar; 