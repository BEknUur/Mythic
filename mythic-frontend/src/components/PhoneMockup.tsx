import React from 'react';

interface PhoneMockupProps {
  src: string;
  alt?: string;
  variant?: 'frame' | 'plain';
  className?: string;
}

// Fallback placeholder image


export function PhoneMockup({ src, alt = 'Book preview', variant = 'frame', className = '' }: PhoneMockupProps) {
  if (variant === 'plain') {
    return (
      <img
        src={src}
        alt={alt}
        className={`w-[300px] h-auto object-cover ${className}`.trim()}
      />
    );
  }

  return (
    <div
      className={`relative w-[238px] h-[490px] rounded-[40px] overflow-hidden shadow-xl ring-1 ring-black/5 bg-gradient-to-br from-white via-gray-100 to-gray-200 dark:from-gray-800 dark:via-gray-700 dark:to-gray-900 ${className}`.trim()}
    >
      {/* Screen */}
      <img src={src} alt={alt} className="w-full h-full object-cover" />
    </div>
  );
} 