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
      const dancingScript = document.createElement('link');
      dancingScript.rel = 'stylesheet';
      dancingScript.href = 'https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Playfair+Display:wght@700&display=swap';
      document.head.appendChild(dancingScript);
      return () => {
        document.head.removeChild(dancingScript);
      };
    }, []);

    return (
      <div
        ref={ref}
        className="w-full h-full relative overflow-hidden select-none romantic-page"
        style={{
          background: 'linear-gradient(135deg, #fff0f5 0%, #ffe4e1 30%, #fce4ec 100%)',
          border: '1px solid rgba(255, 182, 193, 0.6)',
          boxShadow: `
            0 4px 20px rgba(255, 182, 193, 0.3),
            0 8px 40px rgba(255, 105, 180, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.8)
          `,
          borderRadius: '18px',
          color: '#8b5a8b',
          textShadow: '0 1px 2px rgba(255, 255, 255, 0.9)',
        }}
      >
        {/* Декоративные сердца в углах */}
        <div style={{position: 'absolute', top: 18, left: 24, fontSize: 28, opacity: 0.15, pointerEvents: 'none'}}>💖</div>
        <div style={{position: 'absolute', top: 18, right: 24, fontSize: 28, opacity: 0.15, pointerEvents: 'none'}}>💕</div>
        <div style={{position: 'absolute', bottom: 18, left: 24, fontSize: 28, opacity: 0.15, pointerEvents: 'none'}}>💞</div>
        <div style={{position: 'absolute', bottom: 18, right: 24, fontSize: 28, opacity: 0.15, pointerEvents: 'none'}}>💓</div>
        
        {/* Декоративная линия */}
        <div style={{width: '100%', textAlign: 'center', marginTop: 6, marginBottom: 6}}>
          <span style={{fontSize: 24, color: '#e75480', fontFamily: 'Dancing Script, cursive'}}>❦</span>
        </div>
        
        <div
          className="flex flex-col h-full w-full p-6 overflow-y-auto"
          style={{ 
            boxSizing: 'border-box', 
            paddingBottom: 50,
            scrollbarWidth: 'thin',
            scrollbarColor: '#e75480 transparent',
          }}
        >
          {title && (
            <h2
              className="text-center mb-3"
              style={{
                color: '#c71585',
                fontFamily: "'Dancing Script', 'Playfair Display', serif",
                fontSize: 36,
                fontWeight: 700,
                letterSpacing: '1.2px',
                lineHeight: 1.1,
                marginBottom: 12,
                textShadow: '0 2px 8px #fff6fb',
              }}
            >
              {title ? splitCamelCase(title) : null}
            </h2>
          )}
          
          {/* Завиток под заголовком */}
          {title && (
            <div style={{fontSize: 24, color: '#e75480', fontFamily: 'Dancing Script, cursive', marginBottom: 12, textAlign: 'center'}}>❧</div>
          )}
          
          {/* Текст перед изображением */}
          {text && (
            <div
              className="text-center mb-4"
              style={{
                color: '#8b5a8b',
                fontFamily: "'Playfair Display', 'Georgia', serif",
                fontSize: 18,
                wordBreak: 'break-word',
                lineHeight: 1.6,
                textShadow: '0 1px 6px #fff6fb',
                marginBottom: 16,
              }}
              dangerouslySetInnerHTML={{ __html: text }}
            />
          )}
          
          {/* Увеличенное изображение */}
          {image && (
            <div className="flex justify-center mb-4">
              <img
                src={image}
                alt=""
                className="max-w-full"
                style={{
                  maxHeight: '450px',
                  maxWidth: '100%',
                  width: 'auto',
                  objectFit: 'contain',
                  borderRadius: 20,
                  boxShadow: '0 8px 32px rgba(255,182,193,0.3), 0 4px 16px rgba(255,105,180,0.2)',
                  background: '#fff',
                  border: '3px solid #fbcfe8',
                  transition: 'all 0.3s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.02)';
                  e.currentTarget.style.boxShadow = '0 12px 40px rgba(255,182,193,0.4), 0 6px 20px rgba(255,105,180,0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = '0 8px 32px rgba(255,182,193,0.3), 0 4px 16px rgba(255,105,180,0.2)';
                }}
              />
            </div>
          )}
          
          {/* Подпись под изображением */}
          {caption && (
            <div
              className="text-center mb-4"
              style={{
                fontFamily: "'Dancing Script', cursive",
                fontSize: 22,
                color: '#e75480',
                fontStyle: 'italic',
                letterSpacing: '0.5px',
                textShadow: '0 1px 4px #fff6fb',
              }}
            >
              {caption} 💕
            </div>
          )}
        </div>
        
        {/* Улучшенные стили для скроллбара */}
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
          }
          
          .romantic-page .flex.flex-col::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #c71585, #e75480);
          }
        `}</style>
        
        {/* Декоративная линия снизу */}
        <div style={{width: '100%', textAlign: 'center', marginBottom: 6}}>
          <span style={{fontSize: 24, color: '#e75480', fontFamily: 'Dancing Script, cursive'}}>❦</span>
        </div>
        
        <div
          className="absolute bottom-3 right-4 text-lg font-bold"
          style={{
            color: '#c71585',
            fontFamily: "'Dancing Script', 'Playfair Display', serif",
            fontSize: 22,
            textShadow: '0 1px 6px #fff6fb',
          }}
        >
          {number} 💕
        </div>
      </div>
    );
  }
);

RomanticPage.displayName = 'RomanticPage'; 