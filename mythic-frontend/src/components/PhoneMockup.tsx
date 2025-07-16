// components/PhoneMockup.tsx
import React, { useRef, useState, useEffect } from 'react'

interface PhoneMockupProps {
  src: string
  alt?: string
  width?: number
  height?: number
  // новые пропсы
  containerClassName?: string
  imgClassName?: string
}

export function PhoneMockup({
  src,
  alt = 'Mockup image',
  width = 375,
  height = 812,
  containerClassName = '',
  imgClassName = '',
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

  // Пусть остаётся WebP-источник и ленивый лайзинг как раньше
  const webpSrc = src.replace(/\.(png|jpe?g)$/, '.webp')

  return (
    <div
      ref={imgRef}
      className={`relative overflow-hidden rounded-2xl shadow-lg ${containerClassName}`}
      style={{ width, height }}
    >
      {inView && (
        <picture>
          <source type="image/webp" srcSet={webpSrc} />
          <img
            src={src}
            alt={alt}
            loading="lazy"
            decoding="async"
            className={`absolute ${imgClassName}`}
          />
        </picture>
      )}
    </div>
  )
}
