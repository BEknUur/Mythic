import React from 'react';

interface RomanticPageProps {
  title?: string;
  text?: string;
  image?: string;
  caption?: string;
  number: number;
}

function splitCamelCase(str: string) {
  return str.replace(/([а-яё])([А-ЯЁ])/g, '$1 $2');
}

export const RomanticPage = React.forwardRef<HTMLDivElement, RomanticPageProps>(
  ({ title, text, image, caption, number }, ref) => {
    // Подключаем Google Fonts (один раз на страницу)
    React.useEffect(() => {
      const linkId = 'romantic-fonts';
      if (!document.getElementById(linkId)) {
        const dancingScript = document.createElement('link');
        dancingScript.id = linkId;
        dancingScript.rel = 'stylesheet';
        dancingScript.href = 'https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Playfair+Display:wght@400;700&display=swap';
        document.head.appendChild(dancingScript);
      }
    }, []);

    // Определяем компоновку в зависимости от наличия изображения
    const hasImage = image && image.trim() !== '';

    return (
      <div
        ref={ref}
        className="w-full h-full relative overflow-hidden select-none romantic-page"
        style={{
          background: 'linear-gradient(135deg, #fff0f5 0%, #ffe4e1 30%, #fce4ec 100%)',
          border: '1px solid rgba(255, 182, 193, 0.4)',
          boxShadow: `
            0 4px 15px rgba(255, 182, 193, 0.25),
            0 8px 30px rgba(255, 105, 180, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.6)
          `,
          borderRadius: '12px',
          color: '#8b5a8b',
          textShadow: '0 1px 2px rgba(255, 255, 255, 0.7)',
        }}
      >
        {/* Декоративные элементы */}
        <div style={{position: 'absolute', top: 8, left: 12, fontSize: 16, opacity: 0.08, pointerEvents: 'none'}}>💖</div>
        <div style={{position: 'absolute', top: 8, right: 12, fontSize: 16, opacity: 0.08, pointerEvents: 'none'}}>💕</div>
        <div style={{position: 'absolute', bottom: 30, left: 12, fontSize: 16, opacity: 0.08, pointerEvents: 'none'}}>💞</div>
        <div style={{position: 'absolute', bottom: 30, right: 50, fontSize: 16, opacity: 0.08, pointerEvents: 'none'}}>💓</div>
        
        {/* Основной контент */}
        <div
          className={`h-full w-full p-4 ${hasImage ? 'flex gap-4' : 'flex flex-col'}`}
          style={{ 
            boxSizing: 'border-box', 
            paddingBottom: 35,
          }}
        >
          {/* Контент с текстом */}
          <div 
            className={`flex flex-col overflow-y-auto ${hasImage ? 'flex-1' : 'flex-1 justify-center'}`}
            style={{
              scrollbarWidth: 'thin',
              scrollbarColor: '#e75480 transparent',
              paddingRight: hasImage ? '8px' : '0'
            }}
          >
            {/* Декоративная линия */}
            <div style={{width: '100%', textAlign: 'center', marginBottom: 6}}>
              <span style={{fontSize: 14, color: '#e75480', fontFamily: 'Dancing Script, cursive'}}>❦</span>
            </div>
            
            {title && (
              <h2
                className="text-center mb-3"
                style={{
                  color: '#c71585',
                  fontFamily: "'Dancing Script', 'Playfair Display', serif",
                  fontSize: hasImage ? 20 : 24,
                  fontWeight: 700,
                  letterSpacing: '0.5px',
                  lineHeight: 1.2,
                  marginBottom: 8,
                  textShadow: '0 2px 6px #fff6fb',
                }}
              >
                {title ? splitCamelCase(title) : null}
              </h2>
            )}
            
            {/* Завиток под заголовком */}
            {title && (
              <div style={{fontSize: 14, color: '#e75480', fontFamily: 'Dancing Script, cursive', marginBottom: 12, textAlign: 'center'}}>❧</div>
            )}
            
            {/* Текст */}
            {text && (
              <div
                className="text-justify flex-1"
                style={{
                  color: '#8b5a8b',
                  fontFamily: "'Playfair Display', 'Georgia', serif",
                  fontSize: hasImage ? 14 : 16,
                  wordBreak: 'break-word',
                  lineHeight: 1.6,
                  textShadow: '0 1px 4px #fff6fb',
                  overflowWrap: 'break-word',
                  hyphens: 'auto'
                }}
                dangerouslySetInnerHTML={{ __html: text }}
              />
            )}
            
            {/* Декоративная линия снизу (только если нет изображения) */}
            {!hasImage && (
              <div style={{width: '100%', textAlign: 'center', marginTop: 12}}>
                <span style={{fontSize: 14, color: '#e75480', fontFamily: 'Dancing Script, cursive'}}>❦</span>
              </div>
            )}
          </div>
          
          {/* Колонка с изображением */}
          {hasImage && (
            <div 
              className="flex-1 flex flex-col overflow-y-auto"
              style={{
                scrollbarWidth: 'thin',
                scrollbarColor: '#e75480 transparent',
                paddingLeft: '8px',
                minWidth: 0
              }}
            >
              <div className="flex flex-col items-center justify-center h-full">
                <img
                  src={image}
                  alt=""
                  className="max-w-full"
                  style={{
                    maxHeight: '85%',
                    maxWidth: '100%',
                    width: 'auto',
                    height: 'auto',
                    objectFit: 'contain',
                    borderRadius: 12,
                    boxShadow: '0 6px 20px rgba(255,182,193,0.25), 0 3px 10px rgba(255,105,180,0.15)',
                    background: '#fff',
                    border: '2px solid #fbcfe8',
                    transition: 'all 0.3s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.02)';
                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(255,182,193,0.3), 0 4px 15px rgba(255,105,180,0.2)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)';
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(255,182,193,0.25), 0 3px 10px rgba(255,105,180,0.15)';
                  }}
                />
                
                {/* Подпись под изображением */}
                {caption && (
                  <div
                    className="text-center mt-2"
                    style={{
                      fontFamily: "'Dancing Script', cursive",
                      fontSize: 14,
                      color: '#e75480',
                      fontStyle: 'italic',
                      letterSpacing: '0.3px',
                      textShadow: '0 1px 3px #fff6fb',
                      lineHeight: 1.3,
                      maxWidth: '100%',
                      wordWrap: 'break-word'
                    }}
                  >
                    {caption} 💕
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        
        {/* Улучшенные стили */}
        <style>{`
          .romantic-page .flex.flex-col::-webkit-scrollbar {
            width: 8px;
          }
          
          .romantic-page .flex.flex-col::-webkit-scrollbar-track {
            background: rgba(255, 182, 193, 0.1);
            border-radius: 4px;
          }
          
          .romantic-page .flex.flex-col::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #e75480, #ff69b4);
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
          }
          
          .romantic-page .flex.flex-col::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #c71585, #e75480);
          }
          
          .romantic-page .overflow-y-auto::-webkit-scrollbar {
            width: 8px;
          }
          
          .romantic-page .overflow-y-auto::-webkit-scrollbar-track {
            background: rgba(255, 182, 193, 0.1);
            border-radius: 4px;
          }
          
          .romantic-page .overflow-y-auto::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #e75480, #ff69b4);
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
          }
          
          .romantic-page .overflow-y-auto::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #c71585, #e75480);
          }
          
          .romantic-page .overflow-y-auto {
            scroll-behavior: smooth;
            scrollbar-width: thin;
            scrollbar-color: #e75480 rgba(255, 182, 193, 0.1);
          }
          
          /* Мобильная адаптация */
          @media (max-width: 768px) {
            .romantic-page .flex.gap-4 {
              flex-direction: column !important;
              gap: 12px !important;
            }
            
            .romantic-page .flex-1 {
              padding-left: 0 !important;
              padding-right: 0 !important;
            }
          }
          
          @media (max-width: 480px) {
            .romantic-page h2 {
              font-size: 18px !important;
            }
            
            .romantic-page .text-justify {
              font-size: 13px !important;
              text-align: left !important;
            }
            
            .romantic-page img {
              max-height: 200px !important;
            }
          }
        `}</style>
        
        <div
          className="absolute bottom-2 right-3 text-lg font-bold"
          style={{
            color: '#c71585',
            fontFamily: "'Dancing Script', 'Playfair Display', serif",
            fontSize: 16,
            textShadow: '0 1px 4px #fff6fb',
            zIndex: 10
          }}
        >
          {number} 💕
        </div>
      </div>
    );
  }
);

RomanticPage.displayName = 'RomanticPage'; 