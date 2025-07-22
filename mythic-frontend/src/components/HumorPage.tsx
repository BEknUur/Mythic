import React from 'react';

interface HumorPageProps {
  title?: string;
  text?: string;
  image?: string;
  caption?: string;
  number: number;
}

function splitCamelCase(str: string) {
  return str.replace(/([а-яё])([А-ЯЁ])/g, '$1 $2');
}

export const HumorPage = React.forwardRef<HTMLDivElement, HumorPageProps>(
  ({ title, text, image, caption, number }, ref) => {
    // Подключаем Comic Sans (один раз на страницу)
    React.useEffect(() => {
      const comicSans = document.createElement('link');
      comicSans.rel = 'stylesheet';
      comicSans.href = 'https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap';
      document.head.appendChild(comicSans);
      return () => {
        document.head.removeChild(comicSans);
      };
    }, []);

    return (
      <div
        ref={ref}
        className="w-full h-full relative overflow-hidden select-none humor-page"
        style={{
          background: 'linear-gradient(135deg, #fffbe6 0%, #ffe8cc 30%, #fffacd 100%)',
          border: '2px solid #ffb347',
          boxShadow: `0 4px 20px rgba(255, 179, 71, 0.18), 0 8px 40px rgba(255, 165, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.8)`,
          borderRadius: '16px',
          color: '#8b4513',
          textShadow: '0 1px 2px rgba(255, 255, 255, 0.9)',
        }}
      >
        {/* Декоративные эмодзи в углах */}
        <div style={{position: 'absolute', top: 18, left: 24, fontSize: 36, opacity: 0.18, pointerEvents: 'none'}}>😂</div>
        <div style={{position: 'absolute', top: 18, right: 24, fontSize: 36, opacity: 0.18, pointerEvents: 'none'}}>🎭</div>
        <div style={{position: 'absolute', bottom: 18, left: 24, fontSize: 36, opacity: 0.18, pointerEvents: 'none'}}>🎨</div>
        <div style={{position: 'absolute', bottom: 18, right: 24, fontSize: 36, opacity: 0.18, pointerEvents: 'none'}}>📚</div>
        {/* Декоративная линия */}
        <div style={{width: '100%', textAlign: 'center', marginTop: 8, marginBottom: 8}}>
          <span style={{fontSize: 32, color: '#ffb347', fontFamily: 'Comic Neue, Comic Sans MS, cursive'}}>✦</span>
        </div>
        <div
          className="flex flex-col items-center h-full w-full p-8 overflow-y-auto"
          style={{ boxSizing: 'border-box', paddingBottom: 56 }}
        >
          {image && (
            <div className="mb-4 w-full flex justify-center">
              <img
                src={image}
                alt=""
                className="max-w-full"
                style={{
                  maxHeight: 260,
                  width: 'auto',
                  objectFit: 'contain',
                  borderRadius: 20,
                  boxShadow: '0 4px 24px rgba(255,179,71,0.18)',
                  background: '#fff',
                  border: '2.5px solid #ffb347',
                }}
              />
            </div>
          )}
          {caption && (
            <div
              className="text-center mb-4"
              style={{
                fontFamily: 'Comic Neue, Comic Sans MS, cursive',
                fontSize: 24,
                color: '#ff6347',
                fontStyle: 'italic',
                letterSpacing: '0.5px',
              }}
            >
              {caption} 😂
            </div>
          )}
          {title && (
            <h2
              className="text-4xl font-bold text-center mb-2"
              style={{
                color: '#ff6347',
                fontFamily: 'Comic Neue, Comic Sans MS, cursive',
                fontSize: 40,
                fontWeight: 700,
                letterSpacing: '1.5px',
                lineHeight: 1.1,
                marginTop: 8,
                marginBottom: 12,
                textShadow: '0 2px 8px #fff6fb',
              }}
            >
              {title ? splitCamelCase(title) : null}
            </h2>
          )}
          {/* Декоративный элемент под заголовком */}
          {title && (
            <div style={{fontSize: 32, color: '#ffb347', fontFamily: 'Comic Neue, Comic Sans MS, cursive', marginBottom: 8}}>✨</div>
          )}
          {text && (
            <div
              className="text-center"
              style={{
                color: '#8b4513',
                fontFamily: 'Comic Neue, Comic Sans MS, cursive',
                fontSize: 22,
                marginBottom: 36,
                wordBreak: 'break-word',
                lineHeight: 1.7,
                textShadow: '0 1px 6px #fff6fb',
              }}
              dangerouslySetInnerHTML={{ __html: text }}
            />
          )}
        </div>
        {/* Декоративная линия снизу */}
        <div style={{width: '100%', textAlign: 'center', marginBottom: 8}}>
          <span style={{fontSize: 32, color: '#ffb347', fontFamily: 'Comic Neue, Comic Sans MS, cursive'}}>✦</span>
        </div>
        
        {/* Стили скроллбара */}
        <style>{`
          .humor-page .overflow-y-auto::-webkit-scrollbar {
            width: 12px;
          }
          
          .humor-page .overflow-y-auto::-webkit-scrollbar-track {
            background: rgba(255, 179, 71, 0.15);
            border-radius: 6px;
            margin: 4px;
            border: 1px solid rgba(255, 183, 77, 0.2);
          }
          
          .humor-page .overflow-y-auto::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #ffb347, #ffa500, #ff8c00);
            border-radius: 6px;
            border: 2px solid rgba(255, 255, 255, 0.4);
            box-shadow: 0 2px 8px rgba(255, 179, 71, 0.3);
            transition: all 0.3s ease;
          }
          
          .humor-page .overflow-y-auto::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #ff8c00, #ffb347, #ffa500);
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(255, 140, 0, 0.4);
          }
          
          /* Плавная прокрутка */
          .humor-page .overflow-y-auto {
            scroll-behavior: smooth;
            scrollbar-width: thin;
            scrollbar-color: #ffb347 rgba(255, 179, 71, 0.15);
          }
        `}</style>
        
        <div
          className="absolute bottom-4 right-4 text-lg font-bold"
          style={{
            color: '#ff6347',
            fontFamily: 'Comic Neue, Comic Sans MS, cursive',
            fontSize: 24,
            textShadow: '0 1px 6px #fff6fb',
          }}
        >
          {number} 😂
        </div>
      </div>
    );
  }
);

HumorPage.displayName = 'HumorPage'; 