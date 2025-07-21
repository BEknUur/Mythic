import React, { useState, useEffect, useRef } from 'react';
import HTMLFlipBook from 'react-pageflip';

interface FlipBookProps {
  pages?: React.ReactNode[];
}

interface PageProps {
  children?: React.ReactNode;
  number: number;
}

// Улучшенный компонент страницы с мобильной адаптацией
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
 * FlipBook – улучшенная версия с мобильной поддержкой
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

  // Определяем размеры в зависимости от размера экрана
  const [dimensions, setDimensions] = useState({
    width: 800,
    minWidth: 600,
    maxWidth: 1400,
    minHeight: 300
  });

  useEffect(() => {
    const updateDimensions = () => {
      const containerWidth = window.innerWidth;
      const containerHeight = window.innerHeight;
      const isMobile = containerWidth < 768;
      const isSmallMobile = containerWidth < 480;
      
      if (isSmallMobile) {
        setDimensions({
          width: Math.min(containerWidth - 40, 320),
          minWidth: 300,
          maxWidth: 350,
          minHeight: 250
        });
      } else if (isMobile) {
        setDimensions({
          width: Math.min(containerWidth - 60, 450),
          minWidth: 400,
          maxWidth: 500,
          minHeight: 300
        });
      } else {
        setDimensions({
          width: Math.min(containerWidth - 100, 800),
          minWidth: 600,
          maxWidth: 1400,
          minHeight: 300
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    
    // Небольшая задержка для загрузки
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
      <div className="flip-book-wrapper w-full h-full flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <p className="text-red-600">{error}</p>
          <button 
            onClick={() => {
              setError(null);
              setIsReady(false);
              setTimeout(() => setIsReady(true), 100);
            }}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  if (!isReady) {
    return (
      <div className="flip-book-wrapper w-full h-full flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p>Загружаем книгу...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flip-book-wrapper w-full h-full flex items-center justify-center p-4">
      <style>{`
        .flip-page {
          background: white;
          box-shadow: 0 0 20px rgba(0,0,0,0.1);
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          overflow: visible;
          display: flex;
          flex-direction: column;
          min-height: 300px;
          height: auto;
        }
        
        .flip-page-content {
          flex: 1;
          padding: 20px;
          overflow: visible;
          font-family: 'Inter', sans-serif;
          line-height: 1.6;
          height: auto;
          min-height: 250px;
        }
        
        .flip-page-number {
          position: absolute;
          bottom: 10px;
          right: 15px;
          font-size: 14px;
          color: #6b7280;
          font-weight: 500;
        }
        
        .demo-content {
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: center;
        }
        
        .demo-title {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 16px;
          color: #1f2937;
          text-align: center;
        }
        
        .demo-text {
          font-size: 16px;
          margin-bottom: 12px;
          color: #4b5563;
          text-align: justify;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
          .flip-page-content {
            padding: 15px;
          }
          
          .demo-title {
            font-size: 20px;
          }
          
          .demo-text {
            font-size: 14px;
          }
        }
        
        @media (max-width: 480px) {
          .flip-page-content {
            padding: 12px;
          }
          
          .demo-title {
            font-size: 18px;
          }
          
          .demo-text {
            font-size: 13px;
          }
        }
      `}</style>
      
      <HTMLFlipBook
        ref={flipBookRef}
        width={dimensions.width}
        height={1200}
        size="stretch"
        minWidth={dimensions.minWidth}
        maxWidth={dimensions.maxWidth}
        minHeight={dimensions.minHeight}
        maxHeight={1500}
        maxShadowOpacity={0.15}
        showCover={false}
        className="shadow-2xl book-container"
        mobileScrollSupport={true}
        showPageCorners={true}
        useMouseEvents={true}
        flippingTime={600}
        usePortrait={window.innerWidth < 768}
        swipeDistance={30}
        clickEventForward={false}
        drawShadow={true}
        startPage={0}
        startZIndex={0}
        autoSize={false}
        disableFlipByClick={false}
        style={{ margin: '0 auto' }}
        onFlip={(e) => console.log('Page flipped:', e)}
        onChangeOrientation={() => console.log('Orientation changed')}
        onChangeState={(e) => console.log('State changed:', e)}
      >
        {preparedPages}
      </HTMLFlipBook>
    </div>
  );
} 