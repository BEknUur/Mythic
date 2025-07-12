import { useEffect, useState } from 'react';
import { FlipBook } from './FlipBook';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download } from 'lucide-react';
import { api } from '@/lib/api';
import { useAuth } from '@clerk/clerk-react';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';
import React from 'react'; // Added missing import

interface FlipBookReaderProps {
  bookId?: string;
  runId?: string;
  onBack: () => void;
}

// Custom Page component that preserves the cyber-magic styling
const CyberMagicPage = React.forwardRef<HTMLDivElement, { children: React.ReactNode; number: number }>(
  ({ children, number }, ref) => {
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
);
CyberMagicPage.displayName = 'CyberMagicPage';

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
        margin-bottom: 1.5em;
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
  const { getToken } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    // Add CSS animations to the document head
    const style = document.createElement('style');
    style.textContent = `
      @keyframes neonFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
      }
      
      @keyframes pulse {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 0.7; }
      }
      
      @keyframes sparkle {
        from { transform: translateY(0px); }
        to { transform: translateY(-100px); }
      }
      
      .neon-border {
        animation: neonFlow 8s ease infinite;
      }
      
      .inner-glow {
        animation: pulse 4s ease-in-out infinite;
      }
      
      .sparkle-bg {
        animation: sparkle 30s linear infinite;
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
        if (runId) {
          html = await api.getBookContent(runId, token || undefined);
        } else if (bookId) {
          const res = await fetch(api.getSavedBookViewUrl(bookId, token || undefined));
          html = await res.text();
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
      <div className="flex-1 flex flex-col items-center justify-center" style={{
        background: 'linear-gradient(135deg, #f5f2e8 0%, #ede7d3 50%, #e5dcc6 100%)'
      }}>
        <Loader2 className="h-12 w-12 animate-spin" style={{ color: '#b8a082' }} />
        <p className="mt-4 text-lg" style={{ color: '#4a453f' }}>Загружаем вашу волшебную книгу...</p>
      </div>
    );
  }

  const handleDownloadPdf = async () => {
    try {
      const token = await getToken();
      if (runId) await api.downloadFile(runId, 'book.pdf', token || undefined);
      else if (bookId) await api.downloadSavedBook(bookId, 'book.pdf', token || undefined);
    } catch (error) {
      toast({ title: 'Ошибка', description: 'Не удалось скачать PDF', variant: 'destructive' });
    }
  };

  const pageComponents = pages.map((html, idx) => (
    <CyberMagicPage key={idx} number={idx + 1}>
      {html}
    </CyberMagicPage>
  ));

  return (
    <div 
      key={runId || bookId} 
      className="flex-1 flex flex-col"
      style={{
        background: 'linear-gradient(135deg, #f5f2e8 0%, #ede7d3 50%, #e5dcc6 100%)',
        position: 'relative',
      }}
    >
      {/* Subtle animated background */}
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
      
      <header className="flex items-center justify-between p-4 border-b relative z-10" style={{
        background: 'rgba(240, 235, 220, 0.95)',
        borderColor: 'rgba(200, 180, 140, 0.3)',
        backdropFilter: 'blur(10px)',
      }}>
        <Button 
          variant="ghost" 
          onClick={onBack}
          style={{ 
            color: '#6b5b4a',
            borderColor: 'rgba(180, 160, 130, 0.4)',
          }}
          className="hover:bg-orange-100/50"
        >
          <ArrowLeft className="mr-2 h-4 w-4" /> В библиотеку
        </Button>
        <h2 className="text-xl font-semibold" style={{ color: '#4a453f' }}>Ваша Книга</h2>
        <Button 
          onClick={handleDownloadPdf} 
          disabled={!runId && !bookId}
          style={{ 
            color: '#6b5b4a',
            borderColor: 'rgba(180, 160, 130, 0.4)',
          }}
          className="hover:bg-orange-100/50"
        >
          <Download className="mr-2 h-4 w-4" /> Скачать PDF
        </Button>
      </header>
      
      {!loading && pages.length > 0 && (
        <div className="flex-1 overflow-auto flex items-center justify-center p-6 relative z-10">
          <FlipBook key={runId || bookId} pages={pageComponents} />
        </div>
      )}

      {!loading && pages.length === 0 && (
        <div className="flex-1 flex items-center justify-center">
          <p style={{ color: '#4a453f' }}>Не удалось загрузить страницы книги.</p>
        </div>
      )}
    </div>
  );
} 