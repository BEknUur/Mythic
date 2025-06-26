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
  Heart,
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
    <div className="space-y-1">
      {!isCollapsed && (
        <h3 className="text-xs font-medium text-muted-foreground/70 uppercase tracking-wide px-3 py-2">
          {title}
        </h3>
      )}
      <div className="space-y-0.5">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = activeItem === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => handleItemClick(item)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium transition-all duration-200 rounded-md mx-2",
                "hover:bg-accent/50 hover:text-accent-foreground",
                "focus:outline-none focus:ring-2 focus:ring-primary/20",
                isActive 
                  ? "bg-primary text-primary-foreground shadow-sm" 
                  : "text-muted-foreground hover:text-foreground",
                isCollapsed ? "justify-center px-0 w-10 h-10 mx-auto" : "justify-start"
              )}
              title={isCollapsed ? item.label : undefined}
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              {!isCollapsed && (
                <>
                  <span className="flex-1 text-left truncate">{item.label}</span>
                  {item.badge && (
                    <Badge variant="destructive" className="h-5 px-1.5 text-xs font-medium">
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
          "fixed left-0 top-0 z-50 h-full bg-background/95 backdrop-blur-xl border-r border-border/50 transition-all duration-300 ease-in-out shadow-lg",
          isCollapsed ? "w-16" : "w-64",
          "lg:relative lg:translate-x-0",
          !isCollapsed && "translate-x-0",
          isCollapsed && "-translate-x-full lg:translate-x-0",
          className
        )}
      >
        {/* Header */}
        <div className={cn(
          "flex items-center border-b border-border/50 p-4",
          isCollapsed ? "justify-center" : "justify-between"
        )}>
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-gradient-to-br from-pink-500 to-violet-600 rounded-lg flex items-center justify-center shadow-sm">
                <Heart className="h-4 w-4 text-white" />
              </div>
              <span className="font-bold text-lg bg-gradient-to-r from-pink-600 to-violet-600 bg-clip-text text-transparent">
                Mythic
              </span>
            </div>
          )}
          
          {isCollapsed && (
            <div className="w-7 h-7 bg-gradient-to-br from-pink-500 to-violet-600 rounded-lg flex items-center justify-center shadow-sm">
              <Heart className="h-4 w-4 text-white" />
            </div>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="h-7 w-7 p-0 hover:bg-accent/50"
          >
            {isCollapsed ? (
              <Menu className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-auto py-4 space-y-4">
          {renderNavSection("Основное", mainActions)}
          {!isCollapsed && <div className="border-t border-border/30 mx-4" />}
          {renderNavSection("Библиотека", libraryItems)}
          {!isCollapsed && <div className="border-t border-border/30 mx-4" />}
          {renderNavSection("Настройки", settingsItems)}
        </div>

        {/* Footer with progress */}
        {!isCollapsed && (
          <div className="border-t border-border/50 p-4 space-y-3">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground font-medium">Прогресс чтения</span>
                <span className="font-semibold text-primary">{readingProgress}%</span>
              </div>
              <Progress value={readingProgress} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {readingProgress}% завершено
              </p>
            </div>
          </div>
        )}
      </aside>

      {/* Mobile toggle button */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="fixed top-4 left-4 z-40 lg:hidden shadow-lg"
      >
        <Menu className="h-4 w-4" />
      </Button>
    </>
  );
} 