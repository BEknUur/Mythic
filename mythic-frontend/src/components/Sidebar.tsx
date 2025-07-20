import React from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
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
  Sparkles,
  DollarSign,
  LogOut,
  User,
  Compass,
  Bot,
  BookHeart,
  BadgeHelp,
  Ticket,
  FileText,
  LayoutGrid,
  X
} from 'lucide-react';
import { TOUR_STEP_IDS } from './ui/tour';
import { useTour } from './ui/tour';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  isMobile: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle, isMobile }) => {
  const { startTour } = useTour();
  const location = useLocation();

  return (
    <>
      {/* Сайдбар */}
      <aside className={cn(
        "fixed left-0 top-0 z-50 h-full w-80 bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800 transition-transform duration-300 ease-in-out",
        isOpen ? "translate-x-0" : "-translate-x-full",
        !isMobile && "md:relative md:translate-x-0"
      )}>
        {/* Хедер сайдбара */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-3">
              <img src="/logo.png" alt="Mythic AI Logo" className="h-10 w-10" />
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-gray-50">
                  Mythic AI
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">Создаём истории</p>
              </div>
            </Link>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="h-9 w-9 p-0 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl"
          >
            {isMobile ? (
              <X className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            ) : (
              <ChevronLeft className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            )}
          </Button>
        </div>

        {/* Навигация */}
        <div className="p-4 space-y-6 overflow-y-auto h-[calc(100vh-200px)]">
          {/* Секция создания */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-3">
              Создать
            </h3>
            <div className="space-y-2">
              <Button 
                asChild 
                variant="ghost" 
                className="w-full justify-start h-12 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-50 transition-all duration-200 rounded-xl px-4 tour-step-2 touch-target"
                onClick={isMobile ? onToggle : undefined}
              >
                <Link to="/generate">
                  <BookOpen className="h-5 w-5 text-purple-500" />
                  <span className="ml-3 font-medium">Создать книгу</span>
                </Link>
              </Button>

              <Button 
                asChild 
                variant="ghost" 
                className="w-full justify-start h-12 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-50 transition-all duration-200 rounded-xl px-4 touch-target"
                onClick={isMobile ? onToggle : undefined}
              >
                <Link to="/tiktok">
                  <Video className="h-5 w-5 text-red-500" />
                  <div className="flex items-center justify-between w-full ml-3">
                    <span className="font-medium">Книга → TikTok</span>
                    <Badge variant="secondary" className="bg-red-100 text-red-700 text-xs px-2 py-1 dark:bg-red-900/50 dark:text-red-300">
                      Новое
                    </Badge>
                  </div>
                </Link>
              </Button>
            </div>
          </div>

          {/* Секция библиотеки */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-3">
              Библиотека
            </h3>
            <div className="space-y-2">
              <Button 
                asChild 
                variant="ghost" 
                className="w-full justify-start h-12 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-50 transition-all duration-200 rounded-xl px-4 touch-target" 
                id={TOUR_STEP_IDS.MY_BOOKS_BUTTON}
                onClick={isMobile ? onToggle : undefined}
              >
                <Link to="/library">
                  <Library className="h-5 w-5 text-amber-500" />
                  <span className="ml-3 font-medium">Мои книги</span>
                </Link>
              </Button>
              
              <Button 
                asChild 
                variant="ghost" 
                className="w-full justify-start h-12 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-50 transition-all duration-200 rounded-xl px-4 touch-target"
                onClick={isMobile ? onToggle : undefined}
              >
                <Link to="/pricing">
                  <DollarSign className="h-5 w-5 text-green-500" />
                  <span className="ml-3 font-medium">Тарифы</span>
                </Link>
              </Button>
            </div>
          </div>

          {/* Секция помощи */}
          <div>
            <div className="space-y-2">
              <Button 
                asChild 
                variant="ghost" 
                className="w-full justify-start h-12 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-50 transition-all duration-200 rounded-xl px-4 touch-target"
                onClick={isMobile ? onToggle : undefined}
              >
                <Link to="/help">
                  <HelpCircle className="h-5 w-5 text-gray-500" />
                  <span className="ml-3 font-medium">Помощь</span>
                </Link>
              </Button>
            </div>
          </div>
        </div>

        {/* Футер - всегда показывается когда сайдбар открыт */}
        <div className="absolute bottom-6 left-4 right-4">
          <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <Sparkles className="h-5 w-5 text-purple-500 mr-2" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Mythic AI</span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              Превращаем мысли в истории
            </p>
            <div className="text-xs text-gray-400 dark:text-gray-500">
              <p>Связь: t.me/beknur_10</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Кнопка меню для мобильных - показывается только когда сайдбар скрыт */}
      {!isOpen && (
        <Button
          variant="outline"
          size="icon"
          className="fixed top-4 left-4 z-50 bg-white dark:bg-gray-900 dark:border-gray-800 text-gray-800 dark:text-gray-200 shadow-lg touch-target"
          onClick={onToggle}
        >
          <Menu className="h-4 w-4" />
          <span className="sr-only">Открыть меню</span>
        </Button>
      )}
    </>
  );
};

export default Sidebar; 