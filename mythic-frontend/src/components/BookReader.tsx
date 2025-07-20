import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@clerk/clerk-react';
import { api } from '@/lib/api';
import { ArrowLeft, Loader2 } from 'lucide-react';

interface BookReaderProps {
  bookId?: string;
  runId?: string;
  onBack: () => void;
}

export function BookReader({ bookId, runId, onBack }: BookReaderProps) {
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [cssContent, setCssContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const { getToken } = useAuth();
  const { toast } = useToast();
  const styleRef = useRef<HTMLStyleElement | null>(null);

  useEffect(() => {
    loadBookContent();
    // Очищаем стили при размонтировании
    return () => {
      if (styleRef.current && document.head.contains(styleRef.current)) {
        document.head.removeChild(styleRef.current);
      }
    };
    // eslint-disable-next-line
  }, [bookId, runId]);

  const loadBookContent = async () => {
    try {
      setLoading(true);
      const token = await getToken();
      let rawHtml: string;
      
      if (runId) {
        rawHtml = await api.getBookContent(runId, token || undefined);
      } else if (bookId) {
        const response = await fetch(api.getSavedBookViewUrl(bookId, token || undefined));
        rawHtml = await response.text();
      } else {
        throw new Error('Нужен bookId или runId');
      }

      // Извлекаем <style> и <body> из HTML
      const styleMatch = rawHtml.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
      const css = styleMatch ? styleMatch[1] : '';
      setCssContent(css);

      const bodyMatch = rawHtml.match(/<body[^>]*>([\s\S]*)<\/body>/i);
      let bodyContent = bodyMatch ? bodyMatch[1] : rawHtml;

      // Обрабатываем HTML для мобильной адаптивности
      bodyContent = processMobileHTML(bodyContent);
      
      setHtmlContent(bodyContent);

      // Вставляем адаптированные стили в <head>
      if (css) {
        const adaptedCSS = adaptCSSForMobile(css);
        const styleEl = document.createElement('style');
        styleEl.textContent = adaptedCSS;
        document.head.appendChild(styleEl);
        styleRef.current = styleEl;
      }

    } catch (error) {
      console.error('Ошибка загрузки книги:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить книгу',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Адаптируем HTML для мобильных устройств
  const processMobileHTML = (html: string) => {
    // Делаем все изображения адаптивными
    html = html.replace(/<img([^>]*?)>/gi, (match, attributes) => {
      // Добавляем классы для адаптивности если их нет
      if (!attributes.includes('class=')) {
        return `<img${attributes} class="mobile-responsive-image">`;
      } else {
        return match.replace(/class="([^"]*)"/, 'class="$1 mobile-responsive-image"');
      }
    });

    // Оборачиваем контент в мобильно-дружественный контейнер
    return `<div class="mobile-book-container">${html}</div>`;
  };

  // Адаптируем CSS для мобильных устройств
  const adaptCSSForMobile = (css: string) => {
    return css + `
      /* Мобильные улучшения */
      .mobile-book-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        line-height: 1.6 !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        hyphens: auto !important;
      }

      .mobile-responsive-image {
        max-width: 100% !important;
        height: auto !important;
        display: block !important;
        margin: 1rem auto !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
      }

      /* Адаптивная типографика */
      @media (max-width: 768px) {
        .mobile-book-container {
          font-size: 16px !important;
          line-height: 1.7 !important;
        }
        
        .mobile-book-container h1 {
          font-size: 1.75rem !important;
          line-height: 1.3 !important;
          margin-bottom: 1.5rem !important;
          text-align: center !important;
        }
        
        .mobile-book-container h2 {
          font-size: 1.5rem !important;
          line-height: 1.4 !important;
          margin: 1.5rem 0 1rem 0 !important;
        }
        
        .mobile-book-container h3 {
          font-size: 1.25rem !important;
          line-height: 1.4 !important;
          margin: 1.25rem 0 0.75rem 0 !important;
        }
        
        .mobile-book-container p {
          margin-bottom: 1rem !important;
          text-align: justify !important;
          word-spacing: 0.1em !important;
        }
        
        .mobile-book-container blockquote {
          margin: 1rem 0 !important;
          padding: 0.75rem !important;
          font-style: italic !important;
          border-left: 3px solid #f59e0b !important;
          background-color: #fef3c7 !important;
          border-radius: 4px !important;
        }
      }

      /* Улучшения для очень маленьких экранов */
      @media (max-width: 480px) {
        .mobile-book-container {
          font-size: 15px !important;
        }
        
        .mobile-book-container h1 {
          font-size: 1.5rem !important;
        }
        
        .mobile-book-container h2 {
          font-size: 1.25rem !important;
        }
        
        .mobile-book-container h3 {
          font-size: 1.125rem !important;
        }
      }

      /* Исправляем возможные конфликты стилей */
      .mobile-book-container * {
        max-width: 100% !important;
        box-sizing: border-box !important;
      }

      .mobile-book-container table {
        width: 100% !important;
        overflow-x: auto !important;
        display: block !important;
        white-space: nowrap !important;
      }

      .mobile-book-container pre {
        white-space: pre-wrap !important;
        word-break: break-all !important;
      }
    `;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center mobile-padding">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600 dark:text-gray-400" />
          <p className="text-gray-600 dark:text-gray-400">Загружаем вашу книгу...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      {/* Мобильно-дружественная шапка */}
      <div className="sticky top-0 z-10 bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800 safe-area-top">
        <div className="mobile-padding py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={onBack}
              className="text-gray-700 dark:text-gray-300 hover:text-black dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 touch-target"
              size="sm"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Назад</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Контент книги */}
      <div className="flex-1 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-gray-900 dark:to-gray-800">
        <div className="responsive-container py-4 sm:py-6 lg:py-8">
          <div className="mx-auto max-w-4xl">
            {/* Мобильно-адаптированный контейнер книги */}
            <div className="bg-white dark:bg-gray-950 rounded-lg shadow-lg overflow-hidden">
              <div 
                className="book-content mobile-padding py-6 sm:py-8 lg:py-12"
                dangerouslySetInnerHTML={{ __html: htmlContent }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}