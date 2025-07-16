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
            // Красивая рамка для книги
            border: '2px solid #e5e7eb',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1)',
            // Добавляем внутреннюю тень для глубины
            filter: 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))'
          }}
        />
      )}
    </div>
  );
}