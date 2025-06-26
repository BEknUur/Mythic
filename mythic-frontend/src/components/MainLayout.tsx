import { useState } from 'react';
import Sidebar from './Sidebar';
import { Hero } from './Hero';
import { Steps } from './Steps';
import { Form } from './Form';
import { Footer } from './Footer';
import { useToast } from '@/hooks/use-toast';

interface MainLayoutProps {
  onStartScrape: (id: string) => void;
}

export function MainLayout({ onStartScrape }: MainLayoutProps) {
  const [currentView, setCurrentView] = useState('create-book');
  const { toast } = useToast();

  const handleNavigation = (action: string) => {
    setCurrentView(action);
    
    // Handle different navigation actions
    switch(action) {
      case 'create-book':
        // Default view - already shown
        break;
      case 'book-to-tiktok':
        toast({
          title: "🎬 Функция \"Книга → TikTok\" скоро будет доступна!",
          description: "Мы работаем над созданием коротких видео из ваших романтических книг для TikTok и Instagram.",
        });
        break;
      case 'write-fanfic':
        toast({
          title: "✍️ Функция \"Написать фанфик\" скоро будет доступна!",
          description: "Вы сможете создавать уникальные фанфики на основе фотографий и данных профиля.",
        });
        break;
      case 'generate-comic':
        toast({
          title: "🎨 Функция \"Сгенерировать комикс\" скоро будет доступна!",
          description: "Мы создадим комиксы из ключевых моментов вашей истории любви.",
        });
        break;
      case 'my-books':
        toast({
          title: "📚 Функция \"Мои книги\" скоро будет доступна!",
          description: "Здесь будут храниться все ваши созданные книги.",
        });
        break;
      case 'favorites':
        toast({
          title: "⭐ Функция \"Избранное\" скоро будет доступна!",
          description: "Сохраняйте лучшие моменты и страницы из ваших книг.",
        });
        break;
      case 'gallery':
        toast({
          title: "🖼️ Функция \"Мини-галерея\" скоро будет доступна!",
          description: "Быстрый просмотр всех изображений из ваших проектов.",
        });
        break;
      case 'settings':
        toast({
          title: "⚙️ Функция \"Настройки\" скоро будет доступна!",
          description: "Настройте стиль книг, языки и персонализацию.",
        });
        break;
      case 'help':
        toast({
          title: "❓ Нужна помощь?",
          description: "• Введите Instagram URL\n• Нажмите \"Создать книгу\"\n• Дождитесь обработки\n• Скачайте готовую книгу\n\nПо вопросам: t.me/beknur_10",
        });
        break;
    }
  };

  const renderMainContent = () => {
    switch(currentView) {
      case 'create-book':
      default:
        return (
          <>
            <Hero />
            <Steps />
            <Form onStartScrape={onStartScrape} />
            <Footer />
          </>
        );
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar onNavigation={handleNavigation} />
      
      <main className="flex-1 overflow-x-hidden">
        <div className="min-h-screen w-full">
          {renderMainContent()}
        </div>
      </main>
    </div>
  );
} 