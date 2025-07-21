import { useEffect, useState } from 'react';
import { FlipBook } from './FlipBook';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download } from 'lucide-react';
import { api } from '@/lib/api';
import { useAuth } from '@clerk/clerk-react';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';
import React from 'react';
import { HumorPage } from './HumorPage';
import { RomanticPage } from './RomanticPage';
import { FantasyPage } from './FantasyPage';

interface FlipBookReaderProps {
  bookId?: string;
  runId?: string;
  onBack: () => void;
}

// Интерфейс для данных страницы
interface PageData {
  title?: string;
  text?: string;
  image?: string;
  caption?: string;
}

// Компонент для выбора стиля страницы
const StylePage = React.forwardRef<HTMLDivElement, { 
  children: React.ReactNode; 
  number: number;
  style?: string;
  pageData?: PageData;
}>(
  ({ children, number, style, pageData }, ref) => {
    // Выбираем компонент в зависимости от стиля
    switch (style) {
      case 'humor':
        return (
          <HumorPage
            ref={ref}
            number={number}
            title={pageData?.title}
            text={pageData?.text}
            image={pageData?.image}
            caption={pageData?.caption}
          />
        );
      case 'romantic':
        return (
          <RomanticPage
            ref={ref}
            number={number}
            title={pageData?.title}
            text={pageData?.text}
            image={pageData?.image}
            caption={pageData?.caption}
          />
        );
      case 'fantasy':
        return (
          <FantasyPage
            ref={ref}
            number={number}
            title={pageData?.title}
            text={pageData?.text}
            image={pageData?.image}
            caption={pageData?.caption}
          />
        );
      default:
        // Fallback на старый CyberMagicPage для обратной совместимости
        return (
          <div
            ref={ref}
            className="w-full h-full relative overflow-hidden select-none cyber-magic-page"
            style={{
              background: 'linear-gradient(135deg, #f8f6f0 0%, #f0ede5 30%, #e8e3d3 100%)',
              border: '1px solid rgba(200, 180, 140, 0.4)',
              boxShadow: `
                0 4px 20px rgba(160, 140, 100, 0.2),
                0 8px 40px rgba(140, 120, 80, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.6)
              `,
              borderRadius: '8px',
              fontFamily: "'Cormorant Garamond', serif",
              color: '#4a453f',
              textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)',
            }}
          >
            {/* Subtle animated border */}
            <div 
              className="absolute inset-0 rounded-lg pointer-events-none neon-border"
              style={{
                background: 'linear-gradient(45deg, rgba(220, 190, 150, 0.3), rgba(200, 170, 130, 0.2), rgba(240, 210, 170, 0.3))',
                backgroundSize: '300% 300%',
                opacity: 0.6,
                zIndex: -1,
              }}
            />
            
            {/* Inner subtle glow */}
            <div 
              className="absolute pointer-events-none z-10 inner-glow rounded-lg"
              style={{
                top: '8px',
                left: '8px', 
                right: '8px',
                bottom: '8px',
                border: '1px solid rgba(210, 180, 140, 0.5)',
                boxShadow: `
                  0 0 8px rgba(220, 190, 150, 0.3) inset,
                  0 0 15px rgba(200, 170, 130, 0.2)
                `,
                borderRadius: '6px',
              }}
            />
            
            {/* Content with enhanced styling */}
            <div 
              className="relative z-20 w-full h-full cyber-content"
              dangerouslySetInnerHTML={{ __html: children as string }}
            />
          </div>
        );
    }
  }
);
StylePage.displayName = 'StylePage';

// Extract and preserve CSS styles from the backend template
function extractAndPreserveStyles(rawHtml: string): { pages: string[], css: string } {
  const temp = document.createElement('div');
  temp.innerHTML = rawHtml;

  // Extract CSS from style tags
  const styleElements = temp.querySelectorAll('style');
  let css = '';
  styleElements.forEach(style => {
    css += style.textContent || '';
  });

  // Extract font links
  const fontLinks = Array.from(temp.querySelectorAll('link[href*="fonts.googleapis.com"]'))
    .map(link => (link as HTMLLinkElement).href);

  // Load Google Fonts
  fontLinks.forEach(href => {
    if (!document.querySelector(`link[href="${href}"]`)) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      document.head.appendChild(link);
    }
  });

  // Extract pages
  const pageElements = temp.querySelectorAll('#book .page');
  const pages: string[] = [];

  if (pageElements.length > 0) {
    pageElements.forEach(el => {
      // Apply cyber-magic styles to the content
      const styledContent = enhancePageContent(el.innerHTML);
      pages.push(styledContent);
    });
  } else {
    // Fallback
    const bodyMatch = rawHtml.match(/<body[^>]*>([\s\S]*)<\/body>/i);
    if (bodyMatch && bodyMatch[1]) {
      pages.push(enhancePageContent(bodyMatch[1]));
    } else {
      pages.push(enhancePageContent(rawHtml));
    }
  }

  return { pages, css };
}

// Enhance page content with proper CSS classes and styling
function enhancePageContent(htmlContent: string): string {
  // Add CSS variables and styling to the content
  const enhancedContent = `
    <style>
      :root {
        --font-heading: 'Lora', serif;
        --font-body: 'Cormorant Garamond', serif;
        --font-ornamental: 'Cinzel', serif;
        --page-bg: linear-gradient(135deg, #f8f6f0 0%, #f0ede5 30%, #e8e3d3 100%);
        --text-color: #4a453f;
        --heading-color: #6b5b4a;
        --accent-color: #b8a082;
        --highlight-color: #8b7355;
        --meta-text-color: #7a6f5f;
        --cover-text-color: #3d352b;
        --border-color: rgba(200, 180, 140, 0.4);
        --quote-bg: rgba(240, 230, 210, 0.6);
      }
      
      .cyber-content {
        font-family: var(--font-body);
        color: var(--text-color);
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
        line-height: 1.7;
      }
      
      .cyber-content .page-content {
        padding: 1.5rem 1.5rem 3rem 1.5rem; /* Оптимизированные отступы */
        box-sizing: border-box;
        height: 100%;
        font-size: 1.2rem; /* Немного уменьшили для лучшего размещения */
        line-height: 1.6; /* Оптимизированный межстрочный интервал */
        color: var(--text-color);
        font-weight: 400;
        position: relative;
        overflow-y: auto; /* Добавили прокрутку если нужно */
        overflow-x: hidden;
      }
      
      .cyber-content h1, .cyber-content h2 {
        font-family: var(--font-heading);
        font-weight: 700;
        text-align: center;
        letter-spacing: 1px;
        margin-bottom: 0.4em;
        color: var(--heading-color);
        text-shadow: 0 2px 4px rgba(255, 255, 255, 0.8);
      }
      
      .cyber-content h1 { 
        font-size: 2.2em; /* Немного уменьшили для лучшего размещения */
        margin-bottom: 0.8em;
      }
      .cyber-content h2 { 
        font-size: 1.9em; /* Немного уменьшили для лучшего размещения */
        margin-bottom: 1em;
      }
      
      .cyber-content .book-title {
        font-family: var(--font-heading);
        font-size: 3.8em; /* Увеличили размер заголовка книги */
        font-weight: 700;
        margin: 0;
        line-height: 1.1;
        color: var(--heading-color);
        text-shadow: 0 4px 8px rgba(255, 255, 255, 0.9);
        text-align: center;
      }
      
      .cyber-content .book-subtitle {
        font-size: 1.3em; /* Увеличили размер подзаголовка */
        font-style: italic;
        letter-spacing: 1px;
        color: var(--meta-text-color);
        text-align: center;
        margin-top: 1em;
      }
      
      .cyber-content .cover-ornament {
        font-size: 4em;
        color: var(--accent-color);
        margin: 0.5em 0;
        text-align: center;
        filter: drop-shadow(0 2px 4px rgba(255, 255, 255, 0.8));
      }
      
      .cyber-content .page-image-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: calc(100% - 3rem); /* Учитываем оптимизированный нижний отступ */
        padding: 1.5em;
        box-sizing: border-box;
      }
      
      .cyber-content .page-image-container img {
        max-width: 100%;
        max-height: 75%;
        object-fit: cover;
        border: 2px solid var(--border-color);
        border-radius: 8px;
        box-shadow: 
          0 4px 20px rgba(140, 120, 80, 0.3),
          0 8px 40px rgba(160, 140, 100, 0.2);
        transition: all 0.3s ease;
      }
      
      .cyber-content .page-image-container img:hover {
        transform: scale(1.02);
        box-shadow: 
          0 6px 25px rgba(140, 120, 80, 0.4),
          0 12px 50px rgba(160, 140, 100, 0.3);
      }
      
      .cyber-content .image-caption {
        font-size: 1.1em; /* Увеличили размер подписи к изображению */
        color: var(--meta-text-color);
        text-align: center;
        margin-top: 1em;
        max-width: 90%;
        font-style: italic;
      }
      
      .cyber-content .page-number {
        position: absolute;
        bottom: 25px; /* Подняли номер страницы выше */
        font-family: var(--font-body);
        font-size: 1.1em; /* Увеличили размер номера страницы */
        color: var(--meta-text-color);
        z-index: 20;
        font-weight: 600;
        font-variant-numeric: oldstyle-nums; /* Красивые цифры */
      }
      
      .cyber-content .page-number.left { left: 30px; }
      .cyber-content .page-number.right { right: 30px; }
      
      .cyber-content .running-header {
        position: absolute;
        top: 25px;
        font-family: var(--font-body);
        font-style: italic;
        font-size: 1.0em; /* Увеличили размер заголовка */
        color: var(--meta-text-color);
        z-index: 20;
      }
      
      .cyber-content .running-header.left { left: 30px; }
      .cyber-content .running-header.right { right: 30px; }
      
      .cyber-content p {
        margin-bottom: 1em; /* Уменьшили отступ между абзацами */
        text-align: justify;
        font-size: 1.2rem; /* Соответствует основному размеру */
        line-height: 1.6;
      }
      
      .cyber-content .drop-cap p:first-child::first-letter {
        font-family: var(--font-ornamental);
        float: left;
        font-size: 4.5em; /* Увеличили буквицу */
        line-height: 0.8;
        margin: 0.05em 0.1em 0 0;
        color: var(--highlight-color);
        text-shadow: 0 2px 4px rgba(255, 255, 255, 0.8);
      }
      
      .cyber-content .pull-quote {
        font-style: italic;
        text-align: center;
        margin: 1.5em 0;
        padding: 1.2em; /* Увеличили отступы в цитате */
        border-left: 3px solid var(--accent-color);
        background: var(--quote-bg);
        color: var(--highlight-color);
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 8px rgba(180, 160, 130, 0.2);
        font-size: 1.2em; /* Увеличили размер цитаты */
      }
      
      .cyber-content .toc-content {
        padding: 1.5rem 1.5rem 3rem 1.5rem; /* Соответствует основному контенту */
      }
      
      .cyber-content .toc-item {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 1.2em; /* Увеличили отступ между пунктами */
        font-size: 1.2em; /* Увеличили размер пунктов оглавления */
        transition: all 0.3s ease;
        padding: 0.6em 0;
      }
      
      .cyber-content .toc-item:hover {
        color: var(--highlight-color);
        transform: translateX(5px);
      }
      
      .cyber-content .toc-item .leader {
        flex-grow: 1;
        border-bottom: 1px dotted var(--meta-text-color);
        margin: 0 0.5em;
      }
      
      .cyber-content .toc-item .page-num {
        font-weight: 600;
        color: var(--accent-color);
        font-size: 1.1em; /* Увеличили размер номеров страниц в оглавлении */
        font-variant-numeric: oldstyle-nums; /* Красивые цифры */
      }
      
      .cyber-content .chapter-epigraph {
        font-style: italic;
        text-align: center;
        margin-bottom: 1.5em;
        color: var(--meta-text-color);
        font-size: 1.1em; /* Увеличили размер эпиграфа */
        padding: 0.8em;
        background: var(--quote-bg);
        border-radius: 6px;
        border: 1px solid rgba(200, 180, 140, 0.3);
        line-height: 1.6;
      }
      
      .cyber-content .chapter-separator {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, var(--accent-color), transparent);
        margin: 2em 0; /* Увеличили отступы у разделителя */
      }
      
      /* Дополнительные стили для лучшей читаемости */
      .cyber-content strong {
        font-weight: 600;
        color: var(--highlight-color);
      }
      
      .cyber-content em {
        font-style: italic;
        color: var(--meta-text-color);
      }
      
      /* Стили для всех цифр */
      .cyber-content {
        font-variant-numeric: oldstyle-nums;
      }
      
      /* Улучшенные отступы для всех элементов */
      .cyber-content > * {
        margin-bottom: 1.2em;
      }
      
      .cyber-content > *:last-child {
        margin-bottom: 0;
      }
      
      /* Адаптивное масштабирование для длинного контента */
      .cyber-content {
        display: flex;
        flex-direction: column;
        min-height: 100%;
      }
      
      .cyber-content .page-content {
        flex: 1;
        display: flex;
        flex-direction: column;
      }
      
      /* Стиль для прокрутки */
      .cyber-content .page-content::-webkit-scrollbar {
        width: 6px;
      }
      
      .cyber-content .page-content::-webkit-scrollbar-track {
        background: rgba(200, 180, 140, 0.1);
        border-radius: 3px;
      }
      
      .cyber-content .page-content::-webkit-scrollbar-thumb {
        background: rgba(180, 160, 130, 0.5);
        border-radius: 3px;
      }
      
      .cyber-content .page-content::-webkit-scrollbar-thumb:hover {
        background: rgba(180, 160, 130, 0.7);
      }
    </style>
    ${htmlContent}
  `;
  
  return enhancedContent;
}

export function FlipBookReader({ bookId, runId, onBack }: FlipBookReaderProps) {
  const [pages, setPages] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [bookStyle, setBookStyle] = useState<string>('romantic'); // По умолчанию романтический стиль
  const { getToken } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    // Add improved CSS animations and mobile styles to the document head
    const style = document.createElement('style');
    style.textContent = `
      /* Улучшенные анимации с мобильной поддержкой */
      @keyframes sparkle {
        0%, 100% { 
          opacity: 0.3; 
          transform: scale(0.8); 
        }
        50% { 
          opacity: 0.8; 
          transform: scale(1.2); 
        }
      }

      @keyframes float {
        0%, 100% { 
          transform: translateY(0px) rotate(0deg); 
        }
        33% { 
          transform: translateY(-10px) rotate(1deg); 
        }
        66% { 
          transform: translateY(5px) rotate(-1deg); 
        }
      }

      .sparkle-bg {
        animation: float 6s ease-in-out infinite;
      }

      .sparkle-bg::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 25% 25%, rgba(255, 215, 0, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 75% 75%, rgba(255, 192, 203, 0.1) 0%, transparent 50%);
        animation: sparkle 4s ease-in-out infinite;
      }

      /* Мобильная адаптация для FlipBook */
      .stf__parent {
        width: 100% !important;
        height: auto !important;
        min-height: 400px !important;
      }

      @media (max-width: 768px) {
        .stf__parent {
          min-height: 300px !important;
        }
        
        .stf__block {
          width: 100% !important;
          max-width: 350px !important;
          margin: 0 auto !important;
        }
        
        .stf__item {
          font-size: 14px !important;
          line-height: 1.5 !important;
          padding: 0.75rem !important;
        }
      }

      @media (max-width: 480px) {
        .stf__parent {
          min-height: 250px !important;
        }
        
        .stf__block {
          max-width: 280px !important;
        }
        
        .stf__item {
          font-size: 13px !important;
          padding: 0.5rem !important;
        }
      }

      /* Улучшенная читаемость на мобильных */
      .stf__item h1, .stf__item h2, .stf__item h3 {
        font-family: 'Playfair Display', serif !important;
        line-height: 1.2 !important;
        margin-bottom: 0.75rem !important;
        word-wrap: break-word !important;
      }

      .stf__item p {
        font-family: 'Inter', sans-serif !important;
        line-height: 1.6 !important;
        margin-bottom: 0.75rem !important;
        text-align: justify !important;
        word-wrap: break-word !important;
        hyphens: auto !important;
      }

      .stf__item img {
        max-width: 100% !important;
        height: auto !important;
        border-radius: 8px !important;
        margin: 0.75rem auto !important;
        display: block !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
      }

      /* Улучшенные элементы управления для touch устройств */
      .stf__navigation button {
        min-height: 44px !important;
        min-width: 44px !important;
        touch-action: manipulation !important;
      }

      /* Безопасные области для мобильных устройств */
      @supports (padding: max(0px)) {
        .flip-book-header {
          padding-left: max(1rem, env(safe-area-inset-left)) !important;
          padding-right: max(1rem, env(safe-area-inset-right)) !important;
        }
        
        .flip-book-content {
          padding-left: max(2rem, env(safe-area-inset-left)) !important;
          padding-right: max(2rem, env(safe-area-inset-right)) !important;
        }
      }
`;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const token = await getToken();
        let html: string;
        let status: any = null;
        
        if (runId) {
          html = await api.getBookContent(runId, token || undefined);
          // Получаем статус для определения стиля
          try {
            status = await api.getStatus(runId, token || undefined);
            if (status?.style) {
              setBookStyle(status.style);
            }
          } catch (err) {
            console.warn('Не удалось получить статус для определения стиля:', err);
          }
        } else if (bookId) {
          const res = await fetch(api.getSavedBookViewUrl(bookId, token || undefined));
          html = await res.text();
          // Для сохраненных книг стиль может быть в метаданных
          // Пока используем романтический по умолчанию
        } else {
          throw new Error('Нужен bookId или runId');
        }
        
        const { pages: extractedPages } = extractAndPreserveStyles(html);
        setPages(extractedPages);
      } catch (err) {
        toast({ title: 'Ошибка', description: 'Не удалось загрузить книгу', variant: 'destructive' });
      } finally {
        setLoading(false);
      }
    })();
  }, [bookId, runId, getToken, toast]);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-gradient-to-br from-amber-50 to-orange-50 dark:from-gray-900 dark:to-gray-800" style={{
        minHeight: '100vh'
      }}>
        <div className="text-center space-y-4 mobile-padding">
          <Loader2 className="h-12 w-12 animate-spin mx-auto" style={{ color: '#b8a082' }} />
          <p className="text-lg mobile-text" style={{ color: '#4a453f' }}>Загружаем вашу волшебную книгу...</p>
          <p className="text-sm text-gray-500">Подготавливаем страницы для лучшего чтения</p>
        </div>
      </div>
    );
  }

  const handleDownloadPdf = async () => {
    try {
      const token = await getToken();
      if (runId) await api.downloadFile(runId, 'book.pdf', token || undefined);
      else if (bookId) await api.downloadSavedBook(bookId, 'book.pdf', token || undefined);
      toast({ 
        title: 'Готово', 
        description: 'PDF файл скачан на ваше устройство',
      });
    } catch (error) {
      toast({ 
        title: 'Ошибка', 
        description: 'Не удалось скачать PDF. Попробуйте позже.',
        variant: 'destructive' 
      });
    }
  };

  // Создаем компоненты страниц с учетом стиля
  const pageComponents = pages.map((html, idx) => {
    // Парсим HTML для извлечения данных страницы
    const temp = document.createElement('div');
    temp.innerHTML = html;
    
    // Извлекаем данные страницы
    const titleEl = temp.querySelector('h1, h2, h3');
    const textEl = temp.querySelector('p');
    const imageEl = temp.querySelector('img');
    const captionEl = temp.querySelector('.image-caption, .chapter-image-caption');
    
    const pageData: PageData = {
      title: titleEl?.textContent || undefined,
      text: textEl?.textContent || html,
      image: imageEl?.getAttribute('src') || undefined,
      caption: captionEl?.textContent || undefined,
    };

    return (
      <StylePage 
        key={idx} 
        number={idx + 1} 
        style={bookStyle}
        pageData={pageData}
      >
        {html}
      </StylePage>
    );
  });

  return (
    <div 
      key={runId || bookId} 
      className="flex-1 flex flex-col min-h-screen"
      style={{
        background: 'linear-gradient(135deg, #f5f2e8 0%, #ede7d3 50%, #e5dcc6 100%)',
        position: 'relative',
      }}
    >
      {/* Улучшенный анимированный фон */}
      <div 
        className="fixed inset-0 pointer-events-none z-0 sparkle-bg"
        style={{
          backgroundImage: `
            radial-gradient(1px 1px at 20px 30px, rgba(220, 200, 160, 0.4), transparent),
            radial-gradient(1px 1px at 40px 70px, rgba(240, 220, 180, 0.3), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(200, 180, 140, 0.3), transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(210, 190, 150, 0.2), transparent)
          `,
          backgroundRepeat: 'repeat',
          backgroundSize: '200px 100px',
          opacity: 0.6,
        }}
      />
      
      {/* Улучшенная мобильно-дружественная шапка */}
      <header className="flex items-center justify-between flip-book-header py-3 sm:py-4 border-b relative z-10" style={{
        background: 'rgba(240, 235, 220, 0.95)',
        borderColor: 'rgba(200, 180, 140, 0.3)',
        backdropFilter: 'blur(10px)',
      }}>
        <div className="flex items-center min-w-0">
          <Button 
            variant="ghost" 
            onClick={onBack}
            style={{ 
              color: '#6b5b4a',
              borderColor: 'rgba(180, 160, 130, 0.4)',
            }}
            className="hover:bg-orange-100/50 touch-target"
          >
            <ArrowLeft className="mr-2 h-4 w-4" /> 
            <span className="hidden sm:inline">В библиотеку</span>
            <span className="sm:hidden">Назад</span>
          </Button>
        </div>
        
        <div className="flex-1 text-center px-4">
          <h2 className="text-lg sm:text-xl font-semibold mobile-text" style={{ color: '#4a453f', margin: 0 }}>
            Ваша Книга
          </h2>
        </div>
        
        <div className="flex items-center min-w-0">
          <Button
            variant="ghost"
            onClick={handleDownloadPdf}
            className="hover:bg-orange-100/50 touch-target"
            style={{ color: '#6b5b4a' }}
            size="sm"
          >
            <Download className="h-4 w-4 sm:mr-2" />
            <span className="hidden sm:inline">PDF</span>
          </Button>
        </div>
      </header>
      
      {/* Улучшенный контент с мобильной адаптацией */}
      {!loading && pages.length > 0 && (
        <div className="flex-1 flex items-center justify-center flip-book-content py-4 sm:py-6 relative z-10" style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '1rem',
          margin: 0,
          minHeight: 'calc(100vh - 120px)', // Учитываем высоту header
        }}>
          <div className="w-full max-w-6xl flex justify-center items-center">
            <FlipBook key={runId || bookId} pages={pageComponents} />
          </div>
        </div>
      )}

      {!loading && pages.length === 0 && (
        <div className="flex-1 flex items-center justify-center mobile-padding">
          <div className="text-center space-y-4">
            <p style={{ color: '#4a453f' }} className="mobile-text">Не удалось загрузить страницы книги.</p>
            <Button 
              onClick={() => window.location.reload()} 
              variant="outline"
              className="touch-target"
            >
              Попробовать снова
            </Button>
          </div>
        </div>
      )}
    </div>
  );
} 