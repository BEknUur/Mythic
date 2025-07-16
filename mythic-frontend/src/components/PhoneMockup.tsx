import React, { useRef, useState, useEffect } from 'react';

interface PhoneMockupProps {
  src: string;
  alt?: string;
  className?: string;
}

export function PhoneMockup({
  src,
  alt = 'Mockup screenshot',
  className = '',
}: PhoneMockupProps) {
  const [inView, setInView] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    
    const obs = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setInView(true);
          obs.disconnect();
        }
      },
      { rootMargin: '200px' }
    );
    
    obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`relative overflow-hidden ${className}`}
    >
      {inView && (
        <img
          src={src}
          alt={alt}
          loading="lazy"
          decoding="async"
          className="w-full h-auto object-cover"
          style={{
            // Обрезаем серые края - оптимальные значения по твоей картинке
            clipPath: 'inset(15% 20% 15% 20%)', // top right bottom left
            objectPosition: 'center',
            // Красивая рамка для книги с крутой тенью
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '16px',
            // Многослойная тень для реалистичного эффекта
            boxShadow: `
              0 25px 50px -12px rgba(0, 0, 0, 0.25),
              0 8px 16px -8px rgba(0, 0, 0, 0.1),
              0 0 0 1px rgba(255, 255, 255, 0.05),
              inset 0 1px 0 rgba(255, 255, 255, 0.1)
            `,
            // Дополнительный фильтр для глубины
            filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.12))',
            // Легкое свечение
            backdropFilter: 'blur(1px)'
          }}
        />
      )}
    </div>
  );
}