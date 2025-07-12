import React from 'react';

interface FantasyPageProps {
  title?: string;
  text?: string;
  image?: string;
  caption?: string;
  number: number;
}

export const FantasyPage = React.forwardRef<HTMLDivElement, FantasyPageProps>(
  ({ title, text, image, caption, number }, ref) => {
    return (
      <div
        ref={ref}
        className="w-full h-full relative overflow-hidden select-none fantasy-page"
        style={{
          background: 'linear-gradient(135deg, #f8f6f0 0%, #f0ede5 30%, #e8e3d3 100%)',
          border: '1px solid rgba(200, 180, 140, 0.4)',
          boxShadow: `
            0 4px 20px rgba(160, 140, 100, 0.2),
            0 8px 40px rgba(140, 120, 80, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.6)
          `,
          borderRadius: '8px',
          fontFamily: "'Cormorant Garamond', 'Lora', serif",
          color: '#4a453f',
          textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)',
        }}
      >
        {/* Мистическая анимированная рамка */}
        <div 
          className="absolute inset-0 rounded-lg pointer-events-none fantasy-border"
          style={{
            background: 'linear-gradient(45deg, rgba(220, 190, 150, 0.3), rgba(200, 170, 130, 0.2), rgba(240, 210, 170, 0.3))',
            backgroundSize: '300% 300%',
            opacity: 0.6,
            zIndex: -1,
          }}
        />
        
        {/* Внутреннее мистическое свечение */}
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
        
        {/* Контент */}
        <div 
          className="relative z-20 w-full h-full fantasy-content p-6"
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            height: '100%',
          }}
        >
          {/* Заголовок с мистическими символами */}
          {title && (
            <div className="text-center mb-4">
              <div className="text-2xl mb-2" style={{ color: '#8b7355' }}>⚔️</div>
              <h2 
                className="text-3xl font-bold mb-2"
                style={{
                  color: '#6b5b4a',
                  textShadow: '0 2px 4px rgba(255, 255, 255, 0.8)',
                  fontSize: '2.2em',
                  fontWeight: 'bold',
                  fontFamily: "'Lora', serif",
                  letterSpacing: '1px',
                }}
              >
                {title}
              </h2>
              <div className="text-2xl" style={{ color: '#8b7355' }}>⚔️</div>
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
                    border: '2px solid rgba(200, 180, 140, 0.6)',
                    boxShadow: '0 8px 25px rgba(160, 140, 100, 0.3)',
                    borderRadius: '12px',
                  }}
                />
                {/* Мистические декорации */}
                <div className="absolute -top-2 -left-2 text-xl">⚔️</div>
                <div className="absolute -top-2 -right-2 text-xl">🛡️</div>
                <div className="absolute -bottom-2 -left-2 text-xl">⚜️</div>
                <div className="absolute -bottom-2 -right-2 text-xl">⚔️</div>
              </div>
              {caption && (
                <p 
                  className="text-center mt-3 text-lg italic"
                  style={{ color: '#6b5b4a' }}
                >
                  {caption} ⚜️
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
                color: '#4a453f',
                fontFamily: "'Cormorant Garamond', serif",
              }}
              dangerouslySetInnerHTML={{ __html: text }}
            />
          )}
          
          {/* Номер страницы с мистическим символом */}
          <div 
            className="absolute bottom-4 right-4 text-lg font-bold"
            style={{ color: '#6b5b4a' }}
          >
            {number} ⚜️
          </div>
        </div>
      </div>
    );
  }
);

FantasyPage.displayName = 'FantasyPage'; 