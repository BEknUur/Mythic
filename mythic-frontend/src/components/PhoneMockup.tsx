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
            // Добавляем легкую рамку
            border: '1px solid rgba(0, 0, 0, 0.1)',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          }}
        />
      )}
    </div>
  );
}