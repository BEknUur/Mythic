import React from 'react';

interface RomanticPageProps {
  title?: string;
  text?: string;
  image?: string;
  caption?: string;
  number: number;
}

export const RomanticPage = React.forwardRef<HTMLDivElement, RomanticPageProps>(
  ({ title, text, image, caption, number }, ref) => {
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
          borderRadius: '8px',
          fontFamily: "'Playfair Display', 'Georgia', serif",
          color: '#8b5a8b',
          textShadow: '0 1px 2px rgba(255, 255, 255, 0.9)',
        }}
      >
        {/* Нежная анимированная рамка */}
        <div 
          className="absolute inset-0 rounded-lg pointer-events-none romantic-border"
          style={{
            background: 'linear-gradient(45deg, rgba(255, 182, 193, 0.3), rgba(255, 218, 225, 0.2), rgba(255, 105, 180, 0.3))',
            backgroundSize: '300% 300%',
            opacity: 0.6,
            zIndex: -1,
          }}
        />
        
        {/* Внутреннее нежное свечение */}
        <div 
          className="absolute pointer-events-none z-10 inner-glow rounded-lg"
          style={{
            top: '8px',
            left: '8px', 
            right: '8px',
            bottom: '8px',
            border: '1px solid rgba(255, 182, 193, 0.5)',
            boxShadow: `
              0 0 8px rgba(255, 182, 193, 0.3) inset,
              0 0 15px rgba(255, 105, 180, 0.2)
            `,
            borderRadius: '6px',
          }}
        />
        
        {/* Контент */}
        <div 
          className="relative z-20 w-full h-full romantic-content p-6"
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            height: '100%',
          }}
        >
          {/* Заголовок с романтическими символами */}
          {title && (
            <div className="text-center mb-4">
              <div className="text-2xl mb-2" style={{ color: '#ff69b4' }}>💕</div>
              <h2 
                className="text-3xl font-bold mb-2"
                style={{
                  color: '#c71585',
                  textShadow: '0 2px 4px rgba(255, 255, 255, 0.8)',
                  fontSize: '2.2em',
                  fontWeight: 'bold',
                  fontFamily: "'Playfair Display', serif",
                }}
              >
                {title}
              </h2>
              <div className="text-2xl" style={{ color: '#ff69b4' }}>💕</div>
            </div>
          )}
          
          {/* Изображение с подписью */}
          {image && (
            <div className="flex-1 flex flex-col justify-center items-center mb-4">
              <div className="relative">
                <img 
                  src={image} 
                  alt=""
                  className="max-w-full max-h-60 object-cover rounded-lg"
                  style={{
                    border: '2px solid rgba(255, 182, 193, 0.8)',
                    boxShadow: '0 8px 25px rgba(255, 182, 193, 0.4)',
                    borderRadius: '12px',
                  }}
                />
                {/* Романтические декорации */}
                <div className="absolute -top-2 -left-2 text-xl">🌹</div>
                <div className="absolute -top-2 -right-2 text-xl">💖</div>
                <div className="absolute -bottom-2 -left-2 text-xl">✨</div>
                <div className="absolute -bottom-2 -right-2 text-xl">🌹</div>
              </div>
              {caption && (
                <p 
                  className="text-center mt-3 text-lg italic"
                  style={{ color: '#c71585' }}
                >
                  {caption} 💕
                </p>
              )}
            </div>
          )}
          
          {/* Текст */}
          {text && (
            <div 
              className="flex-1 overflow-y-auto"
              style={{
                fontSize: '1.2em',
                lineHeight: '1.7',
                color: '#8b5a8b',
                fontFamily: "'Georgia', serif",
              }}
              dangerouslySetInnerHTML={{ __html: text }}
            />
          )}
          
          {/* Номер страницы с романтическим символом */}
          <div 
            className="absolute bottom-4 right-4 text-lg font-bold"
            style={{ color: '#c71585' }}
          >
            {number} 💕
          </div>
        </div>
      </div>
    );
  }
);

RomanticPage.displayName = 'RomanticPage'; 