import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import {
  BookOpen,
  Video,
  PenTool,
  Palette,
  Library,
  Star,
  Image,
  Settings,
  HelpCircle,
  Menu,
  X,
  ChevronLeft
} from 'lucide-react';

interface SidebarProps {
  className?: string;
  onNavigate?: (action: string) => void;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<any>;
  badge?: string;
  action: string;
}

const mainActions: NavItem[] = [
  {
    id: 'create-book',
    label: 'Создать книгу',
    icon: BookOpen,
    action: 'create-book'
  },
  {
    id: 'book-to-tiktok',
    label: 'Книга → TikTok',
    icon: Video,
    badge: 'Новое',
    action: 'book-to-tiktok'
  },
  {
    id: 'write-fanfic',
    label: 'Написать фанфик',
    icon: PenTool,
    action: 'write-fanfic'
  },
  {
    id: 'generate-comic',
    label: 'Сгенерировать комикс',
    icon: Palette,
    action: 'generate-comic'
  }
];

const libraryItems: NavItem[] = [
  {
    id: 'my-books',
    label: 'Мои книги',
    icon: Library,
    action: 'my-books'
  },
  {
    id: 'favorites',
    label: 'Избранное',
    icon: Star,
    action: 'favorites'
  },
  {
    id: 'gallery',
    label: 'Мини-галерея',
    icon: Image,
    action: 'gallery'
  }
];

const settingsItems: NavItem[] = [
  {
    id: 'settings',
    label: 'Настройки',
    icon: Settings,
    action: 'settings'
  },
  {
    id: 'help',
    label: 'Помощь',
    icon: HelpCircle,
    action: 'help'
  }
];

export function Sidebar({ className, onNavigate }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState('create-book');
  const [readingProgress] = useState(65);

  const handleItemClick = (item: NavItem) => {
    setActiveItem(item.id);
    onNavigate?.(item.action);
  };

  const renderNavSection = (title: string, items: NavItem[]) => (
    <div className="space-y-2">
      {!isCollapsed && (
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide px-4 py-2">
          {title}
        </h3>
      )}
      <div className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = activeItem === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => handleItemClick(item)}
              className={cn(
                "w-full flex items-center gap-4 px-4 py-3 text-base font-medium transition-all duration-200 rounded-xl mx-3",
                "hover:bg-gray-100 dark:hover:bg-gray-800",
                "focus:outline-none focus-visible:ring-2 focus-visible:ring-pink-500/20 focus-visible:ring-offset-0",
                isActive 
                  ? "bg-pink-50 dark:bg-pink-900/20 text-pink-600 dark:text-pink-400 border border-pink-200 dark:border-pink-800 shadow-sm" 
                  : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100",
                isCollapsed ? "justify-center px-0 w-12 h-12 mx-auto" : "justify-start"
              )}
              title={isCollapsed ? item.label : undefined}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {!isCollapsed && (
                <>
                  <span className="flex-1 text-left truncate">{item.label}</span>
                  {item.badge && (
                    <Badge variant="destructive" className="h-6 px-2 text-xs font-medium bg-red-500 hover:bg-red-600">
                      {item.badge}
                    </Badge>
                  )}
                </>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile backdrop */}
      {!isCollapsed && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsCollapsed(true)}
        />
      )}
      
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-50 h-screen bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-all duration-300 ease-in-out",
          isCollapsed ? "w-20" : "w-80",
          "lg:relative lg:translate-x-0",
          !isCollapsed && "translate-x-0",
          isCollapsed && "-translate-x-full lg:translate-x-0",
          className
        )}
      >
        {/* Header */}
        <div className={cn(
          "flex items-center border-b border-gray-200 dark:border-gray-800 p-6",
          isCollapsed ? "justify-center" : "justify-between"
        )}>
          {!isCollapsed && (
            <div className="flex items-center gap-3">
              <span className="font-bold text-2xl text-gray-900 dark:text-white">
                Mythic AI
              </span>
            </div>
          )}
          
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="h-8 w-8 p-0 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            {isCollapsed ? (
              <Menu className="h-5 w-5" />
            ) : (
              <ChevronLeft className="h-5 w-5" />
            )}
          </Button>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-auto py-6 space-y-6">
          {renderNavSection("Основное", mainActions)}
          {!isCollapsed && <div className="border-t border-gray-200 dark:border-gray-700 mx-6" />}
          {renderNavSection("Библиотека", libraryItems)}
          {!isCollapsed && <div className="border-t border-gray-200 dark:border-gray-700 mx-6" />}
          {renderNavSection("Настройки", settingsItems)}
        </div>

        {/* Footer with progress */}
       
      </aside>

      {/* Mobile toggle button */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="fixed top-4 left-4 z-40 lg:hidden shadow-lg bg-white dark:bg-gray-900"
      >
        <Menu className="h-4 w-4" />
      </Button>
    </>
  );
} 