import React from 'react';

interface HumorPageProps {
  title?: string;
  text?: string;
  image?: string;
  caption?: string;
  number: number;
}

export const HumorPage = React.forwardRef<HTMLDivElement, HumorPageProps>(
  ({ title, text, image, caption, number }, ref) => {
    return (
      <div
        ref={ref}
        className="w-full h-full relative overflow-hidden select-none humor-page"
        style={{
          background: 'linear-gradient(135deg, #fff5e6 0%, #ffe8cc 30%, #ffdab9 100%)',
          border: '2px solid #ffb347',
          boxShadow: `
            0 8px 32px rgba(255, 179, 71, 0.3),
            0 16px 64px rgba(255, 165, 0, 0.2),
            inset 0 2px 0 rgba(255, 255, 255, 0.8)
          `,
          borderRadius: '12px',
          fontFamily: "'Comic Sans MS', 'Chalkboard SE', cursive",
          color: '#8b4513',
          textShadow: '0 2px 4px rgba(255, 255, 255, 0.9)',
        }}
      >
        {/* Анимированная рамка с эмодзи */}
        <div 
          className="absolute inset-0 rounded-lg pointer-events-none emoji-border"
          style={{
            background: 'linear-gradient(45deg, rgba(255, 182, 193, 0.4), rgba(255, 218, 185, 0.3), rgba(255, 160, 122, 0.4))',
            backgroundSize: '300% 300%',
            opacity: 0.8,
            zIndex: -1,
          }}
        />
        
        {/* Внутреннее свечение */}
        <div 
          className="absolute pointer-events-none z-10 inner-glow rounded-lg"
          style={{
            top: '10px',
            left: '10px', 
            right: '10px',
            bottom: '10px',
            border: '2px solid rgba(255, 182, 193, 0.6)',
            boxShadow: `
              0 0 12px rgba(255, 182, 193, 0.4) inset,
              0 0 20px rgba(255, 160, 122, 0.3)
            `,
            borderRadius: '8px',
          }}
        />
        
        {/* Контент */}
        <div 
          className="relative z-20 w-full h-full humor-content p-6"
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            height: '100%',
          }}
        >
          {/* Заголовок с эмодзи */}
          {title && (
            <div className="text-center mb-4">
              <h2 
                className="text-3xl font-bold mb-2"
                style={{
                  color: '#ff6347',
                  textShadow: '2px 2px 4px rgba(255, 255, 255, 0.8)',
                  fontSize: '2.2em',
                  fontWeight: 'bold',
                }}
              >
                {title} 😄
              </h2>
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
                    border: '3px solid #ffb347',
                    boxShadow: '0 8px 25px rgba(255, 179, 71, 0.4)',
                    borderRadius: '12px',
                  }}
                />
                {/* Эмодзи-декорации вокруг изображения */}
                <div className="absolute -top-2 -left-2 text-2xl">🎭</div>
                <div className="absolute -top-2 -right-2 text-2xl">🎪</div>
                <div className="absolute -bottom-2 -left-2 text-2xl">🎨</div>
                <div className="absolute -bottom-2 -right-2 text-2xl">🎯</div>
              </div>
              {caption && (
                <p 
                  className="text-center mt-3 text-lg italic"
                  style={{ color: '#ff6347' }}
                >
                  {caption} 😂
                </p>
              )}
            </div>
          )}
          
          {/* Текст */}
          {text && (
            <div 
              className="flex-1 overflow-y-auto"
              style={{
                fontSize: '1.1em',
                lineHeight: '1.6',
                color: '#8b4513',
              }}
              dangerouslySetInnerHTML={{ __html: text }}
            />
          )}
          
          {/* Номер страницы с эмодзи */}
          <div 
            className="absolute bottom-4 right-4 text-lg font-bold"
            style={{ color: '#ff6347' }}
          >
            {number} 📖
          </div>
        </div>
      </div>
    );
  }
);

HumorPage.displayName = 'HumorPage'; 