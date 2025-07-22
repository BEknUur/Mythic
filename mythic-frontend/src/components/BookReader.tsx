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

  // Улучшенная функция для обработки HTML на мобильных
  const processMobileHTML = (html: string) => {
    // Добавляем мобильно-дружественные классы к элементам
    let processedHtml = html
      .replace(/<p([^>]*)>/g, '<p$1 class="mobile-text leading-relaxed mb-4">')
      .replace(/<h1([^>]*)>/g, '<h1$1 class="text-2xl sm:text-3xl lg:text-4xl font-heading mb-6 text-center">')
      .replace(/<h2([^>]*)>/g, '<h2$1 class="text-xl sm:text-2xl lg:text-3xl font-heading mb-4 mt-8">')
      .replace(/<h3([^>]*)>/g, '<h3$1 class="text-lg sm:text-xl lg:text-2xl font-heading mb-3 mt-6">')
      .replace(/<img([^>]*)>/g, '<img$1 class="w-full max-w-md mx-auto rounded-lg shadow-md my-6">');

    return processedHtml;
  };

  // Улучшенная функция для адаптации CSS на мобильных
  const adaptCSSForMobile = (css: string) => {
    return css + `
      /* Мобильная адаптация для книжного контента */
      .book-content {
        font-size: 16px !important;
        line-height: 1.8 !important;
        padding: 1.5rem !important;
        word-wrap: break-word !important;
        /* Менее агрессивные переносы для русского языка */
        hyphens: manual !important;
        -webkit-hyphens: manual !important;
        -moz-hyphens: manual !important;
        -ms-hyphens: manual !important;
        overflow-wrap: break-word !important;
        word-break: normal !important;
        text-rendering: optimizeLegibility !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
      }
      
      @media (max-width: 640px) {
        .book-content {
          font-size: 16px !important;
          line-height: 1.8 !important;
          padding: 1rem !important;
        }
        
        .book-content * {
          max-width: 100% !important;
          word-wrap: break-word !important;
          overflow-wrap: break-word !important;
          /* Только ручные переносы на мобильных для лучшей читаемости */
          hyphens: manual !important;
          -webkit-hyphens: manual !important;
          -moz-hyphens: manual !important;
          word-break: normal !important;
        }
        
        .book-content p {
          margin-bottom: 1.75rem !important;
        }
      }
      
      @media (min-width: 640px) {
        .book-content {
          font-size: 18px !important;
          padding: 2rem !important;
        }
        
        /* На больших экранах можем использовать автоматические переносы */
        .book-content p,
        .book-content li,
        .book-content blockquote {
          hyphens: auto !important;
          -webkit-hyphens: auto !important;
          -moz-hyphens: auto !important;
        }
      }
      
      @media (min-width: 768px) {
        .book-content {
          font-size: 18px !important;
          padding: 2.5rem !important;
        }
      }
      
      @media (min-width: 1024px) {
        .book-content {
          font-size: 19px !important;
          padding: 3rem !important;
        }
      }
      
      .book-content h1, .book-content h2, .book-content h3, .book-content h4 {
        font-family: 'Playfair Display', serif !important;
        line-height: 1.2 !important;
        margin-top: 2rem !important;
        margin-bottom: 1.5rem !important;
        word-wrap: break-word !important;
        /* Заголовки не переносим */
        hyphens: none !important;
        -webkit-hyphens: none !important;
        -moz-hyphens: none !important;
        overflow-wrap: break-word !important;
        word-break: normal !important;
        max-width: 100% !important;
      }
      
      .book-content h1 {
        font-size: 1.875rem !important;
        text-align: center !important;
        margin-bottom: 2.5rem !important;
        margin-top: 1rem !important;
        line-height: 1.1 !important;
      }
      
      @media (max-width: 640px) {
        .book-content h1 {
          font-size: 1.75rem !important;
          margin-bottom: 2rem !important;
        }
      }
      
      @media (min-width: 640px) {
        .book-content h1 {
          font-size: 2.25rem !important;
        }
      }
      
      @media (min-width: 768px) {
        .book-content h1 {
          font-size: 2.5rem !important;
        }
      }
      
      .book-content h2 {
        font-size: 1.5rem !important;
        border-bottom: 2px solid #e5e7eb !important;
        padding-bottom: 0.75rem !important;
        margin-top: 2.5rem !important;
      }
      
      @media (max-width: 640px) {
        .book-content h2 {
          font-size: 1.375rem !important;
          margin-top: 2rem !important;
        }
      }
      
      @media (min-width: 640px) {
        .book-content h2 {
          font-size: 1.75rem !important;
        }
      }
      
      @media (min-width: 768px) {
        .book-content h2 {
          font-size: 2rem !important;
        }
      }
      
      .book-content h3 {
        font-size: 1.25rem !important;
        margin-top: 2rem !important;
      }
      
      @media (max-width: 640px) {
        .book-content h3 {
          font-size: 1.125rem !important;
          margin-top: 1.5rem !important;
        }
      }
      
      @media (min-width: 640px) {
        .book-content h3 {
          font-size: 1.5rem !important;
        }
      }
      
      @media (min-width: 768px) {
        .book-content h3 {
          font-size: 1.625rem !important;
        }
      }
      
      .book-content p {
        margin-bottom: 1.5rem !important;
        text-align: justify !important;
        word-wrap: break-word !important;
        /* Менее агрессивные переносы */
        hyphens: manual !important;
        -webkit-hyphens: manual !important;
        -moz-hyphens: manual !important;
        -ms-hyphens: manual !important;
        overflow-wrap: break-word !important;
        word-break: normal !important;
        line-height: 1.75 !important;
        text-justify: inter-word !important;
        max-width: 100% !important;
      }
      
      @media (max-width: 640px) {
        .book-content p {
          text-align: left !important;
          line-height: 1.8 !important;
          margin-bottom: 1.75rem !important;
        }
      }
      
      .book-content img {
        max-width: 100% !important;
        height: auto !important;
        border-radius: 8px !important;
        margin: 2rem auto !important;
        display: block !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
      }
      
      @media (max-width: 640px) {
        .book-content img {
          margin: 1.5rem auto !important;
        }
      }
      
      .book-content blockquote {
        border-left: 4px solid #f59e0b !important;
        padding: 1.5rem !important;
        margin: 2rem 0 !important;
        background-color: #fef3c7 !important;
        border-radius: 8px !important;
        font-style: italic !important;
        word-wrap: break-word !important;
        hyphens: manual !important;
        -webkit-hyphens: manual !important;
        -moz-hyphens: manual !important;
        overflow-wrap: break-word !important;
        word-break: normal !important;
        line-height: 1.6 !important;
        max-width: 100% !important;
      }
      
      @media (max-width: 640px) {
        .book-content blockquote {
          padding: 1rem !important;
          margin: 1.5rem 0 !important;
        }
      }
      
      .book-content ul, .book-content ol {
        margin-bottom: 1.5rem !important;
        padding-left: 2rem !important;
        max-width: 100% !important;
      }
      
      @media (max-width: 640px) {
        .book-content ul, .book-content ol {
          padding-left: 1.5rem !important;
        }
      }
      
      .book-content li {
        margin-bottom: 0.75rem !important;
        word-wrap: break-word !important;
        hyphens: manual !important;
        -webkit-hyphens: manual !important;
        -moz-hyphens: manual !important;
        overflow-wrap: break-word !important;
        word-break: normal !important;
        line-height: 1.6 !important;
      }
      
      .book-content .chapter {
        page-break-before: always !important;
        margin-top: 3rem !important;
        padding-top: 2rem !important;
        border-top: 1px solid #e5e7eb !important;
      }
      
      @media (max-width: 640px) {
        .book-content .chapter {
          margin-top: 2rem !important;
          padding-top: 1.5rem !important;
        }
      }
      
      /* Дополнительные стили для Table of Contents */
      .book-content .toc,
      .book-content .table-of-contents {
        padding: 1.5rem !important;
        background-color: #f9fafb !important;
        border-radius: 8px !important;
        margin: 2rem 0 !important;
      }
      
      @media (max-width: 640px) {
        .book-content .toc,
        .book-content .table-of-contents {
          padding: 1rem !important;
          margin: 1.5rem 0 !important;
        }
      }
      
      .book-content .toc h1,
      .book-content .toc h2,
      .book-content .table-of-contents h1,
      .book-content .table-of-contents h2 {
        text-align: center !important;
        margin-bottom: 1.5rem !important;
        color: #1f2937 !important;
      }
      
      .book-content .toc ul,
      .book-content .table-of-contents ul {
        list-style: none !important;
        padding-left: 0 !important;
      }
      
      .book-content .toc li,
      .book-content .table-of-contents li {
        padding: 0.5rem 0 !important;
        border-bottom: 1px solid #e5e7eb !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
        hyphens: none !important;
        -webkit-hyphens: none !important;
        -moz-hyphens: none !important;
      }
      
      @media (max-width: 640px) {
        .book-content .toc li,
        .book-content .table-of-contents li {
          font-size: 0.95rem !important;
          padding: 0.4rem 0 !important;
        }
      }
      
      /* Улучшенная типографика для мобильных */
      @media (max-width: 767px) {
        .book-content {
          font-size: 16px !important;
          line-height: 1.8 !important;
        }
        
        .book-content h1 {
          font-size: 1.75rem !important;
          line-height: 1.1 !important;
        }
        
        .book-content h2 {
          font-size: 1.375rem !important;
          line-height: 1.2 !important;
        }
        
        .book-content h3 {
          font-size: 1.125rem !important;
          line-height: 1.3 !important;
        }
      }
      
      /* Безопасные области для мобильных устройств */
      @supports (padding: max(0px)) {
        .book-content {
          padding-left: max(1rem, env(safe-area-inset-left)) !important;
          padding-right: max(1rem, env(safe-area-inset-right)) !important;
          padding-top: max(1rem, env(safe-area-inset-top)) !important;
          padding-bottom: max(1rem, env(safe-area-inset-bottom)) !important;
        }
      }
      
      /* Предотвращение горизонтального скролла */
      .book-content * {
        max-width: 100% !important;
        box-sizing: border-box !important;
      }
      
      /* Улучшенная производительность на мобильных */
      @media (max-width: 768px) {
        .book-content {
          transform: translateZ(0) !important;
          backface-visibility: hidden !important;
          perspective: 1000px !important;
        }
      }
    `;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-50 dark:bg-gradient-to-br dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center space-y-4 mobile-padding">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600 dark:text-gray-400" />
          <p className="text-gray-600 dark:text-gray-400 mobile-text">Загружаем вашу книгу...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-50 dark:bg-gradient-to-br dark:from-gray-900 dark:to-gray-800 flex flex-col mobile-container scroll-smooth">
      {/* Улучшенная мобильно-дружественная шапка */}
      <div className="sticky top-0 z-10 bg-white/95 dark:bg-gray-950/95 border-b border-gray-200 dark:border-gray-800 backdrop-blur-sm mobile-safe-area">
        <div className="responsive-container py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={onBack}
              className="text-gray-700 dark:text-gray-300 hover:text-black dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 touch-target touch-optimized"
              size="sm"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Назад к библиотеке</span>
              <span className="sm:hidden">Назад</span>
            </Button>
            
            {/* Индикатор прогресса чтения на мобильных */}
            <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              <span className="hidden sm:inline">Ваша книга</span>
              <span className="sm:hidden">📖</span>
            </div>
          </div>
        </div>
      </div>

      {/* Улучшенный контент книги */}
      <div className="flex-1 overflow-x-hidden">
        <div className="responsive-container py-4 sm:py-6 lg:py-8">
          <div className="mx-auto max-w-4xl">
            {/* Улучшенный мобильно-адаптированный контейнер книги */}
            <div className="bg-white dark:bg-gray-950 rounded-lg shadow-lg overflow-hidden mobile-card">
              <div 
                className="book-content mobile-padding mobile-reading py-6 sm:py-8 lg:py-12 prose prose-lg max-w-none dark:prose-invert overflow-x-hidden"
                dangerouslySetInnerHTML={{ __html: htmlContent }}
                style={{
                  fontSize: '16px',
                  lineHeight: '1.8',
                  color: '#1f2937',
                  fontFamily: 'Inter, sans-serif',
                  wordWrap: 'break-word',
                  hyphens: 'auto',
                  overflowWrap: 'break-word',
                  maxWidth: '100%',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Плавающая кнопка "Наверх" для длинных книг */}
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        className="fixed bottom-6 right-6 bg-amber-500 hover:bg-amber-600 text-white p-3 rounded-full shadow-lg transition-all duration-300 opacity-75 hover:opacity-100 touch-target touch-optimized z-10 mobile-safe-area"
        aria-label="Наверх"
      >
        <ArrowLeft className="h-5 w-5 rotate-90" />
      </button>
    </div>
  );
}