import React from 'react';

interface FantasyPageProps {
  title?: string;
  text?: string;
  image?: string;
  caption?: string;
  number: number;
}

function splitCamelCase(str: string) {
  return str.replace(/([а-яё])([А-ЯЁ])/g, '$1 $2');
}

export const FantasyPage = React.forwardRef<HTMLDivElement, FantasyPageProps>(
  ({ title, text, image, caption, number }, ref) => {
    // Подключаем Cormorant Garamond и Lora (один раз на страницу)
    React.useEffect(() => {
      const fantasyFonts = document.createElement('link');
      fantasyFonts.rel = 'stylesheet';
      fantasyFonts.href = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@700&family=Lora:wght@700&display=swap';
      document.head.appendChild(fantasyFonts);
      return () => {
        document.head.removeChild(fantasyFonts);
      };
    }, []);

    return (
      <div
        ref={ref}
        className="w-full h-full relative overflow-hidden select-none fantasy-page"
        style={{
          background: 'linear-gradient(135deg, #f8f6f0 0%, #f0ede5 30%, #e8e3d3 100%)',
          border: '1.5px solid rgba(200, 180, 140, 0.4)',
          boxShadow: '0 4px 20px rgba(160, 140, 100, 0.18), 0 8px 40px rgba(140, 120, 80, 0.10), inset 0 1px 0 rgba(255, 255, 255, 0.7)',
          borderRadius: '18px',
          color: '#4a453f',
          textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)',
        }}
      >
        {/* Декоративные эмодзи в углах */}
        <div style={{position: 'absolute', top: 18, left: 24, fontSize: 36, opacity: 0.18, pointerEvents: 'none'}}>⚔️</div>
        <div style={{position: 'absolute', top: 18, right: 24, fontSize: 36, opacity: 0.18, pointerEvents: 'none'}}>🛡️</div>
        <div style={{position: 'absolute', bottom: 18, left: 24, fontSize: 36, opacity: 0.18, pointerEvents: 'none'}}>⚜️</div>
        <div style={{position: 'absolute', bottom: 18, right: 24, fontSize: 36, opacity: 0.18, pointerEvents: 'none'}}>🦄</div>
        {/* Декоративная линия */}
        <div style={{width: '100%', textAlign: 'center', marginTop: 8, marginBottom: 8}}>
          <span style={{fontSize: 32, color: '#bfa76f', fontFamily: 'Cormorant Garamond, Lora, serif'}}>✧</span>
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
                  boxShadow: '0 4px 24px rgba(160,140,100,0.18)',
                  background: '#fff',
                  border: '2.5px solid #bfa76f',
                }}
              />
            </div>
          )}
          {caption && (
            <div
              className="text-center mb-4"
              style={{
                fontFamily: 'Cormorant Garamond, Lora, serif',
                fontSize: 24,
                color: '#6b5b4a',
                fontStyle: 'italic',
                letterSpacing: '0.5px',
              }}
            >
              {caption} ⚜️
            </div>
          )}
          {title && (
            <h2
              className="text-4xl font-bold text-center mb-2"
              style={{
                color: '#6b5b4a',
                fontFamily: 'Cormorant Garamond, Lora, serif',
                fontSize: 44,
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
            <div style={{fontSize: 32, color: '#bfa76f', fontFamily: 'Cormorant Garamond, Lora, serif', marginBottom: 8}}>✦</div>
          )}
          {text && (
            <div
              className="text-center"
              style={{
                color: '#4a453f',
                fontFamily: 'Cormorant Garamond, Lora, serif',
                fontSize: 24,
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
          <span style={{fontSize: 32, color: '#bfa76f', fontFamily: 'Cormorant Garamond, Lora, serif'}}>✧</span>
        </div>
        <div
          className="absolute bottom-4 right-4 text-lg font-bold"
          style={{
            color: '#6b5b4a',
            fontFamily: 'Cormorant Garamond, Lora, serif',
            fontSize: 26,
            textShadow: '0 1px 6px #fff6fb',
          }}
        >
          {number} ⚜️
        </div>
      </div>
    );
  }
);

FantasyPage.displayName = 'FantasyPage'; 