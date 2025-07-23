import React, { useState, useEffect, useRef } from 'react';
import HTMLFlipBook from 'react-pageflip';

interface FlipBookProps {
  pages?: React.ReactNode[];
}

interface PageProps {
  children?: React.ReactNode;
  number: number;
}

// Улучшенный компонент страницы с лучшей мобильной адаптацией
const Page = React.forwardRef<HTMLDivElement, PageProps>(
  function Page({ children, number }, ref) {
    return (
      <div className="flip-page" ref={ref}>
        <div className="flip-page-content">
          {children || (
            <div className="demo-content">
              <h2 className="demo-title">Страница {number}</h2>
              <p className="demo-text">
                Здесь будет содержимое вашей книги. Этот текст является демонстрационным 
                и показывает, как будет выглядеть ваша готовая книга.
              </p>
              <p className="demo-text">
                Книги, созданные с помощью Mythic AI, имеют прекрасное оформление и 
                удобную навигацию на всех устройствах.
              </p>
            </div>
          )}
        </div>
        <div className="flip-page-number">{number}</div>
      </div>
    );
  }
);

/**
 * FlipBook – исправленная версия с улучшенным дизайном
 */
export function FlipBook({ pages }: FlipBookProps) {
  const flipBookRef = useRef<any>(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Подготавливаем страницы-заглушки
  const placeholderPages = Array.from({ length: 6 }).map((_, idx) => (
    <Page key={idx} number={idx + 1} />
  ));

  const preparedPages = pages && pages.length
    ? pages.map((content, idx) => (
        <Page key={idx} number={idx + 1}>
          {content}
        </Page>
      ))
    : placeholderPages;

  // Улучшенные размеры с лучшей адаптивностью
  const [dimensions, setDimensions] = useState({
    width: 800,
    height: 600,
    minWidth: 600,
    maxWidth: 1000,
    minHeight: 450,
    maxHeight: 750
  });

  useEffect(() => {
    const updateDimensions = () => {
      const containerWidth = window.innerWidth;
      const containerHeight = window.innerHeight;
      const isMobile = containerWidth < 768;
      const isSmallMobile = containerWidth < 480;
      
      if (isSmallMobile) {
        // Очень маленькие экраны
        setDimensions({
          width: Math.min(containerWidth - 20, 350),
          height: Math.min(containerHeight - 100, 400),
          minWidth: 300,
          maxWidth: 400,
          minHeight: 350,
          maxHeight: 450
        });
      } else if (isMobile) {
        // Мобильные устройства
        setDimensions({
          width: Math.min(containerWidth - 40, 600),
          height: Math.min(containerHeight - 120, 500),
          minWidth: 450,
          maxWidth: 650,
          minHeight: 400,
          maxHeight: 550
        });
      } else {
        // Десктоп
        setDimensions({
          width: Math.min(containerWidth - 100, 900),
          height: Math.min(containerHeight - 150, 650),
          minWidth: 700,
          maxWidth: 1100,
          minHeight: 500,
          maxHeight: 750
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    
    const timer = setTimeout(() => setIsReady(true), 100);
    
    return () => {
      window.removeEventListener('resize', updateDimensions);
      clearTimeout(timer);
    };
  }, []);

  const handleFlipBookError = (error: any) => {
    console.error('FlipBook error:', error);
    setError('Ошибка загрузки книги');
  };

  if (error) {
    return (
      <div className="flex items-center justify-center w-full h-full text-red-600 bg-red-50 rounded-lg p-8">
        <div className="text-center">
          <p className="text-lg font-medium">{error}</p>
          <button 
            onClick={() => setError(null)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  if (!isReady) {
    return (
      <div className="flex items-center justify-center w-full h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загружаем книгу...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flip-book-wrapper">
      <style>{`
        /* Основные стили страницы */
        .flip-page {
          background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
          box-shadow: 0 4px 20px rgba(0,0,0,0.08);
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          position: relative;
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .flip-page-content {
          flex: 1;
          padding: 24px;
          overflow-y: auto;
          overflow-x: hidden;
          font-size: 16px;
          line-height: 1.7;
          color: #1f2937;
          word-wrap: break-word;
          hyphens: auto;
          
          /* Плавная прокрутка */
          scrollbar-width: thin;
          scrollbar-color: #cbd5e1 transparent;
        }
        
        /* Красивые скроллбары */
        .flip-page-content::-webkit-scrollbar {
          width: 8px;
        }
        
        .flip-page-content::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.05);
          border-radius: 4px;
        }
        
        .flip-page-content::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, #6366f1, #8b5cf6);
          border-radius: 4px;
          transition: all 0.3s ease;
        }
        
        .flip-page-content::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(180deg, #4f46e5, #7c3aed);
        }
        
        .flip-page-number {
          position: absolute;
          bottom: 16px;
          right: 20px;
          font-size: 14px;
          color: #6b7280;
          font-weight: 500;
          z-index: 10;
        }
        
        /* Улучшенное содержимое демо-страниц */
        .demo-content {
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: 16px;
        }
        
        .demo-title {
          font-family: 'Playfair Display', serif;
          font-size: 28px;
          font-weight: 700;
          margin-bottom: 20px;
          color: #1f2937;
          text-align: center;
          line-height: 1.3;
        }
        
        .demo-text {
          font-size: 16px;
          line-height: 1.7;
          color: #4b5563;
          margin-bottom: 16px;
          text-align: justify;
        }
        
        /* Улучшенное отображение изображений */
        .flip-page-content img {
          max-width: 100%;
          height: auto;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          margin: 16px 0;
          display: block;
          object-fit: cover;
        }
        
        /* Центрирование изображений */
        .flip-page-content .page-image-container,
        .flip-page-content .image-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin: 20px 0;
        }
        
        .flip-page-content .page-image-container img,
        .flip-page-content .image-container img {
          max-width: 90%;
          max-height: 300px;
          object-fit: contain;
          border-radius: 12px;
          box-shadow: 0 8px 25px rgba(0,0,0,0.15);
          transition: transform 0.3s ease;
        }
        
        .flip-page-content .page-image-container img:hover,
        .flip-page-content .image-container img:hover {
          transform: scale(1.02);
        }
        
        /* Подписи к изображениям */
        .flip-page-content .image-caption,
        .flip-page-content .caption {
          font-size: 14px;
          color: #6b7280;
          text-align: center;
          margin-top: 12px;
          font-style: italic;
          line-height: 1.5;
        }
        
        /* Улучшенные заголовки */
        .flip-page-content h1,
        .flip-page-content h2,
        .flip-page-content h3 {
          font-family: 'Playfair Display', serif;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 16px;
          line-height: 1.3;
        }
        
        .flip-page-content h1 { font-size: 32px; }
        .flip-page-content h2 { font-size: 26px; }
        .flip-page-content h3 { font-size: 22px; }
        
        /* Улучшенные абзацы */
        .flip-page-content p {
          margin-bottom: 16px;
          text-align: justify;
          line-height: 1.7;
        }
        
        /* Списки */
        .flip-page-content ul,
        .flip-page-content ol {
          margin: 16px 0;
          padding-left: 24px;
        }
        
        .flip-page-content li {
          margin-bottom: 8px;
          line-height: 1.6;
        }
        
        /* Цитаты */
        .flip-page-content blockquote,
        .flip-page-content .quote {
          border-left: 4px solid #6366f1;
          padding-left: 20px;
          margin: 20px 0;
          font-style: italic;
          color: #4b5563;
          background: rgba(99, 102, 241, 0.05);
          padding: 16px 20px;
          border-radius: 0 8px 8px 0;
        }
        
        /* Мобильная адаптация */
        @media (max-width: 768px) {
          .flip-page-content {
            padding: 16px;
            font-size: 15px;
            line-height: 1.6;
          }
          
          .demo-title {
            font-size: 22px;
            margin-bottom: 16px;
          }
          
          .demo-text {
            font-size: 15px;
            text-align: left;
          }
          
          .flip-page-content h1 { font-size: 26px; }
          .flip-page-content h2 { font-size: 22px; }
          .flip-page-content h3 { font-size: 18px; }
          
          .flip-page-number {
            bottom: 12px;
            right: 16px;
            font-size: 12px;
          }
        }
        
        @media (max-width: 480px) {
          .flip-page-content {
            padding: 12px;
            font-size: 14px;
          }
          
          .demo-title {
            font-size: 18px;
            margin-bottom: 12px;
          }
          
          .demo-text {
            font-size: 14px;
          }
          
          .flip-page-content h1 { font-size: 22px; }
          .flip-page-content h2 { font-size: 18px; }
          .flip-page-content h3 { font-size: 16px; }
          
          .flip-page-number {
            bottom: 8px;
            right: 12px;
            font-size: 11px;
          }
        }
        
        /* Wrapper стили */
        .flip-book-wrapper {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
          min-height: 600px;
          box-sizing: border-box;
        }
        
        .book-container {
          box-shadow: 0 20px 50px rgba(0,0,0,0.15) !important;
          border-radius: 12px !important;
          overflow: hidden !important;
        }
        
        @media (max-width: 768px) {
          .flip-book-wrapper {
            padding: 10px;
            min-height: 500px;
          }
        }
        
        @media (max-width: 480px) {
          .flip-book-wrapper {
            padding: 5px;
            min-height: 450px;
          }
        }
      `}</style>
      
      <HTMLFlipBook
        ref={flipBookRef}
        width={dimensions.width}
        height={dimensions.height}
        size="stretch"
        minWidth={dimensions.minWidth}
        maxWidth={dimensions.maxWidth}
        minHeight={dimensions.minHeight}
        maxHeight={dimensions.maxHeight}
        maxShadowOpacity={0.2}
        showCover={false}
        className="book-container"
        mobileScrollSupport={true}
        showPageCorners={true}
        useMouseEvents={true}
        flippingTime={500}
        usePortrait={window.innerWidth < 768}
        swipeDistance={30}
        clickEventForward={false}
        drawShadow={true}
        startPage={0}
        startZIndex={0}
        autoSize={false}
        disableFlipByClick={false}
        style={{ margin: '0 auto' }}
        onFlip={(e: any) => console.log('Page flipped:', e)}
        onChangeOrientation={() => console.log('Orientation changed')}
        onChangeState={(e: any) => console.log('State changed:', e)}
        onInit={() => console.log('FlipBook initialized')}
      >
        {preparedPages}
      </HTMLFlipBook>
    </div>
  );
} 