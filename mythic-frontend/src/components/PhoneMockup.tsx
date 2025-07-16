// components/PhoneMockup.tsx
import React, { useRef, useState, useEffect } from 'react';

interface PhoneMockupProps {
  src: string;      // '/photo.png'
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
      className={`overflow-hidden rounded-2xl shadow-lg ${className}`}
    >
      {inView && (
        <img
          src={src}
          alt={alt}
          loading="lazy"
          decoding="async"
          className="w-full h-auto object-cover"
        />
      )}
    </div>
  );
}
