import React from 'react';
import HTMLFlipBookLib from 'react-pageflip';

// Type assertion для решения проблем с типизацией react-pageflip
const HTMLFlipBook = HTMLFlipBookLib as any;

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
  const [dimensions, setDimensions] = React.useState({
    width: 900,
    height: 700,
    minWidth: 700,
    maxWidth: 1600,
    minHeight: 500,
    maxHeight: 1200
  });

  React.useEffect(() => {
    const updateDimensions = () => {
      const isMobile = window.innerWidth < 768;
      const isSmallMobile = window.innerWidth < 480;
      
      if (isSmallMobile) {
        setDimensions({
          width: Math.min(window.innerWidth - 40, 300),
          height: Math.min(window.innerHeight - 200, 400),
          minWidth: 280,
          maxWidth: 350,
          minHeight: 350,
          maxHeight: 450
        });
      } else if (isMobile) {
        setDimensions({
          width: Math.min(window.innerWidth - 60, 400),
          height: Math.min(window.innerHeight - 180, 500),
          minWidth: 350,
          maxWidth: 450,
          minHeight: 400,
          maxHeight: 550
        });
      } else {
        setDimensions({
          width: 900,
          height: 700,
          minWidth: 700,
          maxWidth: 1600,
          minHeight: 500,
          maxHeight: 1200
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  return (
    <div className="flip-book-wrapper w-full h-full flex items-center justify-center p-4">
      <HTMLFlipBook
        width={dimensions.width}
        height={dimensions.height}
        size="stretch"
        minWidth={dimensions.minWidth}
        maxWidth={dimensions.maxWidth}
        minHeight={dimensions.minHeight}
        maxHeight={dimensions.maxHeight}
        maxShadowOpacity={0.18}
        showCover={false}
        className="shadow-2xl book-container rounded-lg overflow-hidden"
        mobileScrollSupport={true}
        showPageCorners={true}
        useMouseEvents={true}
        flippingTime={800}
        usePortrait={window.innerWidth < 768}
        swipeDistance={30}
        clickEventForward={false}
        drawShadow={true}
        startPage={0}
        style={{ margin: '0 auto' }}
      >
        {preparedPages}
      </HTMLFlipBook>
    </div>
  );
} 