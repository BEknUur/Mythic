// components/PhoneMockup.tsx
import React, { useRef, useState, useEffect } from 'react'

interface PhoneMockupProps {
  /** Путь к картинке, например '/static/images/photo.png' */
  src: string
  alt?: string
  width?: number
  height?: number
  className?: string
}

export function PhoneMockup({
  src,
  alt = 'Mockup image',
  width = 375,
  height = 812,
  className = '',
}: PhoneMockupProps) {
  const [inView, setInView] = useState(false)
  const imgRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!imgRef.current) return
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true)
          obs.disconnect()
        }
      },
      { rootMargin: '200px' }
    )
    obs.observe(imgRef.current)
    return () => obs.disconnect()
  }, [])

  // Автоматически переключаем .png/.jpg → .webp
  const webpSrc = src.replace(/\.(png|jpe?g)$/, '.webp')

  return (
    <div
      ref={imgRef}
      className={`overflow-hidden rounded-2xl shadow-lg ${className}`}
      style={{ width, height }}
    >
      {inView && (
        <picture>
          {/* WebP-версия, если есть */}
          <source type="image/webp" srcSet={webpSrc} />
          {/* Фолбэк на исходное расширение */}
          <img
            src={src}
            alt={alt}
            width={width}
            height={height}
            loading="lazy"
            decoding="async"
            style={{ objectFit: 'cover', width: '100%', height: '100%' }}
          />
        </picture>
      )}
    </div>
  )
}
